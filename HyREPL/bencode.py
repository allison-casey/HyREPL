def decode_multiple(thing):
    "Uses `decode` to decode all encoded values in `thing`."
    rv = []
    while len(thing) > 0:
        i, rest = decode(thing)
        rv.append(i)
        thing = rest
    return rv

def decode(thing):
    "Decodes `thing` and returns the first parsed bencode value encountered as"
    "well as the unparsed rest"
    if thing.startswith(b'd'):
        return decode_dict(thing)
    elif thing.startswith(b'l'):
        return decode_list(thing)
    elif thing.startswith(b'i'):
        return decode_int(thing)

    # assume string
    delim = thing.find(b':')
    size = int(thing[:delim].decode('utf-8'))
    return thing[delim+1:delim+1+size].decode('utf-8'), thing[delim+1+size:]

def decode_int(thing):
    thing = thing[1:] # skip leading 'i'
    end = thing.find(b'e')
    return int(thing[:end], 10), thing[end+1:]

def decode_list(thing):
    thing = thing[1:] # skip leading 'l'
    rv = []
    while len(thing) > 0:
        i, rest = decode(thing)
        rv.append(i)
        thing = rest
        if thing.startswith(b'e'):
            break
    if len(thing) == 0:
        raise ValueError("List without end marker")
    return rv, thing[1:]

def decode_dict(thing):
    thing = thing[1:] # skip leading 'd'
    rv = {}
    while len(thing) > 0:
        # consume keys, then values
        k, rest = decode(thing)
        v, rest = decode(rest)
        rv[k] = v
        thing = rest
        if thing.startswith(b'e'):
            break
    if len(thing) == 0:
        raise ValueError("Dictionary without end marker")
    return rv, thing[1:]

def encode(thing):
    "Returns a bencoded string that represents `thing`. Might throw all sorts"
    "of exceptions if you try to encode weird things. Don't do that."
    if isinstance(thing, int):
        return encode_int(thing)
    elif isinstance(thing, str):
        return encode_str(thing)
    elif isinstance(thing, bytes):
        return encode_bytes(thing)
    elif isinstance(thing, dict):
        return encode_dict(thing)
    elif thing is None:
        return encode_bytes(b"")
    return encode_list(thing)

def encode_int(thing):
    return bytes("i{}e".format(thing), 'utf-8')

def encode_str(thing):
    l = len(bytes(thing, 'utf-8'))
    return bytes("{}:{}".format(l, thing), 'utf-8')

def encode_bytes(thing):
    return bytes("{}:{}".format(len(thing), thing.decode('utf-8')), 'utf-8')

def encode_dict(thing):
    rv = b'd'
    for k, v in thing.items():
        rv += encode(k)
        rv += encode(v)
    return rv + b'e'

def encode_list(thing):
    rv = b'l'
    for i in thing:
        rv += encode(i)
    return rv + b'e'
