# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import csvExporter as csv

class ExporterTestCase(unittest.TestCase):
    script_dir = os.path.dirname(__file__)
    relative_path_to_test_files = 'csv_test_files/'
    path_to_test_files = os.path.join(script_dir, relative_path_to_test_files)

    def test_convert_single_question_with_standard_yes_no_na_answered_yes(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(
            self.path_to_test_files, 'test_convert_single_question_with_standard_yes_no_na_answered_yes_audit.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('temp.csv', allow_overwrite=True)
        self.assertEqual(open('temp.csv', 'r').read(), open(os.path.join(
            self.path_to_test_files, 'test_convert_single_question_with_standard_yes_no_na_answered_yes_expected_output.csv'), 'r').read())
        os.remove('temp.csv')

if __name__ == '__main__':
        unittest.main()
