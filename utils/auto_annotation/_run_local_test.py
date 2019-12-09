import os
import json
import random
import logging
import cv2

work_dir = os.path.dirname(os.path.abspath(__file__))
cvat_dir = os.path.join(work_dir, '..', '..')

sys.path.insert(0, cvat_dir)

from cvat.apps.auto_annotation.inference import run_inference_engine_annotation
import numpy as np


def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)


def pairwise(iterable):
    result = []
    for i in range(0, len(iterable) - 1, 2):
        result.append((iterable[i], iterable[i+1]))
    return np.array(result, dtype=np.int32)


def run_local_test(py_file, mapping_file, bin_file, xml_file, kwargs):

    with open(mapping_file) as json_file:
        try:
            mapping = json.load(json_file)
        except json.decoder.JSONDecodeError:
            logging.critical('JSON file not able to be parsed! Check file')
            return False

    try:
        mapping = mapping['label_map']
    except KeyError:
        logging.critical("JSON Mapping file must contain key `label_map`!")
        logging.critical("Exiting")
        return False

    mapping = {int(k): v for k, v in mapping.items()}
    image_files = kwargs.get('image_files')


    if image_files:
        image_data = [cv2.imread(f) for f in image_files]
    else:
        test_image = np.ones((1024, 1980, 3), np.uint8) * 255
        image_data = [test_image,]
    attribute_spec = {}

    results = run_inference_engine_annotation(image_data,
                                              xml_file,
                                              bin_file,
                                              mapping,
                                              attribute_spec,
                                              py_file,
                                              restricted=restricted)

    if kwargs['serialize']:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'cvat.settings.production'
        import django
        django.setup()

        from cvat.apps.engine.serializers import LabeledDataSerializer

        # NOTE: We're actually using `run_inference_engine_annotation`
        # incorrectly here. The `mapping` dict is supposed to be a mapping
        # of integers -> integers and represents the transition from model
        # integers to the labels in the database. We're using a mapping of
        # integers -> strings. For testing purposes, this shortcut is fine.
        # We just want to make sure everything works. Until, that is....
        # we want to test using the label serializer. Then we have to transition
        # back to integers, otherwise the serializer complains about have a string
        # where an integer is expected. We'll just brute force that.

        for shape in results['shapes']:
            # Change the english label to an integer for serialization validation
            shape['label_id'] = 1

        serializer = LabeledDataSerializer(data=results)

        if not serializer.is_valid():
            logging.critical('Data unable to be serialized correctly!')
            serializer.is_valid(raise_exception=True)

    logging.warning('Program didn\'t have any errors.')
    show_images = kwargs.get('show_images', False)

    if show_images:
        if image_files is None:
            logging.critical("Warning, no images provided!")
            logging.critical('Exiting without presenting results')
            return

        if not results['shapes']:
            logging.warning(str(results))
            logging.critical("No objects detected!")
            return

        show_image_delay = kwargs['show_image_delay']
        for index, data in enumerate(image_data):
            for detection in results['shapes']:
                if not detection['frame'] == index:
                    continue
                points = detection['points']
                # Cv2 doesn't like floats for drawing
                points = [int(p) for p in points]
                color = random_color()
                if detection['type'] == 'rectangle':
                    cv2.rectangle(data, (points[0], points[1]), (points[2], points[3]), color, 3)
                elif detection['type'] in ('polygon', 'polyline'):
                    # polylines is picky about datatypes
                    points = pairwise(points)
                    cv2.polylines(data, [points], 1, color)
            cv2.imshow(str(index), data)
            cv2.waitKey(show_image_delay)
            cv2.destroyWindow(str(index))
