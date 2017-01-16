# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016
import os
import sys
from tzlocal import get_localzone
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools', 'exporter'))
import exporter as exp

logger = exp.configure_logger()


class ExporterTestCase(unittest.TestCase):

    def test_get_missing_export_profile_mapping(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.get_export_profile_mapping(logger, config_setting), msg=message)

    def test_get_missing_export_path(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.get_export_path(logger, config_setting), msg=message)

    def test_get_valid_export_path(self):
        config_setting = {'export_options': {'export_path': '/User/Monty/Dropbox'}}
        self.assertEqual(exp.get_export_path(logger, config_setting), config_setting['export_options']['export_path'])

    def test_get_missing_timezone(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause ' + str(get_localzone()) + ' to be returned'.format(str(config_setting))
            self.assertEqual(exp.get_timezone(logger, config_setting), (str(get_localzone())), msg=message)

    def test_get_valid_timezone(self):
        config_setting = {'export_options': {'timezone': 'America/Chicago'}}
        self.assertEqual(exp.get_timezone(logger, config_setting), config_setting['export_options']['timezone'])

    def test_parse_missing_api_token(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.parse_api_token(logger, config_setting), msg=message)

    def test_parse_malformed_api_token(self):
        config_settings = [{'API': {'token': '123'}}, \
                           {'API': {'token': '031c09cd1z89z43eb77e56dc82ae21588c1364b7fa6f6f59e9a1849191ef1214'}}]
        for config_setting in config_settings:
            self.assertIsNone(exp.parse_api_token(logger, config_setting))

    def test_parse_valid_api_token(self):
        config_setting = {'API': {'token': '031d19ed1e89c43eb77a56dc82be21688c1364b7fa6f6f59e9a1849191ef1214'}}
        self.assertEqual(exp.parse_api_token(logger, config_setting), config_setting['API']['token'])

    def test_get_missing_sync_delay(self):
        config_settings = [{'sync_delay_in_seconds': None}, {'sync_delay_in_seconds': ''}]
        for config_setting in config_settings:
            self.assertEqual(exp.get_sync_delay(logger, config_setting), exp.DEFAULT_SYNC_DELAY_IN_SECONDS)

    def test_get_malformed_sync_delay(self):
        config_settings = [{'sync_delay_in_seconds': 'abc'}, {'sync_delay_in_seconds': -1}]
        for config_setting in config_settings:
            self.assertEqual(exp.get_sync_delay(logger, config_setting), exp.DEFAULT_SYNC_DELAY_IN_SECONDS)

    def test_get_valid_sync_delay(self):
        config_setting = {'sync_delay_in_seconds': 500}
        self.assertEqual(exp.get_sync_delay(logger, config_setting), config_setting['sync_delay_in_seconds'])


if __name__ == '__main__':
    unittest.main()
