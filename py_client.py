import socket
import sys
import tornado.ioloop

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = 'localhost'
port = 80
s.connect((host, port))
pack = bytes(str(input('> ')), 'utf-8')
s.send(pack)
#data = s.recv(1000000)