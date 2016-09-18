# coding=utf8
# part1, client end
# recv is non-blocking but send and sendall is blocking

import socket
import utils
import sys
import select

class client(object):
    def __init__(self, name, host,port):
        self.name = name
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host,self.port))
        except socket.error,e:
            print utils.CLIENT_CANNOT_CONNECT.format(host,port)
            sys.exit(-1)
        self.socket.send(name) #注册名字

    def run(self):
        inputs = [self.socket]
        outputs = [sys.stdin]
        while(True):
            try:
                readables, writeables, exceptional = select.select(inputs, outputs,[])
            except select.error,e:
                print e
                break
            if self.socket in readables: #收到服务器信息
                try:
                    data = self.socket.recv(1024)
                    print("收到服务器信息")
                    print data
                except socket.error, e:
                    print e
                    break
            else: #客户端
                print("请输入你要的指令")
                raw_input("")



if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python client.py Name ServerHost ServerPort"
    else:
        argv = sys.argv[1:]
        client(argv[0],argv[1],argv[2])

