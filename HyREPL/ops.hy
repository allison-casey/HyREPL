;; https://github.com/clojure/tools.nrepl/blob/34093111923031888f8bf6da457aaebc3381d67e/doc/ops.md
;; Missing ops:
;; - ls-sessions
;; Incomplete ops:
;; - load-file (file name not handled)
;; - eval

(import sys)

(defn test [session msg transport]
  
  (.write session 
          {"encoding" "edn"
          "data" (+ "{:remote true, :client-id "  (str  (get msg "id")) ", :name \"localhost:1337\", :dir \"/home/fox/github/hyrepl\", :type \"lein-light-nrepl\", :commands [:editor.eval.clj :editor.clj.doc :editor.cljs.doc :editor.clj.hints :editor.cljs.hints :docs.clj.search :docs.cljs.search :editor.eval.clj.sonar :editor.eval.clj.cancel :editor.eval.cljs :cljs.compile]}")          
          "op" "client.settings"
          "status" ["done"]
          "id" (get msg "id")
          } 
          transport)
  )

(def ops {"client.init" {:f test :desc {}}})


(defmacro/g! defop [name args desc &rest body]
  (if-not (instance? (, str HySymbol) name)
    (macro-error name "Name must be a symbol or a string."))
  (if-not (instance? hy.models.list.HyList args)
    (macro-error args "Arguments must be a list."))
  (if-not (instance? hy.models.dict.HyDict desc)
    (macro-error desc "Description must be a dictionary."))
  (let [[fn-checked
         `(fn ~args
            (let [[g!failed False]]
              (for [g!r (.keys (.get ~desc "requires" {}))]
                (unless (in g!r (second ~args))
                  (.write (first ~args)
                          {"status" ["done"]
                           "id" (.get (second ~args) "id")
                           "missing" (str g!r)} (nth ~args 2))
                  (setv g!failed True)
                  (break)))
              (unless g!failed
                (do
                  ~@body))))]
        [n (str name)]
        [o {:f fn-checked :desc desc}]]
    `(assoc ops ~n ~o)))


(defn find-op [op]
  (if (in op ops)
    (:f (get ops op))
    (fn [s m t]
      (print (.format "Unknown op {} called" op) :file sys.stderr)
      (.write s {"status" ["done"] "id" (.get m "id")} t))))


(defop clone [session msg transport]
       {"doc" "Clones a session"
       "requires" {}
       "optional" {"session" "The session to be cloned. If this is left out, the current session is cloned"}
       "returns" {"new-session" "The ID of the new session"}}
       (import [HyREPL.session [Session]]) ; Imported here to avoid circ. dependency
       (let [[s (Session)]]
         (.write session {"status" ["done"] "id" (.get msg "id") "new-session" (str s)} transport)))


(defop close [session msg transport]
       {"doc" "Closes the specified session"
        "requires" {"session" "The session to close"}
        "optional" {}
        "returns" {}}
       (.write session
               {"status" ["done"]
                "id" (.get msg "id")
                "session" session.uuid}
               transport)
       (import [HyREPL.session [sessions]]) ; Imported here to avoid circ. dependency
       (try
         (del (get sessions (.get msg "session" "")))
         (catch [e KeyError]))
       (.close transport))


(defn make-version [&optional [major 0] [minor 0] [incremental 0]]
  {"major" major
   "minor" minor
   "incremental" incremental
   "version-string" (.join "." (map str [major minor incremental]))})


(defop describe [session msg transport]
       {"doc" "Describe available commands"
       "requires" {}
       "optional" {"verbose?" "True if more verbose information is requested"}
       "returns" {"aux" "Map of auxiliary data"
                 "ops" "Map of operations supported by this nREPL server"
                 "versions" "Map containing version maps, for example of the nREPL protocol supported by this server"}}
       ; TODO: don't ignore verbose argument
       ; TODO: more versions: Python, Hy
       (.write session
               {"status" ["done"]
               "id" (.get msg "id")
               "versions" {"nrepl" (make-version 0 2 7)
                           "java" (make-version)
                           "clojure" (make-version)}
               "ops" (dict-comp k (:desc v) [(, k v) (.items ops)])
               "session" session.uuid}
               transport))


(defop stdin [session msg transport]
       {"doc" "Feeds value to stdin"
       "requires" { "value" "value to feed in" }
       "optional" {}
       "returns" {"status" "\"need-input\" if more input is needed"}}
       (.put sys.stdin (get msg "value"))
       (.task-done sys.stdin))
