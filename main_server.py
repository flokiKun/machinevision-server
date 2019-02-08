import json
import socket
import pathlib
import os
import platform
import threading as thread
import cv2 as cv
import time
from google_images_download import google_images_download
from pdd_prep_data import Prep_Class
from detection_data import Detection
from threading import Thread
import xml_to_csv


class Obj():
    def __init__(self, name, info_data):
        self.info_data = info_data
        self.name = str(name)

    def save(self, dir):
        if not pathlib.Path('{}'.format(dir)).exists():
            os.makedirs(str(dir))
        with open('{}/{}.json'.format(dir, self.name), 'w+') as outfile:
            json.dump(self.info_data, outfile)
            pass

def readNparseObject(id):
    if not pathlib.Path('artifact_objects').exists():
        return """No atrifact_objects dir , can't read Object """
    if not pathlib.Path('artifact_objects/{id}.json'.format(id=id)).exists():
        return """No such file , can't read Object """
    with open('artifact_objects/{id}.json'.format(id=id)) as f:
        object_Data = json.loads(f.read())
    return object_Data

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


def dwn_web_img(request, count_urls, offset):
    response = google_images_download.googleimagesdownload()

    arguments = {
        "keywords": str(request), "limit": count_urls, "print_urls": False, "offset": offset,
        'no_download': True, "extract_metadata": True
    }
    if platform.system() != 'Windows':
        arguments['chromedriver'] = '/usr/lib/chromium-browser/chromedriver'

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
print('Use OpenCV:{}'.format(cv.__version__))
print('Running on {}:{}'.format(host, port))
print('=============================')

threads_max = 5
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.bind((host, port))
except socket.error as e:
    print('[SERVER] ERROR: ' + str(e))

tcp_socket.listen(10)

print('[SERVER] Waiting for a connection...')


def main_loop():
    #TODO : Make all of thus in class (Low Priority)
    conn, addr = tcp_socket.accept()
    try:
        databytes = bytearray()
        while True:
            buffData = conn.recv(4096)
            if not buffData:
                break
            databytes += buffData
        # print(databytes)
        data = databytes.decode('utf-8')
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
        # time.sleep(5)
        try:
            offset = int(recvdata['offset'])
        except KeyError:
            offset = 0
        print('\tquery:{}\trtcount:{}'.format(recvdata['query'], recvdata['rtcount']))
        dwn_web_img(recvdata['query'], int(recvdata['rtcount']) + offset, offset + 1)
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
        new_obj = Obj(name=recvdata['artifact_object']['id'], info_data=recvdata['artifact_object'])
        new_obj.save('artifact_objects')
        conn.send(b'success')

    elif request == 'list_objects':
        obj_list = []
        if not pathlib.Path('artifact_objects').exists():
            print('[SERVER]no such dir')
        else:
            for filename in os.listdir('artifact_objects/'):
                # obj_list.append(filename)
                with open('artifact_objects/{}'.format(filename), 'r') as file_json:
                    obj_list.append(json.load(file_json))
                    file_json.close()
        response = {
            'answer_code': 'list_objects',
            'objects': obj_list
        }
        conn.send(bytes(json.dumps(response), 'utf-8'))

    elif request == 'delete_object':
        try:
            os.remove('artifact_objects/{}.json'.format(recvdata['id']))
            conn.send(b'success')
        except:
            pass
    elif request == 'train_model':
        obj_data = readNparseObject(recvdata['object_id'])
        name = obj_data['title']
        id = recvdata['object_id']
        # repr(obj_data)
        print(obj_data)
        # obj_data['status'] = 1
        Obj(recvdata['object_id'], obj_data).save('artifact_objects')
        print(id)
        prep_data = Prep_Class(name, id)
        prep_data.init_dirs()
        prep_data.img_from_link('new')
        prep_data.separate_img()
        prep_data.gen_labelmap_file()
        prep_data.making_xmls('train')
        prep_data.making_xmls('test')
        xml_to_csv.do_this(name)
        train = '--csv_input=prep_data/{a}/data/train_labels.csv --image_dir=prep_data/{a}/models/model/train --output_path=prep_data/{a}/data/train.record'.format(a=name)
        eval = '--csv_input=prep_data/{a}/data/test_labels.csv --image_dir=prep_data/{a}/models/model/test --output_path=prep_data/{a}/data/test.record'.format(a=name)
        os.system('python3 generate_tfrecords.py '+train)
        os.system('python3 generate_tfrecords.py '+eval)
        prep_data.gen_pipeline()
        print('[SERVER] Data is ready')
        print('[RUN BASH]')
        # obj_data['status'] = 2
        # obj_data['lastActType'] = 2
        # obj_data['lastAct'] = int(round(time.time() * 1000))
        Obj(recvdata['object_id'], obj_data).save('artifact_objects')
        conn.send(b'success')
        # potok = Thread(target=prep_data.gen_train_run_bash_and_run)
        # potok.start()
        # potok.join()

    elif request == 'guess':
        detection = Detection('coco')
        imgs = detection.detection_on_debug_img()
        conn.send(b'https://i.imgur.com/bvcPraS.jpg')
        for img in imgs:
            cv.imshow('res',img)
            cv.waitKey(0)
            cv.destroyAllWindows()
    # elif request == 'stop_train':
    #     pass
    # else:
    # conn.send(b'ERROR wrong request_code')
    # try:
    #    start_new_thread(threaded_client, (conn,))
    # except ConnectionResetError:
    #    pass
    # conn.send(data)


while True:
    try:
        main_loop()
    except KeyboardInterrupt:
        tcp_socket.close()
        break

print('[SERVER] Server is down.')
