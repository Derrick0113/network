# coding=utf8
# part1, client end
# recv is non-blocking but send and sendall is blocking

import socket
import utils
import sys
import select


class Server(object):
    def __init__(self, port,host="0.0.0.0"):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outputs = []
        self.channels = {}
        self.socketMapToName = {}
        self.buff = {}
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error, e:
            print e

    def stop(self):
        try:
            self.socket.close()
        except socket.error, e:
            print e

    def __del__(self):
        try:
            self.socket.close()
        except socket.error, e:
            print e

    def _command_(self, text, csk):
        text = text.split(' ')
        if text[0] == '/join':
            if (len(text) != 2):
                csk.send(utils.SERVER_JOIN_REQUIRES_ARGUMENT)
                return
            channel = text[1]
            if channel in self.channels:
                if (csk in self.channels[channel]):  # 用户已在
                    return
                else:  # 用户不在
                    self.addToNewChannel(channel, csk)
                    return
            else:  # 未存在该channel
                csk.send(utils.SERVER_NO_CHANNEL_EXISTS.format(channel))
                return
        elif text[0] == '/list':
            csk.send("\n".join(self.channels.keys()))
            return
        elif text[0] == '/create':
            if (len(text) != 2):  # 指令用法错误
                csk.send(utils.SERVER_CREATE_REQUIRES_ARGUMENT)
                return
            else:
                channel = text[1]
                if channel in self.channels:
                    csk.send(utils.SERVER_CHANNEL_EXISTS.format(channel))  # 已经存在
                    return
                else:
                    self.channels[channel] = []  # 新建channel,初始化
                    self.addToNewChannel(channel, csk, True)
                    return
        else:
            csk.send(utils.SERVER_INVALID_CONTROL_MESSAGE.format(text[0]))
        return

    def addToNewChannel(self, channel, csk, create=False):
        name, old_channel = self.socketMapToName[csk]
        if (old_channel != None):
            self.channels[old_channel].remove(csk)
            self._sendChannelExcept(old_channel, csk, utils.SERVER_CLIENT_LEFT_CHANNEL.format(name))
        self.socketMapToName[csk] = (name, channel)
        self.channels[channel].append(csk)
        if not create:
            self._sendChannelExcept(channel, csk, utils.SERVER_CLIENT_JOINED_CHANNEL.format(name))
        return

    def _sendChannelExcept(self, channel, csk, text):
        for e in self.channels[channel]:
            if e != csk:
                e.send(text)

    def run(self):
        inputs = [self.socket]
        while True:
            try:
                readable, writeable, exceptional = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            if self.socket in readable:
                client, addr = self.socket.accept()
                self.outputs.append(client)
                inputs.append(client)
            for csk in readable:
                if (csk == self.socket):
                    continue
                text = csk.recv(200)
                if text == "":
                    # disconnect
                    if(csk not in self.socketMapToName):
                        inputs.remove(csk)
                        continue
                    (name, channel) = self.socketMapToName[csk]
                    self._sendChannelExcept(channel,csk, utils.SERVER_CLIENT_LEFT_CHANNEL.format(name))
                    del self.socketMapToName[csk]
                    self.channels[channel].remove(csk)
                    inputs.remove(csk)
                    continue
                if csk not in self.buff:
                    self.buff[csk] = text
                else:
                    self.buff[csk] = self.buff[csk] + text
                if len(self.buff[csk]) >= 200:
                    text = self.buff[csk][0:200]
                    self.buff[csk] = self.buff[csk][200:]
                else:
                    continue

                text = text.strip(' ').strip('\n')
                if (csk not in self.socketMapToName):  # 未起名
                    self.socketMapToName[csk] = (text, None)
                elif text.startswith('/'):  # 命令
                    self._command_(text, csk)
                else:  # 普通文字
                    (name, channel) = self.socketMapToName[csk]
                    if (channel == None):
                        csk.send(utils.SERVER_CLIENT_NOT_IN_CHANNEL)
                    else:
                        self._sendChannelExcept(channel, csk, '[{0}] '.format(name) + text)


if __name__ == '__main__':
    server = Server(sys.argv[1])
    try:
        server.run()
    except KeyboardInterrupt, e:
        server.stop()
