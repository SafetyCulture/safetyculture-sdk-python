import SafetyPy as sp
import yaml
import os


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
        print ex
        return None

def validate_export_path(export_dir):
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
    #logger = logging.getLogger('sp_logger')
    if os.path.exists(scClient.log_dir + 'lastSuccessful.txt'):
        with open (scClient.log_dir + 'lastSuccessful.txt', 'r+') as lastRun:
            lastSuccessful = lastRun.readlines()[0]
    else:
        lastSuccessful = '2000-01-01T00:00:00.000Z'
        with open (scClient.log_dir + 'lastSuccessful.txt', 'w') as lastRun:
            lastRun.write(lastSuccessful)
    #    logger.warning('lastSuccessful.txt NOT FOUND, creating file with default date')

    return lastSuccessful

scClient = sp.sc_client()

export_path = get_export_path()
if export_path:
    validate_export_path(export_path)
else:
    print "No valid export path from config, defaulting to /exports"
    validate_export_path(os.getcwd() + "/exports")

lastSuccessful = get_last_successful()
results = scClient.discover_audits(modified_after = lastSuccessful)

print results['total']

for audit in results['audits']:
    audit_id = audit['audit_id']
    print audit_id
    pdf_doc = scClient.get_pdf(audit_id)
    write_pdf(export_path, pdf_doc, audit_id)
    set_last_successful(audit['modified_at'])
