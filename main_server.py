import socket
import random
import json
from google_images_download import google_images_download
import time
import urllib.request
from _thread import *
import sys


def dwn_web_img(request, count_urls):
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": str(request), "limit": count_urls, "print_urls": False, "offset":1,"extract_metadata": True}
    response.download(arguments)


print('=============================')
print('Machine Vision Server ALPHA')
print('Copyright JaPy Tech.')
print('=============================')


tpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.43.103'
port = 1337

try:
    tpc_socket.bind((host, port))
except socket.error as e:
    print('[SERVER] ERROR: ' + str(e))


def threaded_client(conn):
    conn.send(str.encode('[SEVER]Welcome, send your data\n'))
    while True:
        data = conn.recv(1048576)
        reply = '[SERVER]Server output: ' + data.decode('utf-8')
        if not data:
            break
        conn.sendall(str.encode(reply))
    conn.close()


tpc_socket.listen(10)

print('[SERVER] Waiting for a connection...')


def main_loop():
    conn, addr = tpc_socket.accept()
    try:
        data = conn.recv(1048576)
        data = data.decode('utf-8')
        print('[SERVER] Received data from ' + addr[0] + ':\n\t' + data)
        if data is not None:
            try:
                recvdata = json.loads(data)
            except:
                recvdata = {'reqimg':None,'query':None,'rtcount':None}
                print('[SERVER]Recv data is not JSON!')
        else:
            recvdata = []
    except socket.error:
        print('!ERROR! Too much size for us')
        recvdata = {}
    try:
        request = recvdata['request_code']
        print('[SERVER] Request: {}'.format(request))
        pass
    except KeyError:
        request = ''
        print('[SERVER]Wrong request type')
        pass

    if request == 'reqimg':
        print('Waiting....')
        time.sleep(5)
        print('\tquery:{}\trtcount:{}'.format(recvdata['query'], recvdata['rtcount']))
        dwn_web_img(recvdata['query'], recvdata['rtcount'])
        meta_json = json.loads(open('logs/{}.json'.format(recvdata['query'])).read())
        answer = '{ \"answer_code\": \"query_metadata\", \"metadata\":' + str(meta_json) + '}'
        print('[SERVER] Sending metadata:\n\t{}'.format(str(meta_json)))
        conn.send(bytes(answer, 'utf-8'))
    # else:
        # conn.send(b'ERROR wrong request_code')

    # try:
    #    start_new_thread(threaded_client, (conn,))
    # except ConnectionResetError:
    #    pass
    # conn.send(data)


while True:
    main_loop()
