# -*- coding: utf8 -*-
import argparse
import datetime
import errno
import logging
import os
import re
import sys
import yaml
import json
import csv
import pydash
from pydash import _
from xlrd import open_workbook
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp
from tools.export_users import export_users
from tools.import_grs import import_grs
# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG
actions = {}

def process_desired_state(server_state, desired_state):
    """
    Processes the user provided input file and determines any actions that need to happen because the server state is different than the desired state
    :param server_state: The list of all users and their associated groups in the server
    :param desired_state: The input provided by the user
    :return: None
    """
    group_id =[]
    with open(desired_state) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        next(csvReader, None)
        for email, lastname, firstname, groups in csvReader:
            group_list = []
            if groups != "":
                group_list = groups.split(",")
                group_list = [group.strip(' ') for group in group_list]
            if email not in [user for user in server_state]:
                actions[email] = {'action': 'add', 'groups': group_list, 'user_id':'', 'user_data': {'firstname': firstname, 'lastname': lastname, 'email': email, 'reset_password_required': True} }
            else:
                group_names_server = server_state[email]['groups'][0::2]
                group_names_desired = groups.split(',')
                group_names_desired = [group.strip(' ') for group in group_names_desired]
                group_diff = [i for i in group_names_desired if i not in group_names_server]
                if group_diff != [] and group_diff != ['']:
                    actions[email] = {'action': 'add to group', 'groups': group_diff, 'user_id': server_state[email]['user_id'] }

def process_server_state(server_state, desired_state):
    """
    Determines any actions that need to happen because the server state is different than the desired state
    :param server_state: The list of all users and their associated groups in the server
    :param desired_state: The input provided by the user
    :return: None
    """
    with open(desired_state) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        next(csvReader, None)
        userlist = {}

        for row in csvReader:
            email = row[0]
            userlist[email] = {'groups': row[3]}

        emails = userlist.keys()

        for user, _ in server_state.items():

            if user not in emails:
                actions[user] = {'action': 'deactivate', 'groups': [], 'user_id': server_state[user]['user_id']}
            else:
                group_diff = []
                group_names_server = server_state[user]['groups'][0::2]
                group_names_desired = userlist[user]['groups'].split(',')
                group_names_desired = [group.strip(' ') for group in group_names_desired]
                group_diff = [i for i in group_names_server if i not in group_names_desired]
                if group_diff != [] and group_diff != ['']:
                    actions[user] = {'action': 'remove from group', 'groups': group_diff, 'user_id': server_state[user]['user_id']}

def execute_actions(all_group_details, sc_client):
    """
    Syncs the user base as per the user provided input file
    :param all_group_details: All the group details in the organisation of requesting user
    :param sc_client: Client to access the SafetyCulture methods
    :return: None
    """
    for keys in actions.keys():
        group_list = actions[keys]['groups']
        if actions[keys]['action'] == 'add':
            data = actions[keys]['user_data']
            response = json.loads(sc_client.add_user_to_org(data))
            if response:
                user_id = response['user']['user_id']
                if group_list != []:
                    for group_name in group_list:
                        target_group = _.find(all_group_details['groups'], {'name': group_name})
                        if target_group:
                            data = {'user_id': user_id}
                            sc_client.add_user_to_group(target_group['id'], data)

        if actions[keys]['action'] == 'add to group':
            user_id = actions[keys]['user_id']
            for group_name in group_list:
                target_group = _.find(all_group_details['groups'], {'name': group_name})
                if target_group:
                    sc_client.add_user_to_group(target_group['id'], {'user_id': user_id})

        if actions[keys]['action'] == 'deactivate':
            user_id = actions[keys]['user_id']
            data = {'status': 'inactive'}
            sc_client.update_user(user_id, data)

        if actions[keys]['action'] == 'remove from group':
            user_id = actions[keys]['user_id']
            for group_name in group_list:
                target_group = _.find(all_group_details['groups'], {'name': group_name})
                if target_group:
                    sc_client.remove_user(target_group['id'], user_id)


def sync_users(api_token, input_filepath):
    """
    Load local User data, get system User data, compare and add users to system
    """
    sc_client = sp.SafetyCulture(api_token)
    logger = import_grs.configure_logger()

    # Validating the CSV input first
    dataValidator = open(input_filepath,'r')
    reader= csv.reader(dataValidator)
    header = next(reader)
    if header != ['email', 'lastname', 'firstname', 'groups']:
        logger.info('Header Missing')
        return
    for data in reader:
        if len(data) != 4:
            logger.info('Invalid row length: %s' % data)
            return
        data[0] = str(data[0])
        data[1] = str(data[1])
        data[2] = str(data[2])
        data[3] = str(data[3])

    all_group_details = json.loads(sc_client.get_all_groups_in_org().content)
    server_users = export_users.get_all_users_and_groups(api_token)

    process_desired_state(server_users, input_filepath)
    process_server_state(server_users, input_filepath)
    execute_actions(all_group_details, sc_client)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()
    api_token = args.token
    input_filepath = args.file
    sync_users(api_token, input_filepath)