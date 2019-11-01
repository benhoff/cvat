import os
import sys
import json
import argparse
import random
import logging

import numpy as np
import cv2

work_dir = os.path.dirname(os.path.abspath(__file__))
cvat_dir = os.path.join(work_dir, '..', '..')

sys.path.insert(0, cvat_dir)

from cvat.apps.tf_server_client.tf_handlers import do_inference


def _get_kwargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--py', required=True, help='Path to the python interpt file')
    parser.add_argument('--pb', required=True, help='Path to the inference file')
    parser.add_argument('--json', required=True, help='Path to the JSON mapping file')
    parser.add_argument('--restricted', dest='restricted', action='store_true')
    parser.add_argument('--unrestricted', dest='restricted', action='store_false')
    parser.add_argument('--image-files', nargs='*', help='Paths to image files you want to test')

    parser.add_argument('--show-images', action='store_true', help='Show the results of the annotation in a window')
    parser.add_argument('--show-image-delay', default=0, type=int, help='Displays the images for a set duration in milliseconds, default is until a key is pressed')
    parser.add_argument('--serialize', default=False, action='store_true', help='Try to serialize the result')
    
    return vars(parser.parse_args())

    py_file = kwargs['py']
    pb_file = kwargs['pb']
    mapping_file = kwargs['json']

    if not os.path.isfile(py_file):
        logging.critical('Py file not found! Check the path')
        return

    if not os.path.isfile(bin_file):
        logging.critical('Bin file is not found! Check path!')
        return

    if not os.path.isfile(xml_file):
        logging.critical('XML File not found! Check path!')
        return

    if not os.path.isfile(mapping_file):
        logging.critical('JSON file is not found! Check path!')
        return

    with open(mapping_file) as json_file:
        try:
            mapping = json.load(json_file)
        except json.decoder.JSONDecodeError:
            logging.critical('JSON file not able to be parsed! Check file')
            return

    try:
        mapping = mapping['label_map']
    except KeyError:
        logging.critical("JSON Mapping file must contain key `label_map`!")
        logging.critical("Exiting")
        return

    mapping = {int(k): v for k, v in mapping.items()}

    restricted = kwargs['restricted']
    image_files = kwargs.get('image_files')

    if image_files:
        image_data = [cv2.imread(f) for f in image_files]
    else:
        test_image = np.ones((1024, 1980, 3), np.uint8) * 255
        image_data = [test_image,]
    attribute_spec = {}

    results = do_inference(image_data,
                           mapping,
                           attribute_spec,
                           py_file,
                           restricted=restricted)

def main():
    kwargs = _get_kwargs()
