import time
import sys
from HyREPL.session import Session
from HyREPL import bencode

import threading
from socketserver import ForkingMixIn, TCPServer, BaseRequestHandler

class ReplServer(ForkingMixIn, TCPServer): pass

sessions = {}

class ReplRequestHandler(BaseRequestHandler):
    session = None

    def handle(self):
        print("New client")
        buf = b""
        while True:
            newstuff = self.request.recv(1024)
            if len(newstuff) == 0:
                break
            buf += newstuff
            try:
                msg, rest = bencode.decode(buf)
                buf = rest
            except Exception as e:
                print(e)
                continue

            if self.session is None:
                if msg.get("session") in sessions:
                    self.session = sessions[msg.get("session")]
                else:
                    self.session = Session(sessions)
                    sessions[self.session.uuid] = self.session

            self.session.handle(msg, self.request)
        print("Client gone")

def start_tcp_server(ip, port):
    s = ReplServer((ip, port), ReplRequestHandler)
    t = threading.Thread(target=s.serve_forever)
    t.daemon = True
    t.start()
    return t

if __name__ == '__main__':
	# start_server('127.0.0.1', 1337)
    port = 1337
    while True:
        try:
            t = start_tcp_server('127.0.0.1', port)
        except OSError:
            port += 1
        else:
            sys.stdout.write("Listening on {}\a\n".format(port))
            sys.stdout.flush()
            while True:
                time.sleep(1)
            t.join()
