(import sys)
(import [HyREPL.bencode [encode decode decode-multiple]])

(defreader b [expr] `(bytes ~expr "utf-8"))

(defmacro assert-multi [&rest cases]
  (let [[s (list-comp `(assert ~c) [c cases])]]
    `(do ~s)))

(defn test_bencode []
  (let [[d {"foo" 42 "spam" [1 2 "a"]}]]
    (assert (= d (-> d encode decode first))))

  (let [[d (decode-multiple (+
                              #b"d5:value1:47:session36:31594b80-7f2e-4915-9969-f1127d562cc42:ns2:Hye"
                              #b"d6:statusl4:donee7:session36:31594b80-7f2e-4915-9969-f1127d562cc4e"))]]
    (assert-multi
      (= (len d) 2)
      (instance? dict (first d))
      (instance? dict (second d))
      (= (. d [0] ["value"]) "4")
      (= (. d [0] ["ns"]) "Hy")
      (instance? list (. d [1] ["status"]))
      (= (len (. d [1] ["status"])) 1)
      (= (. d [1] ["status"] [0]) "done"))))
