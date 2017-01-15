# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
import yaml
import pytz
import errno
from tzlocal import get_localzone

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from SafetyPy import SafetyPy as sp

LOG_LEVEL = logging.DEBUG
DEFAULT_CONFIG_FILENAME = 'config.yaml'
DEFAULT_SYNC_DELAY_IN_SECONDS = 900


def log_exception(logger, ex, message):
    """
    :param logger:
    :param ex:
    :param message:
    :return:
    """
    if logger is not None:
        logger.critical(message)
        logger.critical(ex)


def parse_api_token(logger, config_settings):
    """
    Parameters:   config_settings:  config object - contents of yaml file

    :return:       API token if token matches expected pattern
                  None if token is invalid or missing
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
        log_exception(logger, ex, 'Exception parsing API token from config.yaml')
        return None


def get_sync_delay(logger, config_settings):
    """
    Attempt to extract sync_delay_in_seconds from config settings

    :param logger:
    :param config_settings: config object - contents of yaml file
    :return: The  sync delay time in seconds or DEFAULT_SYNC_DELAY_IN_SECONDS if not provided or in error
    """
    try:
        sync_delay = config_settings['sync_delay_in_seconds']
        sync_delay_is_valid = re.match('^[0-9]+$', str(sync_delay))
        if sync_delay_is_valid and sync_delay >= 0:
            if sync_delay < DEFAULT_SYNC_DELAY_IN_SECONDS:
                '{0} seconds'.format(logger.info(
                    'Sync delay is less than the minimum recommended value of ' + str(DEFAULT_SYNC_DELAY_IN_SECONDS)))
            return sync_delay
        else:
            logger.info('Invalid sync_delay_in_seconds from the configuration file, defaulting to {0}'.format(str(
                DEFAULT_SYNC_DELAY_IN_SECONDS)))
            return DEFAULT_SYNC_DELAY_IN_SECONDS
    except Exception as ex:
        log_exception(logger, ex,
                      'Exception parsing sync_delay from the configuration file, defaulting to {0}'.format(str(
                          DEFAULT_SYNC_DELAY_IN_SECONDS)))
        return DEFAULT_SYNC_DELAY_IN_SECONDS


def get_export_profile_mapping(logger, config_settings):
    """
    Attempt to extract export profile IDs from config file
    If valid IDs are found, return a dict mapping templates to
      export profiles
    Otherwise return None

    :param logger:
    :param config_settings:
    :return: dict of valid export_profile_id mappings, or None
    """
    try:
        profile_mapping = {}
        export_profile_settings = config_settings['export_profiles']
        if export_profile_settings is not None:
            profile_lines = export_profile_settings.split(' ')
            for profile in profile_lines:
                template_id = profile[:profile.index(':')]
                if template_id not in profile_mapping.keys():
                    profile_mapping[template_id] = profile
        return profile_mapping
    except KeyError:
        logger.debug('No export profile key in the configuration file')
        return None
    except Exception as ex:
        log_exception(logger, ex, 'Exception getting export profiles from the configuration file')
        return None


def get_export_path(logger, config_settings):
    """
    Attempt to extract export path from config settings

    :param config_settings:
    :type logger: the logger
    :return: export path, None if path is invalid or missing
    """
    try:
        export_path = config_settings['export_options']['export_path']
        if export_path:
            return export_path
        else:
            return None
    except Exception as ex:
        log_exception(logger, ex, 'Exception getting export path from the configuration file')
        return None


def get_timezone(logger, config_settings):
    """
    Attempt to extract Olson timezone from config settings

    :return: extracted timezone, default to local timezone on exception
    """
    try:
        timezone = config_settings['export_options']['timezone']
        if timezone is None or timezone not in pytz.all_timezones:
            timezone = get_localzone()
            logger.info('No valid timezone found in config file, defaulting to local timezone')
        return str(timezone)
    except Exception as ex:
        log_exception(logger, ex, 'Exception parsing timezone from config file')
        timezone = get_localzone()
        return str(timezone)


def configure_logging(path_to_log_directory):
    """

    :param path_to_log_directory:
    :return:
    """
    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
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


def create_directory_if_not_exists(logger, path):
    """
    Creates 'path' if it does not exist

    If creation fails, the application will crash

    :param logger:
    :param path: The path to ensure it exists
    """
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            log_exception(logger, ex, 'An error happened trying to create ' + path)
            raise


def write_export_doc(logger, export_dir, export_doc, filename, extension):
    """
    Parameters:  export_doc:   String representation of document
                 filename:     Desired name of file on disk
    Returns:     None
    """
    file_path = os.path.join(export_dir, filename + '.' + extension)
    if os.path.isfile(file_path):
        logger.info('Overwriting existing report at ' + file_path)
    try:
        with open(file_path, 'w') as export_file:
            export_file.write(export_doc)
    except Exception as ex:
        log_exception(logger, ex, 'Exception while writing' + file_path + ' to file')


def set_last_successful(date_modified):
    with open('last_successful.txt', 'w') as last_modified_file:
        last_modified_file.write(date_modified)


def get_last_successful(logger):
    """
    :return: timestamp stored in last_successful.txt or timestamp
             old enough to effectively be the beginning of time
    """
    if os.path.isfile('last_successful.txt'):
        with open('last_successful.txt', 'r+') as last_run:
            last_successful = last_run.readlines()[0]
    else:
        beginning_of_time = '2000-01-01T00:00:00.000Z'
        last_successful = beginning_of_time
        with open('last_successful.txt', 'w') as last_run:
            last_run.write(last_successful)
        logger.info('Searching for audits since beginning of time')

    return last_successful


def parse_export_filename(header_items, filename_item_id):
    for item in header_items:
        if item['item_id'] == filename_item_id:
            if 'responses' in item.keys():
                if 'text' in item['responses'].keys() and item['responses']['text'].strip() != '':
                    return item['responses']['text']


def get_filename_item_id(logger, config_settings):
    try:
        filename_item_id = config_settings['export_options']['filename']
        if filename_item_id is not None:
            return filename_item_id
        else:
            return None
    except Exception as ex:
        log_exception(logger, ex, 'Exception retrieving setting "filename" from the configuration file')
        return None


def configure_logger():
    log_dir = os.path.join(os.getcwd(), 'log')
    create_directory_if_not_exists(None, log_dir)
    configure_logging(log_dir)
    logger = logging.getLogger('exporter_logger')
    return logger


def configure():
    logger = configure_logger()

    path_to_config_file, export_formats = parse_command_line_arguments(logger)

    # TODO: move these into a load_config_settings()
    config_settings = yaml.safe_load(open(path_to_config_file))
    api_token = parse_api_token(logger, config_settings)
    export_path = get_export_path(logger, config_settings)
    timezone = get_timezone(logger, config_settings)
    export_profiles = get_export_profile_mapping(logger, config_settings)
    filename_item_id = get_filename_item_id(logger, config_settings)
    sync_delay_in_seconds = get_sync_delay(logger, config_settings)

    sc_client = sp.SafetyCulture(api_token)

    if export_path is not None:
        create_directory_if_not_exists(logger, export_path)
    else:
        logger.info('Invalid export path was found in ' + path_to_config_file + ', defaulting to /exports')
        export_path = os.path.join(os.getcwd(), 'exports')
        create_directory_if_not_exists(logger, export_path)

    return logger, export_path, timezone, export_formats, export_profiles, filename_item_id, sc_client, \
        sync_delay_in_seconds


def show_usage_and_exit():
    print 'Usage:'
    print 'python exporter.py [--format pdf | docx | json] [--config <filename>]'
    sys.exit(1)


def parse_command_line_arguments(logger):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file to use, defaults to ' + DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--format', nargs='*', help='formats to download, valid options are pdf, json, docx')
    args = parser.parse_args()

    config_filename = DEFAULT_CONFIG_FILENAME
    if args.config is not None:
        if os.path.isfile(args.config):
            logger.debug(config_filename + ' passed as config argument')
            config_filename = args.config
        else:
            logger.error(config_filename + ' is not a valid config file')
            show_usage_and_exit()

    export_formats = ['pdf']
    if args.format is not None and len(args.format) > 0:
        valid_export_formats = ['json', 'docx', 'pdf']
        export_formats = []
        for option in args.format:
            if option not in valid_export_formats:
                print option + ' is not a valid export format.  Valid options are pdf, json, or docx'
                logger.info('invalid export format argument: ' + option)
            else:
                export_formats.append(option)

    return config_filename, export_formats


def loop(logger, sc_client, export_formats, export_profiles, filename_item_id, export_path, timezone,
         sync_delay_in_seconds):
    while True:
        last_successful = get_last_successful(logger)
        results = sc_client.discover_audits(modified_after=last_successful)

        if results is not None:
            logger.info(str(results['total']) + ' audits discovered')
            export_count = 1
            export_total = results['total']

            for audit in results['audits']:
                logger.info('Processing audit (' + str(export_count) + '/' + str(export_total) + ')')
                export_count += 1
                audit_id = audit['audit_id']
                logger.info('downloading ' + audit_id)
                audit_json = sc_client.get_audit(audit_id)
                template_id = audit_json['template_id']

                if template_id in export_profiles.keys():
                    export_profile_id = export_profiles[template_id]
                else:
                    export_profile_id = None

                if filename_item_id is not None:
                    export_filename = parse_export_filename(audit_json['header_items'], filename_item_id)
                    if export_filename is None:
                        export_filename = audit_id
                else:
                    export_filename = audit_id

                export_doc = None
                for export_format in export_formats:
                    if export_format in ['pdf', 'docx']:
                        export_doc = sc_client.get_export(audit_id, timezone, export_profile_id, export_format)
                    elif export_format == 'json':
                        export_doc = json.dumps(audit_json, indent=4)
                    write_export_doc(logger, export_path, export_doc, export_filename, export_format)
                logger.debug('setting last modified to ' + audit['modified_at'])
                set_last_successful(audit['modified_at'])
        logger.info('Next check with be in ' + sync_delay_in_seconds + ' seconds. Waiting...')
        time.sleep(sync_delay_in_seconds)


def main():
    try:
        logger, export_path, timezone, export_formats, export_profiles, filename_item_id, sc_client, \
            sync_delay_in_seconds = configure()

        loop(logger, sc_client, export_formats, export_profiles, filename_item_id, export_path, timezone,
             sync_delay_in_seconds)
    except KeyboardInterrupt:
        print "Interrupted by user, exiting."
        sys.exit(0)

if __name__ == '__main__':
    main()
