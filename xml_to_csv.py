import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from lxml import etree


def xml_to_csv(path):
    xml_list = []
    for xml_file in os.listdir(path+'/'):
        # print(xml_file)
        parser = etree.XMLParser(recover=True)
        tree = ET.parse(path+'/'+xml_file,parser=parser)
        root = tree.getroot()
        if root is not None:
            for member in root.findall('object'):
                value = (root.find('filename').text,
                         int(root.find('size')[0].text),
                         int(root.find('size')[1].text),
                         member[0].text,
                         int(member[4][0].text),
                         int(member[4][1].text),
                         int(member[4][2].text),
                         int(member[4][3].text)
                         )
                xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def do_this(objecn_name):
    for directory in ['train','eval']:
        image_path = os.getcwd() + '/prep_data/{}/models/model/{}'.format(objecn_name,directory)
        # print(image_path)
        csv_output_path = os.getcwd() + '/prep_data/{}'.format(objecn_name)
        xml_df = xml_to_csv(image_path)
        xml_df.to_csv('{}/{}_labels.csv'.format(csv_output_path,directory), index=None)
        # print('{}/{}_labels.csv'.format(csv_output_path,directory))
        # print('Successfully converted xml to csv.')

