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
from datetime import timedelta
import dateutil.parser
import yaml
import pytz
import shutil
# noinspection PyUnresolvedReferences
from builtins import input
from tzlocal import get_localzone
import unicodecsv as csv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp
from tools import csvExporter

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

# Stores the API access token and other configuration settings
DEFAULT_CONFIG_FILENAME = 'config.yaml'

# Wait 15 minutes by default between sync attempts
DEFAULT_SYNC_DELAY_IN_SECONDS = 900

# Only download audits older than 10 minutes
DEFAULT_MEDIA_SYNC_OFFSET_IN_SECONDS = 600

# The file that stores the "date modified" of the last successfully synced audit
SYNC_MARKER_FILENAME = 'last_successful.txt'

# The file that stores the ISO date/time string of the last successful actions export
ACTIONS_SYNC_MARKER_FILENAME = 'last_successful_actions_export.txt'

# the file that stores all exported actions in CSV format
ACTIONS_EXPORT_FILENAME = 'iauditor_actions.csv'

# Whether to export inactive items to CSV
DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV = True

# When exporting actions to CSV, if property is None, print this value to CSV
EMPTY_RESPONSE = ''

# Not all Audits will actually contain an Audit Title item. For examples, when Audit Title rules are set, the Audit Title item is not going to be included by default.
# When this item ID is specified in the custom export filename configuration, the audit_data.name property will be used to populate the data as it covers all cases.
AUDIT_TITLE_ITEM_ID = 'f3245d40-ea77-11e1-aff1-0800200c9a66'

# Properties kept in settings dictionary which takes its values from config.YAML
API_TOKEN = 'api_token'
EXPORT_PATH = 'export_path'
PREFERENCES = 'preferences'
FILENAME_ITEM_ID = 'filename_item_id'
SYNC_DELAY_IN_SECONDS = 'sync_delay_in_seconds'
EXPORT_INACTIVE_ITEMS_TO_CSV = 'export_inactive_items_to_csv'
MEDIA_SYNC_OFFSET_IN_SECONDS = 'media_sync_offset_in_seconds'
EXPORT_FORMATS = 'export_formats'

# Used to create a default config file for new users
DEFAULT_CONFIG_FILE_YAML = [
    'API:',
    '\n    token: ',
    '\nexport_options:',    
    '\n    export_path:',
    '\n    filename:',
    '\n    csv_options:',
    '\n        export_inactive_items: false',
    '\n    preferences:',
    '\n    sync_delay_in_seconds:',
    '\n    media_sync_offset_in_seconds:',
]


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


def load_export_inactive_items_to_csv(logger, config_settings):
    """
    Attempt to parse export_inactive_items from config settings. Value of true or false is expected.
    True means the CSV exporter will include inactive items. False means the CSV exporter will exclude inactive items.
    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 value of export_inactive_items_to_csv if valid, else DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV
    """
    try:
        export_inactive_items_to_csv = config_settings['export_options']['csv_options']['export_inactive_items']
        if not isinstance(export_inactive_items_to_csv, bool):
            logger.info('Invalid export_inactive_items value from configuration file, defaulting to true')
            export_inactive_items_to_csv = DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV
        return export_inactive_items_to_csv
    except Exception as ex:
        log_critical_error(logger, ex,
                           'Exception parsing export_inactive_items from the configuration file, defaulting to {0}'.
                           format(str(DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV)))
        return DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV


def load_setting_sync_delay(logger, config_settings):
    """
    Attempt to parse delay between sync loops from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 extracted sync delay if valid, else DEFAULT_SYNC_DELAY_IN_SECONDS
    """
    try:
        sync_delay = config_settings['export_options']['sync_delay_in_seconds']
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
        log_critical_error(logger, ex,
                           'Exception parsing sync_delay from the configuration file, defaulting to {0}'.format(str(
                               DEFAULT_SYNC_DELAY_IN_SECONDS)))
        return DEFAULT_SYNC_DELAY_IN_SECONDS


