# coding=utf8
# part1, client end
# recv is non-blocking but send and sendall is blocking

import socket
import utils
import sys
import select

class Server(object):
    def __init__(self, host,port):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outputs = []
        try:
            self.socket.bind((self.host,self.port))
            self.socket.listen(5)
        except socket.error,e:
            print e

    def run(self):
        inputs = [self.socket]
        while True:
            try:
                readable,writeable,exceptional = select.select(inputs,self.outputs,[])
            except select.error,e:
                break
            if self.socket in readable:
                client,addr = self.socket.accept()
                self.outputs.append(client)
                inputs.append(client)
            for csk in readable:
                csk.recv(1024) # 读取1024个字节




if __name__ == '__main__':
    server = Server("0.0.0.0", 8888)
    server.run()
