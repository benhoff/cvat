import os
import argparse
import logging


def _get_kwargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--py', help='Path to the python interpt file')
    parser.add_argument('--xml', help='Path to the xml file')
    parser.add_argument('--bin', help='Path to the bin file')
    parser.add_argument('--json', help='Path to the JSON mapping file')

    parser.add_argument('--model-name', help='English name given to a model in the Model Manager')
    parser.add_argument('--job-id', type=int, help='integer job id used to test model. Can be found on the CVAT page')

    parser.add_argument('--restricted', dest='restricted', action='store_true')
    parser.add_argument('--unrestricted', dest='restricted', action='store_false')
    parser.add_argument('--image-files', nargs='*', help='Paths to image files you want to test')

    parser.add_argument('--show-images', action='store_true', help='Show the results of the annotation in a window')
    parser.add_argument('--show-image-delay', default=0, type=int, help='Displays the images for a set duration in milliseconds, default is until a key is pressed')
    parser.add_argument('--serialize', default=False, action='store_true', help='Try to serialize the result')
    
    return vars(parser.parse_args())


def _valid_docker_args(model_name, job_id):
    pass


def _valid_local_args(py_file, mapping_file, bin_file, xml_file) -> bool:
    if py_file is None or not os.path.isfile(py_file):
        logging.critical('Py file not found! Check the path')
        return False

    if bin_file is None or not os.path.isfile(bin_file):
        logging.critical('Bin file is not found! Check path!')
        return False

    if xml_file is None or not os.path.isfile(xml_file):
        logging.critical('XML File not found! Check path!')
        return False

    if mapping_file is None or not os.path.isfile(mapping_file):
        logging.critical('JSON file is not found! Check path!')
        return False


    return True


def main():
    kwargs = _get_kwargs()

    py_file = kwargs.get('py')
    mapping_file = kwargs.get('json')
    bin_file = kwargs.get('bin')
    xml_file = kwargs.get('xml')

    model_name = kwargs.get('model_name')
    job_id = kwargs.get('job_id')

    # NOTE: This might move
    restricted = kwargs['restricted']

    is_docker_test = mdoel_name or job_id or job_id == 0
    is_local_test = py_file or mapping_file or bin_file or xml_file

    if is_docker_test:
        if not _valid_docker_args(model_name, job_id):
            return 1
        from _run_docker_test import run_docker_test
        run_docker_test(model_name, job_id, kwargs)

    if is_local_test:
        if not _valid_local_args(py_file, mapping_file, bin_file, xml_file):
            return 2

        from _run_local_test import run_local_test
        run_local_test(py_file, mapping_file, bin_file, xml_file, kwargs)


if __name__ == '__main__':
    main()
