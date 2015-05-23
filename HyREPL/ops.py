# https://github.com/clojure/tools.nrepl/blob/34093111923031888f8bf6da457aaebc3381d67e/doc/ops.md
# Missing ops:
# - describe
# - interrupt
# - ls-sessions
# Incomplete ops:
# - load-file (file name not handled)
# - eval

from HyREPL.eval import HyreplSTDIN, HyREPL
from HyREPL.workarounds import hints, work_around_it
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
def eval_expr(session, msg, transport):
    if msg["code"] in hints.keys():
        work_around_it(session, msg, transport)
        return
    d = HyREPL(msg, session, lambda x: session.write(x, transport))
    d.start()

@set_description(handles={"load-file": {}})
def eval_file(session, msg, transport):
    code = msg["file"].split(" ", 2)[2]
    print(code)
    msg["code"] = code
    del msg["file"]
    find_op("eval")(session, msg, transport)

@set_description(handles={"clone": {}})
def clone_sess(session, msg, transport):
    from HyREPL.session import Session
    sess = Session()
    session.write({"status": ["done"], "id": msg["id"], "new-session": str(sess)}, transport)

@set_description(handles={"close": {}})
def close_sess(session, msg, transport):
    try:
        from HyREPL.session import sessions
        del sessions[msg.get("session", "")]
    except KeyError:
        pass
    transport.close()

@set_description(handles={"describe": {}})
def describe_self(session, msg, transport):
    reply = {"status": ["done"],
            "id": msg["id"],
            "versions": { "nrepl": { "major": 2, "minor": 1 } }, # XXX: java and clojure versions?
            "ops": {}, # XXX
            "session": session.uuid}
    session.write(reply, transport)

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
                          "returns": {"status": "\"need-input\" will be sent if we need stdin"}}})
def add_stdin(session, msg, transport):
    sys.stdin.put(msg["value"])
    sys.stdin.task_done()
