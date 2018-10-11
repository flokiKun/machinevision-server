import socket
import sys
import tornado.ioloop

s = socket.socket()
host = 'localhost'
port = 8007

def main():
    s.connect((host, port))
    pack=bytes(str(input('> ')), 'utf-8')
    s.send(pack)
    #data = s.recv(1000000)

main()
tornado.ioloop.IOLoop.current().start()
