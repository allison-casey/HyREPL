(import sys [uuid [uuid4]])
(import
  [HyREPL [bencode]]
  [HyREPL.ops [find-op]])


(def sessions {})


(defclass Session [object]
  [[status ""]
   [eval-id ""]
   [eval-msg ""]
   [last-traceback None]
   [--init--
     (fn [self]
       (setv self.uuid (str (uuid4)))
       (assoc sessions self.uuid self)
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
       (assoc msg "session" self.uuid)
       (print "out:" msg :file sys.stderr)
       (try
         (.sendall transport (bencode.encode msg))
         (except [e OSError]
           (print (.format "Client gone: {}" e) :file sys.stderr))))]
   [handle
     (fn [self msg transport]
       (print "in:" msg :file sys.stderr)
       ((find-op (.get msg "op")) self msg transport))]])