def load_setting_preference_mapping(logger, config_settings):
    """
    Attempt to parse preference settings from config settings

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 export preference mapping if valid, else None
    """
    try:
        preference_mapping = {}
        preference_settings = config_settings['export_options']['preferences']
        if preference_settings is not None:
            preference_lines = preference_settings.split(' ')
            for preference in preference_lines:
                template_id = preference[:preference.index(':')]
                if template_id not in preference_mapping.keys():
                    preference_mapping[template_id] = preference
        return preference_mapping
    except KeyError:
        logger.debug('No preference key in the configuration file')
        return None
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception getting preferences from the configuration file')
        return None


def load_setting_export_path(logger, config_settings):
    """
    Attempt to extract export path from config settings

    :param config_settings:  config settings loaded from config file
    :param logger:           the logger
    :return:                 export path, None if path is invalid or missing
    """
    try:
        export_path = config_settings['export_options']['export_path']
        if export_path is not None:
            return export_path
        else:
            return None
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception getting export path from the configuration file')
        return None


def load_setting_media_sync_offset(logger, config_settings):
    """

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 media sync offset parsed from file, else default media sync offset
                             defined as global constant
    """
    try:
        media_sync_offset = config_settings['export_options']['media_sync_offset_in_seconds']
        if media_sync_offset is None or media_sync_offset < 0 or not isinstance(media_sync_offset, int):
            media_sync_offset = DEFAULT_MEDIA_SYNC_OFFSET_IN_SECONDS
        return media_sync_offset
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception parsing media sync offset from config file')
        return DEFAULT_MEDIA_SYNC_OFFSET_IN_SECONDS


