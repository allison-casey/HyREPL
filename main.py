from hyrepl.connection import nREPLServerHandler

def main():
    try:
        t = nREPLServerHandler("localhost", 9999)
        t.start()
        while True:
            pass
    except KeyboardInterrupt:
        t.stop()


if __name__ == '__main__':
    main()