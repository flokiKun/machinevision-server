import json
import socket
import pathlib
import os
import threading as thread
#import cv2 as cv
from google_images_download import google_images_download

class Obj():
    def __init__(self,name,info_data):
        self.info_data = info_data
        self.name = str(name)

    def save(self,dir):
        if not pathlib.Path('{}'.format(dir)).exists():
            os.makedirs(str(dir))
        with open('{}/{}.json'.format(dir,self.name),'w+') as outfile:
            json.dump(self.info_data,outfile)
            pass

# class Potok(thread.Thread):
#
#     def __init__(self, name,func):
#         thread.Thread.__init__(self)
#         self.name = name
#         self.func = func
#         func()
#
#     def run(self):
#         print('Bla')


def dwn_web_img(request, count_urls,offset):
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": str(request), "limit": count_urls, "print_urls": False, "offset":offset,'no_download':True,"extract_metadata": True,'chromedriver':'/usr/lib/chromium-browser/chromedriver'}
    response.download(arguments)

def get_my_ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    res = s.getsockname()[0]
    s.close()
    return res

# CONST


host = get_my_ipv4()
port = 1337

print('=============================')
print('Machine Vision Server ALPHA')
print('Copyright JaPy Tech.')
# print('Use OpenCV:{}'.format(cv.__version__))
print('Running on {}:{}'.format(host,port))
print('=============================')

threads_max = 5
tpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tpc_socket.bind((host, port))
except socket.error as e:
    print('[SERVER] ERROR: ' + str(e))


tpc_socket.listen(10)

print('[SERVER] Waiting for a connection...')


def main_loop():
    conn, addr = tpc_socket.accept()
    try:
        data = conn.recv(1048576)
        data = data.decode('utf-8')
        if data != '':
            print('[SERVER] Received data from ' + addr[0] + ':\n\t' + data)
        if data is not None:
            try:
                recvdata = json.loads(data)
            except:
                recvdata = {'reqimg': None, 'query': None, 'rtcount': None, 'offset': None}
        else:
            recvdata = []
    except socket.error as e:
        print('!ERROR! {}'.format(str(e)))
        recvdata = {}
    try:
        request = recvdata['request_code']
        print('[SERVER] Request: {}'.format(request))
        pass
    except KeyError:
        request = ''
        pass

    if request == 'reqimg':
        print('Waiting....')
        #time.sleep(5)
        try:
            offset=int(recvdata['offset'])
        except KeyError:
            offset = 0
        print('\tquery:{}\trtcount:{}'.format(recvdata['query'], recvdata['rtcount']))
        dwn_web_img(recvdata['query'], int(recvdata['rtcount'])+offset,offset+1)
        with open('logs/{}.json'.format(recvdata['query'])) as f:
            meta_json = json.loads(f.read())
        response = {
            "response_code": "query_metadata",
            "metadata": meta_json
        }
        response = json.dumps(response)
        print('[SERVER] Sending:\n\t{}'.format(response))
        conn.send(bytes(response, 'utf-8'))
        print('[SERVER] Success')

    elif request == 'new_object':
        new_obj = Obj(name=recvdata['artifact_object']['id'],info_data=recvdata['artifact_object'])
        new_obj.save('artifact_objects')
        conn.send(b'success')

    elif request == 'list_objects':
        obj_list=[]
        if not pathlib.Path('artifact_objects').exists():
            print('[SERVER]no such dir')
        else:
            for filename in os.listdir('artifact_objects/'):
                #obj_list.append(filename)
                with open('artifact_objects/{}'.format(filename),'r') as file_json:
                    obj_list.append(json.load(file_json))
                    file_json.close()
        response = {
            'answer_code': 'list_objects',
            'objects': obj_list
        }
        conn.send(bytes(json.dumps(response),'utf-8'))
    elif request == 'delete_object':
        try:
            os.remove('artifact_objects/{}.json'.format(recvdata['id']))
        except:
            pass

    # else:
        # conn.send(b'ERROR wrong request_code')

    # try:
    #    start_new_thread(threaded_client, (conn,))
    # except ConnectionResetError:
    #    pass
    # conn.send(data)

while True:
    main_loop()
