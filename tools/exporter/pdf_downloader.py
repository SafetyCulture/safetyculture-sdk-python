import logging
import os

import yaml

import SafetyPy as sp


def log_exception(ex, message):
    logger = logging.getLogger('pdf_logger')
    logger.critical(message)
    logger.critical(ex)

def get_export_path():
    current_dir = os.getcwd()
    with open('pdf_config.yaml', 'r') as config_file:
        config = yaml.load(config_file)
    try:
        export_path = config['export_options']['export_path']
        if export_path:
            return current_dir + export_path
        else:
            return None
    except Exception as ex:
        log_exception(ex, 'Exception getting export path from pdf_config.yaml')
        return None


def configure_logging(self):
    LOG_LEVEL = logging.DEBUG

    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    pdf_logger = logging.getLogger('pdf_logger')
    pdf_logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=self.log_dir + log_filename)
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
    with open (export_dir + '/' + filename + '.pdf', 'w') as pdf_file:
        pdf_file.write(pdf_doc)

def set_last_successful(dateModified):
    with open(scClient.log_dir + 'lastSuccessful.txt', 'w') as lastModifiedFile:
        lastModifiedFile.write(dateModified)

def get_last_successful():
    logger = logging.getLogger('sp_logger')
    if os.path.exists(scClient.log_dir + 'lastSuccessful.txt'):
        with open (scClient.log_dir + 'lastSuccessful.txt', 'r+') as lastRun:
            lastSuccessful = lastRun.readlines()[0]
    else:
        lastSuccessful = '2000-01-01T00:00:00.000Z'
        with open (scClient.log_dir + 'lastSuccessful.txt', 'w') as lastRun:
            lastRun.write(lastSuccessful)
        logger.warning('lastSuccessful.txt NOT FOUND, creating file with default date')

    return lastSuccessful

scClient = sp.sc_client()
logger = logging.getLogger('pdf_logger')

export_path = get_export_path()
if export_path:
    ensure_exports_folder_exists(export_path)
else:
    logger.info('No valid export path from config, defaulting to /exports')
    ensure_exports_folder_exists(os.getcwd() + '/exports')

lastSuccessful = get_last_successful()
results = scClient.discover_audits(modified_after = lastSuccessful)

logger.info(str(results['total']) + ' audits discovered')

for audit in results['audits']:
    audit_id = audit['audit_id']
    logger.info('processing ' + audit_id)
    pdf_doc = scClient.get_pdf(audit_id)
    write_pdf(export_path, pdf_doc, audit_id)
    set_last_successful(audit['modified_at'])
