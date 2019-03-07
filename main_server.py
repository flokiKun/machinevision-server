import asyncio
import socket
import json
import pathlib
import os
import platform
import cv2 as cv
from google_images_download import google_images_download
from pdd_prep_data import Prep_Class
import xml_to_csv

CWD = '/home/furoki_sama/projects/machinevision-server/'

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
    if not pathlib.Path(CWD+'artifact_objects').exists():
        return """No atrifact_objects dir , can't read Object """
    if not pathlib.Path(CWD+'artifact_objects/{id}.json'.format(id=id)).exists():
        return """No such file , can't read Object """
    with open(CWD+'artifact_objects/{id}.json'.format(id=id)) as f:
        object_Data = json.load(f)
    return object_Data


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


async def handle_echo(reader, writer):

    databytes = bytearray()
    while True:
        buffData = await reader.read(100)
        if not buffData:
            break
        databytes += buffData

    data = databytes.decode('utf-8')

    if data != '':
        print('[SERVER] Received data from client' + ':\n\t' + data)
    if data is not None:
        try:
            recvdata = json.loads(data)
        except:
            recvdata = {'reqimg': None, 'query': None, 'rtcount': None, 'offset': None}
    else:
        recvdata = []
    try:
        request = recvdata['request_code']
    except Exception:
        request = 'None'

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
        writer.write(bytes(response, 'utf-8'))
        await writer.drain()
        print('[SERVER] Success')

    elif request == 'list_objects':
        obj_list = []
        path_to_artobj = CWD+'artifact_objects'
        path_check = os.path.exists(path_to_artobj)
        if not path_check:
            print('[SERVER]no such dir')
        else:
            for filename in os.listdir(path_to_artobj+'/'):
                # obj_list.append(filename)
                with open(path_to_artobj+'/{}'.format(filename), 'r') as file_json:
                    obj_list.append(json.load(file_json))
                    file_json.close()
        response = {
            'answer_code': 'list_objects',
            'objects': obj_list
        }
        writer.write(bytes(json.dumps(response), 'utf-8'))
        await writer.drain()

    elif request == 'new_object':
        new_obj = Obj(name=recvdata['artifact_object']['id'], info_data=recvdata['artifact_object'])
        new_obj.save('artifact_objects')
        writer.write(b'success')
        await writer.drain()

    elif request == 'delete_object':
        try:
            os.remove('/home/furoki_sama/projects/machinevision-server/artifact_objects/{}.json'.format(recvdata['id']))
            writer.write(b'success')
            await writer.drain()
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
        # prep_data.making_xmls('train')
        # prep_data.making_xmls('test')
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
        writer.write(b'success')
        await writer.drain()
        # task = asyncio.ensure_future(prep_data.gen_train_run_bash_and_run())
    else:
        pass
    # print("Send: %r" % message)
    # writer.write(data)
    # await writer.drain()

    # print("Close the client socket")
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo,get_my_ipv4(), 1337, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
