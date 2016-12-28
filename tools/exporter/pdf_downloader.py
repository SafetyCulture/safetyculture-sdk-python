# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import argparse
import logging
import os
import sys
from datetime import datetime
import yaml
import pytz
from tzlocal import get_localzone
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from SafetyPy import SafetyPy as sp


DEFAULT_CONFIG_FILE = 'pdf_config.yaml'
LOG_LEVEL = logging.DEBUG


def log_exception(ex, message):
    logger.critical(message)
    logger.critical(ex)


def get_export_profile_mapping(config_settings):
    """
    Attempt to extract export profile id's from config file
    If valid id's are found, return a dict mapping templates to
      export profiles
    Otherwise return None

    :param config_settings:
    :return: dict of valid export_profile_id's, or None
    """
    try:
        profile_mapping = {}
        export_profile_settings = config_settings['export_profiles']
        if export_profile_settings is not None:
            profile_lines = export_profile_settings.split(" ")
            for profile in profile_lines:
                template_id = profile[:profile.index(':')]
                if template_id not in profile_mapping.keys():
                    profile_mapping[template_id] = profile
        return profile_mapping
    except KeyError as ex:
        logger.debug('No export profile key in ' + config_filename)
        return None
    except Exception as ex:
        log_exception(ex, 'Exception getting export profiles from ' + config_filename)
        return None

def get_export_path(config_settings):
    """
    Attempt to extract export path from config settings
    :return: export path, None if path is invalid or missing
    """
    try:
        export_path = config_settings['export_options']['export_path']
        if export_path:
            return export_path
        else:
            return None
    except Exception as ex:
        log_exception(ex, 'Exception getting export path from ' + config_filename)
        return None


def get_timezone(config_settings):
    """
    Attempt to extract Olson timezone from config settings
    :return: extracted timezone, default to local timezone on exception
    """
    try:
        timezone = config_settings['export_options']['timezone']
        if timezone is None or timezone not in pytz.all_timezones:
            timezone = get_localzone()
            logger.info('no valid timezone in ' + config_filename + ', defaulting to local timezone')
        return str(timezone)
    except Exception as ex:
        log_exception(ex, 'Exception parsing timezone from ' + config_filename)
        timezone = get_localzone()
        return str(timezone)


def ensure_log_folder_exists(log_dir):
    """
    check for log subdirectory (current directory + '/log/')
    create it if it doesn't exist
    """
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


def configure_logging(log_dir):
    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    pdf_logger = logging.getLogger('pdf_logger')
    pdf_logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=os.path.join(log_dir, log_filename))
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    pdf_logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(LOG_LEVEL)
    sh.setFormatter(formatter)
    pdf_logger.addHandler(sh)


def ensure_exports_folder_exists(export_dir):
    """
    check for export subdirectory
    create it if it doesn't exist
    """
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)


def write_pdf(export_dir, pdf_doc, filename):
    """
    Parameters:  pdf_doc:  String representation of pdf document
                 filename: Desired name of file on disk
    Returns:     None
    """
    file_path = os.path.join(export_dir, filename + '.pdf')
    if os.path.isfile(file_path):
        logger.info('Overwriting existing PDF report at ' + file_path)
    try:
        with open(file_path, 'w') as pdf_file:
            pdf_file.write(pdf_doc)
    except Exception as ex:
        log_exception(ex, "Exception while writing" + file_path + " to file")


def set_last_successful(date_modified):
    with open('last_successful.txt', 'w') as last_modified_file:
        last_modified_file.write(date_modified)


def get_last_successful():
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
            if 'responses'in item.keys():
                if 'text' in item['responses'].keys() and item['responses']['text'].strip() != "":
                    return item['responses']['text']


def get_filename_item_id(config_settings):
    try:
        filename_item_id = config_settings['export_options']['filename']
        if filename_item_id is not None:
            return filename_item_id
        else:
            return None
    except Exception as ex:
        log_exception(ex, "Exception retrieving filename_item_id from " + config_filename)
        return None


def main(config_filename):
    sc_client = sp.safetyculture()

    config_settings = yaml.safe_load(open(config_filename))
    export_path = get_export_path(config_settings)
    timezone = get_timezone(config_settings)
    export_profiles = get_export_profile_mapping(config_settings)
    filename_item_id = get_filename_item_id(config_settings)

    if export_path is not None:
        ensure_exports_folder_exists(export_path)
    else:
        logger.info('No valid export path from ' + config_filename + ', defaulting to /exports')
        export_path = os.path.join(os.getcwd(), 'exports')
        ensure_exports_folder_exists(export_path)

    last_successful = get_last_successful()
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

            pdf_doc = sc_client.get_pdf(audit_id, timezone, export_profile_id)
            write_pdf(export_path, pdf_doc, export_filename)
            set_last_successful(audit['modified_at'])


log_dir = os.path.join(os.getcwd(), 'log')
ensure_log_folder_exists(log_dir)
configure_logging(log_dir)
logger = logging.getLogger('pdf_logger')

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='config file to use, defaults to pdf_config.yaml')
args = parser.parse_args()
if args.config is not None:
    config_filename = args.config
    if os.path.isfile(config_filename):
        logger.debug(config_filename + ' passed as config argument')
    else:
        config_filename = DEFAULT_CONFIG_FILE
        logger.info('config filename invalid, defaulting to' + DEFAULT_CONFIG_FILE)
else:
    config_filename = DEFAULT_CONFIG_FILE

main(config_filename)
