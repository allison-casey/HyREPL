(import sys [uuid [uuid4]] [threading [Lock]])
(import
  [HyREPL [bencode]]
  [HyREPL.ops [find-op]])


(def sessions {})


(defclass Session [object]
  [[status ""]
   [eval-id ""]
   [repl None]
   [last-traceback None]
   [--init--
     (fn [self]
       (setv self.uuid (str (uuid4)))
       (assoc sessions self.uuid self)
       (setv self.lock (Lock))
       None)]
   [--str--
     (fn [self]
       self.uuid)]
   [--repr--
     (fn [self]
       self.uuid)]
   [write
     (fn [self msg transport]
       (assert (in "id" msg))
       (unless (in "session" msg)
         (assoc msg "session" self.uuid))
       (print "out:" msg :file sys.stderr)
       (try
         (.sendall transport (bencode.encode msg))
         (except [e OSError]
           (print (.format "Client gone: {}" e) :file sys.stderr))))]
   [handle
     (fn [self msg transport]
       (print "in:" msg :file sys.stderr)
       ((find-op (.get msg "op")) self msg transport))]])
