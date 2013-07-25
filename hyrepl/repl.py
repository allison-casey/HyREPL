import imp
import sys
import traceback
from io import StringIO
from hy.lex.machine import Machine
from hy.compiler import hy_compile
from hy.importer import ast_compile, hy_eval, import_buffer_to_hst
from hy.lex import tokenize

#from debug.debugger import debug


class Repl(object):
    mod = imp.new_module("__main__")

    def eval(self, code):
        self.ret = []
        print("Received: %s" % code)
        try:
            ret = tokenize(code)
        except:
            self._format_excp(sys.exc_info())
            return self.ret
        oldout = sys.stdout
        oldin = sys.stdin
        stdout = None
        #sys.stdout = StringIO()
        for i in ret:
            try:
                print("Sending code to hy_eval...")
                p = hy_eval(i, self.mod.__dict__, "__main__")
                print("Evaluated")
            except:
                self._format_excp(sys.exc_info())
            else:
                self.ret.append({"value": p, "ns": None})
                #if p == None:
                    #stdout = sys.stdout.getvalue()
                    #if stdout:
                    #    self.ret.append({'out': stdout})
        #sys.stdout = oldout
        #print(stdout)
        return self.ret

    def _format_excp(self, trace):
        exc_type, exc_value, exc_traceback = trace
        self.ret.append({'status': ['eval-error'], 'ex': exc_type.__name__, 'root-ex': exc_type.__name__})
        self.ret.append({'err': str(exc_value)})

    def eval_file(*args):
        pass
