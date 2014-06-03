from hy.importer import ast_compile, hy_eval
from hy.lex import tokenize
from queue import Queue
import imp
import sys
import threading
import traceback
from io import StringIO


class HyreplSTDIN(Queue):
    """This is hack to override sys.stdin."""
    def __init__(self, write):
        super().__init__()
        self.writer = write

    def readline(self):
        """Hackin'"""
        self.writer({"status": ["need-input"]})

        # such clever
        # much hack
        # wow
        self.join()
        return self.get()


class HyREPL(threading.Thread):
    """Repl simulation."""

    # As with normal hy evulation, everything is in reality a top level module.
    mod = imp.new_module("__main__")

    def __init__(self, msg, writer):
        # Making this a thread so we can kill it if it halts
        threading.Thread.__init__(self)
        self.writer = writer
        self.msg = msg
        sys.stdin = HyreplSTDIN(writer)

    def run(self):
        """Evals the given code."""
        code = self.msg["code"]

        # We might catch errors when tokenizing code.
        try:
            tokens = tokenize(code)
        except:
            self._format_excp(sys.exc_info())
            return self.ret

        # Setting stdout in a way so we can catch anything printed and return that
        oldout = sys.stdout
        oldin = sys.stdin
        stdout = None

        # TODO: add ID to responses
        # TODO: add 'eval_msg' updates too the current session
        for i in tokens:
            try:
                sys.stdout = StringIO()
                p = str(hy_eval(i, self.mod.__dict__, "__main__"))
            except:
                sys.stdout = oldout
                self._format_excp(sys.exc_info())
            else:
                #Debugging purposes
                #sys.stdout = oldout
                self.writer({"value": p, "ns": 'Hy'})

                #If there is nothing in return, we see if anything is in stdout
                if p == "None":
                    stdout = sys.stdout.getvalue()
                    if stdout:
                        self.writer({'out': stdout})

        sys.stdout = oldout
        self.writer({"status": ["done"]})
        return True

    def _format_excp(self, trace):
        # Format return exception
        exc_type, exc_value, exc_traceback = trace
        self.writer({'status': ['eval-error'], 'ex': exc_type.__name__, 'root-ex': exc_type.__name__})
        self.writer({'err': str(exc_value)})

    def eval_file(*args):
        """MIA"""
        pass
