;; https://github.com/clojure/tools.nrepl/blob/34093111923031888f8bf6da457aaebc3381d67e/doc/ops.md
;; Missing ops:
;; - describe
;; - interrupt
;; - ls-sessions
;; Incomplete ops:
;; - load-file (file name not handled)
;; - eval
;
(import sys threading)
(import
  [HyREPL.eval [HyREPL]]
  [HyREPL.workarounds [hints work-around-it]])


(def descriptions {})


(defn set-description [handles &optional requires expects]
  (fn [f]
    ; TODO: make this do more useful things
    (assoc descriptions (tuple (.keys handles)) f)))


(defn find-op [op]
  (let [r]
    (for [[args f] (.items descriptions)]
      (when (in op args)
        (setv r f)
        (break)))
    r))


(with-decorator (set-description {"eval" {}})
  (defn eval-expr [session msg transport]
    (if (in (.get msg "code") (.keys hints))
      (work-around-it session msg transport)
      (let [[d (HyREPL msg session (fn [x] (.write session x transport)))]]
        (.start d)))))


(with-decorator (set-description {"load-file" {}})
  (defn load-file [session msg transport]
    (let [[code (get (.split (get msg "file") " " 2) 2)]]
      (print code :file sys.stderr)
      (assoc msg "code" code)
      (del (get msg "file"))
      ((find-op "eval") session msg transport))))


(with-decorator (set-description {"clone" {}})
  (defn clone-session [session msg transport]
    (import [HyREPL.session [Session]]) ; Imported here to avoid circular dependency
    (let [[s (Session)]] ; TODO: actual cloning: globals dictionary
      (.write session {"status" ["done"] "id" (.get msg "id") "new-session" (str s)} transport))))


(with-decorator (set-description {"close" {}})
  (defn close-session [session msg transport]
    (import [HyREPL.session [sessions]]) ; Imported here to avoid circular dependency
    (try
      (del (get sessions (.get msg "session" "")))
      (catch [e KeyError]))
    (.close transport)))


(with-decorator (set-description {"describe" {}})
  (defn describe [session msg transport]
    (.write session
            {"status" ["done"]
            "id" (.get msg "id")
            "versions" { "nrepl" {"major" 2 "minor" 1 }} ; XXX: java and clojure versions?
            "ops" {} ; XXX
            "session" session.uuid}
            transport)))


(with-decorator (set-description
                  {"stdin" {"doc" "bla" "requires" "stdin" "optional" {} "returns" {"status" "\"need-input\" if input is needed"}}}
                  (, "session")
                  (, "eval"))
  (defn add-stdin [session msg transport]
    (.put sys.stdin (get msg "value"))
    (.task-done sys.stdin)))
