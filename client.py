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
    asd = True
    try:
        sock.sendall(msg)
        while asd == True:
            response = str(sock.recv(2048), 'utf-8')
            if response:
                for i in decode(response):
                    print(i)

                break
    except KeyboardInterrupt:
        sock.close()
        del sock


#client(ip, port, {"op": "eval", "code": '(def b 2)'})
#client(ip, port, {"op": "eval", "code": '(+ 2 b)'})
client(ip, port, {"op": "eval", "code": '(def a (input))'})
client(ip,port, {"op": "stdin", "value": "test"})
client(ip,port, {"op": "eval", "code": "(print a)"})

