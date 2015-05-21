def encode(thing):
    if isinstance(thing, dict):
        return encode_dict(thing)
    elif isinstance(thing, str):
        return encode_bytes(bytes(thing, 'utf-8'))
    elif isinstance(thing, bytes):
        return encode_bytes(thing)
    elif isinstance(thing, int):
        return encode_int(thing)
    else:
        try:
            return encode_iterable(thing)
        except Exception:
            raise

def encode_int(thing):
    return "i{!s}e".format(thing)

def encode_bytes(thing):
    return "{}:{}".format(len(thing), thing.decode('utf-8'))

def encode_iterable(thing):
    rv = "l"
    for i in thing:
        rv += encode(i)
    return rv + "e"

def encode_dict(thing):
    rv = "d"
    for k, v in thing.items():
        rv += encode(k)
        rv += encode(v)
    return rv + "e"

def decode(thing):
    if thing.startswith(bytes("i", 'utf-8')):
        return decode_int(thing[1:])
    elif thing.startswith(bytes("l", 'utf-8')):
        return decode_list(thing[1:])
    elif thing.startswith(bytes("d", 'utf-8')):
        return decode_dict(thing[1:])

    delimit = thing.find(bytes(':', 'utf-8'))
    size = thing[:delimit].decode('utf-8')
    if len(thing[delimit+1:]) != int(size, 10):
        raise ValueError("Expected string length {}, got {}".format(len(thing[delimit+1:]), size))
    return thing[delimit+1:].decode('utf-8')

def decode_int(thing):
    if not thing.endswith(bytes('e', 'utf-8')):
        raise ValueError("Integer does not end with 'e': {}".format(thing))
    return int(thing[:-1], 10)

def decode_list(thing):
    if not thing.endswith(bytes('e', 'utf-8')):
        raise ValueError("List does not end with 'e': {}".format(thing))
    thing = thing[:-1]
    rv = []
    changed = True
    while len(thing) > 0 and changed:
        changed = False
        for idx in range(len(thing) + 1):
            try:
                t = decode(thing[:idx])
                rv.append(t)
                thing = thing[idx:]
                changed = True
                break
            except Exception as err:
                pass
    if len(thing) > 0:
        raise ValueError("Malformed list")
    return rv

def decode_dict(thing):
    if not thing.endswith(bytes('e', 'utf-8')):
        raise ValueError("Dict does not end with 'e': {}".format(thing))

    items = list(reversed(decode_list(thing)))
    rv = {}
    while len(items) > 0:
        key = items.pop()
        val = items.pop()
        rv[key] = val

    return rv
