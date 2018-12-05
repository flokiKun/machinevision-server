import os
import pathlib
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import numpy
import cv2
import urllib3
import json
import xml_to_csv as xtc

# File , that preper dir to ma

class Prep_Class():
    def __init__(self, object):
        self.rootdir = os.getcwd()  # String
        self.object_name = str(object)
        self.isnew = False
        if not pathlib.Path('prep_data').exists():
            os.mkdir('prep_data')
        if not pathlib.Path('prep_data/{}'.format(self.object_name)).exists():
            self.isnew = True

    def chech_dirs(self):
        print('Check')

    def init_dirs(self):
        if self.isnew:
            os.makedirs(self.rootdir + '/prep_data/{}'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/data'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model/train'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model/eval'.format(self.object_name))

    def img_from_link(self, mode):
        http = urllib3.PoolManager()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if mode == 'separate':
            with open(self.rootdir + '/logs/{}'.format(self.object_name + '.json')) as f:
                json_f = json.load(f)
            f.close()
            print('[Parser] Starting download:{} count:{}'.format(self.object_name, len(json_f)))
            for i in range(0, len(json_f)):
                r = http.request('GET', json_f[i]['image_link'], preload_content=False)
                path = self.rootdir + '/prep_data/{}/models/model/train/'.format(self.object_name)
                with open(path + 'IMG{}.png'.format(i), 'wb') as out:
                    while True:
                        data = r.read()  # chuck
                        if not data:
                            break
                        out.write(data)
                out.close()
                r.release_conn()
            print('[Parser] Download done!')

    def gen_xml_for_img(self, img_info, folder):
        img = img_info[0]
        img_name = img_info[1]
        class_count = img_info[2]
        class_name = img_info[3]
        img_whc = img.shape
        dictionary = {
            'folder': str(folder),
            'filename': img_name[:4],
            'path': self.rootdir + '/prep_data/{}/models/model/{}/{}'.format(self.object_name, folder, img_name),
            'source': {'database': 'Unknown'},
            'size': {'width': img_whc[0], 'height': img_whc[1], 'depth': 3},
            'segmented': 0
        }

        for i in range(0, class_count):
            dictionary.update({
                'object': {'name': self.object_name, 'pose': 'Unspecified', 'truncated': 1, 'difficult': 0, 'bndbox':
                    {'xmin': 0, 'ymin': 0, 'xmax': img_whc[0], 'ymax': img_whc[1]
                     }}
            })
        with open(self.rootdir + '/prep_data/{}/models/model/{}/{}'.format(self.object_name, folder,
                                                                           img_name[:len(img_name) - 4] + '.xml'),'w+') as out_file:
            out_file.write(parseString(dicttoxml(dictionary, custom_root='annotation', attr_type=False)).toprettyxml())
            out_file.close()

    def making_xmls(self, dir):
        path = self.rootdir + '/prep_data/{}/models/model/{}/'.format(self.object_name, dir)
        # print(os.listdir(path))
        for img_file in os.listdir(path):
            img_path = path + img_file
            img = cv2.imread(img_path, 0)
            if img is not None:
                # cv2.imshow('img', img)
                # self.gen_xml_for_img([img, self.object_name, 1, self.object_name,img_file],dir)
                self.gen_xml_for_img([img, img_file, 1, self.object_name],dir)

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


# info = ([],'anime',1,'anime-chan')
dirs = Prep_Class('knife')
# dirs.init_dirs()
# dirs.gen_xml_for_img(info,'eval')
# dirs.making_xmls('train')
#dirs.img_from_link('separate')
dirs.making_xmls('train')
dirs.making_xmls('eval')
xtc.do_this('knife')

