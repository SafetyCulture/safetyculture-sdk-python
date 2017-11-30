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

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

def main():
    """
    Load local User data, get system User data, compare and add users to system
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-t', '--token', required=True)
    args = parser.parse_args()
    file_path = args.file
    api_token = args.token

    sc_client = sp.SafetyCulture(api_token)

    org_id = sc_client.get_my_org()
    users_of_org = json.loads(sc_client.get_users_of_group(org_id))
    json_all_groups = json.loads(sc_client.get_all_groups_in_org().content)

    with open(file_path) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        next(csvReader, None)
        for email, firstname, lastname, groups in csvReader:
            group_list=[]
            if groups != "":
                group_list = groups.split(",")
                group_list = [group.strip(' ') for group in group_list]
            if email not in [user['email'] for user in users_of_org['users']]:
                user_data = { 'firstname': firstname, 'lastname': lastname, 'email': email }
                user_id = json.loads(sc_client.add_user_to_org(user_data))['user']['user_id']
                if group_list:
                    for group_name in group_list:
                        target_group = _.find(json_all_groups['groups'], {'name': group_name})
                        sc_client.add_user_to_group(target_group['id'], { 'user_id': user_id })
            else:
                if group_list:
                    for group_name in group_list:
                        target_user = _.find(users_of_org['users'], {'email': email})
                        target_group = _.find(json_all_groups['groups'], {'name': group_name})
                        payload = {
                            'user_id': target_user['user_id']
                        }
                        sc_client.add_user_to_group(target_group['id'], payload)


if __name__ == '__main__':
    main()