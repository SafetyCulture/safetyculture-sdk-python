import argparse
import logging
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp
from collections import OrderedDict
import pydash
from pydash import _

# the file that stores all exported users in CSV format
USER_EXPORT_FILENAME = 'iauditor_users.csv'

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

def get_all_users_and_groups(api_token):
    """
    Exports a dictionary of all active users from iAuditor organisation and their associated groups
    :return: A sorted dictionary of all active users and their associated groups
    """
    sc_client = sp.SafetyCulture(api_token)
    org_id = sc_client.get_my_org()
    groups_list = []
    user_map = {}

    users_of_org = json.loads(sc_client.get_users_of_group(org_id))
    for user in users_of_org['users']:
        if user['status'] != 'active':
            continue
        email = user['email']
        user_map[email] = {'groups': [], 'firstname': user['firstname'], 'lastname': user['lastname'], 'user_id': user['user_id']}

    all_group_details = json.loads(sc_client.get_all_groups_in_org().content)
    groups_list = [g['id'] for g in all_group_details['groups']]

    for group_id in groups_list:
        users_in_group = json.loads(sc_client.get_users_of_group(group_id))
        groups = all_group_details['groups']
        target_group = _.find(groups, {'id': group_id})
        group_name = target_group['name']

        for user in users_in_group['users']:
            if user['status'] != 'active':
                continue
            email = user['email']
            user_map[email]['user_id'] = user['user_id']
            if email in user_map:
                if group_name not in user_map[email]['groups']:
                    user_map[email]['groups'].append(str(group_name))
                    user_map[email]['groups'].append(str(group_id))

            else:
                user_map[email]['groups'] = [group_name]
                user_map[email]['groups'] = [group_name]

    sorted_user_map = OrderedDict(sorted(user_map.items(), key=lambda t: t[0]))
    return sorted_user_map

def save_users_and_groups_to_csv(user_data, csv_output_filepath):
    """
    Creates a CSV file with exported user data
    :param user_data: The exported user data
    :param csv_output_filepath: The output file to save
    :return: None
    """
    full_output_path = os.path.join(os.getcwd(), csv_output_filepath)
    with open(full_output_path, 'wb') as f:
        fields = ['email', 'lastname', 'firstname', 'groups']
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for key, val in sorted(user_data.items()):
            val['groups'] = ", ".join(val['groups'][0::2])
            row = {'email': key}
            row.update(val)
            w.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    args = parser.parse_args()
    api_token = args.token

    exported_users = get_all_users_and_groups(api_token)
    for user in exported_users:
        # removing the user ID to keep the CSV output user-friendly
        del exported_users[user]['user_id']
    save_users_and_groups_to_csv(exported_users, csv_output_filepath=USER_EXPORT_FILENAME)

