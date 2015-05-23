import sys
import threading
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

from HyREPL import bencode
from HyREPL import session

class ReplServer(ThreadingMixIn, TCPServer): pass

def start_server(ip, port):
    s = ReplServer((ip, port), ReplRequestHandler)
    t = threading.Thread(target=s.serve_forever)
    t.daemon = True
    t.start()
    return (t, s)

class ReplRequestHandler(BaseRequestHandler):
    session = None

    def handle(self):
        print("New client", file=sys.stderr)
        buf = b""
        while True:
            try:
                newstuff = self.request.recv(1024)
            except OSError:
                break
            if len(newstuff) == 0:
                break
            buf += newstuff
            try:
                msg, rest = bencode.decode(buf)
                buf = rest
            except Exception as e:
                print(e, file=sys.stderr)
                continue

            if self.session is None:
                self.session = session.sessions.get(msg.get("session"))
                if self.session is None:
                    self.session = session.Session()

            self.session.handle(msg, self.request)
        print("Client gone", file=sys.stderr)
