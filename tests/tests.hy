(import os queue socket sys threading time)
(import
  [io [StringIO]]
  [socketserver [ThreadingMixIn UnixStreamServer]])

(import [HyREPL.bencode [encode decode decode-multiple]])
(import [HyREPL.server [ReplRequestHandler]])

(defreader b [expr] `(bytes ~expr "utf-8"))

(defmacro assert-multi [&rest cases]
  (let [[s (list-comp `(assert ~c) [c cases])]]
    `(do ~s)))

(def sock "/tmp/HyREPL-test")
(defclass ReplUnixStreamServer [ThreadingMixIn UnixStreamServer])
(defclass TestServer []
  [[--init--
     (fn [self]
       (try
         (os.unlink sock)
         (except [e FileNotFoundError]))
       (setv self.o sys.stderr)
       (setv self.s (ReplUnixStreamServer sock ReplRequestHandler))
       (setv self.t (threading.Thread :target (. self s serve-forever)))
       (setv (. self t daemon) True)
       (setv sys.stderr (StringIO))
       None)]
   [--enter--
     (fn [self]
       (.start self.t)
       self)]
   [--exit--
     (fn [self &rest args]
       (.shutdown self.s)
       (setv sys.stderr self.o)
       (.join self.t))]])


(defn soc-send [message &optional [return-reply True]]
  (let [[s (socket.socket :family socket.AF-UNIX)]
        [r []]]
    (.connect s sock)
    (.sendall s (encode message))
    (when return-reply
      (.setblocking s False)
      (let [[buf #b""]]
        (while True
          (try
            (+= buf (.recv s 1))
            (except [e BlockingIOError]))
          (try
            (setv (, resp rest) (decode buf))
            (except [e Exception]
              (continue)))
          (setv buf rest)
          (.append r resp)
          (when (in "done" (.get resp "status" []))
            (break)))))
    (.close s)
    r))


(defn test-bencode []
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


(defn test-code-eval []
  "simple eval
  Example output from the server:
  [{'session': '0361c419-ef89-4a86-ae1a-48388be56041', 'ns': 'Hy', 'value': '4'}, 
               {'status': ['done'], 'session': '0361c419-ef89-4a86-ae1a-48388be56041'}]
  "
  (with [[(TestServer)]]
        (let [[code {"op" "eval" "code" "(+ 2 2)"}]
              [ret (soc-send code)]
              [(, value status) ret]]
          (assert-multi
            (= (len ret) 2)
            (= (. value ["value"]) "4")
            (in "done" (. status ["status"]))
            (= (. value ["session"]) (. status ["session"]))))))


(defn test-stdout-eval []
  "stdout eval
  Example output from the server:
  [{'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'ns': 'Hy', 'value': 'None'},
               {'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'out': 'Hello World\n'},
               {'status': ['done'], 'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4'}]
  "
  (with [[(TestServer)]]
        (let [[code {"op" "eval" "code" "(print \"Hello World\")"}]
              [ret (soc-send code)]
              [(, value out status) ret]]
          (assert-multi
            (= (len ret) 3)
            (= (. value ["value"]) "None")
            (= (. out ["out"]) "Hello World\n")
            (in "done" (. status ["status"]))
            (= (. value ["session"]) (. out ["session"]) (. status ["session"]))))))


(defn stdin-send [code my-queue]
  (.put my-queue (soc-send code)))


(defn test-stdin-eval []
    "stdin eval
    The current implementation will send all the responses back
    into the first thread which dispatched the (def...), so we throw
    it into a thread and add a Queue to get it.
    Bad hack. But it works.

    Example output from the server:
        [{'status': ['need-input'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'},
         {'session': 'ec100813-8e76-4d69-9116-6460c1db4428', 'ns': 'Hy', 'value': 'test'},
         {'status': ['done'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'}]
    "
    (with [[(TestServer)]]
          (let [[my-queue (queue.Queue)]
                [code {"op" "eval" "code" "(def a (input))"}]
                [t (threading.Thread :target stdin-send :args [code my-queue])]]
            (.start t)
            ; Might encounter a race condition where
            ; we send stdin before we eval (input)
            (time.sleep 0.5)

            (soc-send {"op" "stdin" "value" "test"} :return-reply False)

            (.join t)

            (let [[ret (.get my-queue)]
                  [(, input-request value status) ret]]
              (assert-multi
                (= (len ret) 3)
                (= (. value ["value"]) "test")
                (= (. input-request ["status"]) ["need-input"])
                (in "done" (. status ["status"]))
                (= (. value ["session"]) (. input-request ["session"]) (. status ["session"])))))))
