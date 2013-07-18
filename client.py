import socket
import sys
import threading
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


a = threading.Thread(target=client, args=(ip, port, {"op": "eval", "code": "(while true (+ 2 2 2))"}))
b = threading.Thread(target=client, args=(ip, port, {"op": "eval", "code": "(+ 3 1)"}))
c = threading.Thread(target=client, args=(ip, port, {"op": "ls-sessions"}))
a.start()
b.start()
c.start()