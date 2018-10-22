import socket
import sys
#import tornado.ioloop

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = 'localhost'
port = 1337
s.connect((host, port))
pack = bytes(' { "request_code":"reqimg", "query":"ya eblan", "rtcount":"5" }', 'utf-8')
s.send(pack)
#data = s.recv(1000000)