(import traceback)

(defn is-callable [f]
  (hasattr f "__call__"))

(defn get-workaround [code]
  (let [rv]
    (for [w (.keys hints)]
      (when (or (and (callable? w) (w code)) (= w code))
        (setv rv (get hints w))
        (break)))
    (if (is-not rv None)
      (fn [s msg t]
        (.write s {"out" "success" "id" (.get msg "id")} t)
        (rv s msg (fn [m]
                    (assoc m "id" (.get msg "id"))
                    (.write s m t)))
        (.write s {"status" ["done"] "id" (.get msg "id")} t))
      None)))

(defn work-around-init-1 [session msg w]
  (w {"value" ":" "ns" "Hy"}))

(defn work-around-init-2 [session msg w]
  (w {"value" "[\"/\" \":\"]" "ns" "Hy"}))

(defn work-around-init-3 [s m w]
  (w {"value" "None"}))

(defn work-around-init-4 [s m w]
  (w {"value" "\"not installed\""}))

(defn work-around-traceback [session msg w]
  (let [[items []]]
    (with [session.lock]
      (for [i (traceback.extract_tb session.last_traceback)]
        (.append items (.format "{}({}:{})"
                                (get i 2)
                                (first i)
                                (second i)))))
    (w {"value" (+ "[\n\b\n" (.join "\n" items) "\n\b\n nil nil nil]") "ns" (.get msg "ns" "Hy")})))

(defn work-around-last [session msg w]
  (w {"value" "nil"}))

(defn work-around-fake [session msg w]
  (w {"value" "[\":\" nil]"}))

(defn work-around-namespace [session msg w]
  (w {"value" "\"Hy\""}))

(def hints
  { ; Workarounds for Fireplace
  (+ "(do (println \"success\") (symbol (str (System/getProperty \"path.separator\") "
    "(System/getProperty \"java.class.path\"))))")
  work-around-init-1
  "[(System/getProperty \"path.separator\") (System/getProperty \"java.class.path\")]"
  work-around-init-2
  "[(symbol (str \"\\n\\b\" (apply str (interleave (repeat \"\\n\") (map str (.getStackTrace *e)))) \"\\n\\b\\n\")) *3 *2 *1]"
  work-around-traceback
  "(*1 1)" work-around-last
  "(*2 2)" work-around-last
  "(*3 3)" work-around-last
  "[(System/getProperty \"path.separator\") (System/getProperty \"fake.class.path\")]"
  work-around-fake

   ; Workarounds for cider
  "(str *ns*)"
  work-around-namespace
  "(when (clojure.core/resolve 'clojure.main/repl-requires)\n      (clojure.core/map clojure.core/require clojure.main/repl-requires))"
  work-around-init-3
   "(try\n      (require \'cider.nrepl.version)\n      (:version-string @(resolve \'cider.nrepl.version/version))\n    (catch Throwable _ \"not installed\"))"
   work-around-init-4
  })
