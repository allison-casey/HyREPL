import socket
import threading
import socketserver
import uuid
import time
import sys
from io import StringIO

# from debug.debugger import debug
from nrepl.bencode import encode, decode 
from hyrepl.session import Session
from hyrepl.repl import Repl
#from hyrepl.errors import NREPLError


operations = {}
required_map = {}


class HyreplSTDIN(StringIO):
    def __init__(self):
        self.self2 = None
        self.sess = None
        self.hook = lambda: None

    def readline(self):
        """Hackin'"""
        ret = self.hook(self.self2, self.sess)
        print(ret)
        while True:
            if ret:
                print("readline got activated!")
                break
        print(ret)
        return ret


class NREPLTypeError(TypeError):
    def __init__(self, expression, message):
        super(NREPLTypeError, self).__init__(message)
        self.expression = expression

    def __str__(self):
        return (
            super(NREPLTypeError, self).__str__() + " (line %s, column %d)" % (
                self.expression.start_line,
                self.expression.start_column
            )
        )


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """The actuall thread we launch on ever request"""
    allow_reuse_address = True
    sessions = {} 
    outs = []
    sys.stdin = HyreplSTDIN()

    def send(self):
        for i in self.outs:
            print(self.outs)
            ret = encode(i)
            self.request.sendall(bytes(ret, 'utf-8'))
            self.outs.remove(i)

    def _hack(self2, self, sess):
        print("Starting thread with reqeust")
        threading.Thread(target=self.send_request, args=(self, sess)).start()
        time.sleep(1000)

    def send_request(self2, self, sess):
        ret = encode({"status": ["need-input"], "session": sess})
        self.request.sendall(bytes(ret, 'utf-8'))

    def handle(self):
        ret = {"status": []}
        in_data = str(self.request.recv(1024), 'utf-8')
        cur_thread = threading.current_thread()
        #debug(cur_thread)
        dec_dat = decode(in_data)
        decoded_data = [i for i in dec_dat][0]
        if "session" not in decoded_data:
            sess = str(uuid.uuid4()) 
            self.sessions[sess] = None
        ret["session"] = sess
        sys.stdin.self2 = self
        sys.stdin.sess = sess
        sys.stdin.hook = self._hack
        if decoded_data["op"] in operations:
            op = decoded_data["op"]
            self.sessions[sess] = operations[op](self, sess, decoded_data)
        if self.sessions[sess] != None:
            ret.update(self.sessions[sess])
        ret["status"].append("done")
        self.outs.append(ret)
        self.send()
        return 0

    def operation(operation_val):
        def _(fn):
            operations[operation_val] = fn
        return _

    def required_params(*args):
        def _(fn):
            def check(self, sess, expr):
                for i in args:
                    if i not in list(expr.keys()):
                        # If we are missing a required param in the map
                        # Gief better handling
                        raise
                return fn(self, sess, expr)
            return check
        return _

    @operation("eval")
    @required_params("code")
    def eval_operation(self, session, msg):
        repl = Repl()
        ret = repl.eval(msg["code"])
        for i in ret:
            m = {"session": session}
            m.update(i)
            self.outs.append(m)
        return None
        
    @operation("clone")
    def clone_operation(self, session, msg):
        return {"new-session": sess}

    @operation("close")
    @required_params("session")
    def close_operation(self, session, msg):
        del sessions[session.uuid]

    @operation("describe")
    def describe_operation(self, session, msg):
        pass

    @operation("interrupt")
    @required_params("session")
    def interrupt_operation(self, session, msg):
        if "interrupt-id" in list(msg.keys()):
            id = msg["interrupt-id"]
        session.interrupt(id)
        return "interrupted"

    @operation("load-file")
    @required_params("file")
    def load_file_operation(self, session, msg):
        pass

    @operation("ls-sessions")
    def ls_sessions_opeartion(self, session, msg):
        return {"sessions": list(self.sessions.keys())}

    @operation("stdin")
    def stdin_operation(self, session, msg):
        print(msg)
        print(sys.stdin.hook)
        sys.stdin.hook = msg["value"]
        print(sys.stdin.hook)
        return None

    @operation("ls-sub-sessions")
    def sub_sessions(self,session,msg):
        #debug(session.status)
        return {"subs": session.ret_sess()}


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded server"""
    daemon_threads = True


class nREPLServerHandler(object):
    """Server abstraction"""

    def __init__(self, host, port):
        while True:
            try:
                self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
            except:
                pass
            else:
                print("Connected!")
                break
        self.ip, self.port = self.server.server_address

    def start(self):
        """Starts the server"""
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        """Stops the server"""
        del self.server_thread
        self.server.shutdown()

