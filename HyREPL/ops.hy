;; https://github.com/clojure/tools.nrepl/blob/34093111923031888f8bf6da457aaebc3381d67e/doc/ops.md
;; Missing ops:
;; - interrupt
;; - ls-sessions
;; Incomplete ops:
;; - load-file (file name not handled)
;; - eval

(import sys)
(import
  [HyREPL.eval [HyREPL :as repl]]
  [HyREPL.workarounds [hints work-around-it]])


(def ops {})
(defmacro defop [name args desc &rest body]
  (if-not (instance? HySymbol name)
    (macro-error name "Name must be a symbol."))
  (if-not (instance? hy.models.list.HyList args)
    (macro-error args "Arguments must be a list."))
  (if-not (instance? hy.models.dict.HyDict desc)
    (macro-error desc "Description must be a dictionary."))
  ; TODO: verify messages: all req'd keys present?
  (let [[n (.replace (str name) "_" "-")]
        [f `(fn ~args ~@body)]
        [o {:f f :desc desc}]]
    `(assoc ops ~n ~o)))


(defn find-op [op]
  (if (in op ops)
    (:f (get ops op))
    (fn [s m t]
      (print (.format "Unknown op {} called" op) :file sys.stderr)
      (.write s {"status" ["done"] "id" (.get m "id")} t))))


(defop eval [session msg transport]
       {"doc" "Evaluates code."
       "requires" {"code" "The code to be evaluated"
                  "session" "The ID of the session in which the code will be evaluated"}
       "optional" {"id" "An opaque message ID that will be included in the response"}
       "returns" {"ex" "Type of the exception thrown, if any. If present, `value` will be absent."
                 "ns" "The current namespace after the evaluation of `code`. For HyREPL, this will always be `Hy`."
                 "root-ex" "Same as `ex`"
                 "values" "The values returned by `code` if execution was successful. Absent if `ex` and `root-ex` are present"}}
       (if (in (get msg "code") (.keys hints))
         (work-around-it session msg transport)
         (.start
           (repl msg session
                 (fn [x] (.write session x transport))))))


(defop load-file [session msg transport]
       {"doc" "Loads a body of code. Delegates to `eval`"
       "requires" {"file" "full body of code"}
       "optional" {"file-name" "name of the source file, for example for exceptions"
                  "file-path" "path to the source file"}
       "returns" (get (:desc (get ops "eval")) "returns")}
       (let [[code (-> (get msg "file")
                     (.split " " 2)
                     (get 2))]]
         (print (.strip code) :file sys.stderr)
         (assoc msg "code" code)
         (del (get msg "file"))
         ((find-op "eval") session msg transport)))


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
