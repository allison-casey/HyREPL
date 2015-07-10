;; This stuff is really ugly and should be nuked ASAP.
; It prevents us from having to fork all sorts of clients though, so we got that going for, which is nice.

(import traceback)

(def workarounds {})
(defmacro def-workaround [match args &rest body]
  `(assoc workarounds ~match (fn ~args ~@body)))

(defn is-callable [f]
  (hasattr f "__call__"))

(defn get-workaround [code]
  (let [rv]
    (for [w (.keys workarounds)]
      (when (or (and (callable? w) (w code)) (= w code))
        (setv rv (get workarounds w))
      (break)))
    (if (none? rv)
      (fn [s m] (get m "code"))
      rv)))

; Workarounds for Fireplace
(def-workaround (+ "(do (println \"success\") "
                   "(symbol (str (System/getProperty \"path.separator\") "
                   "(System/getProperty \"java.class.path\"))))")
                [session msg]
                ":")

(def-workaround (+ "[(System/getProperty \"path.separator\") "
                   "(System/getProperty \"java.class.path\")]")
                [session msg]
                "[\"/\" \":\"]")

(def-workaround (+ "[(symbol (str \"\\n\\b\" (apply str (interleave "
                   "(repeat \"\\n\") (map str (.getStackTrace *e)))) "
                   "\"\\n\\b\\n\")) *3 *2 *1]")
                [session msg]
                (let [[items []]]
                  (with [session.lock]
                    (for [i (traceback.extract-tb session.last-traceback)]
                      (.append items (.format "{}({}:{})"
                                              (get i 2)
                                              (first i)
                                              (second i)))))
                  (+ "(quote " "[\n\b\n" (.join "\n" items) "\n\b\n nil nil nil]" ")")))

(def-workaround (fn [c] (in c ["(*1 1)" "(*2 2)" "(*3 3)"]))
                [session msg]
                "\"None\"")

(def-workaround (+ "[(System/getProperty \"path.separator\") "
                   "(System/getProperty \"fake.class.path\")]")
                [session msg]
                "[\":\" \"None\"]")

(def-workaround (fn [c] (.startswith c "(clojure.walk/macroexpand-all (quote"))
                [session msg]
                (.replace (get msg "code") "clojure.walk/macroexpand-all" "macroexpand" 1))

; Workarounds for cider
(def-workaround "(str *ns*)"
                [session msg]
                "\"Hy\"")

(def-workaround (+ "(when (clojure.core/resolve 'clojure.main/repl-requires)\n "
                   "     (clojure.core/map clojure.core/require clojure.main/"
                   "repl-requires))")
                [session msg]
                "\"None\"")

(def-workaround (+ "(try\n      (require \'cider.nrepl.version)\n      "
                   "(:version-string @(resolve \'cider.nrepl.version/version))"
                   "\n    (catch Throwable _ \"not installed\"))")
                [session msg]
                "\"not installed\"")

(def-workaround "(clojure.stacktrace/print-cause-trace *e)"
                [session msg]
                "(do (import traceback) (.print_last traceback))")

