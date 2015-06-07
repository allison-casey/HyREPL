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
      rv
      (fn [s m] (get m "code")))))

(defn work-around-init-1 [session msg]
  ":")

(defn work-around-init-2 [session msg]
  "[\"/\" \":\"]")

(defn work-around-init-3 [s m]
  "\"None\"")

(defn work-around-init-4 [s m]
  "\"not installed\"")

(defn work-around-traceback [session msg]
  (let [[items []]]
    (with [session.lock]
      (for [i (traceback.extract_tb session.last_traceback)]
        (.append items (.format "{}({}:{})"
                                (get i 2)
                                (first i)
                                (second i)))))
    (+ "(quote " "[\n\b\n" (.join "\n" items) "\n\b\n nil nil nil]" ")")))

(defn work-around-last [session msg]
  "\"None\"")

(defn work-around-fake [session msg]
  "[\":\" \"None\"]")

(defn work-around-namespace [session msg]
  "\"Hy\"")

(defn work-around-macroexpand-all [session msg]
  (.replace (get msg "code") "clojure.walk/macroexpand-all" "macroexpand" 1))

(def hints
  { ; Workarounds for Fireplace
  (+ "(do (println \"success\") (symbol (str (System/getProperty \"path.separator\") "
    "(System/getProperty \"java.class.path\"))))")
  work-around-init-1
  "[(System/getProperty \"path.separator\") (System/getProperty \"java.class.path\")]"
  work-around-init-2
  "[(symbol (str \"\\n\\b\" (apply str (interleave (repeat \"\\n\") (map str (.getStackTrace *e)))) \"\\n\\b\\n\")) *3 *2 *1]"
  work-around-traceback
   (fn [c] (in c ["(*1 1)" "(*2 2)" "(*3 3)"])) work-around-last
  "[(System/getProperty \"path.separator\") (System/getProperty \"fake.class.path\")]"
  work-around-fake
   (fn [c] (.startswith c "(clojure.walk/macroexpand-all (quote"))
   work-around-macroexpand-all


   ; Workarounds for cider
  "(str *ns*)"
  work-around-namespace
  "(when (clojure.core/resolve 'clojure.main/repl-requires)\n      (clojure.core/map clojure.core/require clojure.main/repl-requires))"
  work-around-init-3
   "(try\n      (require \'cider.nrepl.version)\n      (:version-string @(resolve \'cider.nrepl.version/version))\n    (catch Throwable _ \"not installed\"))"
   work-around-init-4
  })
