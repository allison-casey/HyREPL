import asyncio
import uuid
from HyREPL.session import SessionHandle, Sessions, Session
from HyREPL import bencode

class BencodeProtocol(asyncio.StreamReaderProtocol):
    """Basic bencode protocol for the standar transport"""

    sess = Sessions()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.buf = b""

    def connection_made(self, transport):
        # Assigning the transport
        self.transport = transport

    def data_received(self, data):
        # TODO: Rewrite so we dont loose data
        self.buf += data
        try:
            msg, rest = bencode.decode(self.buf)
            print(type(msg), msg, self.buf)
            self.buf = rest
        except Exception as err:
            # Lets just handle the fetching of more data if
            # bencodes decoder never gets an end
            # TODO: This dosnt really work
            #lr = yield from self.reader.readline()
            #print("exception")
            #print(lr)
            return
        else:
            if len(msg) == 0:
                return
            # We need to reply with bytes
            ret = bencode.encode(msg)
            # self.transport.write(ret)

        # Looking for a session inside the keys, and if there is one
        # we assing the old session thread
        if not "session" in msg.keys():
            session = Session(self.transport, uuid.uuid4())
        elif self.sess.check_uuid(msg["session"]):
            #print("\nTrue")
            session = self.sess.get_uuid(msg["session"])

        # Should need some revising
        th = SessionHandle(msg, self.sess, session)
        session.thread = th
        self.sess.add_uuid(session)
        th.start()
        if len(self.buf) != 0:
            # Maybe there's another message
            self.data_received(b"")

    def feed_eof(self):
        pass

    def callback(self, x):
        # wat
        pass
