# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

from tzlocal import get_localzone
import unittest
import exporter as ex

class exporterTestCase(unittest.TestCase):

    def test_get_missing_export_profile_mapping(self):
        for config_settings in [{}, None, '']:
            self.assertIsNone(ex.get_export_profile_mapping(config_settings))

    def test_get_missing_export_path(self):
        for config_settings in [{}, None, '']:
            self.assertIsNone(ex.get_export_path(config_settings))

    def test_get_missing_timezone(self):
        for config_settings in [{}, None, '']:
            self.assertEquals(ex.get_timezone(config_settings), (str(get_localzone())))

if __name__ == '__main__':
    unittest.main()