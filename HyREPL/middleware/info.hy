(import sys inspect)

(import
  [hy.models.symbol [HySymbol]]
  [HyREPL.ops [ops]]
  [HyREPL.middleware.eval [eval-module]])

(require HyREPL.ops)


(defn resolve-symbol [sym]
  (setv sym (.replace sym "-" "_"))
  (when (.endswith sym "?")
    (setv sym (+ "is-" (slice sym 0 -1))))
  (try
    (eval (HySymbol sym) (. eval-module --dict--))
    (except [e NameError]
      None)))


(defn get-info [symbol]
  (let [[s (resolve-symbol symbol)]]
    (if (not (none? s))
      {"doc" (if (hasattr s '--doc--)
               (. s --doc--)
               "No doc string")
       "name" symbol
       "ns" (cond
              [(hasattr s '--package--) (. s --package--)]
              [(hasattr s '--module--) (. s --module--)]
              [True "Hy"])
       "static" "true"}
      {})))


(defop info [session msg transport]
       {"doc" "Provides information on symbol"
        "requires" {"symbol" "The symbol to look up"}
        "returns" {"status" "done"}}
       (print msg :file sys.stderr)
       (let [[info (get-info (.get msg "symbol"))]]
         (.write session
                 {"value" info
                  "id" (.get msg "id")
                  "status" (if (empty? info) ["no-info" "done"] ["done"])}
                 transport)))
