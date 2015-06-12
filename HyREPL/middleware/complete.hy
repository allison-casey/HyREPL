; Inspired by
; https://github.com/clojure-emacs/cider-nrepl/blob/master/src/cider/nrepl/middleware/complete.clj

(import sys re)

(import
  hy.macros hy.compiler hy.core.language
  [hy.models.symbol [HySymbol]]
  [hy.completer [Completer]])

(import [HyREPL.ops [ops]])
(require HyREPL.ops)

(import [HyREPL.middleware.eval [eval-module]])


(defn make-type [item &optional override-type]
  (let [[t (type item)]]
    (cond
      [(and (is-not override-type None) (= t (. make-type --class--)))
       override-type]
      [(= t (. dir --class--)) "function"]
      [(= t dict) "namespace"]
      [True (. t --name--)])))


(defclass TypedCompleter [hy.completer.Completer]
  [[attr-matches
    (fn [self text]
      (setv m (re.match r"(\S+(\.[\w-]+)*)\.([\w-]*)$" text))
      (try
        (let [[(, expr attr) (.group m 1 3)]
              [expr (.replace expr "_" "-")]
              [attr (.replace attr "_" "-")]
              [obj (eval (HySymbol expr) (. self namespace))]
              [words (dir obj)]
              [n (len attr)]
              [matches []]]
          (for [w words]
            (when (= (slice w 0 n) attr)
              (.append matches
                       {"candidate" (.format "{}.{}" expr (.replace w "_" "-"))
                        "type" (make-type obj)})))
          matches)
        (except [e Exception]
          (print e)
          (raise e)
          [])))]
   [global-matches
    (fn [self text]
      (let [[matches []]]
        (for [p (. self path) (, k v) (.items p)]
          (when (instance? str k)
            (setv k (.replace k "_" "-"))
            (when (.startswith k text)
              (.append matches {"candidate" k
                                "type" (make-type v)}))))
        matches))]])


(defn get-completions [stem &optional extra]
  (let [[comp (TypedCompleter (. eval-module --dict--))]]
    (cond
      [(in "." stem) (.attr-matches comp stem)]
      [True (.global-matches comp stem)])))


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
