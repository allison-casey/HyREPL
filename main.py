import asyncio
from HyREPL.server import BencodeProtocol

def start_server(ip,port):
	factory = lambda: BencodeProtocol(asyncio.StreamReader())
	#factory = asyncio.async(BencodeProtocol(asyncio.StreamReader()))
	loop = asyncio.get_event_loop()
	asyncio.async(loop.create_server(factory, ip, port))

	try:
	    loop.run_forever()
	except KeyboardInterrupt:
	    print("exit")
	finally:
	    loop.close()

if __name__ == '__main__':
	start_server('127.0.0.1', 1337)