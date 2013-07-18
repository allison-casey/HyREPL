import socket
import threading
import socketserver
import uuid
from nrepl.bencode import encode, decode 

from hyrepl.session import Session
from hyrepl.errors import NREPLError
from debug.debugger import debug


operations = {}
required_map = {}


class NREPLTypeError(TypeError):
    def __init__(self, expression, message):
        super(NREPLTypeError, self).__init__(message)
        self.expression = expression

    def __str__(self):
        return (super(NREPLTypeError, self).__str__() + " (line %s, column %d)"
                % (self.expression.start_line,
                   self.expression.start_column))

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
            decoded_data["session"] = sess

        else:
            sess = decoded_data["session"]


        if decoded_data["op"] in list(operations.keys()):
            returned_value = operations[decoded_data["op"]](self, self.sessions[sess], decoded_data)


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
    @required_params("session", "code")
    def eval_operation(self, session, msg):

        code = session.eval(msg["code"], id=msg.get("id", False))

        return {"status": ["done"], "code": code}

    @operation("clone")
    def clone_operation(self, session, msg):
        sess = str(uuid.uuid4())

        to_be_cloned_session = sessions[session.uuid]

        to_be_cloned_session.uuid = sess
        sessions[sess] = to_be_cloned_session

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
        pass

    @operation("load-file")
    @required_params("file")
    def load_file_operation(self, session, msg):
        pass

    @operation("ls-sessions")
    def ls_sessions_opeartion(self, session, msg):
        return {"sessions": list(self.sessions.keys())}

    @operation("stdin")
    @required_params("stdin")
    def stdin_operation(self, session, msg):
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

