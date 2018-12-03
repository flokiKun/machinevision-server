import os
import pathlib
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import numpy
import cv2
import urllib
import json


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


    def img_from_link(self,mode):
        if mode == 'separate':
            with open(self.rootdir + '/logs/{}'.format(self.object_name+'.json')) as f:
                json_f = json.load(f)
                for i in range(0, len(json_f)):
                    print(json_f[i]['image_link'])


    def gen_xml_for_img(self, img_info, folder):
        img = img_info[0]
        img_name = img_info[1]
        class_count = img_info[2]
        class_name = img_info[3]
        img_whc = img.shape
        dictionary = {
            'folder': str(folder),
            'filename': img_name,
            'path': self.rootdir + '/prep_data/{}/models/model/{}/{}'.format(self.object_name, folder, img_name),
            'source': {'database': 'Unknown'},
            'size': {'width': img_whc[0], 'height': img_whc[1], 'depth': 3},
            'segmented': 0
        }

        for i in range(0,class_count):
            dictionary.update({
                'object': {'name': img_name, 'pose': 'Unspecified', 'truncated': 1, 'difficult': 0, 'bndbox':
                    {'xmin': 0, 'ymin': 0, 'xmax': img_whc[0], 'ymax': img_whc[1]
                     }}
                })
        with open(self.rootdir + '/prep_data/{}/models/model/{}/{}'.format(self.object_name, folder, class_name+'.xml'),'w+') as out_file:
            out_file.write(parseString(dicttoxml(dictionary, custom_root='annotation', attr_type=False)).toprettyxml())
            out_file.close()

    def making_xmls(self,dir):
        path = self.rootdir + '/prep_data/{}/models/model/{}/'.format(self.object_name, dir)
        for img_file in os.listdir(path):
            try:
                img = cv2.imread(path+img_file, 0)
                self.gen_xml_for_img(img_info=[img,self.object_name,1,self.object_name],folder='train')
            except AttributeError:
                pass

            # cv2.imshow('img',img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


# info = ([],'anime',1,'anime-chan')
dirs = Prep_Class('knife')
dirs.init_dirs()
# dirs.gen_xml_for_img(info,'eval')
# dirs.making_xmls('train')
dirs.img_from_link('separate')