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

DEFAULT_CONFIG_FILENAME = 'config.yaml'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    args = parser.parse_args()
    api_token = args.token
    sc_client = sp.SafetyCulture(api_token)
    org_id = sc_client.get_my_org()
    groups_list = []
    user_map = {}

    users_of_org = json.loads(sc_client.get_users_of_group(org_id))
    for user in users_of_org['users']:
        if user['status'] != 'active':
            continue
        email = user['email']
        user_map[email] = {'groups': [], 'firstname': user['firstname'], 'lastname': user['lastname']}

    json_all_groups = json.loads(sc_client.get_all_groups_in_org().content)
    groups_list = [g['id'] for g in json_all_groups['groups']]

    for group_id in groups_list:
        users_in_group = json.loads(sc_client.get_users_of_group(group_id))
        groups = json_all_groups['groups']
        target_group = _.find(groups, {'id': group_id})
        group_name = target_group['name']

        for user in users_in_group['users']:
            if user['status'] != 'active':
                continue
            email = user['email']
            if email in user_map:
                if group_name not in user_map[email]['groups']:
                    user_map[email]['groups'].append(str(group_name))
            else:
                user_map[email]['groups'] = [group_name]

    sorted_user_map = OrderedDict(sorted(user_map.items(), key=lambda t: t[0]))
    create_csv(sorted_user_map)


def create_csv(csv_map):
    with open('tools/export_user/'+ USER_EXPORT_FILENAME , 'wb') as f:
        fields = ['email', 'lastname', 'firstname', 'groups']
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for key, val in sorted(csv_map.items()):
            val['groups'] = ", ".join(val['groups'])
            row = {'email': key}
            row.update(val)
            w.writerow(row)


if __name__ == '__main__':
    main()
