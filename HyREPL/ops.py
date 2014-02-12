from HyREPL.eval import HyreplSTDIN, HyREPL
import threading
import sys


_descriptions = dict()

def set_description(requires=None, expects=None, handles=None):
    def _(fn):
        op = tuple(handles.keys())
        # TODO: Actually make this do MORE
        _descriptions[op] = fn
    return _


def find_op(op):
    for args, fn in _descriptions.items():
        if op in args:
            return fn








@set_description(handles={"eval": {}})

def eval_expr(session, sessions, msg):
    print(session)
    print(sessions)
    d = HyREPL(msg, session.write)
    d.start()



# Yes, this is a totally sane decorator
@set_description(
                # session needs to be defined at a higher level
                requires=("session"),
                # eval needs to be present somewhere as a middleware
                # at a lower level
                expects=("eval"),
                # The expected input and info
                handles={"stdin":
                         {"doc": "blach",
                          "requires": "stdin",
                          "optional": {},
                          "returns": {"status" "\"need-input\" will be sent if we need stdin"}}})
def add_stdin(sessions, session, msg):
    sys.stdin.put(msg["value"])
    sys.stdin.task_done()
