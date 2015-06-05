; Inspired by
; https://github.com/clojure-emacs/cider-nrepl/blob/master/src/cider/nrepl/middleware/complete.clj

(import sys)

(import hy.macros hy.compiler)

(import [HyREPL.ops [ops]])
(require HyREPL.ops)

(import [HyREPL.middleware.eval [eval-module]])


(defn get-names-types [d]
  (sorted
    (list-comp
      {:name (.replace n "_" "-")
       :type (. (type (get d n)) --name--)}
      [n (filter (fn [x] (instance? str x)) (.keys d))])
    :key (fn [x] (:name x))))


(defn get-completions [sym extra]
  (let [[everything []]]
    (.extend everything (get-names-types eval-module.--dict--))
    (.extend everything (get-names-types (locals)))
    (.extend everything (get-names-types --builtins--))
    (.extend everything (get-names-types (globals)))
    ;; Only import macros in current namespace
    (.extend everything (get-names-types hy.macros.-hy-macros))
    (for [k (.keys hy.macros.-hy-macros)]
      (.extend everything (get-names-types (get hy.macros.-hy-macros k))))
    (.extend everything (get-names-types hy.compiler.-compile-table))
    (list-comp
      {"candidate" (:name c)
       "type" (:type c)}
      [c (filter (fn [x] (and (instance? str (:name x)) (in sym (:name x))))
       everything)])))


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



