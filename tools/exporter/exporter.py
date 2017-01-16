# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import argparse
import errno
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
import yaml
import pytz
from tzlocal import get_localzone

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from SafetyPy import SafetyPy as sp

LOG_LEVEL = logging.DEBUG
DEFAULT_CONFIG_FILENAME = 'config.yaml'
DEFAULT_SYNC_DELAY_IN_SECONDS = 900


def log_exception(logger, ex, message):
    """
    Write exception details and message to log file

    :param logger:  the logger
    :param ex:      exception to log
    :param message: descriptive message to log details of where/why ex occurred
    :return:
    """
    if logger is not None:
        logger.critical(message)
        logger.critical(ex)


def parse_api_token(logger, config_settings):
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
        log_exception(logger, ex, 'Exception parsing API token from config.yaml')
        return None


def get_sync_delay(logger, config_settings):
    """
    Attempt to parse delay between sync loops from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 extracted sync delay if valid, else DEFAULT_SYNC_DELAY_IN_SECONDS
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
    Attempt to parse export_profile settings from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 export profile mapping if valid, else None
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

    :param config_settings:  config settings loaded from config file
    :param logger:           the logger
    :return:                 export path, None if path is invalid or missing
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
    Attempt to parse timezone from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 timezone from config if valid, else local timezone for this machine
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
    Configure logger

    :param path_to_log_directory:  path to folder to write log file in
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

    :param logger:  the logger
    :param path:    the path to ensure it exists
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
    Write exported document to disk at specified location with specified file name

    :param logger:      the logger
    :param export_dir:  path to folder for exports
    :param export_doc:  export document to write
    :param filename:    filename to give exported document
    :param extension:   extension to give exported document
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
    """
    Set last successful value in last_successful.txt with the most recent modified_at value from audit json

    :param date_modified:   modified_at value from most recently downloaded audit json
    :return:
    """
    with open('last_successful.txt', 'w') as last_modified_file:
        last_modified_file.write(date_modified)


def get_last_successful(logger):
    """
    Check for last_successful.txt to get last_successful time value, else default to 'beginning of time'

    :param logger:  the logger
    :return:        last_successful value extracted from last_successful.txt, 2000-01-01
                    (the beginning of time) if no valid time is parsed
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
    """
    Get 'response' value of specified header item to use for export file name

    :param header_items:      header_items array from audit json
    :param filename_item_id:  item_id from config settings
    :return:                  'response' value of specified item from audit json
    """
    for item in header_items:
        if item['item_id'] == filename_item_id:
            if 'responses' in item.keys():
                if 'text' in item['responses'].keys() and item['responses']['text'].strip() != '':
                    return item['responses']['text']


def get_filename_item_id(logger, config_settings):
    """
    Attempt to parse item_id for file naming from config settings

    :param logger:          the logger
    :param config_settings: config settings loaded from config file
    :return:                item_id extracted from config_settings if valid, else None
    """
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
    """
    Declare and validate existence of log directory; create and configure logger object

    :return:  instance of configured logger object
    """
    log_dir = os.path.join(os.getcwd(), 'log')
    create_directory_if_not_exists(None, log_dir)
    configure_logging(log_dir)
    logger = logging.getLogger('exporter_logger')
    return logger

def load_config_settings(logger, path_to_config_file):
    """
    Load config settings from config file

    :param logger:              the logger
    :param path_to_config_file: location of config file
    :return:                    api_token, export_path, timezone, export_profiles,
                                filename_item_id, sync_delay_in_seconds values
                                loaded from config file
    """
    config_settings = yaml.safe_load(open(path_to_config_file))
    api_token = parse_api_token(logger, config_settings)
    export_path = get_export_path(logger, config_settings)
    timezone = get_timezone(logger, config_settings)
    export_profiles = get_export_profile_mapping(logger, config_settings)
    filename_item_id = get_filename_item_id(logger, config_settings)
    sync_delay_in_seconds = get_sync_delay(logger, config_settings)

    return api_token, export_path, timezone, export_profiles, filename_item_id, sync_delay_in_seconds


def configure():
    """
    Instantiate and configure logger, load config settings from file, instantiate SafetyCulture SDK
    
    :return:   logger object, instance of SafetyCulture SDK object, config settings
    """
    logger = configure_logger()
    path_to_config_file, export_formats = parse_command_line_arguments(logger)

    api_token, export_path, timezone, export_profiles, filename_item_id, sync_delay_in_seconds =  \
        load_config_settings(logger, path_to_config_file)

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
    """
    In the case of invalid command line arguments being passed,
    provide example of proper argument usage and exit
    """
    print 'Usage:'
    print 'python exporter.py [--format pdf | docx | json] [--config <filename>]'
    sys.exit(1)


def parse_command_line_arguments(logger):
    """
    Parse command line arguments received, if any
    Print example if invalid arguments are passed

    :param logger:  the logger
    :return:        config_filename passed as argument if any, else DEFAULT_CONFIG_FILENAME
                    export_formats passed as argument if any, else 'pdf'
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file to use, defaults to ' + DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--format', nargs='*', help='formats to download, valid options are pdf, json, docx')
    args = parser.parse_args()

    config_filename = DEFAULT_CONFIG_FILENAME
    if args.config is not None:
        if os.path.isfile(args.config):
            config_filename = args.config
            logger.debug(config_filename + ' passed as config argument')
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
    """
    Loop sync until interrupted by user

    :param logger:                 the logger
    :param sc_client:              instance of SafetyCulture SDK object
    :param export_formats:         export formats to download
    :param export_profiles:        export profiles to apply to exported documents
    :param filename_item_id:       header item item_id for file naming
    :param export_path:            path to folder in which to write exported documents
    :param timezone:               timezone to apply to exported documents
    :param sync_delay_in_seconds:  number of seconds between sync loops
    """
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
        logger.info('Next check will be in ' + sync_delay_in_seconds + ' seconds. Waiting...')
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
