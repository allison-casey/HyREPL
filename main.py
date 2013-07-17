from hyrepl.connection import nREPLServerHandler
from hyrepl.operations import operations


def main():
    try:
        print(operations)
        t = nREPLServerHandler("localhost", 9999)
        t.start()
        while True:
            pass
    except KeyboardInterrupt:
        t.stop()


if __name__ == '__main__':
    main()