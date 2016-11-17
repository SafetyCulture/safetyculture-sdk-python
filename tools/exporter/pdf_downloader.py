import logging
import os
import sys
from datetime import datetime

import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from SafetyPy import SafetyPy as sp


def log_exception(ex, message):
    logger = logging.getLogger('pdf_logger')
    logger.critical(message)
    logger.critical(ex)


def get_export_path():
    with open('pdf_config.yaml', 'r') as config_file:
        config = yaml.load(config_file)
    try:
        export_path = config['export_options']['export_path']
        if export_path:
            return os.path.join(os.path.dirname(__file__), export_path)
        else:
            return None
    except Exception as ex:
        log_exception(ex, 'Exception getting export path from pdf_config.yaml')
        return None


def ensure_log_folder_exists(log_dir):
    '''
    check for log subdirectory (current directory + '/log/')
    create it if it doesn't exist
    '''
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


def configure_logging(log_dir):
    LOG_LEVEL = logging.DEBUG

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
    '''
    check for export subdirectory
    create it if it doesn't exist
    '''
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)


def write_pdf(export_dir, pdf_doc, filename):
    '''
    Parameters:  pdf_doc:  String representation of pdf document
                 filename: Desired name of file on disk
    Returns:     None
    '''
    logger = logging.getLogger('pdf_logger')
    file_path = os.path.join(export_dir, filename + '.pdf')
    if os.path.isfile(file_path):
        logger.info('Overwriting existing PDF report at ' + file_path)
    try:
        with open(file_path, 'w') as pdf_file:
            pdf_file.write(pdf_doc)
    except Exception as ex:
        log_exception(ex, "Exception while writing" + file_path + " to file")


def set_last_successful(date_modified):
    with open(os.path.join(sc_client.log_dir, 'last_successful.txt'), 'w') as last_modified_file:
        last_modified_file.write(date_modified)


def get_last_successful():
    logger = logging.getLogger('sp_logger')
    if os.path.exists(os.path.join(sc_client.log_dir, 'last_successful.txt')):
        with open(os.path.join(sc_client.log_dir, 'last_successful.txt'), 'r+') as last_run:
            last_successful = last_run.readlines()[0]
    else:
        beginning_of_time = '2000-01-01T00:00:00.000Z'
        last_successful = beginning_of_time
        with open(os.path.join(sc_client.log_dir, 'last_successful.txt'), 'w') as last_run:
            last_run.write(last_successful)
        logger.info('Searching for audits since beginning of time')

    return last_successful


sc_client = sp.safetyculture()

log_dir = os.path.join(os.getcwd(), 'log')

ensure_log_folder_exists(log_dir)
configure_logging(log_dir)
logger = logging.getLogger('pdf_logger')

export_path = get_export_path()
if export_path is not None:
    ensure_exports_folder_exists(export_path)
else:
    logger.info('No valid export path from config, defaulting to /exports')
    export_path = os.path.join(os.getcwd(), 'exports')
    ensure_exports_folder_exists(export_path)

last_successful = get_last_successful()
results = sc_client.discover_audits(modified_after=last_successful)

logger.info(str(results['total']) + ' audits discovered')

for audit in results['audits']:
    audit_id = audit['audit_id']
    logger.info('downloading ' + audit_id)
    pdf_doc = sc_client.get_pdf(audit_id)

    write_pdf(export_path, pdf_doc, audit_id)
    set_last_successful(audit['modified_at'])
