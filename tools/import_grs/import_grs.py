import argparse
import datetime
import errno
import logging
import os
import re
import sys
import yaml
from xlrd import open_workbook
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

DEFAULT_CONFIG_FILENAME = 'config.yaml'


def configure_logging(path_to_log_directory):
    """
    Configure logger

    :param path_to_log_directory:  path to directory to write log file in
    :return:
    """
    log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
    importer_logger = logging.getLogger('importer_logger')
    importer_logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=os.path.join(path_to_log_directory, log_filename))
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    importer_logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(LOG_LEVEL)
    sh.setFormatter(formatter)
    importer_logger.addHandler(sh)


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
    logger = logging.getLogger('importer_logger')
    return logger


def load_setting_api_access_token(logger, config_settings):
    """
    Attempt to parse API token from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 API token if valid, else None
    """
    try:
        api_token = config_settings['API']['token']
        token_is_valid = re.match('^[a-f0-9]{64}$', api_token)
        if token_is_valid:
            logger.debug('API token matched expected pattern')
            return api_token
        else:
            logger.error('API token failed to match expected pattern')
            return None
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception parsing API token from config.yaml')
        return None


def load_setting_input_filename(logger, config_settings):
    """
    Attempt to parse input filename from config settings
    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 input filename from config file if valid, else None
    """

    try:
        filename = config_settings['input_filename']
        filename_is_valid = re.match('.+xls|.+xlsx', filename)
        if filename_is_valid:
            logger.debug('Filename matched expected pattern')
            return filename
        else:
            logger.error('Filename failed to match expected pattern, acceptable formats are xls and xlsx')
            return None
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception parsing input filename from config.yaml')


def load_config_settings(logger, path_to_config_file):
    """
    Load config settings from config file

    :param logger:              the logger
    :param path_to_config_file: location of config file
    :return:                    settings dictionary containing values for:
                                api_token, input_filename
    """
    config_settings = yaml.safe_load(open(path_to_config_file))
    settings = {
        'api_token': load_setting_api_access_token(logger, config_settings),
        'input_filename': load_setting_input_filename(logger, config_settings),
    }

    return settings


def read_workbook(logger, input_filename):
    """
    Read the contents of input_filename and return
    :param logger:         The logger
    :param input_filename: Filepath of the spreadsheet to read
    :return:  Dict of response sets
    """
    wb_response_sets = {}
    if os.path.isfile(input_filename):
        wb = open_workbook(input_filename)
        for sheet in wb.sheets():
            name = sheet.name
            wb_response_sets[name] = []

            number_of_rows = sheet.nrows
            for row in range(1, number_of_rows):
                if sheet.cell(row, 0).value != "":
                    label_object = {
                        'label': sheet.cell(row, 0).value,
                    }
                    wb_response_sets[name].append(label_object)
        return wb_response_sets
    else:
        logger.error('{0} does not appear to be a valid file'.format(input_filename))


def get_rs_id_by_name(name, response_sets):
    """
    Return the response_set that matches the passed name
    :param name:          Name of response_set to return
    :param response_sets: List of response_sets to check
    :return:              Response_set with the passed name
    """

    for rs in response_sets:
        if rs['name'] == name:
            return rs


def handle_matching_rs(logger, local_response_sets, remote_response_sets, response_set_name, sc_client):
    """
    :param logger:               The logger
    :param local_response_sets:  Response_set data pulled from spreadsheet
    :param remote_response_sets: Response_set data pulled from API
    :param response_set_name:    Name of the response_set
    :param sc_client:            Instance of SDK client
    :return:                     None
    """
    local_response_set = local_response_sets[response_set_name]
    responseset_id = get_rs_id_by_name(response_set_name, remote_response_sets)['responseset_id']

    remote_response_set = sc_client.get_response_set(responseset_id)
    remote_responses = remote_response_set['responses']

    local_labels = [str(x['label']) for x in local_response_set]
    remote_labels = [str(x['label']) for x in remote_response_set['responses']]

    local_diff = [x for x in local_labels if x not in remote_labels]
    remote_diff = [x for x in remote_labels if x not in local_labels]

    if len(local_diff) > 0:
        logger.debug('there is a local response to create in {0}'.format(responseset_id))
        for label in local_diff:
            payload = {
                'label': label
            }
            sc_client.create_response(responseset_id, payload)

    if len(remote_diff) > 0:
        logger.debug('there is a remote response to delete in {0}'.format(responseset_id))
        remote_diff_ids = [x['id'] for x in remote_responses if x['label'] in remote_diff]
        for response_id in remote_diff_ids:
            sc_client.delete_response(responseset_id, response_id)

    if len(local_diff) == 0 and len(remote_diff) == 0:
        logger.debug('{0} on server matches local responseset - no changes to make'.format(responseset_id))


def main():
    """
    Load local response_set data, get remote response_set data, compare and reconcile
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-t', '--token', required=True)
    args = parser.parse_args()
    file_path = args.file
    api_token = args.token

    logger = configure_logger()
    sc_client = sp.SafetyCulture(api_token)

    if file_path is not None:
        local_response_sets = read_workbook(logger, file_path)
        if local_response_sets is not None:
            remote_response_sets = sc_client.get_response_sets()
            remote_rs_names = [x['name'] for x in remote_response_sets]

            for response_set_name in local_response_sets:
                if response_set_name in remote_rs_names:
                    handle_matching_rs(logger, local_response_sets, remote_response_sets, response_set_name, sc_client)
                else:
                    name = response_set_name
                    responses = local_response_sets[response_set_name]
                    sc_client.create_response_set(name, responses)


if __name__ == '__main__':
    main()