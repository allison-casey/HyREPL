import socket
import sys
from nrepl.bencode import encode, decode


ip = '127.0.0.1'
port = 9999

def client(ip, port, message):
    msg = bytes(encode(message), 'utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(msg)
        response = str(sock.recv(1024), 'utf-8')
        print([i for i in decode(response)])
    finally:
        sock.close()


client(ip, port, {"op": "eval", "code": "(+ 2 2 2)"})
client(ip, port, {"op": "eval", "code": "(+ 3 3 3 3)"})
client(ip, port, {"op": "ls-sessions"})