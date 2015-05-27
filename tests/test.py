#!/usr/bin/env python
import os, unittest, subprocess, re, signal, time
import socket
import threading
import queue
import sys
import os

from socketserver import ThreadingMixIn, UnixStreamServer

from HyREPL.bencode import encode, decode, decode_multiple
from HyREPL.server import ReplRequestHandler

sock = "/tmp/HyREPL-test"
class TestServer(ThreadingMixIn, UnixStreamServer): pass
def start_server():
    try:
        os.unlink(sock)
    except FileNotFoundError:
        pass
    s = TestServer(sock, ReplRequestHandler)
    t = threading.Thread(target=s.serve_forever)
    t.daemon = True
    t.start()
    def stop():
        s.shutdown()
        t.join()
    return stop

def soc_send(message, return_reply=True):
    s = socket.socket(family=socket.AF_UNIX)
    s.connect(sock)
    s.sendall(encode(message))
    if not return_reply:
        s.close()
        return []
    s.setblocking(False)

    ret = []
    buf = b""
    while True:
        try:
            resp = s.recv(1)
            buf += resp
        except BlockingIOError:
            pass
        try:
            response, rest = decode(buf)
        except:
            continue
        buf = rest

        ret.append(response)
        if "done" in response.get("status", []):
            break
    s.close()
    return ret

def test_code_eval():
    """
    simple eval
    Example output from the server:
        [{'session': '0361c419-ef89-4a86-ae1a-48388be56041', 'ns': 'Hy', 'value': '4'}, 
         {'status': ['done'], 'session': '0361c419-ef89-4a86-ae1a-48388be56041'}]
    """
    stop = start_server()
    code = {"op": "eval", "code": "(+ 2 2)"}
    ret = soc_send(code)
    value, status = ret
    stop()

    assert len(ret) == 2
    assert value["value"] == '4'
    assert "done" in status["status"]
    assert value["session"] == status["session"]


def test_stdout_eval():
    """
    stdout eval
    Example output from the server:
        [{'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'ns': 'Hy', 'value': 'None'}, 
         {'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'out': 'Hello World\n'}, 
         {'status': ['done'], 'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4'}]
    """

    stop = start_server()
    code = {"op": "eval", "code": '(print "Hello World")'}
    ret = soc_send(code)
    value, out, status = ret
    stop()

    assert len(ret) == 3
    assert value["value"] == 'None'
    assert out["out"] == "Hello World\n"
    assert "done" in status["status"]
    assert value["session"] == out["session"] == status["session"]


def stdin_send(code, my_queue):
    ret = soc_send(code)
    my_queue.put(ret)

def test_stdin_eval():
    """
    stdin eval
    The current implementation will send all the responses back
    into the first thread which dispatched the (def...), so we throw
    it into a thread and add a Queue to get it.
    Bad hack. But it works.

    Example output from the server:
        [{'status': ['need-input'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'}, 
         {'session': 'ec100813-8e76-4d69-9116-6460c1db4428', 'ns': 'Hy', 'value': 'test'}, 
         {'status': ['done'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'}]
    """

    stop = start_server()

    my_queue = queue.Queue()

    code = {"op": "eval", "code": '(def a (input))'}
    t = threading.Thread(target=stdin_send, args=(code, my_queue))
    t.start()

    # Might encounter a race condition where 
    # we send stdin before we eval (input)
    time.sleep(0.5)

    code = {"op": "stdin", "value": "test"}
    soc_send(code, return_reply=False)

    t.join()
    ret = my_queue.get()

    input_request, value, status = ret
    stop()

    assert len(ret) == 3
    assert value["value"] == 'test'
    assert input_request["status"] == ["need-input"]
    assert "done" in status["status"]
    assert value["session"] == input_request["session"] == status["session"]
