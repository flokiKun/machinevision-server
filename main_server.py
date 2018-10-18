import socket
import random
import json
from google_images_download import google_images_download
import urllib.request
from _thread import *
import sys


def dwn_web_img(request, count_urls):
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": str(request), "limit": count_urls, "print_urls": False, "offset": random.randrange(1, 100),
                 "extract_metadata": True}
    response.download(arguments)


print('Machine Vision Server ALPHA')
print('Copyright JP Tech.')

tpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        if data is not None:
            recvdata = json.loads(data)
        else:
            recvdata = []
        print(data)
    except socket.error:
        print('!ERROR! Too much size for us')
        recvdata = {}
    print('[SERVER]New data from {}:{}'.format(addr[0], addr[1]))

    request = recvdata['request_code']
    print('[SERVER]Rev  :{}'.format(request))

    if request == 'regimg':
        dwn_web_img(recvdata['query'], recvdata['rtcount'])
        meta_json = open('logs/{}.json'.format(recvdata['query']), 'r')
        answer = '{ \"answer_code\": \"query_metadata\", \"metadata\":' + str(meta_json) + '}'
        conn.send(bytes(answer, 'utf-8'))
        meta_json.close()
    else:
        conn.send(b'ERROR wrong request_code')

    # try:
    #    start_new_thread(threaded_client, (conn,))
    # except ConnectionResetError:
    #    pass
    # conn.send(data)


while True:
    main()
