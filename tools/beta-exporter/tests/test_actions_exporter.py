# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import exporter

script_dir = os.path.dirname(__file__)
relative_path_to_test_files = 'actions_export_test_files/'
path_to_test_files = os.path.join(script_dir, relative_path_to_test_files)

def load_json_from_file(filename):
    return json.load(open(os.path.join(path_to_test_files, filename), 'r'))

class ExporterTestCase(unittest.TestCase):

    def test_transform_of_action_json_ojbect_to_array(self):
        single_action_json_from_api = load_json_from_file('single_action_from_api.json')
        expected_action_transformed_to_array = load_json_from_file('single_action_transformed_to_array.json')
        actual_action_transformed_to_array = exporter.transform_action_object_to_list(single_action_json_from_api)
        self.assertEqual(expected_action_transformed_to_array, actual_action_transformed_to_array)

if __name__ == '__main__':
    unittest.main()

