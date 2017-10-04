import datetime
import errno
import json
import logging
import os
import requests
import sys
from xlrd import open_workbook
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

input_filename = 'grs_1.xlsx'

api_token = 'my_api_token'

auth_header = {'Authorization': 'Bearer {0}'.format(api_token)}

def configure_logging(path_to_log_directory):
    """
    Configure logger

    :param path_to_log_directory:  path to directory to write log file in
    :return:
    """
    log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
    exporter_logger = logging.getLogger('exporter_logger')
    exporter_logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=os.path.join(path_to_log_directory, log_filename))
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    exporter_logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(LOG_LEVEL)
    sh.setFormatter(formatter)
    exporter_logger.addHandler(sh)


def log_critical_error(logger, ex, message):
    """
    Logs the exception at 'CRITICAL' log level

    :param logger:  the logger
    :param ex:      exception to log
    :param message: descriptive message to log details of where/why ex occurred
    """
    if logger is not None:
        logger.critical(message)
        logger.critical(ex)


def create_directory_if_not_exists(logger, path):
    """
    Creates 'path' if it does not exist

    If creation fails, an exception will be thrown

    :param logger:  the logger
    :param path:    the path to ensure it exists
    """
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            log_critical_error(logger, ex, 'An error happened trying to create ' + path)
            raise


def configure_logger():
    """
    Declare and validate existence of log directory; create and configure logger object

    :return:  instance of configured logger object
    """
    log_dir = os.path.join(os.getcwd(), 'log')
    create_directory_if_not_exists(None, log_dir)
    configure_logging(log_dir)
    logger = logging.getLogger('exporter_logger')
    return logger


def read_workbook(input_filename):
    wb_response_sets = {}

    wb = open_workbook(input_filename)
    for sheet in wb.sheets():
        name = sheet.name
        wb_response_sets[name] = []

        number_of_rows = sheet.nrows
        for row in range(1, number_of_rows):
            label_object = {}

            label_object['label'] = sheet.cell(row, 0).value
            label_object['short_label'] = sheet.cell(row, 1).value
            wb_response_sets[name].append(label_object)
    return wb_response_sets


def get_response_sets():
    response_sets = requests.get('https://api.safetyculture.io/response_sets', headers=auth_header)
    if response_sets.status_code == 200:
        return response_sets.json()
    else:
        print response_sets


def get_response_set(response_set_id):
    api_url = 'https://api.safetyculture.io/response_sets/{0}'.format(response_set_id)
    response_set = requests.get(api_url, headers=auth_header)
    if response_set.status_code == 200:
        return response_set.json()
    else:
        print response_set.status_code


def build_grs_payload(responses, name):
    payload = {}
    payload['name'] = name
    payload['responses'] = responses
    return payload

def is_identical(remote_response_set, local_response_set):
    if remote_response_set == local_response_set:
        return True
    else:
        return False


def strip_id(response):
    del response['id']


def get_rs_id_by_name(name, response_sets):
    for rs in response_sets:
        if rs['name'] == name:
            return rs


def handle_matching_rs(local_response_sets, remote_response_sets, response_set_name):
    local_response_set = local_response_sets[response_set_name]

    responseset_id = get_rs_id_by_name(response_set_name, remote_response_sets)['responseset_id']

    remote_response_set = get_response_set(responseset_id)

    remote_responses = remote_response_set['responses']
    map(strip_id, remote_responses)

    if is_identical(local_response_set, remote_responses):
        print 'Yep. They are identical'
    else:
        print local_response_set
        print '_-_' * 20
        print remote_responses


def create_remote_response_set(local_response_sets, response_set_name):
    payload = build_grs_payload(local_response_sets[response_set_name], response_set_name)
    status = requests.post('https://api.safetyculture.io/response_sets', data=json.dumps(payload), headers=auth_header)

logger = configure_logger()
sc_client = sp.SafetyCulture(api_token)

local_response_sets = read_workbook(input_filename)
remote_response_sets = get_response_sets()
remote_rs_names = [x['name'] for x in remote_response_sets]

for response_set_name in local_response_sets:
    if response_set_name in remote_rs_names:
        handle_matching_rs(local_response_sets, remote_response_sets, response_set_name)
    else:
        print 'creating new remote response set'
        create_remote_response_set(local_response_sets, response_set_name)




