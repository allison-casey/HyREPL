import asyncio
import nrepl.bencode as nrepl
import io
from HyREPL.session import SessionHandle, Sessions

StringIO = io.StringIO



nrepl._read_fns = {"i": nrepl._read_int,
                   "l": nrepl._read_list,
                   "d": nrepl._read_map,
                   "e": lambda _: None,
                   # EOF
                   None: lambda _: None}


def _read_list(s):
    data = []
    #gotten_end = False
    while True:
        datum = nrepl._read_datum(s)
        #if datum == "end":
        #    gotten_end = True
        if not datum:
            break
        data.append(datum)

    #if not gotten_end:
    #    raise Exception("No end gotten!")

    return data

nrepl._read_list = _read_list

# Terrible hack, but we basicaly make sure we get the end of a message by
# Throwing an exception when "end" is never returned from _read_datum
# Needs a better solution until we are sure the server alwys recieves the
# whole message

class BencodeProtocol(asyncio.StreamReaderProtocol):
    sess = Sessions()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print(data)
        self._task = asyncio.async(self.handle_sess(data))
        self._task.add_done_callback(self.callback)


    def callback(self, x):
        pass


    @asyncio.coroutine
    def handle_sess(self, data):
        iostring = io.StringIO(data.decode())
        try:
            a = nrepl._read_datum(iostring)
        except:
            # Lets just handle the fetching of more data if
            # bencodes decoder never gets an end
            lr = yield from self.reader.readline()
            print("exception")
            print(lr)
        else:
            # We need to reply with bytes
            ret = bytes(nrepl.encode(a), "utf-8")
            #self.transport.write(ret)

        if not "session" in a.keys():
            n = str(self.sess.get_uuid())
        else:
            n = ret["session"]

        th = SessionHandle(a, n, self.transport)
        self.sess.add_uuid(n, th)
        th.start()



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


