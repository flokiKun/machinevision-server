import socket
import random
import json
#from google_images_download import google_images_download
import urllib.request
from _thread import *
import sys

#def dwn_web_img(request):
#    response = google_images_download.googleimagesdownload()
#    arguments = {"keywords": str(request), "limit": 5, "print_urls": False,'no_numbering':True,'prefix':str(request)}
#    response.download(arguments)

tpc_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '192.168.43.103'
port = 1337

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
        data = data.decode('utf-8')
        print(data)
    except socket.error:
        data =b'!ERROR! Too much size for us'
    print('[SERVER]New data from {}:{}'.format(addr[0], addr[1]))
    print('[SERVER]Recv:{}'.format('JSON'))

    requset = json.loads(data)['requestCode']
    print('[SERVER]JSON:{}'.format(requset))
    #dwn_web_img(data.decode('utf-8'))
    try:
        conn.send(b'[SERVER]Img was download to server!')
    except socket.error:
        pass
    #try:
    #    start_new_thread(threaded_client, (conn,))
    #except ConnectionResetError:
    #    pass
    #conn.send(data)

while True:
    main()

