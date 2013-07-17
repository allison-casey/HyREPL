from hyrepl.repl import repl


class Session(object):
    def __init__(self, UUID):
        self.repl = repl

        self.uuid = uuid
        self.threads = {}

    def clone(self):
        pass

    def eval(self):
        pass

    def close(self):
        pass

    def interrupt(self):
        pass