class CommandHandler(object):
    def __init__(self):
        self.commands = {
                "connections":self.h_connections,
                "info":self.h_info
        }

    def parse(self, command):
        command_s = command.split()
        function  = self.commands.get(command_s[0].lower(), lambda **args: None)
        function(*command_s[1:])

    def h_connections(self, **args):
        raise NotImplementedError

    def h_info(self, **args):
        raise NotImplementedError