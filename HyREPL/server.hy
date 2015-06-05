(import
  sys
  threading
  time
  [socketserver [ThreadingMixIn TCPServer BaseRequestHandler]])

(import [HyREPL [bencode session]])

; TODO: move these includes somewhere else
(import [HyREPL.middleware [test eval complete]])

(defclass ReplServer [ThreadingMixIn TCPServer])

(defclass ReplRequestHandler [BaseRequestHandler]
  [[session None]
   [handle
     (fn [self]
       (print "New client" :file sys.stderr)
       (let [[buf (bytearray)]
             [msg (,)]]
         (while True
           (try
             (.extend buf (.recv self.request 1024))
             (catch [e OSError]
               (break)))
           (when (= (len buf) 0)
             (break))
           (try
             (do
               (setv m (bencode.decode buf))
               (.clear buf)
               (.extend buf (get m 1)))
             (catch [e Exception]
               (print e :file sys.stderr)
               (continue)))
           (when (is self.session None)
             (setv self.session (.get session.sessions (.get (get m 0)
                                                                 "session")))
             (when (is self.session None)
               (setv self.session (session.Session))))
           (.handle self.session (get m 0) self.request))
         (print "Client gone" :file sys.stderr)))]])


(defn start-server [ip port]
  (let [[s (ReplServer (, ip port) ReplRequestHandler)]
        [t (threading.Thread :target s.serve-forever)]]
    (setv t.daemon True)
    (.start t)
    (, t s)))


(defmain [&rest args]
  (let [[port 1337]]
    (while True
      (try
        (start-server "127.0.0.1" port)
        (catch [e OSError]
          (setv port (inc port)))
        (else
          (print (.format "Listening on {}" port) :file sys.stderr)
          (while True
            (time.sleep 1)))))))
