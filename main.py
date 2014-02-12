import asyncio
from HyREPL.server import BencodeProtocol

#factory = lambda: BencodeProtocol(asyncio.StreamReader())
#factory = asyncio.async(BencodeProtocol(asyncio.StreamReader()))
#loop = asyncio.get_event_loop()
#asyncio.async(loop.create_server(factory, '127.0.0.1', 8888))



loop = asyncio.get_event_loop()

def start_server():
    proto_factory = lambda: BencodeProtocol(asyncio.StreamReader())
    return loop.create_server(proto_factory, '127.0.0.1', 8888)

s = loop.run_until_complete(start_server())


try:

    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    loop.close()
