import uuid
import threading

from hyrepl.repl import Repl
#from debug.debugger import debug


class Session(object):
    def __init__(self, UUID):
        self.repl = Repl()
        self.uuid = UUID
        # All code is sent with threads so 
        # it is possible to kill off any code that gets stcuk
        self.code_evals = {}
        # True = code is being evaluated
        # False = Code have been interrupted
        # None = Nothing is happening 
        self.status = 'session-idle'

    def eval(self, code, id=False):
        self.status = 'evaluating'
        if id:
            self.code_evals[id] = self.repl.eval(code)
            eval_code = self.code_evals[id]()
        else:
            t = self.repl.eval(code)
            eval_code = t()
        self.status = 'done'
        if id:
            del self.code_evals[id]
        return eval_code

    def interrupt(self, id):
        if id not in list(self.code_evals):
            self.status = 'interrupt-id-mismatch' 
        else:    
            del self.code_evals[id]
            self.status = 'interrupted'

    def ret_sess(self):
        return self.code_evals

