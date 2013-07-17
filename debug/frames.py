import inspect, sys, os, blessings, itertools

class FrameResults(object):
    def __init__(self, frame, objectInspector = None ):
        self.frame = frame
        self.objectInspector = objectInspector
        self.msg = None
        self.t = blessings.Terminal()


    def tabAll(self, data):

        return map(lambda i: "\t" + i, data)
    def toInfo(self):
        data = []
        data.append(self.t.yellow("----------Frame Report----------"))
        if self.msg:
            data.append("{0}: {1}".format(self.t.cyan("Message"), self.t.red(self.msg)))
        data.append("{0}: {1}".format(self.t.cyan("File"), self.t.red(self.frame.f_code.co_filename)))
        data.append("{0}: {1}".format(self.t.cyan("Line"), self.t.red(str(self.frame.f_lineno))))
        if self.objectInspector:
            localObjects = set()
            for variable, pointer in self.frame.f_locals.items():
                if not callable(pointer):
                    inspectedObject = self.objectInspector.inspect(pointer)
                    localObjects.add(inspectedObject)
            data.append(self.t.cyan("Local Variables") + ": " + ["",self.t.red("None")][len(localObjects) == 0])
            for object in localObjects:
                data.extend( self.tabAll(object.toInfo()) )


            globalObjects = set()
            for variable, pointer in self.frame.f_globals.items():
                if inspect.isclass(pointer) and not inspect.isbuiltin(pointer):
                    inspectedObject = self.objectInspector.inspect(pointer)
            data.append(self.t.cyan("Global Variables") + ": " + ["",self.t.red("None")][len(globalObjects) == 0])
            for object in globalObjects:
                data.extend( self.tabAll(object.toInfo()) )
        return data

class FrameInspector(object):
    def __init__(self):
        pass
    def inspect(self, frame, objectInspector=None):
        result = FrameResults(frame, objectInspector)
        return result