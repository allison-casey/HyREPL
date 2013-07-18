from hy.lex.machine import Machine
from hy.compiler import hy_compile
from hy.importer import ast_compile, hy_eval, import_buffer_to_hst
from hy.lex import tokenize
from debug.debugger import debug
import imp


class Repl(object):
    mod = imp.new_module("nrpl-module")
    
    def eval(self, code):
        debug(code)
        ret = tokenize(code)
        for i in ret:
            p = hy_eval(i, self.mod.__dict__, "__main__")
            debug(p)
        return p

    def eval_file(*args):
        pass

