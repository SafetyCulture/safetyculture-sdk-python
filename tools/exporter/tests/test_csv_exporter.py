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

    def test_unit_one(self):
        # single question field with standard yes/no/na answer set, answered 'yes'
        csv_exporter = csv.CsvExporter(json.load(open('csv_test_files/unit_test_1_audit.json', 'r')))
        csv_exporter.write('', 'temp.csv', 'wb')
        self.assertEqual(open('temp.csv', 'r').read(), open('csv_test_files/unit_test_1_expected_output.csv', 'r').read())


if __name__ == '__main__':
        unittest.main()