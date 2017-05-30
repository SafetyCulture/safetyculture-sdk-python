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
import datetime
import dateutil.parser
import yaml
import pytz
from tzlocal import get_localzone
import csvExporter as csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp

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

# Whether to export inactive items to CSV
DEFAULT_EXPORT_INACTIVE_ITEMS_TO_CSV = True


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
        log_critical_error(logger, ex,
                           'Exception parsing sync_delay from the configuration file, defaulting to {0}'.format(str(
                               DEFAULT_SYNC_DELAY_IN_SECONDS)))
        return DEFAULT_SYNC_DELAY_IN_SECONDS


def load_setting_export_profile_mapping(logger, config_settings):
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
        log_critical_error(logger, ex, 'Exception getting export profiles from the configuration file')
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


def load_setting_export_timezone(logger, config_settings):
    """
    If a user supplied timezone is found in the config settings it will
    be used to set the dates in the generated audit report, otherwise
    a local timezone will be used.

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 a timezone from config if valid, else local timezone for this machine
    """
    try:
        timezone = config_settings['export_options']['timezone']
        if timezone is None or timezone not in pytz.all_timezones:
            timezone = get_localzone()
            logger.info('No valid timezone found in config file, defaulting to local timezone')
        return str(timezone)
    except Exception as ex:
        log_critical_error(logger, ex, 'Exception parsing timezone from config file')
        timezone = get_localzone()
        return str(timezone)


def load_setting_media_sync_offset(logger, config_settings):
    """

    :param logger:           the logger
    :param config_settings:  config settings loaded from config file
    :return:                 media sync offset parsed from file, else default media sync offset
                             defined as global constant
    """
    try:
        media_sync_offset = config_settings['media_sync_offset_in_seconds']
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
    else:
        beginning_of_time = '2000-01-01T00:00:00.000Z'
        last_successful = beginning_of_time
        with open(SYNC_MARKER_FILENAME, 'w') as last_run:
            last_run.write(last_successful)
        logger.info('Searching for audits since the beginning of time: ' + beginning_of_time)

    return last_successful


