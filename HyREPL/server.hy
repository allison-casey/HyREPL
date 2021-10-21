(import
  [functools [partial]]
  sys
  threading
  time
  [socketserver [ThreadingMixIn TCPServer BaseRequestHandler]])

(import [HyREPL [bencode session]])

; TODO: move these includes somewhere else
(import [HyREPL.middleware [test eval complete info]])

(require [hy.contrib.walk [let]])

(defclass ReplServer [ThreadingMixIn TCPServer]
  (setv allow-reuse-address True))

(defclass ReplRequestHandler [BaseRequestHandler]
  (setv session None)

  (defn --init-- [self cooperative &rest args]
    (setv self.cooperative cooperative)
    (.--init-- (super) #*args))

  (defn handle [self]
    (print "New client" :file sys.stderr)
    (let [buf (bytearray)
          tmp None
          msg (,)]
      (while True
        (try
          (setv tmp (.recv self.request 1024))
          (except [e OSError]
            (break)))
        (when (= (len tmp) 0)
          (break))
        (.extend buf tmp)
        (try
          (do
            (setv m (bencode.decode buf))
            (.clear buf)
            (.extend buf (get m 1)))
          (except [e Exception]
            (print e :file sys.stderr)
            (continue)))
        (when (is self.session None)
          (setv self.session (.get session.sessions (.get (get m 0)
                                                          "session")))
          (when (is self.session None)
            (setv self.session (session.Session))))
        (.handle self.session (get m 0) self.request self.cooperative))
      (print "Client gone" :file sys.stderr))))


(defn start-server [&optional [ip "127.0.0.1"] [port 1337] [cooperative False]]
  (let [s (ReplServer (, ip port) (partial ReplRequestHandler cooperative))
        t (threading.Thread :target s.serve-forever)]
    (setv t.daemon True)
    (.start t)
    (, t s)))

(defn poll []
  "Evaluate all expressions that have
   been sent to the server since the
   last time this function was called.

   Only applies to a cooperative server"
  (eval.process-delayed-evaluations))

(defmain [&rest args]
  (setv port
        (if (> (len args) 0)
            (try
              (int (last args))
              (except [_ ValueError]
                1337))
            1337))
  (while True
    (try
       (start-server "127.0.0.1" port)
       (except [e OSError]
         (setv port (inc port)))
       (else
         (print (.format "Listening on {}" port) :file sys.stderr)
         (while True
           (time.sleep 1))))))
