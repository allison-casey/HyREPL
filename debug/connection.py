import socket

class ConnectionHandler(object):
    def __init__(self, host, port, connect=False):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.SO_REUSEADDR) # need to set nonblocking :>

        #self.sock.setblocking(0)
        # todo add recv implementation

        if connect:
            self.connect()

    def connect(self):
        self.sock.connect((self.host, int(self.port)))

    def send(self, data):
        data = bytes(data, 'utf-8')
        self.sock.send(data)
    
    def recv(self, amount=1024):
        raise NotImplementedError
    def parse(self, data):
        raise NotImplementedError
    def disconnect(self):
        raise NotImplementedError