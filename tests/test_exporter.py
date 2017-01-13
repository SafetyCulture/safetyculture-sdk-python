# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016
import os
import sys
from tzlocal import get_localzone
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools', 'exporter'))
import exporter as ex

class exporterTestCase(unittest.TestCase):

    def test_get_missing_export_profile_mapping(self):
        for config_settings in [{}, None, '']:
            message = '{0} should cause None to be returned'.format(str(config_settings))
            self.assertIsNone(ex.get_export_profile_mapping(config_settings), msg=message)

    def test_get_missing_export_path(self):
        for config_settings in [{}, None, '']:
            message = '{0} should cause None to be returned'.format(str(config_settings))
            self.assertIsNone(ex.get_export_path(config_settings), msg=message)

    def test_get_missing_timezone(self):
        for config_settings in [{}, None, '']:
            message = '{0} should cause ' + str(get_localzone()) + ' to be returned'.format(str(config_settings))
            self.assertEqual(ex.get_timezone(config_settings), (str(get_localzone())), msg=message)

if __name__ == '__main__':
    unittest.main()