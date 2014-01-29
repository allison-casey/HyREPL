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



class BencodeProtocol(asyncio.StreamReaderProtocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print(data)
        iostring = io.StringIO(data.decode())
        try:
            a = nrepl._read_datum(iostring)
            print(a)
        except:
            # Lets just handle the fetching of more data if
            # bencodes decoder never gets an end
            lr = self.reader.readline()
            print(lr)

        # We need to reply with bytes
        ret = bytes(nrepl.encode(a), "utf-8")
        print(ret)
        self.transport.write(ret)

        self.transport.close()

    def bencode_send(self, data):
        self.transport(send)

    # Lets wrap this!
    @property
    def reader():
        return self._stream_reader

    @property
    def writer():
        return self._stream_writer





factory = lambda: BencodeProtocol(asyncio.StreamReader())
loop = asyncio.get_event_loop()
l = loop.create_server(factory, '127.0.0.1', 8888)
s = loop.run_until_complete(l)

try:

    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    server.close()
    loop.close()



