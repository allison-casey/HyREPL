from hyrepl.repl import Repl
import threading


class Session(object):
    def __init__(self, UUID):
        self.repl = Repl()

        self.uuid = UUID

        # All code is sent with threads so 
        # it is possible to kill off any code that gets stcuk
        self.threads = {}

    def clone(self):
        pass

    def eval(self):
        pass

    def close(self):
        pass

    def interrupt(self):
        pass