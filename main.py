import asyncio
from HyREPL.server import BencodeProtocol

factory = lambda: BencodeProtocol(asyncio.StreamReader())
#factory = asyncio.async(BencodeProtocol(asyncio.StreamReader()))
loop = asyncio.get_event_loop()
asyncio.async(loop.create_server(factory, '127.0.0.1', 8888))

try:

    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    loop.close()
