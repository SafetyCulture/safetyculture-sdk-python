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
import errno
from datetime import datetime
import requests

DEFAULT_EXPORT_TIMEZONE = 'Etc/UTC'
DEFAULT_EXPORT_FORMAT = 'pdf'
GUID_PATTERN = '[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$'
HTTP_USER_AGENT_ID = 'safetyculture-python-sdk'


class SafetyCulture:
    def __init__(self, api_token):

        self.current_dir = os.getcwd()
        self.log_dir = self.current_dir + '/log/'

        self.api_url = 'https://api.safetyculture.io/'
        self.audit_url = self.api_url + 'audits/'
        self.template_search_url = self.api_url + 'templates/search?field=template_id&field=name'

        self.create_directory_if_not_exists(self.log_dir)
        self.configure_logging()
        logger = logging.getLogger('sp_logger')

        token_is_valid = re.match('^[a-f0-9]{64}$', api_token)

        if token_is_valid:
            self.api_token = api_token
        else:
            logger.error('API token failed to match expected pattern')
            self.api_token = None

        if self.api_token:
            self.custom_http_headers = {
                'User-Agent': HTTP_USER_AGENT_ID,
                'Authorization': 'Bearer ' + self.api_token
            }
        else:
            logger.error('No valid API token parsed! Exiting!')
            sys.exit(1)

    def authenticated_request_get(self, url):
        return requests.get(url, headers=self.custom_http_headers)

    def authenticated_request_post(self, url, data):
        return requests.post(url, data, headers=self.custom_http_headers)

    def parse_json(self, json_to_parse):
        """
        Parse JSON string to OrderedDict and return

        :param json_to_parse:  string representation of JSON
        :return:               OrderedDict representation of JSON
        """
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(json_to_parse)

    def log_critical_error(self, ex, message):
        """
        Write exception and description message to log

        :param ex:       Exception instance to log
        :param message:  Descriptive message to describe exception
        """
        logger = logging.getLogger('sp_logger')

        if logger is not None:
            logger.critical(message)
            logger.critical(ex)

    def configure_logging(self):
        """
        Configure logging to log to std output as well as to log file
        """
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

    def create_directory_if_not_exists(self, path):
        """
        Creates 'path' if it does not exist

        If creation fails, an exception will be thrown

        :param path:    the path to ensure it exists
        """
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                self.log_critical_error(ex, 'An error happened trying to create ' + path)
                raise

    def discover_audits(self, template_id=None, modified_after=None, completed=True):
        """
        Return IDs of all completed audits if no parameters are passed, otherwise restrict search
        based on parameter values
        :param template_id:     Restrict discovery to this template_id
        :param modified_after:  Restrict discovery to audits modified after this UTC timestamp
        :param completed:       Restrict discovery to audits marked as completed, default to True
        :return:                JSON object containing IDs of all audits returned by API
        """

        logger = logging.getLogger('sp_logger')

        last_modified = modified_after if modified_after is not None else '2000-01-01T00:00:00.000Z'

        search_url = self.audit_url + 'search?field=audit_id&field=modified_at&order=asc&modified_after=' \
            + last_modified
        log_string = '\nInitiating audit_discovery with the parameters: ' + '\n'
        log_string += 'template_id    = ' + str(template_id) + '\n'
        log_string += 'modified_after = ' + str(last_modified) + '\n'
        log_string += 'completed      = ' + str(completed) + '\n'
        logger.info(log_string)

        if template_id is not None:
            search_url += '&template=' + template_id
        if completed is not False:
            search_url += '&completed=true'

        response = self.authenticated_request_get(search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        number_discovered = str(result['total']) if result is not None else '0'
        log_message = 'on audit_discovery: ' + number_discovered + ' discovered using ' + search_url

        self.log_http_status(response.status_code, log_message)
        return result

    def discover_templates(self, modified_after=None, modified_before=None):
        """
        Query API for all template IDs if no parameters are passed, otherwise restrict search based on parameters

        :param modified_after:   Restrict discovery to templates modified after this UTC timestamp
        :param modified_before:  Restrict discovery to templates modified before this UTC timestamp
        :return:                 JSON object containing IDs of all templates returned by API
        """
        search_url = self.template_search_url
        if modified_before is not None:
            search_url += '&modified_before=' + modified_before
        if modified_after is not None:
            search_url += '&modified_after=' + modified_after

        response = self.authenticated_request_get(search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        log_message = 'on template discovery using ' + search_url

        self.log_http_status(response.status_code, log_message)
        return result

    def get_export_profile_ids(self, template_id=None):
        """
        Query API for all export profile IDs if no parameters are passed, else restrict to template_id passed
        :param template_id: template_id to obtain export profiles for
        :return:            JSON object containing template name: export profile pairs if no errors, or None
        """
        profile_search_url = self.api_url + 'export_profiles/search'
        if template_id is not None:
            profile_search_url += '?template=' + template_id
        response = self.authenticated_request_get(profile_search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        return result

    def get_export_profile(self, export_profile_id):
        """
        Query API for export profile corresponding to passed profile_id

        :param export_profile_id:  Export profile ID of the profile to retrieve
        :return:                   Export profile in JSON format
        """
        profile_id_pattern = '^template_[a-fA-F0-9]{32}:' + GUID_PATTERN
        profile_id_is_valid = re.match(profile_id_pattern, export_profile_id)

        if profile_id_is_valid:
            export_profile_url = self.api_url + '/export_profiles/' + export_profile_id
            response = self.authenticated_request_get(export_profile_url)
            result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
            log_message = 'on export profile retrieval of ' + export_profile_id

            self.log_http_status(response.status_code, log_message)
            return result
        else:
            self.log_critical_error(ValueError,
                                    'export_profile_id {0} does not match expected pattern'.format(export_profile_id))
            return None

    def get_export_job_id(self, audit_id, timezone=DEFAULT_EXPORT_TIMEZONE, export_profile_id=None,
                          export_format=DEFAULT_EXPORT_FORMAT):
        """
        Request export job ID from API and return it

        :param audit_id:           audit_id to retrieve export_job_id for
        :param timezone:           timezone to apply to exports
        :param export_profile_id:  export profile to apply to exports
        :param export_format:      desired format of exported document
        :return:                   export job ID obtained from API
        """
        export_url = self.audit_url + audit_id + '/export?format=' + export_format + '&timezone=' + timezone

        if export_profile_id is not None:
            profile_id_pattern = '^template_[a-fA-F0-9]{32}:' + GUID_PATTERN
            profile_id_is_valid = re.match(profile_id_pattern, export_profile_id)
            if profile_id_is_valid:
                export_url += '&export_profile=' + export_profile_id
            else:
                self.log_critical_error(ValueError,
                                        'export_profile_id {0} does not match expected pattern'.format(
                                            export_profile_id))

        response = self.authenticated_request_post(export_url, data=None)
        result = response.json() if response.status_code == requests.codes.ok else None
        log_message = 'on request to ' + export_url

        self.log_http_status(response.status_code, log_message)
        return result

    def poll_for_export(self, audit_id, export_job_id):
        """
        Poll API for given export job until job is complete or excessive failed attempts occur
        :param audit_id:       audit_id of the export to poll for
        :param export_job_id:  export_job_id of the export to poll for
        :return:               href for export download
        """
        job_id_pattern = '^' + GUID_PATTERN
        job_id_is_valid = re.match(job_id_pattern, export_job_id)

        if job_id_is_valid:
            delay_in_seconds = 5
            poll_url = self.audit_url + audit_id + '/exports/' + export_job_id
            export_attempts = 1
            poll_status = self.authenticated_request_get(poll_url)
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
                        logger.info('attempt # {0} exporting report for: ' + audit_id.format(str(export_attempts)))
                        retry_id = self.get_export_job_id(audit_id)
                        return self.poll_for_export(audit_id, retry_id['id'])
                    else:
                        logger.error('export for ' + audit_id + ' failed {0} times - skipping'.format(export_attempts))
            else:
                logger.critical('Unexpected response from API: {0}'.format(status))

        else:
            self.log_critical_error(ValueError,
                                    'export_job_id {0} does not match expected pattern'.format(export_job_id))

    def download_export(self, export_href):
        """

        :param export_href:  href for export document to download
        :return:             String representation of exported document
        """

        try:
            response = self.authenticated_request_get(export_href)
            result = response.content if response.status_code == requests.codes.ok else None
            log_message = 'on GET for href: ' + export_href

            self.log_http_status(response.status_code, log_message)
            return result

        except Exception as ex:
            self.log_critical_error(ex, 'Exception occurred while attempting download_export({0})'.format(export_href))

    def get_export(self, audit_id, timezone=DEFAULT_EXPORT_TIMEZONE, export_profile_id=None,
                   export_format=DEFAULT_EXPORT_FORMAT):
        """
        Obtain exported document from API and return string representation of it

        :param audit_id:           audit_id of export to obtain
        :param timezone:           timezone to apply to exports
        :param export_profile_id:  ID of export profile to apply to exports
        :param export_format:      desired format of exported document
        :return:                   String representation of exported document
        """
        export_job_id = self.get_export_job_id(audit_id, timezone, export_profile_id, export_format)['id']
        export_href = self.poll_for_export(audit_id, export_job_id)

        export_content = self.download_export(export_href)
        return export_content

    def get_media(self, audit_id, media_id):
        """
        Get media item associated with a specified audit and media ID
        :param audit_id:    audit ID of document that contains media 
        :param media_id:    media ID of image to fetch
        :return:            The Content-Type will be the MIME type associated with the media, 
                            and the body of the response is the media itself.
        """
        url = self.audit_url + audit_id + '/media/' + media_id
        response = requests.get(url, headers=self.custom_http_headers, stream=True)
        return response

    def get_web_report(self, audit_id):
        """
        Generate Web Report link associated with a specified audit
        :param audit_id:   Audit ID
        :return:           Web Report link
        """
        url = self.audit_url + audit_id + '/web_report_link'
        response = self.authenticated_request_get(url)
        result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
        self.log_http_status(response.status_code, 'on GET web report for ' + audit_id)
        if result:
            return result.get('url')
        else:
            return None

    def get_audit(self, audit_id):
        """
        Request JSON representation of a single specified audit and return it

        :param audit_id:  audit_id of document to fetch
        :return:          JSON audit object
        """
        response = self.authenticated_request_get(self.audit_url + audit_id)
        result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
        log_message = 'on GET for ' + audit_id

        self.log_http_status(response.status_code, log_message)
        return result

    def log_http_status(self, status_code, message):
        """
        Write http status code and descriptive message to log

        :param status_code:  http status code to log
        :param message:      to describe where the status code was obtained
        """

        logger = logging.getLogger('sp_logger')
        status_description = requests.status_codes._codes[status_code][0]
        log_string = str(status_code) + ' [' + status_description + '] status received ' + message
        logger.info(log_string) if status_code == requests.codes.ok else logger.error(log_string)