def configure_logging(path_to_log_directory):
    """
    Configure logger

    :param path_to_log_directory:  path to directory to write log file in
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


def save_web_report_link_to_file(logger, export_dir, web_report_data):
    """
    Write Web Report links to 'web-report-links.csv' on disk at specified location
    Any existing file with the same name will be appended to
    :param logger:          the logger
    :param export_dir:      path to directory for exports
    :param web_report_data:     Data to write to CSV: Template ID, Template name, Audit ID, Audit name, Web Report link
    """
    if not os.path.exists(export_dir):
        logger.info("Creating directory at {0} for Web Report links.".format(export_dir))
        os.makedirs(export_dir)
    file_path = os.path.join(export_dir, 'web-report-links.csv')
    if os.path.isfile(file_path):
        logger.info('Appending Web Report link to ' + file_path)
        try:
            with open(file_path, 'ab') as web_report_link_csv:
                wr = csv.writer(web_report_link_csv, dialect='excel', quoting=csv.QUOTE_ALL)
                wr.writerow(web_report_data)
                web_report_link_csv.close()
        except Exception as ex:
            log_critical_error(logger, ex, 'Exception while writing' + file_path + ' to file')
    else:
        logger.info('Creating ' + file_path)
        logger.info('Appending web report to ' + file_path)
        try:
            with open(file_path, 'wb') as web_report_link_csv:
                wr = csv.writer(web_report_link_csv, dialect='excel', quoting=csv.QUOTE_ALL)
                wr.writerow(['Template ID', 'Template Name', 'Audit ID', 'Audit Name',  'Web Report Link'])
                wr.writerow(web_report_data)
                web_report_link_csv.close()
        except Exception as ex:
            log_critical_error(logger, ex, 'Exception while writing' + file_path + ' to file')


def save_exported_actions_to_csv_file(logger, export_path, actions_array):
    """
    Write Actions to 'iauditor_actions.csv' on disk at specified location
    :param logger:          the logger
    :param export_path:     path to directory for exports
    :param actions_array:   Array of action objects to be converted to CSV and saved to disk
    """
    if not actions_array:
        logger.info('No actions returned after ' + get_last_successful_actions_export(logger))
        return
    filename = ACTIONS_EXPORT_FILENAME
    file_path = os.path.join(export_path, filename)
    logger.info('Exporting ' + str(len(actions_array)) + ' actions to ' + file_path)
    if os.path.isfile(file_path):
        actions_csv = open(file_path, 'ab')
        actions_csv_wr = csv.writer(actions_csv, dialect='excel', quoting=csv.QUOTE_ALL)
    else:
        actions_csv = open(file_path, 'wb')
        actions_csv_wr = csv.writer(actions_csv, dialect='excel', quoting=csv.QUOTE_ALL)
        actions_csv_wr.writerow([
            'actionId', 'description', 'assignee', 'priority', 'priorityCode', 'status', 'statusCode', 'dueDatetime',
            'audit', 'auditId', 'linkedToItem', 'linkedToItemId', 'creatorName', 'creatorId', 'createdDatetime',
            'modifiedDatetime', 'completedDatetime', 'site', 'title'
        ])
    for action in actions_array:
        actions_list = transform_action_object_to_list(action)
        actions_csv_wr.writerow(actions_list)
        del actions_list


def transform_action_object_to_list(action):
    priority_codes = {0: 'None', 10: 'Low', 20: 'Medium', 30: 'High'}
    status_codes = {0: 'To Do', 10: 'In Progress', 50: 'Done', 60: 'Cannot Do'}
    get_json_property = csvExporter.get_json_property
    actions_list = [get_json_property(action, 'action_id'), get_json_property(action, 'description')]
    assignee_list = []
    for assignee in get_json_property(action, 'assignees'):
        assignee_list.append(get_json_property(assignee, 'name'))
    actions_list.append(", ".join(assignee_list))
    actions_list.append(get_json_property(priority_codes, get_json_property(action, 'priority')))
    actions_list.append(get_json_property(action, 'priority'))
    actions_list.append(get_json_property(status_codes, get_json_property(action, 'status')))
    actions_list.append(get_json_property(action, 'status'))
    actions_list.append(get_json_property(action, 'due_at'))
    actions_list.append(get_json_property(action, 'audit', 'name'))
    actions_list.append(get_json_property(action, 'audit', 'audit_id'))
    actions_list.append(get_json_property(action, 'item', 'label'))
    actions_list.append(get_json_property(action, 'item', 'item_id'))
    actions_list.append(get_json_property(action, 'created_by', 'name'))
    actions_list.append(get_json_property(action, 'created_by', 'user_id'))
    actions_list.append(get_json_property(action, 'created_at'))
    actions_list.append(get_json_property(action, 'modified_at'))
    actions_list.append(get_json_property(action, 'completed_at'))
    actions_list.append(get_json_property(action, 'site'))
    actions_list.append(get_json_property(action, 'title'))
    return actions_list


def save_exported_media_to_file(logger, export_dir, media_file, filename, extension):
    """
    Write exported media item to disk at specified location with specified file name.
    Any existing file with the same name will be overwritten.
    :param logger:      the logger
    :param export_dir:  path to directory for exports
    :param media_file:  media file to write to disc
    :param filename:    filename to give exported image
    :param extension:   extension to give exported image
    """
    if not os.path.exists(export_dir):
        logger.info("Creating directory at {0} for media files.".format(export_dir))
        os.makedirs(export_dir)
    file_path = os.path.join(export_dir, filename + '.' + extension)
    if os.path.isfile(file_path):
        logger.info('Overwriting existing report at ' + file_path)
    try:
        with open(file_path, 'wb') as out_file:
            shutil.copyfileobj(media_file.raw, out_file)
        del media_file
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception while writing' + file_path + ' to file')


def save_exported_document(logger, export_dir, export_doc, filename, extension):
    """
    Write exported document to disk at specified location with specified file name.
    Any existing file with the same name will be overwritten.
    :param logger:      the logger
    :param export_dir:  path to directory for exports
    :param export_doc:  export document to write
    :param filename:    filename to give exported document
    :param extension:   extension to give exported document
    """
    file_path = os.path.join(export_dir, filename + '.' + extension)
    if os.path.isfile(file_path):
        logger.info('Overwriting existing report at ' + file_path)
    try:
        with open(file_path, 'wb') as export_file:
            export_file.write(export_doc)
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception while writing' + file_path + ' to file')


def update_sync_marker_file(date_modified):
    """
    Replaces the contents of the sync marker file with the most
    recent modified_at date time value from audit JSON data

    :param date_modified:   modified_at value from most recently downloaded audit JSON
    :return:
    """
    with open(SYNC_MARKER_FILENAME, 'w') as sync_marker_file:
        sync_marker_file.write(date_modified)


def get_last_successful(logger):
    """
    Read the date and time of the last successfully exported audit data from the sync marker file

    :param logger:  the logger
    :return:        A datetime value (or 2000-01-01 if syncing since the 'beginning of time')
    """
    if os.path.isfile(SYNC_MARKER_FILENAME):
        with open(SYNC_MARKER_FILENAME, 'r+') as last_run:
            last_successful = last_run.readlines()[0]
            last_successful = last_successful.strip()

    else:
        beginning_of_time = '2000-01-01T00:00:00.000Z'
        last_successful = beginning_of_time
        with open(SYNC_MARKER_FILENAME, 'w') as last_run:
            last_run.write(last_successful)
        logger.info('Searching for audits since the beginning of time: ' + beginning_of_time)
    return last_successful


def update_actions_sync_marker_file(logger, date_modified):
    """
    Replaces the contents of the actions sync marker file with the the date/time string provided
    :param logger:   The logger
    :param date_modified:   ISO string
    """
    try:
        with open(ACTIONS_SYNC_MARKER_FILENAME, 'w') as actions_sync_marker_file:
            actions_sync_marker_file.write(date_modified)
    except Exception as ex:
        log_critical_error(logger, ex, 'Unable to open ' + ACTIONS_SYNC_MARKER_FILENAME + ' for writing')
        exit()


def get_last_successful_actions_export(logger):
    """
    Reads the actions sync marker file to determine the date and time of the most last successfully exported action.
    The actions sync marker file is expected to contain a single ISO formatted datetime string.
    :param logger:  the logger
    :return:        A datetime value (or 2000-01-01 if syncing since the 'beginning of time')
    """
    if os.path.isfile(ACTIONS_SYNC_MARKER_FILENAME):
        with open(ACTIONS_SYNC_MARKER_FILENAME, 'r+') as last_run:
            last_successful_actions_export = last_run.readlines()[0]
            logger.info('Searching for actions modified after ' + last_successful_actions_export)
    else:
        beginning_of_time = '2000-01-01T00:00:00.000Z'
        last_successful_actions_export = beginning_of_time
        with open(ACTIONS_SYNC_MARKER_FILENAME, 'w') as last_run:
            last_run.write(last_successful_actions_export)
        logger.info('Searching for actions since the beginning of time: ' + beginning_of_time)
    return last_successful_actions_export


def parse_export_filename(audit_json, filename_item_id):
    """
    Get 'response' value of specified header item to use for export file name

    :param header_items:      header_items array from audit JSON
    :param filename_item_id:  item_id from config settings
    :return:                  'response' value of specified item from audit JSON
    """
    if filename_item_id is None:
        return None
    # Not all Audits will actually contain an Audit Title item. For examples, when Audit Title rules are set, the Audit Title item is not going to be included by default.
    # When this item ID is specified in the custom export filename configuration, the audit_data.name property will be used to populate the data as it covers all cases.
    if filename_item_id == AUDIT_TITLE_ITEM_ID and 'audit_data' in audit_json.keys() and 'name' in audit_json['audit_data'].keys():
        return audit_json['audit_data']['name'].replace('/','_')
    for item in audit_json['header_items']:
        if item['item_id'] == filename_item_id:
            if 'responses' in item.keys():
                if 'text' in item['responses'].keys() and item['responses']['text'].strip() != '':
                    return item['responses']['text']
    return None


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
        log_critical_error(logger, ex, 'Exception retrieving setting "filename" from the configuration file')
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
    :return:                    settings dictionary containing values for:
                                api_token, export_path, preferences,
                                filename_item_id, sync_delay_in_seconds loaded from
                                config file, media_sync_offset_in_seconds
    """
    config_settings = yaml.safe_load(open(path_to_config_file))
    settings = {
        API_TOKEN: load_setting_api_access_token(logger, config_settings),
        EXPORT_PATH: load_setting_export_path(logger, config_settings),
        PREFERENCES: load_setting_preference_mapping(logger, config_settings),
        FILENAME_ITEM_ID: get_filename_item_id(logger, config_settings),
        SYNC_DELAY_IN_SECONDS: load_setting_sync_delay(logger, config_settings),
        EXPORT_INACTIVE_ITEMS_TO_CSV: load_export_inactive_items_to_csv(logger, config_settings),
        MEDIA_SYNC_OFFSET_IN_SECONDS: load_setting_media_sync_offset(logger, config_settings)
    }

    return settings


