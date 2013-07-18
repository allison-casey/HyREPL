import socket
import threading
import socketserver
import uuid
from hyrepl.session import Session

from debug.debugger import debug
from nrepl.bencode import encode, decode 


operations = {}


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """The actuall thread we launch on ever request"""

    sessions = {}

    def handle(self):
        in_data = str(self.request.recv(1024), 'utf-8')

        #cur_thread = threading.current_thread()
        decoded_data = [i for i in decode(in_data)][0]
        
        if "session" not in decoded_data:
            sess = str(uuid.uuid4()) 
            self.sessions[sess] = Session(sess)
        else:
            sess = decoded_data["session"]


        if decoded_data["op"] in list(operations.keys()):
            returned_value = operations[decoded_data["op"]](self, self.sessions[sess])


        if returned_value != None:
            returned_dict = {"session": sess}
            returned_dict.update(returned_value)
            debug(returned_dict)
            encoded_data = encode(returned_dict)
            
            #debug(encoded_data)

            self.request.sendall(bytes(encoded_data, 'utf-8'))



    def operation(operation_val):
        def _(fn):
            operations[operation_val] = fn
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
        return {"sessions": list(self.sessions.keys())}


    @operation("stdin")
    def stdin_operation(self, session):
        pass





class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded server"""
    daemon_threads = True
    allow_reuse_address = True



class nREPLServerHandler(object):
    """Server abstraction"""

    def __init__(self, host, port):
        self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
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

