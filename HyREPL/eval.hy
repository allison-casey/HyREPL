(import types sys [threading [Thread]] traceback [io [StringIO]] [queue [Queue]])
(import
  [hy.importer [ast-compile hy-eval]]
  [hy.lex [tokenize]]
  [hy.lex.exceptions [LexException]])


(defclass HyReplSTDIN [Queue]
  ; """This is hack to override sys.stdin."""
  [[--init--
     (fn [self write msg]
       (.--init-- (super))
       (setv self.writer write)
       (setv self.msg msg)
       None)]
   [readline
     (fn [self]
       (self.writer {"status" ["need-input"] "id" (.get self.msg "id")})
       (.join self)
       (.get self))]])


(defclass HyREPL [Thread]
  ; """Repl simulation. This is a thread so hangs don't block everything."""
  [[mod (types.ModuleType "__main__")] ; TODO: make this per-session instead of global?
   [--init--
     (fn [self msg session writer]
       (.--init-- (super))
       (setv self.writer writer)
       (setv self.msg msg)
       (setv self.session session)
       (setv sys.stdin (HyReplSTDIN writer msg))
       None)]
   [run
     (fn [self]
       (let [[code (get self.msg "code")]]
         (try
           (setv self.tokens (tokenize code))
           (catch [e Exception]
             (.format-excp self (sys.exc-info))
             (self.writer {"status" ["done"] "id" (.get self.msg "id")}))
           (else
             ; TODO: add 'eval_msg' updates too the current session
             (let [[oldout sys.stdout]]
               (for [i self.tokens]
                 (let [[p (StringIO)]]
                   (try
                     (do
                       (setv sys.stdout (StringIO))
                       (.write p (str (hy-eval i self.mod.--dict-- "__main__"))))
                     (except [e Exception]
                       (setv sys.stdout oldout)
                       (.format-excp self (sys.exc-info)))
                     (else
                       (self.writer {"value" (.getvalue p) "ns" (.get self.msg "ns" "Hy") "id" (.get self.msg "id")})
                       (when (and (= (.getvalue p) "None") (bool (.getvalue sys.stdout)))
                         (self.writer {"out" (.getvalue sys.stdout) "id" (.get self.msg "id")}))))))
               (setv sys.stdout oldout)
               (self.writer {"status" ["done"] "id" (.get self.msg "id")}))))))]
   [format-excp
     (fn [self trace]
       (let [[exc-type (first trace)]
             [exc-value (second trace)]
             [exc-traceback (get trace 2)]]
         (setv self.session.last-traceback exc-traceback)
         (self.writer {"status" ["eval-error"]
                      "ex" (. exc-type --name--)
                      "root-ex" (. exc-type --name--)
                      "id" (.get self.msg "id")})
         (when (instance? LexException exc-value)
           (when (is exc-value.source None)
             (setv exc-value.source ""))
           (setv exc-value (.format "LexException: {}" exc-value.message)))
         (self.writer {"err" (.strip (str exc-value)) "id" (.get self.msg "id")})))]])
