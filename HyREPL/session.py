from uuid import uuid4
from HyREPL.ops import find_op
from HyREPL import bencode

class Session(object):
    """ The session object contains all the info about the
        specefic session."""
    status = ""
    eval_id = ""
    eval_msg = ""

    def __init__(self, sessions):
        self.sessions = sessions
        self.uuid = str(uuid4())
        self.sessions[self.uuid] = self

    def __str__(self):
        return self.uuid

    def __repr__(self):
        return self.uuid

    def write(self, msg, transport):
        assert "id" in msg
        msg["session"] = self.uuid
        print("out:", msg)
        transport.sendall(bencode.encode(msg))

    def handle(self, msg, transport):
        print("in:", msg)
        op = find_op(msg["op"])
        op(self, self.sessions, msg, transport)
