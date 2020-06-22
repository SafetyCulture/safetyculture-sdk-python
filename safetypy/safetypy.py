# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016
# pylint: disable=E1101

import collections
import json
import logging
import os
import re
import sys
import time
import errno
from builtins import input
from datetime import datetime
import requests
from getpass import getpass

DEFAULT_EXPORT_FORMAT = 'PDF'
GUID_PATTERN = '[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$'
HTTP_USER_AGENT_ID = 'safetyculture-python-sdk'


def get_user_api_token(logger):
    """
    Generate iAuditor API Token
    :param logger:  the logger
    :return:        API Token if authenticated else None
    """
    username = input("iAuditor username: ")
    password = getpass()
    generate_token_url = "https://api.safetyculture.io/auth"
    payload = "username=" + username + "&password=" + password + "&grant_type=password"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
    }
    response = requests.request("POST", generate_token_url, data=payload, headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()['access_token']
    else:
        logger.error('An error occurred calling ' + generate_token_url + ': ' + str(response.json()))
        return None


class SafetyCulture:
    def __init__(self, api_token):
        self.current_dir = os.getcwd()
        self.log_dir = self.current_dir + '/log/'
        self.api_url = 'https://api.safetyculture.io/'
        self.audit_url = self.api_url + 'audits/'
        self.template_search_url = self.api_url + 'templates/search?field=template_id&field=name'
        self.response_set_url = self.api_url + 'response_sets'
        self.get_my_groups_url = self.api_url + 'share/connections'
        self.all_groups_url = self.api_url + 'groups'
        self.add_users_url = self.api_url + 'users'
        
        self.create_directory_if_not_exists(self.log_dir)
        self.configure_logging()
        logger = logging.getLogger('sp_logger')
        try:
            token_is_valid = re.match('^[a-f0-9]{64}$', api_token)
            if token_is_valid:
                self.api_token = api_token
            else:
                logger.error('API token failed to match expected pattern')
                self.api_token = None
        except Exception as ex:
            self.log_critical_error(ex, 'API token is missing or invalid. Exiting.')
            exit()
        if self.api_token:
            self.custom_http_headers = {
                'User-Agent': HTTP_USER_AGENT_ID,
                'Authorization': 'Bearer ' + self.api_token
            }
        else:
            logger.error('No valid API token parsed! Exiting.')
            sys.exit(1)

    def authenticated_request_get(self, url):
        return requests.get(url, headers=self.custom_http_headers)

    def authenticated_request_post(self, url, data):
        self.custom_http_headers['content-type'] = 'application/json'
        response = requests.post(url, data, headers=self.custom_http_headers)
        del self.custom_http_headers['content-type']
        return response

    def authenticated_request_put(self, url, data):
        self.custom_http_headers['content-type'] = 'application/json'
        response = requests.put(url, data, headers=self.custom_http_headers)
        del self.custom_http_headers['content-type']
        return response

    def authenticated_request_delete(self, url):
        return requests.delete(url, headers=self.custom_http_headers)

    @staticmethod
    def parse_json(json_to_parse):
        """
        Parse JSON string to OrderedDict and return
        :param json_to_parse:  string representation of JSON
        :return:               OrderedDict representation of JSON
        """
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(json_to_parse.decode('utf-8'))

    @staticmethod
    def log_critical_error(ex, message):
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

    def get_preference_ids(self, template_id=None):
        """
        Query API for all preference IDs if no parameters are passed, else restrict to template_id passed
        :param template_id: template_id to obtain export preferences for
        :return:            JSON object containing list of preference objects
        """
        preference_search_url = self.api_url + 'preferences/search'
        if template_id is not None:
            preference_search_url += '?template_id=' + template_id
        response = self.authenticated_request_get(preference_search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        return result

    def get_export_job_id(self, audit_id, preference_id=None, export_format=DEFAULT_EXPORT_FORMAT):
        """
        Request export job ID from API and return it

        :param audit_id:           audit_id to retrieve export_job_id for
        :param preference_id:      preference to apply to exports
        :param export_format:      desired format of exported document
        :return:                   export job ID obtained from API
        """
        export_url = self.audit_url + audit_id + '/report'
        if export_format == 'docx': # convert old command line format 
            export_format = 'WORD' 
        export_data = {'format': export_format.upper()}

        if preference_id is not None:
            preference_id_pattern = '^template_[a-fA-F0-9]{32}:' + GUID_PATTERN
            preference_id_is_valid = re.match(preference_id_pattern, preference_id)
            if preference_id_is_valid:
                export_data['preference_id'] = preference_id.split(':')[1]
            else:
                self.log_critical_error(ValueError,
                                        'preference_id {0} does not match expected pattern'.format(
                                            preference_id))

        response = self.authenticated_request_post(export_url, data=json.dumps(export_data))
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
            poll_url = self.audit_url + audit_id + '/report/' + export_job_id
            export_attempts = 1
            poll_status = self.authenticated_request_get(poll_url)
            status = poll_status.json()
            logger = logging.getLogger('sp_logger')
            if 'status' in status.keys():
                if status['status'] == 'IN_PROGRESS':
                    logger.info(str(status['status']) + ' : ' + audit_id)
                    time.sleep(delay_in_seconds)
                    return self.poll_for_export(audit_id, export_job_id)

                elif status['status'] == 'SUCCESS':
                    logger.info(str(status['status']) + ' : ' + audit_id)
                    return status['url']

                else:
                    if export_attempts < 2:
                        export_attempts += 1
                        logger.info('attempt # {0} exporting report for: ' + audit_id.format(str(export_attempts)))
                        retry_id = self.get_export_job_id(audit_id)
                        return self.poll_for_export(audit_id, retry_id['messageId'])
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

    def get_export(self, audit_id, preference_id=None, export_format=DEFAULT_EXPORT_FORMAT):
        """
        Obtain exported document from API and return string representation of it

        :param audit_id:           audit_id of export to obtain
        :param preference_id:  ID of preference to apply to exports
        :param export_format:      desired format of exported document
        :return:                   String representation of exported document
        """
        export_job_id = self.get_export_job_id(audit_id, preference_id, export_format)['messageId']
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
        if response.status_code == requests.codes.ok:
            return response
        else:
            self.log_http_status(response.status_code, "on GET for media {0}".format(response.text))
            return None

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

    def get_audit_actions(self, date_modified, offset=0, page_length=100):
        """
        Get all actions created after a specified date. If the number of actions found is more than 100, this function will
        page until it has collected all actions

        :param date_modified:   ISO formatted date/time string. Only actions created after this date are are returned.
        :param offset:          The index to start retrieving actions from
        :param page_length:     How many actions to fetch for each page of action results
        :return:                Array of action objects
        """
        logger = logging.getLogger('sp_logger')
        actions_url = self.api_url + 'actions/search'
        response = self.authenticated_request_post(
            actions_url,
            data=json.dumps({
                "modified_at": {"from": str(date_modified)},
                "offset": offset,
                "status": [0, 10, 50, 60]
            })
        )
        result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
        self.log_http_status(response.status_code, 'GET actions')
        if result is None or None in [result.get('count'), result.get('offset'), result.get('total'), result.get('actions')]:
            return None
        return self.get_page_of_actions(logger, date_modified, result, offset, page_length)

    def get_page_of_actions(self, logger, date_modified, previous_page, offset=0, page_length=100):
        """
        Returns a page of action search results

        :param logger: the logger
        :param date_modified: fetch from that date onwards
        :param previous_page: a page of action search results
        :param offset: the index to start retrieving actions from
        :param page_length: the number of actions to return on the search page (max 100)
        :return: Array of action objects
        """
        if previous_page['count'] + previous_page['offset'] < previous_page['total']:
            logger.info('Paging Actions. Offset: ' + str(offset + page_length) + '. Total: ' + str(previous_page['total']))
            next_page = self.get_audit_actions(date_modified, offset + page_length)
            if next_page is None:
                return None
            return next_page + previous_page['actions']
        elif previous_page['count'] + previous_page['offset'] == previous_page['total']:
            return previous_page['actions']

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

    def create_response_set(self, name, responses):
        """
        Create new response_set
        :param payload:  Name and responses of response_set to create
        :return:
        """
        payload = json.dumps({'name': name, 'responses': responses})
        response = self.authenticated_request_post(self.response_set_url, payload)
        log_message = 'on POST for new response_set: {0}'.format(name)
        self.log_http_status(response.status_code, log_message)

    def get_response_sets(self):
        """
        GET and return all response_sets
        :return: response_sets accessible to user
        """
        response = self.authenticated_request_get(self.response_set_url)
        result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
        log_message = 'on GET for response_sets'
        self.log_http_status(response.status_code, log_message)
        return result

    def get_response_set(self, responseset_id):
        """
        GET individual response_set by id
        :param responseset_id:  responseset_id of response_set to GET
        :return: response_set
        """
        response = self.authenticated_request_get('{0}/{1}'.format(self.response_set_url, responseset_id))
        result = self.parse_json(response.content) if response.status_code == requests.codes.ok else None
        log_message = 'on GET for {0}'.format(responseset_id)
        self.log_http_status(response.status_code, log_message)
        return result

    def create_response(self, responseset_id, response):
        """
        Create response in existing response_set
        :param responseset_id: id of response_set to add response to
        :param response:       response to add
        :return:               None
        """
        url = '{0}/{1}/responses'.format(self.response_set_url, responseset_id)
        response = self.authenticated_request_post(url, json.dumps(response))
        log_message = 'on POST for new response to: {0}'.format(responseset_id)
        self.log_http_status(response.status_code, log_message)

    def delete_response(self, responseset_id, response_id):
        """
        DELETE individual response by id
        :param responseset_id: responseset_id of response_set containing response to be deleted
        :param response_id:    id of response to be deleted
        :return:               None
        """
        url = '{0}/{1}/responses/{2}'.format(self.response_set_url, responseset_id, response_id)
        response = self.authenticated_request_delete(url)
        log_message = 'on DELETE for response_set: {0}'.format(responseset_id)
        self.log_http_status(response.status_code, log_message)

    def get_my_org(self):
        """
        GET the organisation ID of the requesting user
        :return: The organisation ID of the user
        """
        response = self.authenticated_request_get(self.get_my_groups_url)
        log_message = 'on GET for organisations and groups of requesting user'
        self.log_http_status(response.status_code, log_message)
        my_groups_and_orgs = json.loads(response.content)
        org_id = [group['id'] for group in my_groups_and_orgs['groups'] if group['type'] == "organisation"][0]
        return org_id

    def get_all_groups_in_org(self):
        """
        GET all the groups in the requesting user's organisation
        :return: all the groups of the organisation
        """
        response = self.authenticated_request_get(self.all_groups_url)
        log_message = 'on GET for all groups of organisation'
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    def get_users_of_group(self, group_id):
        """
        GET all the users of the organisations or group
        :param group_id: ID of organisation or group
        :return: array of users
        """
        url = '{0}/{1}/users'.format(self.all_groups_url, group_id)
        response = self.authenticated_request_get(url)
        log_message = 'on GET for users of group: {0}'.format(group_id)
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def add_user_to_org(self, user_data):
        """
        POST adds a user to organisation
        :param user_data: data of the user to be added
        :return: userID of the user created in the organisation
        """
        url = self.add_users_url
        response = self.authenticated_request_post(url, json.dumps(user_data))
        log_message = 'on POST for adding a user to organisation'
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def add_user_to_group(self, group_id, user_data):
        """
        POST adds a user to organisation
        :param user_data: contains user ID of user to be added
        :return: userID of the user created in the organisation
        """
        url = '{0}/{1}/users'.format(self.all_groups_url, group_id)
        response = self.authenticated_request_post(url, json.dumps(user_data))
        log_message = 'on POST for adding a user to group'
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def update_user(self, user_id, user_data):
        """
        PUT updates user details such as user status(active/inactive)
        :param user_id: The ID of the user to update
        :return:  None
        """
        url = '{0}/{1}'.format(self.add_users_url, user_id)
        response = self.authenticated_request_put(url, json.dumps(user_data))
        log_message = 'on PUT for updating a user'
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    def remove_user(self, role_id, user_id):
        """
        Removes a user from an group/organisation
        :param role_id: The ID of the group or organisation
        :param user_id: The ID of the user to remove
        :return: {ok: true} on successful deletion
        """
        url = '{0}/{1}/users/{2}'.format(self.all_groups_url, role_id, user_id)
        response = self.authenticated_request_delete(url)
        log_message = 'on DELETE for user from group'
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    @staticmethod
    def log_http_status(status_code, message):
        """
        Write http status code and descriptive message to log

        :param status_code:  http status code to log
        :param message:      to describe where the status code was obtained
        """
        logger = logging.getLogger('sp_logger')
        status_description = requests.status_codes._codes[status_code][0]
        log_string = str(status_code) + ' [' + status_description + '] status received ' + message
        logger.info(log_string) if status_code == requests.codes.ok else logger.error(log_string)
