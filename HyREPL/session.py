import sys

from uuid import uuid4
from HyREPL.ops import find_op
from HyREPL import bencode

sessions = {}

class Session(object):
    """ The session object contains all the info about the
        specefic session."""
    status = ""
    eval_id = ""
    eval_msg = ""
    last_traceback = None

    def __init__(self):
        self.uuid = str(uuid4())
        sessions[self.uuid] = self

    def __str__(self):
        return self.uuid

    def __repr__(self):
        return self.uuid

    def write(self, msg, transport):
        assert "id" in msg
        msg["session"] = self.uuid
        print("out:", msg, file=sys.stderr)
        transport.sendall(bencode.encode(msg))

    def handle(self, msg, transport):
        print("in:", msg, file=sys.stderr)
        find_op(msg["op"])(self, msg, transport)
