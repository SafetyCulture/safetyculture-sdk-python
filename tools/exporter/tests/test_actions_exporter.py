# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import exporter

class ExporterTestCase(unittest.TestCase):
    script_dir = os.path.dirname(__file__)
    relative_path_to_test_files = 'actions_export_test_files/'
    path_to_test_files = os.path.join(script_dir, relative_path_to_test_files)

    def test_transform_of_action_json_ojbect_to_array(self):
        example_action_json = json.load(open(os.path.join(self.path_to_test_files, 'single_action_from_api.json'), 'r'))
        single_action_transformed_to_array = json.load(open(os.path.join(self.path_to_test_files, 'single_action_transformed_to_array.json'), 'r'))
        actual_action_transformed_to_array = exporter.transform_action_object_to_list(example_action_json)
        self.assertEqual(single_action_transformed_to_array, actual_action_transformed_to_array)


if __name__ == '__main__':
    unittest.main()