def parse_export_filename(header_items, filename_item_id):
    """
    Get 'response' value of specified header item to use for export file name

    :param header_items:      header_items array from audit JSON
    :param filename_item_id:  item_id from config settings
    :return:                  'response' value of specified item from audit JSON
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
                                api_token, export_path, timezone, export_profiles,
                                filename_item_id, sync_delay_in_seconds loaded from
                                config file, media_sync_offset_in_seconds
    """
    config_settings = yaml.safe_load(open(path_to_config_file))
    settings = {
        'api_token': load_setting_api_access_token(logger, config_settings),
        'export_path': load_setting_export_path(logger, config_settings),
        'timezone': load_setting_export_timezone(logger, config_settings),
        'export_profiles': load_setting_export_profile_mapping(logger, config_settings),
        'filename_item_id': get_filename_item_id(logger, config_settings),
        'sync_delay_in_seconds': load_setting_sync_delay(logger, config_settings),
        'export_inactive_items_to_csv': load_export_inactive_items_to_csv(logger, config_settings),
        'media_sync_offset_in_seconds': load_setting_media_sync_offset(logger, config_settings)
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
    config_settings['export_formats'] = export_formats
    sc_client = sp.SafetyCulture(config_settings['api_token'])

    if config_settings['export_path'] is not None:
        create_directory_if_not_exists(logger, config_settings['export_path'])
    else:
        logger.info('Invalid export path was found in ' + path_to_config_file + ', defaulting to /exports')
        config_settings['export_path'] = os.path.join(os.getcwd(), 'exports')
        create_directory_if_not_exists(logger, config_settings['export_path'])

    return sc_client, config_settings


def parse_command_line_arguments(logger):
    """
    Parse command line arguments received, if any
    Print example if invalid arguments are passed

    :param logger:  the logger
    :return:        config_filename passed as argument if any, else DEFAULT_CONFIG_FILENAME
                    export_formats passed as argument if any, else 'pdf'
                    list_export_profiles if passed as argument, else None
                    do_loop False if passed as argument, else True
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file to use, defaults to ' + DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--format', nargs='*', help='formats to download, valid options are pdf, json, docx')
    parser.add_argument('--list_export_profiles', nargs='*', help='display all export profiles, or restrict to specific'
                                                                  ' template_id if supplied as additional argument')
    parser.add_argument('--loop', nargs='*', help='execute continuously until interrupted')
    args = parser.parse_args()

    config_filename = DEFAULT_CONFIG_FILENAME
    if args.config is not None:
        if os.path.isfile(args.config):
            config_filename = args.config
            logger.debug(config_filename + ' passed as config argument')
        else:
            logger.error(config_filename + ' is not a valid config file')
            sys.exit(1)

    export_formats = ['pdf']
    if args.format is not None and len(args.format) > 0:
        valid_export_formats = ['json', 'docx', 'pdf', 'csv']
        export_formats = []
        for option in args.format:
            if option not in valid_export_formats:
                print '{0} is not a valid export format.  Valid options are pdf, json, or docx'.format(option)
                logger.info('invalid export format argument: {0}'.format(option))
            else:
                export_formats.append(option)

    loop_enabled = True if args.loop is not None else False

    return config_filename, export_formats, args.list_export_profiles, loop_enabled


def show_export_profiles_and_exit(list_export_profiles, sc_client):
    """
    Display export profiles to stdout and exit

    :param list_export_profiles: empty list for all profiles, list of template_ids if specified at command line
    :param sc_client:            instance of SDK object, used to retrieve profiles
    """
    row_boundary = '|' + '-' * 136 + '|'
    row_format = '|{0:<25} | {1:<25} | {2:<80}|'
    print row_boundary
    print row_format.format('Template Name', 'Profile Name', 'Profile ID')
    print row_boundary

    if len(list_export_profiles) > 0:
        for template_id in list_export_profiles:
            profile = sc_client.get_export_profile_ids(template_id)
            template_name = str(profile['export_profiles'][0]['templates'][0]['name'])
            profile_name = str(profile['export_profiles'][0]['name'])
            profile_id = str(profile['export_profiles'][0]['id'])
            print row_format.format(template_name, profile_name, profile_id)
            print row_boundary
        sys.exit()
    else:
        profiles = sc_client.get_export_profile_ids()
        for profile in profiles['export_profiles']:
            template_name = str(profile['templates'][0]['name'])[:19]
            profile_name = str(profile['name'])[:19]
            profile_id = str(profile['id'])
            print row_format.format(template_name, profile_name, profile_id)
            print row_boundary
        sys.exit(0)


def sync_exports(logger, sc_client, settings):
    """
    Perform sync, exporting documents modified since last execution

    :param logger:    the logger
    :param sc_client: instance of SDK object
    :param settings:  dict containing settings values
    """
    export_formats = settings['export_formats']
    export_profiles = settings['export_profiles']
    filename_item_id = settings['filename_item_id']
    export_path = settings['export_path']
    timezone = settings['timezone']
    export_inactive_items_to_csv = settings['export_inactive_items_to_csv']
    media_sync_offset = settings['media_sync_offset_in_seconds']
    last_successful = get_last_successful(logger)
    results = sc_client.discover_audits(modified_after=last_successful)

    if results is not None:
        logger.info(str(results['total']) + ' audits discovered')
        export_count = 1
        export_total = results['total']

        for audit in results['audits']:
            logger.info('Processing audit (' + str(export_count) + '/' + str(export_total) + ')')
            modified_at = dateutil.parser.parse(audit['modified_at'])
            now = datetime.datetime.utcnow()
            elapsed_time_difference = (pytz.utc.localize(now) - modified_at)
            if elapsed_time_difference > datetime.timedelta(seconds=media_sync_offset):
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
                    elif export_format == 'csv':
                        csv_exporter = csv.CsvExporter(audit_json, export_inactive_items_to_csv)
                        export_filename = audit_json['template_id']
                        csv_exporter.append_converted_audit_to_bulk_export_file(os.path.join(export_path, export_filename + '.csv'))
                        continue
                    save_exported_document(logger, export_path, export_doc, export_filename, export_format)
                logger.debug('setting last modified to ' + audit['modified_at'])
                update_sync_marker_file(audit['modified_at'])
            else:
                logger.info('Audit\'s modified_at value is less than {0} seconds in the past, skipping for now!'.format(media_sync_offset))


def loop(logger, sc_client, settings):
    """
    Loop sync until interrupted by user

    :param logger:     the logger
    :param sc_client:  instance of SafetyCulture SDK object
    :param settings:   dictionary containing config settings values
    """
    sync_delay_in_seconds = settings['sync_delay_in_seconds']
    while True:
        sync_exports(logger, sc_client, settings)
        logger.info('Next check will be in ' + str(sync_delay_in_seconds) + ' seconds. Waiting...')
        time.sleep(sync_delay_in_seconds)


def main():
    try:
        logger = configure_logger()
        path_to_config_file, export_formats, export_profiles_to_list, loop_enabled = parse_command_line_arguments(logger)
        sc_client, settings = configure(logger, path_to_config_file, export_formats)

        if export_profiles_to_list is not None:
            show_export_profiles_and_exit(export_profiles_to_list, sc_client)

        if loop_enabled:
            loop(logger, sc_client, settings)
        else:
            sync_exports(logger, sc_client, settings)
            logger.info('Completed sync process, exiting')

    except KeyboardInterrupt:
        print "Interrupted by user, exiting."
        sys.exit(0)


if __name__ == '__main__':
    main()
