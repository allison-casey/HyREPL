import uuid
import threading
from HyREPL.ops import find_op
import nrepl.bencode as nrepl


class Session(object):
    """ The session object contains all the info about the
        specefic session."""
    status = ""
    thread = None
    eval_id = ""
    eval_msg = ""

    def __init__(self, transport, uuid):
        self.uuid = str(uuid)
        self.transport = transport

    def __str__(self):
        return self.uuid

    def __repr__(self):
        return self.uuid

    def write(self, d):
        #lets try and keep oure out writer here
        print(d)
        l = {"session": self.uuid}
        f = dict( list(l.items()) + list(d.items()))
        f = bytes(nrepl.encode(f), "utf-8")
        self.transport.write(f)



class Sessions():
    """ Object keeping track of the session and corresponding thread """
    uuids = {}

    def del_uuid(self, uuid):
        del self.uuids[uuid]

    def add_uuid(self, uuid, thread):
        self.uuids[uuid] = thread

    def get_uuid(self, uuid):
        return self.uuids[uuid]

    def get_status(uuid):
        pass

    def kill():
        pass


class SessionHandle(threading.Thread):
    """ Basic handler/thread for all of our session work
        like finding the correct op for the msg we got."""

    def __init__(self, msg, sessions, session):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sessions = sessions
        self.session = session
        self.msg = msg

    def run(self):
        ret = find_op(self.msg["op"])
        ret(self.session, self.sessions, self.msg)

