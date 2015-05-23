(import time sys [HyREPL.server [start-server]])

(defmain [&rest args]
  (let [[port 1337]]
    (while True
      (try
        (start-server "127.0.0.1" port)
        (catch [e OSError]
          (setv port (inc port)))
        (else
          (print (.format "Listening on {}" port))
          (while True
            (time.sleep 1)))))))

