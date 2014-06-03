import uuid
import threading
from HyREPL.ops import find_op
import nrepl.bencode as nrepl


class Session(object):
    """ The session object contains all the info about the
        specefic session."""
    status = ""
    eval_id = ""
    eval_msg = ""
    _thread = None

    def __init__(self, transport, uuid):
        self.uuid = str(uuid)
        self.transport = transport

    def __str__(self):
        return self.uuid

    def __repr__(self):
        return self.uuid


    def write(self, d):
        #lets try and keep oure out writer here
        #print(d)
        #print("Heyooo")
        l = {"session": self.uuid}
        f = dict( list(l.items()) + list(d.items()))
        ret = nrepl.encode(f)
        f = bytes(ret, "utf-8")
        self.transport.write(f)
        if "done" in ret and "status" in ret:
            # Asyncio blocks the writing, because async.
            # Cheap workaround so we always get the responses
            # This should only trigger if the status of the nrepl
            # contains done and status. 
            # However, this will fail if someone decides to print "status done".
            self.transport.write_eof()

    @property
    def thread(self):
        return self._thread

    @thread.setter
    def thread(self, th):
        if self._thread:
            del self._thread
        self._thread = th

    @thread.deleter
    def thread(self):
        del self._thread



class Sessions():
    """ Object keeping track of the session and corresponding thread """
    uuids = {}

    def del_uuid(self, uuid):
        del self.uuids[uuid]

    def add_uuid(self, uuid):
        self.uuids[str(uuid)] = uuid

    def check_uuid(self, uuid):
        #print(str(uuid))
        #print(self.uuids)
        if str(uuid) in self.uuids.keys():
            return True
        return False

    def get_uuid(self, uuid):
        return self.uuids[str(uuid)]

    def kill(self, uuid):
        self.uuids[str(uuid)].thread.stop()
        del self.uuids[str(uuid)]


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

