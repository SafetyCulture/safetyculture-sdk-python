#Author: Larry Landon
#Copyright: SafetyCulture, Ltd.

import requests
import json
from datetime import datetime
import os
import time
import logging
import collections
import yaml
import re
import sys

class sc_client:

    def __init__(self):
        self.current_dir = os.getcwd()
        self.log_dir = self.current_dir + '/log/'

        self.api_url = 'https://api.safetyculture.io/'
        self.audit_url = self.api_url + 'audits/'
        self.template_search_url = self.api_url + 'templates/search?field=template_id&field=name'

        self.validate_log_directory(self.log_dir)
        self.configure_logging()
        self.api_key = self.parse_api_key()

        if self.api_key:
            self.auth_header = {'Authorization': 'Bearer ' + self.api_key }
        else:
            print "No valid API key parsed!"
            print "Exiting!"
            sys.exit()

    def parse_api_key(self):
        logger = logging.getLogger('sp_logger')
        with open('config.yaml', 'r') as f:
            config = yaml.load(f)

        try:
            api_key = config['API']['key']
            key_is_valid = re.match('[a-z0-9]{64}', api_key)
            if key_is_valid:
                logger.debug('API key matched pattern')
                return api_key
            else:
                logger.error('API key: ' + api_key + ' failed pattern match')
                return None
        except Exception as ex:
                logger.exception('')
                return None


    def configure_logging(self):
        log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
        sp_logger = logging.getLogger('sp_logger')
        sp_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

        fh = logging.FileHandler(filename=self.log_dir + log_filename)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        sp_logger.addHandler(fh)

    def validate_log_directory(self, log_dir):
        '''
        check for log subdirectory (current directory + '/log/')
        create it if it doesn't exist
        '''
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)

    #discover_audits takes no arguments, and returns a list of all audits visible to the API token used in auth_header
    def discover_audits(self, template_id = None, modified_after = None, completed = False):
        '''
        Parameters: (optional) template_id     Restrict discovery to this template_id
                    (optional) modified_after  Restrict discovery to audits modified after this value

        Passing no parameters, it will return all audits with no restrictions
        '''

        logger = logging.getLogger('sp_logger')


        if modified_after == None:
            lastModified = '2000-01-01T00:00:00.000Z'
        else:
            lastModified = modified_after

        search_url = self.audit_url + 'search?field=audit_id&field=modified_at&modified_after='+lastModified
        log_string = '\nInitiating audit_discovery with the parameters: ' + '\n'
        log_string += 'template_id    = ' + str(template_id) + '\n'
        log_string += 'modified_after = '+ str(lastModified) + '\n'
        log_string += 'completed      = ' + str(completed) + '\n'
        logger.info(log_string)

        if template_id:
            search_url += '&template=' + template_id

        if completed:
            search_url += '&completed=true'

        results = requests.get(search_url, headers = self.auth_header)
        status_code = results.status_code

        if status_code / 100 == 2:
            response = results.json()
            logger.info(str(status_code) + ' status received on audit_discovery: ' + str(response['total']) + ' discovered')
            return response
        else:
            logger.error(str(status_code) + ' status received on audit_discovery using ' + search_url)
            return None

    def discover_templates(self, modified_after = None, modified_before = None):
        '''
        Parameters: (optional) modified_after   Restrict discovery to templates modified after this value
                    (optional) modified_before  Restrict discovery to templates modified before this value

        Passing no parameters, it will discover templates with no restrictions
        '''
        logger = logging.getLogger('sp_logger')

        search_url = self.template_search_url
        if modified_before != None:
            search_url += '&modified_before=' + modified_before
        if modified_after != None:
            search_url += '&modified_after=' + modified_after

        template_ids = requests.get(search_url, headers = self.auth_header)

        logger.info(str(template_ids.status_code) + ' received on template discovery')

        return template_ids.json()


    def get_export_id(self, audit_id):
        '''
        Parameters : audit_id   Retrieves export_id for given audit_id
        Returns:     export ID from API
        '''
        export_url = self.audit_url + audit_id + '/export?format=pdf&timezone=Australia/Brisbane'
        export_response =  requests.post(export_url, headers = self.auth_header)
        return export_response.json()


    def poll_for_export(self, audit_id, export_id):
        '''
        Parameters:  audit_id  audit_id of the export to poll for
                     export_id export_id of the export to poll for
        Return:      href for export download
        '''
        delay = .5
        poll_url = self.audit_url + audit_id + '/exports/' + export_id
        poll_status = requests.get(poll_url, headers = self.auth_header)
        status = poll_status.json()

        if 'status' in status.keys():
            if (status['status'] == 'IN PROGRESS'):
                print status['status'] + ' : ' + audit_id
                time.sleep(delay)
                return self.poll_for_export(audit_id, export_id)

            elif status['status'] == 'SUCCESS':
                print status['status'] + ' : ' + audit_id
                return status['href']

        else:
            #TODO:
            #  Consider adding limitations to how many times it will retry a given audit
            #   That way, if for some reason an audit will *always* fail, it won't get stuck in a loop forever.
            print 'retrying export process for: ' + audit_id
            retry_id = self.get_export_id(audit_id)
            return self.poll_for_export(audit_id, retry_id['id'])

    def download_pdf(self, pdf_href):
        '''
        Parameters:  pdf_href:  href obtained from poll_for_export for export doc to download
        Returns:     String representation of pdf docuemnt
        '''

        logger = logging.getLogger('sp_logger')

        doc_file = requests.get(pdf_href, headers = self.auth_header)

        logger.info(str(doc_file.status_code) + ' status received on GET for href: ' + pdf_href)

        return doc_file.content

    def write_json(self, doc_json, filename):
        print 'writing ' + filename + ' to file!'
        with open (self.export_dir + filename + '.json', 'w') as json_file:
            json.dump(doc_json, json_file, indent=4)


    def get_pdf(self, audit_id):
        '''
        Parameters: audit_id of pdf to obtain
        Returns: string representation of pdf document
        '''
        export_id = self.get_export_id(audit_id)['id']
        pdf_href = self.poll_for_export(audit_id, export_id)
        pdf_doc = self.download_pdf(pdf_href)
        return pdf_doc

    def get_audit(self, audit_id):
        '''
        Parameters: audit_id of document to fetch
        Returns:    JSON audit object
        '''

        logger = logging.getLogger('sp_logger')

        get_doc = requests.get(self.audit_url + audit_id, headers = self.auth_header)

        if get_doc.status_code == 200:
            logger.info(str(get_doc.status_code) + ' status received on GET for ' + audit_id)
            doc_json = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(get_doc.content)
            return doc_json
        else:
            logger.error(str(get_doc.status_code) + ' status received on GET for ' + audit_id)
