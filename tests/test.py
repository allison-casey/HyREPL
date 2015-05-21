#!/usr/bin/env python
import os, unittest, subprocess, re, signal, time
import socket
import threading
import queue
import sys

from HyREPL.bencode import encode, decode, decode_multiple
from main import start_server

ip = "localhost"
port = 1337

def test_bencode():
    d = { "foo": 42, "spam": [1, 2, 'a'] }

    print(decode(b"d5:value1:47:session36:31594b80-7f2e-4915-9969-f1127d562cc42:ns2:Hyed6:statusl4:donee7:session36:31594b80-7f2e-4915-9969-f1127d562cc4e"))
    assert d == decode(encode(d))[0]

def soc_send(message, return_reply=True):
    reply = socket.create_connection((ip, port))
    read_from = reply.makefile('rw')
    msg = encode(message)
    ret = []
    reply.sendall(msg)
    if return_reply:
        while True:
            response = read_from.read(2048)
            if response:
                [ret.append(l) for l in decode_multiple(bytes(response, 'utf-8'))]
            if "done" in response and "status" in response:
                break
            reply.close()
    return ret


def test_code_eval():
    """
    Example output from the server:
        [{'session': '0361c419-ef89-4a86-ae1a-48388be56041', 'ns': 'Hy', 'value': '4'}, 
         {'status': ['done'], 'session': '0361c419-ef89-4a86-ae1a-48388be56041'}]
    """

    code = {"op": "eval", "code": "(+ 2 2)"}
    ret = soc_send(code)
    value, status = ret

    assert len(ret) == 2
    assert value["value"] == '4'
    assert "done" in status["status"]
    assert value["session"] == status["session"]


def test_stdout_eval():
    """
    Example output from the server:
        [{'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'ns': 'Hy', 'value': 'None'}, 
         {'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4', 'out': 'Hello World\n'}, 
         {'status': ['done'], 'session': '2d6b48d8-4a3e-49a6-9131-3321a11f70d4'}]
    """

    code = {"op": "eval", "code": '(print "Hello World")'}
    ret = soc_send(code)
    value, out, status = ret

    assert len(ret) == 3
    assert value["value"] == 'None'
    assert out["out"] == "Hello World\n"
    assert "done" in status["status"]
    assert value["session"] == out["session"] == status["session"]


def stdin_send(code, my_queue):
    ret = soc_send(code)
    my_queue.put(ret)


def test_stdin_eval():

    """The current implementation will send all the responses back
    into the first thread which dispatched the (def...), so we throw
    it into a thread and add a Queue to get it.
    Bad hack. But it works.

    Example output from the server:
        [{'status': ['need-input'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'}, 
         {'session': 'ec100813-8e76-4d69-9116-6460c1db4428', 'ns': 'Hy', 'value': 'test'}, 
         {'status': ['done'], 'session': 'ec100813-8e76-4d69-9116-6460c1db4428'}]
    """

    my_queue = queue.Queue()


    code = {"op": "eval", "code": '(def a (input))'}
    t = threading.Thread(target=stdin_send, args=(code,my_queue))
    t.start()

    # Might encounter a race condition where 
    # we send stdin before we eval (input)
    import time
    time.sleep(0.5)

    code = {"op": "stdin", "value": "test"}
    soc_send(code, return_reply=False)

    t.join()
    ret = my_queue.get()

    input_request, value, status = ret

    assert len(ret) == 3
    assert value["value"] == 'test'
    assert input_request["status"] == ["need-input"]
    assert "done" in status["status"]
    assert value["session"] == input_request["session"] == status["session"]
