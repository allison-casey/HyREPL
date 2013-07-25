from debug.objects import *
from debug.frames import *

from debug.connection import ConnectionHandler

class DebuggingInstance(object):
    def __init__(self, host, port):
        self.frameInspector = FrameInspector()
        self.objectInspector = ObjectInspector()
        self.connectionManager = ConnectionHandler(host, port, connect=True)
        self.n = lambda a: "\n".join(a.toInfo() + ["\n"])
    def debug(self, msg, frame=None, object=None):
        msg = str(msg) # errors when passing lists and such
        # possible addition could include resolution based on types, i.e list => ", ".join(msg)
        if frame:
            if frame == "current":
                result = self.debug_msg(inspect.currentframe().f_back, msg, inspector=self.objectInspector)
            else:
                result = self.debug_frame(frame, msg)
        if object:
            result = self.debug_object(object, msg)
        if not frame and not object:
            result = self.debug_msg(inspect.currentframe().f_back, msg, inspector=None)
        # result will have a .toInfo() method
        self.connectionManager.send(self.n(result))

    def debug_object(self, object, msg):
        obj = self.objectInspector.inspect(object)
        obj.msg = msg
        return obj
    def debug_frame(self, frame, msg):
        frame = self.frameInspector.inspect(frame)
        frame.msg = msg
        return frame
    def debug_msg(self, frame, msg, inspector):
        frame = self.frameInspector.inspect(frame, objectInspector=inspector)
        frame.msg = msg;
        return frame

#DI = DebuggingInstance("localhost", 13337);
def f(*args): pass
debug = f