import os
import pathlib
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import numpy
import cv2
import urllib3
import json
import xml_to_csv as xtc
import urllib.request as ur
import urllib.error
import time
import ssl

# File , that preper dir to ma

class Prep_Class():
    def __init__(self, object, id):
        self.rootdir = os.getcwd()  # String
        self.object_name = str(object)
        self.id = id
        self.isnew = False
        if not pathlib.Path('prep_data').exists():
            os.mkdir('prep_data')

    def chech_dirs(self):
        print('Check')

    def init_dirs(self):
        if not pathlib.Path('prep_data/{}'.format(self.object_name)).exists():
            self.isnew = True

        if self.isnew:
            os.makedirs(self.rootdir + '/prep_data/{}'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/data'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model/train'.format(self.object_name))
            os.makedirs(self.rootdir + '/prep_data/{}/models/model/test'.format(self.object_name))

    def img_from_link(self,method):
        count_links = 0
        http = urllib3.PoolManager()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        with open(self.rootdir + '/artifact_objects/{}'.format(self.id + '.json')) as f:
            json_f = json.load(f)
        f.close()
        json_links = json_f["queries"]
        for k in range(0,len(json_links)):
            count_links += len(json_links[k]['whitelist'])
        print('[Parser] Starting download:{} count:{}'.format(self.object_name,count_links))
        if method == 'oldi':
            path = self.rootdir + '/prep_data/{}/models/model/train/'.format(self.object_name)
            for i in range(0, len(json_links)):
                r = http.request('GET', json_links[i], preload_content=False)
                with open(path + 'IMG{}.jpg'.format(i), 'wb') as out:
                    while True:
                        data = r.read()  # chuck
                        if not data:
                            break
                        out.write(data)
                out.close()
                r.release_conn()
        elif method == 'new':
            path = self.rootdir + '/prep_data/{}/models/model/train/'.format(self.object_name)
            # print(json_links)
            for i in range(0,len(json_links)):
                img_num = 0
                for link in json_links[i]['whitelist']:
                    try:
                        start_time = time.time()
                        img_num += 1
                        ur.urlretrieve(link,path+'{}_{}_{}.jpg'.format('IMG',json_links[i]['title'],str(img_num)))
                        all_time = round((start_time - time.time()) * -10, 2)
                        print('[Img Parser] Download {}_{}_{} in {}'.format('IMG',json_links[i]['title'],str(img_num),all_time))
                    # urllib.error.HTTPError or ssl.SSLError or urllib.error.ContentTooShortError
                    except Exception as e:
                        print('[Img Parser] {} , skip..'.format(str(e)))
                        pass
        print('[Parser] Download done!')

    def separate_img(self):
        path = self.rootdir + '/prep_data/{}/models/model/'.format(self.object_name)
        eeval = True
        for i in os.listdir(path+'train/'):
            if eeval:
                os.rename(path+'train/{}'.format(i), path+'test/{}'.format(i))
                eeval = False
            else:
                eeval = True

    def gen_xml_for_img(self, img_info, folder):
        img = img_info[0]
        img_name = img_info[1]
        class_count = img_info[2]
        class_name = img_info[3]
        img_whc = img.shape
        dictionary = {
            'folder': str(folder),
            'filename': img_name, # [:4]
            'path': self.rootdir + '/prep_data/{}/models/model/{}/{}'.format(self.object_name, folder, img_name),
            'source': {'database': 'Unknown'},
            'size': {'width': img_whc[1], 'height': img_whc[0], 'depth': 3},
            'segmented': 0
        }

        for i in range(0, class_count):
            dictionary.update({
                'object': {'name': self.object_name, 'pose': 'Unspecified', 'truncated': 1, 'difficult': 0, 'bndbox':
                    {'xmin': 0, 'ymin': 0, 'xmax': img_whc[1], 'ymax': img_whc[0]
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

    def gen_labelmap_file(self):
        with open('prep_data/{}/data/labelmap.pbtxt'.format(self.object_name),'w') as file:
            s = """
                item {
                    id: 1
                    name: '%s'
                    }
                """ % self.object_name
            file.write(s)
            file.close()

    def gen_train_run_bash_and_run(self):
        # with open('run_train.sh', 'r') as bash:
        s = """\
        #! /bin/bash
        cd ~/tensorflow/models/research
        export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
        cd ~/projects/machinevision-server
        python3 /home/furoki_sama/tensorflow/models/research/object_detection/model_main.py --pipline_config_path="prep_data/{object_name}/data/pipeline.config" --model_dir="prep_data/{object_name}/models/model/{object_name}_model" --num_train_steps=100000 --sample_1_of_n_eval_examples=1 --alsologtostderr
        """
        s.format(object_name=self.object_name)
        # bash.close()
        os.system(s)

    def gen_class(self):
        s = """def class_text_to_int(row_label):
                if row_label == '%s':
                    return 1
                else:
                    None
            """ % self.object_name
        with open('class_text_to_int.py','r+') as f:
            f.truncate(0)
            f.write(s)
            f.close()

    def gen_pipeline(self):
        def fill_word(word, count):
            res = []
            for i in range(0, count):
                res.append(str(word))
            return tuple(res)

        with open('pre_trained_model/ssd_mobilenet_v1_0.75_depth_300x300_coco14_sync_2018_07_03/pipeline.config','r') as sample:
            labelmap = 'prep_data/{}/data/labelmap.pbtxt'.format(self.object_name)
            train_record = 'prep_data/{}/data/train.record'.format(self.object_name)
            test_record = 'prep_data/{}/data/test.record'.format(self.object_name)
            values = (labelmap,train_record,labelmap,test_record)
            new_sample = str(sample.read()) % values
            sample.close()

        with open('prep_data/{}/data/pipleline.config'.format(self.object_name), 'w') as new_file:
            new_file.write(new_sample)
            new_file.close()

#  python3 generate_tfrecords.py --csv_input=~/projects/machinevision-server/prep_data/knife/train_labels.csv --image_dir=prep_data/knife/models/model/train --output_path=prep_data/knife/train.record
#
# info = ([],'anime',1,'anime-chan')
#dirs = Prep_Class('chair')
# dirs.init_dirs()
# dirs.gen_xml_for_img(info,'test')
# dirs.making_xmls('train')
#dirs.img_from_link('new')
#dirs.separate_img()
#dirs.making_xmls('train')
#dirs.making_xmls('test')
#xtc.do_this('chair')

if __name__ == '__main__':
    object = Prep_Class('jojo','F65XF6X5B7L0YPVR')
    # object.img_from_link('new')
    # object.separate_img()