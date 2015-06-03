(import traceback)

(defn work-around-it [session msg transport]
  ((get hints (get msg "code"))
   session msg (fn [m]
                 (assoc m "id" (get msg "id"))
                 (.write session m transport))))

(defn work-around-init-1 [session msg w]
  (w {"out" "success"})
  (w {"value" ":" "ns" "Hy"})
  (w {"status" ["done"]}))

(defn work-around-init-2 [session msg w]
  (w {"out" "success"})
  (w {"value" "[\"/\" \":\"]" "ns" "Hy"})
  (w {"status" ["done"]}))

(defn work-around-traceback [session msg w]
  (w {"out" "success"})
  (let [[items []]]
    (for [i (traceback.extract_tb session.last_traceback)]
      (.append items (.format "{}({}:{})"
                              (get i 2)
                              (first i)
                              (second i))))
    (w {"value" (+ "[\n\b\n" (.join "\n" items) "\n\b\n nil nil nil]") "ns" (.get msg "ns" "Hy")}))
  (w {"status" ["done"]}))

(defn work-around-last [session msg w]
  (w {"out" "success"})
  (w {"value" "nil"})
  (w {"status" ["done"]}))

(defn work-around-fake [session msg w]
  (w {"out" "success"})
  (w {"value" "[\":\" nil]"})
  (w {"status" ["done"]}))

(defn work-around-namespace [session msg w]
  (w {"out" "success"})
  (w {"value" "\"user\""}) ; XXX: use "Hy" instead?
  (w {"status" ["done"]}))

(def hints {
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
  "(str *ns*)"
  work-around-namespace
  })
