# import sys
# import os
# from safetypy import safetypy as sp
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import argparse
import datetime
import errno
import logging
import os
import re
import sys
import yaml
import json
import requests
import csv
from xlrd import open_workbook
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from safetypy import safetypy as sp

# Possible values here are DEBUG, INFO, WARN, ERROR and CRITICAL
LOG_LEVEL = logging.DEBUG

DEFAULT_CONFIG_FILENAME = 'config.yaml'
def main():
    sc_client = sp.SafetyCulture('b9b278f0cd8825ceac18a585115163ea56001c3589eb6b3c5bcd13c3b4f13550')
    print("1111111111")
    response = sc_client.get_orgs()
    # json_load = json.load(response)
    json_load = json.loads(response.content)
    org_role_id = ""
    groups_list = []
    user_map = dict()

    for i in json_load['groups']:
        if i['type'] == 'organisation':
            org_role_id = i['id']
            json_load = json.loads(sc_client.get_users_of_groups(org_role_id))
            for i in json_load['users']:
                if i['status'] == 'active':
                    email = i['email']
                    user_map[email] = list()

        elif i['type'] == 'group':
            groups_list.append(i['id'])

    print "ROLE ID ::: " + org_role_id

    for group in groups_list:
        json_load = json.loads(sc_client.get_users_of_groups(group))
        # print json_load
        # user_map = {}
        for user in json_load['users']:
            email = user['email']
            # print user_map[email]
            if email in user_map:
                user_map[email].append(str(group))
            else:
                user_map[email] = [group]

    for i in user_map:
        print i, user_map[i]

    create_csv(user_map)


def create_csv(csv_map):
    with open('tools/export_user/mycsvfile.csv', 'wb') as f:
        w = csv.writer(f)
        w.writerows(csv_map.items())


if __name__ == '__main__':
    main()



