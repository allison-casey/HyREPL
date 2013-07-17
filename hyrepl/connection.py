import socket
import threading
import socketserver
import uuid
from hyrepl.session import Session

from debug.debugger import debug
from nrepl.bencode import encode, decode 



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    connections = []
    operations = {}

    def handle(self):
        self.l.append(uuid.uuid4())
        data = str(self.request.recv(1024), 'utf-8')
        #cur_thread = threading.current_thread()
        
        ret = [i for i in decode(data)][0]
        
        debug("Thread: {} Data: {}".format(cur_thread, self.l))
        
        res = encode(ret)
        
        self.request.sendall(bytes(res, 'utf-8'))


    def operation(self, operation):
        def _(fn):
            self.operations[operation] = fn
        return _


    @operation("eval")
    def eval_operation(self, session):
        pass

    @operation("clone")
    def clone_operation(self, session):
        pass


    @operation("close")
    def close_operation(self, session):
        pass


    @operation("describe")
    def describe_operation(self, session):
        pass


    @operation("interrupt")
    def interrupt_operation(self, session):
        pass


    @operation("load-file")
    def load_file_operation(self, session):
        pass


    @operation("ls-sessions")
    def ls_sessions_opeartion(self, session):
        pass


    @operation("stdin")
    def stdin_operation(self, session):
        pass





class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True



class nREPLServerHandler(object):
    def __init__(self, host, port):
        self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
        self.ip, self.port = self.server.server_address

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        del self.server_thread
        self.server.shutdown()

