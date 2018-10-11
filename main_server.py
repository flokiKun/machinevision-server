import socket
import sys
import tornado.ioloop

s = socket.socket()
host = 'localhost'
port = 8007
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()

def main():

    data = conn.recv(50)
    print('client is at',addr,data)
    #conn.send(data)

main()
tornado.ioloop.IOLoop.current().start()
conn.close()
