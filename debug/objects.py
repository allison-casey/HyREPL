import inspect

import blessings


class ObjectResults(object):
    def __init__(self, obj):
        self.obj = obj
        self.msg = None
        self.t = blessings.Terminal()

        if not self.obj:
            return # the object is invalid

        self.hash = str(hash(obj))
        self.variables = []
        self.methods = []
        self.ifClassGetInfo(obj)
    def getInheritance(self, obj, joiner="=>"):
        parent_objects = inspect.getmro(obj)
        parents = [parent.__name__ for parent in parent_objects]
        parents = parents[1:] # ignore the first parent
        parents = parents[::-1] # reverse the list
        return joiner.join(parents)

    def ifClassGetInfo(self, obj):
        if hasattr(obj, "__class__"):
            if obj.__class__ != type:
                self._class = obj.__class__
            else:
                self._class = obj
        else:
            self._class = obj
        self.name = self._class.__name__
        self.file = inspect.getfile(self._class)
        self.module = inspect.getmodule(self._class)
        self.inheritance = self.getInheritance(self._class, "=>")
    def toInfo(self):
        if not self.obj:
            return [] # the object is invalid
        data = []
        data.append(self.t.yellow("----------Object Report---------"))
        if self.msg:
            data.append('{0} : {1}'.format(self.t.cyan("Message"), self.t.red(self.msg)))
        data.append("{0}: {1}({2})".format(self.t.cyan("Name"), self.t.red(self.name), self.t.green(self.inheritance)))
        data.append("{0}: {1}".format(self.t.cyan("Hash"), self.t.red(self.hash)))
        data.append("{0}: {1}".format(self.t.cyan("File"), self.t.red(self.file)))
        data.append("{0}: ".format(self.t.cyan("Variables")) + ["", self.t.red("None")][self.variables == []] )
        for var_name, var_value in self.variables:
            data.append("\t{0} = {1}".format(self.t.green(var_name), self.t.red(repr(var_value))))
        data.append("{0}: ".format(self.t.cyan("Methods")) + ["", self.t.red("None")][self.methods == []])
        for method_name, method_value in self.methods:
            f_args = inspect.formatargspec(*inspect.getargspec(method_value))[1:-1]
            data.append("\t{0}({1})".format(self.t.green("{0}.{1}".format(self.name, method_name)), self.t.red(f_args)))

        return data

class ObjectInspector(object):
    def __init__(self):
        pass
    def inspect(self, obj):
        try:
            result = ObjectResults(obj)
            result.variables = list(self.getVariablesFromObject(obj))
            result.methods = inspect.getmembers(obj, inspect.ismethod)
            return result
        except:
            return ObjectResults(None) # set invalid object for [] return
    def getVariablesFromObject(self, obj):
        all_methods = inspect.getmembers(obj);
        for (key, item) in all_methods:
            if not callable(item) and not (key.startswith("__") and key.endswith("__")):
                yield (key, item)