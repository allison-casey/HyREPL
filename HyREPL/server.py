import asyncio
import nrepl.bencode as nrepl
import uuid
from HyREPL.session import SessionHandle, Sessions, Session



class BencodeProtocol(asyncio.StreamReaderProtocol):
    """Basic bencode protocol for the standar transport"""

    sess = Sessions()

    def connection_made(self, transport):
        # Assigning the transport
        self.transport = transport

    def data_received(self, data):
        # TODO: Rewrite so we dont loose data
        print(data)
        self._task = asyncio.async(self.handle_sess(data))
        self._task.add_done_callback(self.callback)


    def callback(self, x):
        # wat
        pass


    @asyncio.coroutine
    def handle_sess(self, data):
        try:
            msg = list(nrepl.decode(data.decode()))[0]
            print(msg)
        except:
            # Lets just handle the fetching of more data if
            # bencodes decoder never gets an end
            # TODO: This dosnt really work
            lr = yield from self.reader.readline()
            print("exception")
            print(lr)
        else:
            # We need to reply with bytes
            ret = bytes(nrepl.encode(msg), "utf-8")
            #self.transport.write(ret)

        # Looking for a session inside the keys, and if there is one
        # we assing the old session thread
        if not "session" in msg.keys():
            session = Session(self.transport, uuid.uuid4())
        elif self.sess.get_uuid(msg["session"]):
            session = msg["session"]

        # Should need some revising
        th = SessionHandle(msg, self.sess, session)
        session.thread = th
        self.sess.add_uuid(session)
        th.start()
