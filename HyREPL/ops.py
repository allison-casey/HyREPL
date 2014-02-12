

_descriptions = {}

def set_description(requires=None, expects=None, handles=None):
    def _(fn):
        op = handles.keys()
        _description[op]
    return _


def find_op(op):
    return None # fn


@set_description(
                # session needs to be defined at a higher level
                requires=("session"),
                # eval needs to be present somewhere as a middleware
                # at a lower level
                expects=("eval"),
                # The expected input and info
                handles={"stdin":
                         {"doc": "blach",
                          "requires": "stdin",
                          "optional": {},
                          "returns": {"status" "\"need-input\" will be sent if we need stdin"}}})
def add_stdin(transport, msg):
    pass
