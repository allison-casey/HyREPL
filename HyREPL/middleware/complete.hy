; Inspired by
; https://github.com/clojure-emacs/cider-nrepl/blob/master/src/cider/nrepl/middleware/complete.clj

(import sys)

(import hy.macros hy.compiler hy.core.language)

(import [HyREPL.ops [ops]])
(require HyREPL.ops)

(import [HyREPL.middleware.eval [eval-module]])


(defn make-type [item override-type]
  (let [[t (type item)]]
    (cond
      [(and (is-not override-type None) (= t (. make-type --class--)))
       override-type]
      [(= t (. dir --class--)) "function"]
      [(= t dict) "namespace"]
      [True (. t --name--)])))


(defop complete [session msg transport]
       {"doc" "Returns a list of symbols matching the specified (partial) symbol."
        "requires" {"symbol" "The symbol to look up"
                    "session" "The current session"}
        "optional" {"context" "Completion context"
                    "extra-metadata" "List of additional metadata"}
        "returns" {"completions" "A list of possible completions"}}
       (print "Complete: " msg :file sys.stderr)
       (.write session {"id" (.get msg "id")
                        "completions" (get-completions (.get msg "symbol") (.get msg "extra-metadata" []))
                        "status" ["done"]}
               transport))

(defn get-completions-core [stem dict &optional override-type]
  (if (in "." stem)
    (let [[s (.split stem "." 1)]
          [m (.get dict (first s))]]
      (list-comp
        {:name (+ (first s) "." (:name x))
         :type (:type x)}
        [x (if (none? m)
             []
             (get-completions-core (second s)
                                   (if (hasattr m '--dict--)
                                     (. m --dict--)
                                     (. m --class-- --dict--))))]))
    ; TODO:
    ; [ ] sort items such that '--foo--' comes after 'foo'
    (sorted (list-comp
              {:name (.replace k "_" "-")
               :type (make-type v override-type)}
              [(, k v) (.items dict)]
              (and (instance? str k) (.startswith k stem)))
            :key (fn [x] (:name x)))))

(defn get-completions [stem &optional extra]
  ; TODO:
  ; - [X] macros, compiler defined stuff like list-comp
  ; - [X] user defined macros
  ; - [ ] don't ignore extra data
  ; - [X] deduplication
  (let [[seen (set)]
        [f (fn [x]
             (print x)
             (if (in (:name x) seen)
               False
               (do
                 (.add seen (:name x))
                 True)))]]
    (list-comp
      {"candidate" (:name c)
       "type" (:type c)}
      [c (+ (get-completions-core stem eval-module.--dict--)
            (get-completions-core stem hy.macros.-hy-macros 'macro)
            (get-completions-core stem hy.core.language.--dict-- 'macro)
            (reduce +
                    (list-comp
                      (get-completions-core stem n 'macro)
                      [n (.values hy.macros.-hy-macros)]))
            (get-completions-core stem hy.compiler.-compile-table 'macro)
            (get-completions-core stem (get eval-module.--dict-- "__builtins__")))]
      (f c))))
