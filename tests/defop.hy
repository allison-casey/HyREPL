(import sys)

(import [HyREPL.ops [ops find-op]])
(require HyREPL.ops)   ; for `defop`

(defmacro assert-multi [&rest cases]
  (let [[s (list-comp `(assert ~c) [c cases])]]
    `(do ~s)))

(defclass MockSession []
  [[--init--
    (fn [self]
      (setv self.messages [])
      None)]
   [write
    (fn [self msg transport]
      (.append self.messages msg))]])

(defn test-defop-verify-message []
  (let [[m (MockSession)]]
    (defop "vtest1-requires" [s m t]
           {"requires" {"foo" "the foo"}}
           (.write s (.get m "foo") t))
    ((find-op "vtest1-requires")
              m {} None)
    ((find-op "vtest1-requires")
              m {"foo" 'bar} None)
    (assert-multi (= (len m.messages) 2)
                  (!= (first m.messages) {})
                  (= (second m.messages) 'bar))))


(defn test-defop-success []
  (defop o1 [] {})
  (defop o2 [a] {})
  (defop o3 [] {"doc" "I'm a docstring!"})
  (defop "o4-something.foo" [] {})
  (assert-multi
    (in "o1" ops)
    (in "o2" ops)
    (in "o3" ops)
    (in "o4-something.foo" ops)
    (= (:desc (get ops "o3")) {"doc" "I'm a docstring!"})))

(defmacro macroexpand-multi-assert-fail [&rest macros]
  (let [[s (list-comp `(try
                         (macroexpand ~m)
                         (except [e hy.errors.HyMacroExpansionError])
                         (else
                           (assert False (.format "Compiling {} should have failed" ~m))))
             [m macros])]]
  `(do ~s)))

(defn test-defop-fail []
  (macroexpand-multi-assert-fail
    '(defop op1 "no" {})
    '(defop op1 [] "maybe")))
