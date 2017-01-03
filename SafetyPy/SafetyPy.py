# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import collections
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
import requests
import yaml

DEFAULT_EXPORT_TIMEZONE = 'Etc/UTC'
DEFAULT_EXPORT_FORMAT = 'pdf'

class safetyculture:
    def __init__(self):

        self.current_dir = os.getcwd()
        self.log_dir = self.current_dir + '/log/'

        self.api_url = 'https://api.safetyculture.io/'
        self.audit_url = self.api_url + 'audits/'
        self.template_search_url = self.api_url + 'templates/search?field=template_id&field=name'

        self.validate_log_directory(self.log_dir)
        self.configure_logging()
        logger = logging.getLogger('sp_logger')

        module_dir = os.path.dirname(__file__)
        self.config_settings = yaml.safe_load(open(os.path.join(module_dir, "config.yaml")))

        self.api_token = self.parse_api_token(self.config_settings)

        if self.api_token:
            self.auth_header = {'Authorization': 'Bearer ' + self.api_token}
        else:
            logger.error('No valid API token parsed! Exiting!')
            sys.exit()

    def parse_api_token(self, config):
        logger = logging.getLogger('sp_logger')
        try:
            api_token = config['API']['token']
            token_is_valid = re.match('^[a-z0-9]{64}$', api_token)
            if token_is_valid:
                logger.debug('API token matched expected pattern')
                return api_token
            else:
                logger.error('API token failed to match expected')
                return None
        except Exception as ex:
            self.log_exception(ex, 'Exception parsing API token from config.yaml')
            return None

    def log_exception(self, ex, message):
        logger = logging.getLogger('sp_logger')
        logger.critical(message)
        logger.critical(ex)

    def log_http_status(self, status_code, message):
        logger = logging.getLogger('sp_logger')
        status_description = requests.status_codes._codes[status_code][0]
        log_string = str(status_code) + ' [' + status_description + '] status received ' + message
        logger.info(log_string) if status_code == requests.codes.ok else logger.error(log_string)

    def configure_logging(self):
        log_level = logging.DEBUG

        log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
        sp_logger = logging.getLogger('sp_logger')
        sp_logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

        fh = logging.FileHandler(filename=self.log_dir + log_filename)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        sp_logger.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(log_level)
        sh.setFormatter(formatter)
        sp_logger.addHandler(sh)

    def validate_log_directory(self, log_dir):
        """
        check for log subdirectory (current directory + '/log/')
        create it if it doesn't exist
        """
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)

    def discover_audits(self, template_id=None, modified_after=None, completed=False):
        """
        Parameters: (optional) template_id     Restrict discovery to this template_id
                    (optional) modified_after  Restrict discovery to audits modified
                                               after this UTC timestamp
                    (optional) completed       Restrict discovery to audits marked
                                               as completed, default to False
        Passing no parameters, it will return all audits with no restrictions
        """
        logger = logging.getLogger('sp_logger')

        last_modified = modified_after if modified_after is not None else '2000-01-01T00:00:00.000Z'

        search_url = self.audit_url + 'search?field=audit_id&field=modified_at&order=asc&modified_after=' + last_modified
        log_string = '\nInitiating audit_discovery with the parameters: ' + '\n'
        log_string += 'template_id    = ' + str(template_id) + '\n'
        log_string += 'modified_after = ' + str(last_modified) + '\n'
        log_string += 'completed      = ' + str(completed) + '\n'
        logger.info(log_string)

        if template_id is not None:
            search_url += '&template=' + template_id
        if completed is not False:
            search_url += '&completed=true'

        response = requests.get(search_url, headers=self.auth_header)
        result = response.json() if response.status_code == requests.codes.ok else None
        number_discovered = str(result['total']) if result is not None else '0'
        log_message = 'on audit_discovery: ' + number_discovered + ' discovered using ' + search_url

        self.log_http_status(response.status_code, log_message)
        return result

    def discover_templates(self, modified_after=None, modified_before=None):
        """
        Parameters: (optional) modified_after   Restrict discovery to templates modified
                                                after this UTC timestamp
                    (optional) modified_before  Restrict discovery to templates modified
                                                before this UTC timestamp

        Passing no parameters, it will discover templates with no restrictions
        """
        search_url = self.template_search_url
        if modified_before is not None:
            search_url += '&modified_before=' + modified_before
        if modified_after is not None:
            search_url += '&modified_after=' + modified_after

        response = requests.get(search_url, headers=self.auth_header)
        result = response.json() if response.status_code == requests.codes.ok else None
        log_message = 'status received on template discovery using ' + search_url

        self.log_http_status(response.status_code, log_message)
        return result

    def get_export_profile(self, export_profile_id):
        """
        :param export_profile_id:  Export profile ID of the profile to retrieve
        :return:                   Export profile in JSON format
        """
        profile_id_pattern = '^template_[a-fA-F0-9]{32}:[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$'
        profile_id_is_valid = re.match(profile_id_pattern, export_profile_id)

        if profile_id_is_valid:
            export_profile_url = self.api_url + '/export_profiles/' + export_profile_id
            response = requests.get(export_profile_url, headers=self.auth_header)

            if response.status_code == requests.codes.ok:
                result = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(response.content)
            else:
                result = None

            log_message = 'status received on export profile retrieval of ' + export_profile_id
            self.log_http_status(response.status_code, log_message)
            return result
        else:
            self.log_exception(ValueError, 'export_profile_id %s does not match pattern' % export_profile_id)
            return None

    def get_export_job_id(self, audit_id, timezone=DEFAULT_EXPORT_TIMEZONE, export_profile_id=None, export_format=DEFAULT_EXPORT_FORMAT):
        """
        Parameters : audit_id           Retrieves export_job_id for given audit_id
                     timezone           Timezone to apply to exports
                     export_profile_id  Export Profile to apply to exports
        Returns:     export ID from API
        """
        export_url = self.audit_url + audit_id + '/export?format=' + export_format + '&timezone=' + timezone

        if export_profile_id is not None:
            profile_id_pattern = '^template_[a-fA-F0-9]{32}:[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$'
            profile_id_is_valid = re.match(profile_id_pattern, export_profile_id)
            if profile_id_is_valid:
                export_url += '&export_profile=' + export_profile_id
            else:
                self.log_exception(ValueError, 'export_profile_id %s does not match pattern' % export_profile_id)

        response = requests.post(export_url, headers=self.auth_header)
        log_message = 'status received on request to ' + export_url
        result = response.json() if response.status_code == requests.codes.ok else None

        self.log_http_status(response.status_code, log_message)
        return result

    def poll_for_export(self, audit_id, export_job_id):
        """
        Parameters:  audit_id  audit_id of the export to poll for
                     export_job_id of the export to poll for
        Return:      href for export download
        """
        job_id_pattern = '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        job_id_is_valid = re.match(job_id_pattern, export_job_id)

        if job_id_is_valid:
            delay_in_seconds = 5
            poll_url = self.audit_url + audit_id + '/exports/' + export_job_id
            export_attempts = 1
            poll_status = requests.get(poll_url, headers=self.auth_header)
            status = poll_status.json()
            logger = logging.getLogger('sp_logger')
            if 'status' in status.keys():
                if status['status'] == 'IN PROGRESS':
                    logger.info(str(status['status']) + ' : ' + audit_id)
                    time.sleep(delay_in_seconds)
                    return self.poll_for_export(audit_id, export_job_id)

                elif status['status'] == 'SUCCESS':
                    logger.info(str(status['status']) + ' : ' + audit_id)
                    return status['href']
            else:
                if export_attempts < 2:
                    export_attempts += 1
                    logger.info('retrying export process for: ' + audit_id)
                    retry_id = self.get_export_job_id(audit_id)
                    return self.poll_for_export(audit_id, retry_id['id'])
                else:
                    logger.error('export for ' + audit_id + ' failed more than once - skipping')
        else:
            self.log_exception(ValueError, 'export_job_id %s does not match expected pattern' % export_job_id)

    def download_export(self, export_href):
        """
        Parameters:  export_href:  href obtained from poll_for_export for export doc to download
        Returns:     String representation of document
        """
        response = requests.get(export_href, headers=self.auth_header)
        log_message = 'status received on GET for href: ' + export_href
        result = response.content if response.status_code == requests.codes.ok else None

        self.log_http_status(response.status_code, log_message)
        return result

    def get_export(self, audit_id, timezone=DEFAULT_EXPORT_TIMEZONE, export_profile_id=None, export_format=DEFAULT_EXPORT_FORMAT):
        """
        Parameters: audit_id                        audit_id of export to obtain
                    (optional) timezone             timezone to apply to exports
                    (optional) export_profile_id    export profile to apply to exports
        Returns: string representation of export document
        """
        export_job_id = self.get_export_job_id(audit_id, timezone, export_profile_id, export_format)['id']
        export_href = self.poll_for_export(audit_id, export_job_id)
        export_content = self.download_export(export_href)
        return export_content

    def get_audit(self, audit_id):
        """
        Parameters: audit_id of document to fetch
        Returns:    JSON audit object
        """
        response = requests.get(self.audit_url + audit_id, headers=self.auth_header)
        log_message = 'status received on GET for ' + audit_id

        if response.status_code == requests.codes.ok:
            result = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(response.content)
        else:
            result = None

        self.log_http_status(response.status_code, log_message)
        return result