def configure(logger, path_to_config_file, export_formats):
    """
    instantiate and configure logger, load config settings from file, instantiate SafetyCulture SDK
    :param logger:              the logger
    :param path_to_config_file: path to config file
    :param export_formats:      desired export formats
    :return:                    instance of SafetyCulture SDK object, config settings
    """

    config_settings = load_config_settings(logger, path_to_config_file)
    config_settings[EXPORT_FORMATS] = export_formats
    sc_client = sp.SafetyCulture(config_settings[API_TOKEN])

    if config_settings[EXPORT_PATH] is not None:
        create_directory_if_not_exists(logger, config_settings[EXPORT_PATH])
    else:
        logger.info('Invalid export path was found in ' + path_to_config_file + ', defaulting to /exports')
        config_settings[EXPORT_PATH] = os.path.join(os.getcwd(), 'exports')
        create_directory_if_not_exists(logger, config_settings[EXPORT_PATH])

    return sc_client, config_settings


def parse_command_line_arguments(logger):
    """
    Parse command line arguments received, if any
    Print example if invalid arguments are passed

    :param logger:  the logger
    :return:        config_filename passed as argument if any, else DEFAULT_CONFIG_FILENAME
                    export_formats passed as argument if any, else 'pdf'
                    list_epreferences if passed as argument, else None
                    do_loop False if passed as argument, else True
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file to use, defaults to ' + DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--format', nargs='*', help='formats to download, valid options are pdf, '
                                                    'json, docx, csv, media, web-report-link, actions')
    parser.add_argument('--list_preferences', nargs='*', help='display all preferences, or restrict to specific'
                                                                  ' template_id if supplied as additional argument')
    parser.add_argument('--loop', nargs='*', help='execute continuously until interrupted')
    parser.add_argument('--setup', action='store_true', help='Automatically create new directory containing the '
                                                             'necessary config file.'
                        'Directory will be named iAuditor Audit Exports, and will be placed in your current directory')
    args = parser.parse_args()

    config_filename = DEFAULT_CONFIG_FILENAME

    if args.setup:
        initial_setup(logger)
        exit()

    if args.config is not None:
        if os.path.isfile(args.config):
            config_filename = args.config
            logger.debug(config_filename + ' passed as config argument')
        else:
            logger.error(config_filename + ' is not a valid config file')
            sys.exit(1)

    export_formats = ['pdf']
    if args.format is not None and len(args.format) > 0:
        valid_export_formats = ['json', 'docx', 'pdf', 'csv', 'media', 'web-report-link', 'actions']
        export_formats = []
        for option in args.format:
            if option not in valid_export_formats:
                print('{0} is not a valid export format.  Valid options are pdf, json, docx, csv, web-report-link, '
                      'media, or actions'.format(option))
                logger.info('invalid export format argument: {0}'.format(option))
            else:
                export_formats.append(option)

    loop_enabled = True if args.loop is not None else False

    return config_filename, export_formats, args.list_preferences, loop_enabled


def initial_setup(logger):
    """
    Creates a new directory in current working directory called 'iauditor_exports_folder'.  If 'iauditor_exports_folder'
    already exists the setup script will notify user that the folder exists and exit. Default config file placed
    in directory, with user API Token. User is asked for iAuditor credentials in order to generate their
    API token.
    :param logger:  the logger
    """
    # setup variables
    current_directoy_path = os.getcwd()
    exports_folder_name = 'iauditor_exports_folder'

    # get token, set token
    token = sp.get_user_api_token(logger)

    if not token:
        logger.critical("Problem generating API token.")
        exit()
    DEFAULT_CONFIG_FILE_YAML[1] = '\n    token: ' + str(token)

    # create new directory
    create_directory_if_not_exists(logger, exports_folder_name)

    # write config file
    path_to_config_file = os.path.join(current_directoy_path, exports_folder_name, 'config.yaml')
    if os.path.exists(path_to_config_file):
        logger.critical("Config file already exists at {0}".format(path_to_config_file))
        logger.info("Please remove or rename the existing config file, then retry this setup program.")
        logger.info('Exiting.')
        exit()
    try:
        config_file = open(path_to_config_file, 'w')
        config_file.writelines(DEFAULT_CONFIG_FILE_YAML)
    except Exception as ex:
        log_critical_error(logger, ex, "Problem creating " + path_to_config_file)
        logger.info("Exiting.")
        exit()
    logger.info("Default config file successfully created at {0}.".format(path_to_config_file))
    os.chdir(exports_folder_name)
    choice = input('Would you like to start exporting audits from:\n  1. The beginning of time\n  '
                   '2. Now\n  Enter 1 or 2: ')
    if choice == '1':
        logger.info('Audit exporting set to start from earliest audits available')
        get_last_successful(logger)
    else:
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        update_sync_marker_file(now)
        logger.info('Audit exporting set to start from ' + now)
    exit()


def show_preferences_and_exit(list_preferences, sc_client):
    """
    Display preferences to stdout and exit

    :param list_preferences: empty list for all preference, list of template_ids if specified at command line
    :param sc_client:            instance of SDK object, used to retrieve preferences
    """
    row_boundary = '|' + '-' * 136 + '|'
    row_format = '|{0:<37} | {1:<40} | {2:<10}| {3:<10}|'
    print(row_boundary)
    print(row_format.format('Preference ID', 'Preference Name', 'Global', 'Default'))
    print(row_boundary)

    if len(list_preferences) > 0:
        for template_id in list_preferences:
            preferences = sc_client.get_preference_ids(template_id)
            for preference in preferences['preferences']:
                preference_id = str(preference['id'])
                preference_name = str(preference['label'])[:35]
                is_global = str(preference['is_global'])
                is_default = str(preference['is_default'])
                print(row_format.format(preference_id, preference_name, is_global, is_default))
                print(row_boundary)
        sys.exit()
    else:
        preferences = sc_client.get_preference_ids()
        for preference in preferences['preferences']:
            preference_id = str(preference['id'])
            preference_name = str(preference['label'])[:35]
            is_global = str(preference['is_global'])
            is_default = str(preference['is_default'])
            print(row_format.format(preference_id, preference_name, is_global, is_default))
            print(row_boundary)
        sys.exit(0)

def export_actions(logger, settings, sc_client):
    """
    Export all actions created after date specified
    :param logger:      The logger
    :param settings:    Settings from command line and configuration file
    :param sc_client:   instance of safetypy.SafetyCulture class
    """
    logger.info('Exporting iAuditor actions')
    last_successful_actions_export = get_last_successful_actions_export(logger)
    actions_array = sc_client.get_audit_actions(last_successful_actions_export)
    if actions_array is not None:
        logger.info('Found ' + str(len(actions_array)) + ' actions')
        save_exported_actions_to_csv_file(logger, settings[EXPORT_PATH], actions_array)
        utc_iso_datetime_now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        update_actions_sync_marker_file(logger, utc_iso_datetime_now)


def sync_exports(logger, settings, sc_client):
    """
    Perform sync, exporting documents modified since last execution

    :param logger:    the logger
    :param settings:  Settings from command line and configuration file
    :param sc_client: Instance of SDK object
    """
    if 'actions' in settings[EXPORT_FORMATS]:
        export_actions(logger, settings, sc_client)
    if not bool(set(settings[EXPORT_FORMATS]) & {'pdf', 'docx', 'csv', 'media', 'web-report-link', 'json'}):
        return
    last_successful = get_last_successful(logger)
    list_of_audits = sc_client.discover_audits(modified_after=last_successful)
    if list_of_audits is not None:
        logger.info(str(list_of_audits['total']) + ' audits discovered')
        export_count = 1
        export_total = list_of_audits['total']
        for audit in list_of_audits['audits']:
            logger.info('Processing audit (' + str(export_count) + '/' + str(export_total) + ')')
            process_audit(logger, settings, sc_client, audit)
            export_count += 1


def check_if_media_sync_offset_satisfied(logger, settings, audit):
    """
    Check if the media sync offset is satisfied. The media sync offset is a duration in seconds specified in the
    configuration file. This duration is the amount of time audit media is given to sync up with SafetyCulture servers
    before this tool exports the audit data.
    :param logger:    The logger
    :param settings:  Settings from command line and configuration file
    :param audit:     Audit JSON
    :return:          Boolean - True if the media sync offset is satisfied, otherwise, returns false.
    """
    modified_at = dateutil.parser.parse(audit['modified_at'])
    now = datetime.utcnow()
    elapsed_time_difference = (pytz.utc.localize(now) - modified_at)
    # if the media_sync_offset has been satisfied
    if not elapsed_time_difference > timedelta(seconds=settings[MEDIA_SYNC_OFFSET_IN_SECONDS]):
        logger.info('Audit {0} modified too recently, some media may not have completed syncing. Skipping export until next sync cycle'.format(
            audit['audit_id']))
        return False
    return True


def process_audit(logger, settings, sc_client, audit):
    """
    Export audit in the format specified in settings. Formats include PDF, JSON, CSV, MS Word (docx), media, or
    web report link.
    :param logger:      The logger
    :param settings:    Settings from command line and configuration file
    :param sc_client:   instance of safetypy.SafetyCulture class
    :param audit:       Audit JSON to be exported
    """
    if not check_if_media_sync_offset_satisfied(logger, settings, audit):
        return
    audit_id = audit['audit_id']
    logger.info('downloading ' + audit_id)
    audit_json = sc_client.get_audit(audit_id)
    template_id = audit_json['template_id']
    preference_id = None
    if settings[PREFERENCES] is not None and template_id in settings[PREFERENCES].keys():
        preference_id = settings[PREFERENCES][template_id]
    export_filename = parse_export_filename(audit_json, settings[FILENAME_ITEM_ID]) or audit_id
    for export_format in settings[EXPORT_FORMATS]:
        if export_format in ['pdf', 'docx']:
            export_audit_pdf_word(logger, sc_client, settings, audit_id, preference_id, export_format, export_filename)
        elif export_format == 'json':
            export_audit_json(logger, settings, audit_json, export_filename)
        elif export_format == 'csv':
            export_audit_csv(settings, audit_json)
        elif export_format == 'media':
            export_audit_media(logger, sc_client, settings, audit_json, audit_id, export_filename)
        elif export_format == 'web-report-link':
            export_audit_web_report_link(logger, settings, sc_client, audit_json, audit_id, template_id)
    logger.debug('setting last modified to ' + audit['modified_at'])
    update_sync_marker_file(audit['modified_at'])


def export_audit_pdf_word(logger, sc_client, settings, audit_id, preference_id, export_format, export_filename):
    """
    Save Audit to disk in PDF or MS Word format
    :param logger:      The logger
    :param sc_client:   instance of safetypy.SafetyCulture class
    :param settings:    Settings from command line and configuration file
    :param audit_id:    Unique audit UUID
    :param preference_id:   Unique preference UUID
    :param export_format:       'pdf' or 'docx' string
    :param export_filename:     String indicating what to name the exported audit file
    """
    export_doc = sc_client.get_export(audit_id, preference_id, export_format)
    save_exported_document(logger, settings[EXPORT_PATH], export_doc, export_filename, export_format)


def export_audit_json(logger, settings, audit_json, export_filename):
    """
    Save audit JSON to disk
    :param logger:      The logger
    :param settings:    Settings from the command line and configuration file
    :param audit_json:  Audit JSON
    :param export_filename:     String indicating what to name the exported audit file
    """
    export_format = 'json'
    export_doc = json.dumps(audit_json, indent=4)
    save_exported_document(logger, settings[EXPORT_PATH], export_doc.encode(), export_filename, export_format)


def export_audit_csv(settings, audit_json):
    """
    Save audit CSV to disk.
    :param settings:    Settings from command line and configuration file
    :param audit_json:  Audit JSON
    """
    csv_exporter = csvExporter.CsvExporter(audit_json, settings[EXPORT_INACTIVE_ITEMS_TO_CSV])
    csv_export_filename = audit_json['template_id']
    csv_exporter.append_converted_audit_to_bulk_export_file(
        os.path.join(settings[EXPORT_PATH], csv_export_filename + '.csv'))


def export_audit_media(logger, sc_client, settings, audit_json, audit_id, export_filename):
    """
    Save audit media files to disk
    :param logger:      The logger
    :param sc_client:   instance of safetypy.SafetyCulture class
    :param settings:    Settings from command line and configuration file
    :param audit_json:  Audit JSON
    :param audit_id:    Unique audit UUID
    :param export_filename:     String indicating what to name the exported audit file
    """
    media_export_path = os.path.join(settings[EXPORT_PATH], 'media', export_filename)
    media_id_list = get_media_from_audit(logger, audit_json)
    for media_id in media_id_list.keys():
        media_file = sc_client.get_media(audit_id, media_id)
        if media_file is None:
            logger.warn("Failed to save media object {0}".format(media_id))
            continue
        media_export_filename = media_id
        logger.info("Saving media_{0} to disc.".format(media_id))
        save_exported_media_to_file(logger, media_export_path, media_file, media_export_filename, media_id_list[media_id])


def export_audit_web_report_link(logger, settings, sc_client, audit_json, audit_id, template_id):
    """
    Save web report link to disk in a CSV file.
    :param logger:      The logger
    :param sc_client:   instance of safetypy.SafetyCulture class
    :param settings:    Settings from command line and configuration file
    :param audit_json:  Audit JSON
    :param audit_id:    Unique audit UUID
    :param template_id: Unique template UUID
    """
    web_report_link = sc_client.get_web_report(audit_id)
    web_report_data = [
        template_id,
        csvExporter.get_json_property(audit_json, 'template_data', 'metadata', 'name'),
        audit_id,
        csvExporter.get_json_property(audit_json, 'audit_data', 'name'),
        web_report_link
    ]
    save_web_report_link_to_file(logger, settings[EXPORT_PATH], web_report_data)


def get_media_from_audit(logger, audit_json):
    """
    Retrieve media IDs from a audit JSON
    :param logger: the logger
    :param audit_json: single audit JSON
    :return: list of media IDs
    """
    media_id_list = dict()
    for item in audit_json['header_items'] + audit_json['items']:
        # This condition checks for media attached to question and media type fields.
        if 'media' in item.keys():
            for media in item['media']:
                name, ext = get_media_file_name_and_ext(logger, media)
                media_id_list[name] = ext

        # This condition checks for media attached to signature and drawing type fields.
        if 'responses' in item.keys() and 'image' in item['responses'].keys():
            name, ext = get_media_file_name_and_ext(logger, item['responses']['image'])
            media_id_list[name] = ext

        # This condition checks for media attached to information type fields.
        if 'options' in item.keys() and 'media' in item['options'].keys():
            name, ext = get_media_file_name_and_ext(logger, item['options']['media'])
            media_id_list[name] = ext

    logger.info("Discovered {0} media files associated with {1}.".format(len(media_id_list), audit_json['audit_id']))
    return media_id_list

def get_media_file_name_and_ext(logger, media):
    """
    Retrive the media file extension from 'file_ext' of the media block.
    If, the attribute is missing or is an empty string, default to .jpg
    :param logger: the logger
    :param media: the media block
    :return: Tuple containing the media-id and its file extension
    """
    if 'file_ext' in media.keys() and len(media['file_ext']) > 0:
        return media['media_id'], media['file_ext']
    logger.info("Did not find valid file_ext for {0}. Defaulting to .jpg".format(media['media_id']))
    return media['media_id'], 'jpg'

def loop(logger, sc_client, settings):
    """
    Loop sync until interrupted by user
    :param logger:     the logger
    :param sc_client:  instance of SafetyCulture SDK object
    :param settings:   dictionary containing config settings values
    """
    sync_delay_in_seconds = settings[SYNC_DELAY_IN_SECONDS]
    while True:
        sync_exports(logger, settings, sc_client)
        logger.info('Next check will be in ' + str(sync_delay_in_seconds) + ' seconds. Waiting...')
        time.sleep(sync_delay_in_seconds)


def main():
    try:
        logger = configure_logger()
        path_to_config_file, export_formats, preferences_to_list, loop_enabled = parse_command_line_arguments(logger)
        sc_client, settings = configure(logger, path_to_config_file, export_formats)

        if preferences_to_list is not None:
            show_preferences_and_exit(preferences_to_list, sc_client)

        if loop_enabled:
            loop(logger, sc_client, settings)
        else:
            sync_exports(logger, settings, sc_client)
            logger.info('Completed sync process, exiting')

    except KeyboardInterrupt:
        print("Interrupted by user, exiting.")
        sys.exit(0)


if __name__ == '__main__':
    main()
