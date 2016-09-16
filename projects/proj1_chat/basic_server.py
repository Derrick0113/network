import socket
import sys
import signal, os


class basic_server(object):
    def __init__(self, port):
        self._socket = socket.socket()
        self._socket.bind(("0.0.0.0", port))
        self._socket.listen(5)
        print("The server is running")
        self.__run()

    def __run(self):
        while (True):
            (new_socket, address) = self._socket.accept()
            message = new_socket.recv(1024)
            print(message)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("error usage")
        sys.exit(1)

    port = int(sys.argv[1])
    basic_server(port)
