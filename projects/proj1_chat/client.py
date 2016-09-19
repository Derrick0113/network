# coding=utf8
# part1, client end
# recv is non-blocking but send and sendall is blocking

import socket
import utils
import sys
import select


class client(object):
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = []
        try:
            self.socket.connect((self.host, self.port))
        except socket.error, e:
            print utils.CLIENT_CANNOT_CONNECT.format(host, port)
            sys.exit(-1)
        self.socket.send(name)  # 注册名字

    def __del__(self):
        self.socket.close()

    def run(self):
        inputs = [self.socket, sys.stdin]
        outputs = []
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()
        while (True):
            try:
                readables, writeables, exceptional = select.select(inputs, outputs, [])
            except select.error, e:
                print e
                break
            for rec in readables:
                if self.socket == rec:
                    try:
                        data = self.socket.recv(1024)
                        if (data == ""):
                            self.socket.close()
                            self.writeToStdout(utils.CLIENT_SERVER_DISCONNECTED.format(self.host, self.port))
                            sys.exit(-1)
                        self.writeToStdout(data)
                    except socket.error, e:
                        print e
                        break
                elif sys.stdin == rec:
                    in_text = sys.stdin.readline()
                    self.socket.send(in_text.ljust(200))
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()


    def writeToStdout(self, data):
        sys.stdout.write(utils.CLIENT_WIPE_ME)
        sys.stdout.write('\r' + data + '\n')
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python client.py Name ServerHost ServerPort"
    else:
        argv = sys.argv[1:]
        try:
            client(argv[0], argv[1], argv[2]).run()
        except KeyboardInterrupt, e:
            del client
