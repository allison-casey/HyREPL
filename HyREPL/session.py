import uuid
import threading
from HyREPL.ops import find_op
import nrepl.bencode as nrepl


class Sessions():
    uuids = {}

    def del_uuid(self, uuid):
        del self.uuids[uuid]

    def get_uuid(self):
        new = uuid.uuid4()
        return new

    def add_uuid(self, uuid, thread):
        self.uuids[uuid] = thread

    def check_uuid(self, uuid):
        return self.uuids[uuid]

    def get_status():
        pass

    def kill():
        pass


class SessionHandle(threading.Thread):
    status = None

    def __init__(self, msg, sess, transport):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sess = sess
        self.msg = msg
        self.transport = transport

    def write(self, d):
        l = {"session": self.sess}
        f = dict( list(l.items()) + list(d.items()))
        f = bytes(nrepl.encode(f), "utf-8")
        self.transport.write(f)

    def run(self):
        ret = find_op(self.msg["op"])
        ret(self.write, self.msg)

    def get_status():
        return self.status
