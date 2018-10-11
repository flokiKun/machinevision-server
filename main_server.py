import socket
from _thread import *
import sys


tpc_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = 'localhost'
port = 80

try:
    tpc_socket.bind((host, port))
except socket.error as e:
    print(str(e))

def threaded_client(conn):
    conn.send(str.encode('[SEVER]Welcome, send your data\n'))
    while True:
        data = conn.recv(1048576)
        reply = '[SERVER]Server output: ' + data.decode('utf-8')
        if not data:
            break
        conn.sendall(str.encode(reply))
    conn.close()

tpc_socket.listen(5)

print('[SERVER]Waiting for a connection...')

def main():
    conn, addr = tpc_socket.accept()
    try:
        data = conn.recv(1048576)
    except socket.error:
        data =b'!ERROR! Too much size for us'
    print('[SERVER]New data from {}:{}'.format(addr[0], addr[1]))
    print('[SERVER]Recv:{}'.format(data.decode('utf-8')))
    try:
        start_new_thread(threaded_client, (conn,))
    except ConnectionResetError:
        pass
    #conn.send(data)

while True:
    main()