import time
import sys
from HyREPL.server import start_server

if __name__ == '__main__':
    port = 1337
    while True:
        try:
            t, _ = start_server('127.0.0.1', port)
        except OSError:
            port += 1
        else:
            sys.stdout.write("Listening on {}\a\n".format(port))
            sys.stdout.flush()
            while True:
                time.sleep(1)
            t.join()
