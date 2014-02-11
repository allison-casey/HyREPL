import asyncio
import nrepl.bencode as nrepl
import io

StringIO = io.StringIO



nrepl._read_fns = {"i": nrepl._read_int,
                   "l": nrepl._read_list,
                   "d": nrepl._read_map,
                   "e": lambda _: "end",
                   # EOF
                   None: lambda _: None}


def _read_list(s):
    data = []
    gotten_end = False
    while True:
        datum = nrepl._read_datum(s)
        if datum == "end":
            gotten_end = True
        if not datum:
            break
        data.append(datum)

    if not gotten_end:
        raise Exception("No end gotten!")

    return data

nrepl._read_list = _read_list

# Terrible hack, but we basicaly make sure we get the end of a message by
# Throwing an exception when "end" is never returned from _read_datum
# Needs a better solution until we are sure the server alwys recieves the
# whole message

import uuid

class Sessions():
   uuids = {}

   def del_uuid(self, uuid):
       del self.uuids[uuid]

   def get_uuid(self):
       new = uuid.uuid4()
       self.uuids[new] = None
       return new

   def check_uuid(self, uuid):
       return self.uuids[uuid]


class BencodeProtocol(asyncio.StreamReaderProtocol):
    sess = Sessions()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print("lol")
        self._task = asyncio.async(self.handle_sess(data))
        self._task.add_done_callback(self.callback)


    def callback(self, x):
        pass


    @asyncio.coroutine
    def handle_sess(self, data):
        print(data)
        iostring = io.StringIO(data.decode())
        try:
            a = nrepl._read_datum(iostring)
        except:
            # Lets just handle the fetching of more data if
            # bencodes decoder never gets an end
            lr = self.reader.readline()
            print("exception")
        else:
            # We need to reply with bytes
            ret = bytes(nrepl.encode(a), "utf-8")
            print(ret)
            self.transport.write(ret)

        if not "session" in ret.keys():
            n = self.sess.get_uuid()
        else:
            n = ret["session"]

        # ...

        self.transport.close()


    def terminated(self, f):
        if f.done() and not f.cancelled():
            pass

    # Lets wrap this!
    @property
    def reader(self):
        return self._stream_reader


    @property
    def writer():
        return self._stream_writer


