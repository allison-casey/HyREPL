import socket
import sys
import threading
import time
from nrepl.bencode import encode, decode


ip = '127.0.0.1'
port = 9999

def client(ip, port, message):
    msg = bytes(encode(message), 'utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(msg)
        while True:
            response = str(sock.recv(2048), 'utf-8')
            if response:
                print(response)
                print([i for i in decode(response)])
            time.sleep(0.5)
    finally:
        sock.close()


client(ip, port, {"op": "eval", "code": '(+ 1 a)'})
