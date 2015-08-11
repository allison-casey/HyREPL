(import sys inspect)

(import
  [hy.models.symbol [HySymbol]]
  [HyREPL.ops [ops]]
  [HyREPL.middleware.eval [eval-module]])

(require HyREPL.ops)


(defn resolve-symbol [sym]
  (setv sym (.replace sym "-" "_"))
  (when (.endswith sym "?")
    (setv sym (+ "is-" (cut sym 0 -1))))
  (try
    (eval (HySymbol sym) (. eval-module --dict--))
    (except [e NameError]
      None)))


(defn get-info [symbol]
  (let [[s (resolve-symbol symbol)]
        [d (inspect.getdoc s)]
        [c (inspect.getcomments s)]
        [sig (and (callable s) (try (inspect.signature s) (except [e Exception])))]
        [rv {}]]
    (print "Got object " s " for symbol " symbol)
    (when (not (none? s))
      (.update rv {"doc" (or d c "No doc string")
                   "static" "true"
                   "ns" (or (. (inspect.getmodule s) --name--) "Hy")
                   "name" symbol})
      (try
        (.update rv
                 "file" (inspect.getfile s))
        (except [e TypeError]))
      (when sig
        (.update rv  {"arglists-str" (str sig)})))
    rv))


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
