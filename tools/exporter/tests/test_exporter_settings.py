# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016

import os
import sys
from tzlocal import get_localzone
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import exporter as exp

logger = exp.configure_logger()


class ExporterTestCase(unittest.TestCase):

    def test_return_None_if_no_export_profile_mapping_was_given(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.load_setting_export_profile_mapping(logger, config_setting), msg=message)

    def test_return_None_if_no_export_path_was_given(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.load_setting_export_path(logger, config_setting), msg=message)

    def test_use_user_supplied_unix_style_export_path_if_given(self):
        config_setting = {'export_options': {'export_path': '/User/Monty/Dropbox'}}
        self.assertEqual(exp.load_setting_export_path(logger, config_setting), config_setting['export_options']['export_path'])

    def test_use_user_supplied_windows_style_export_path_if_given(self):
        config_setting = {'export_options': {'export_path': r'C:\Users\Monty\Dropbox'}}
        self.assertEqual(exp.load_setting_export_path(logger, config_setting), config_setting['export_options']['export_path'])

    def test_use_local_timezone_if_none_given(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause ' + str(get_localzone()) + ' to be returned'.format(str(config_setting))
            self.assertEqual(exp.load_setting_export_timezone(logger, config_setting), (str(get_localzone())), msg=message)

    def test_use_valid_timezone_from_settings_if_given(self):
        config_setting = {'export_options': {'timezone': 'America/Chicago'}}
        self.assertEqual(exp.load_setting_export_timezone(logger, config_setting), config_setting['export_options']['timezone'])

    def test_return_None_if_API_token_is_missing(self):
        config_settings = [{}, None, '']
        for config_setting in config_settings:
            message = '{0} should cause None to be returned'.format(str(config_setting))
            self.assertIsNone(exp.load_setting_api_access_token(logger, config_setting), msg=message)

    def test_return_None_if_API_token_has_invalid_format(self):
        config_settings = [{'API': {'token': '123'}},
                           {'API': {'token': '031c09cd1z89z43eb77e56dc82ae21588c1364b7fa6f6f59e9a1849191ef1214'}}]
        for config_setting in config_settings:
            self.assertIsNone(exp.load_setting_api_access_token(logger, config_setting))

    def test_successfully_parse_a_valid_API_token(self):
        config_setting = {'API': {'token': '031d19ed1e89c43eb77a56dc82be21688c1364b7fa6f6f59e9a1849191ef1214'}}
        self.assertEqual(exp.load_setting_api_access_token(logger, config_setting), config_setting['API']['token'])

    def test_use_default_if_sync_delay_setting_is_missing(self):
        config_settings = [{'sync_delay_in_seconds': None}, {'sync_delay_in_seconds': ''}]
        for config_setting in config_settings:
            self.assertEqual(exp.load_setting_sync_delay(logger, config_setting), exp.DEFAULT_SYNC_DELAY_IN_SECONDS)

    def test_use_default_if_sync_delay_setting_is_invalid(self):
        config_settings = [{'sync_delay_in_seconds': 'abc'}, {'sync_delay_in_seconds': -1}]
        for config_setting in config_settings:
            self.assertEqual(exp.load_setting_sync_delay(logger, config_setting), exp.DEFAULT_SYNC_DELAY_IN_SECONDS)

    def test_use_user_supplied_sync_delay_if_valid(self):
        config_setting = {'sync_delay_in_seconds': 500}
        self.assertEqual(exp.load_setting_sync_delay(logger, config_setting), config_setting['sync_delay_in_seconds'])

    def test_return_None_if_no_proxy_setting_is_given(self):
        config_settings = [{'proxy': {'https:': ''}}, {'proxy': {'https:': None} }, '', None]
        for config_setting in config_settings:
            self.assertEqual(exp.load_setting_proxy(logger, config_setting), None);

    def test_return_None_if_proxy_ip_is_invalid(self):
        config_settings = [{'proxy': {'https': '192.168.6.b:8080'}}, {'proxy': {'https': '256.254.0.81:2154'}},{'proxy': {'https': '192.168.6.1'}}]
        for config_setting in config_settings:
            self.assertEqual(exp.load_setting_proxy(logger, config_setting), None);
        
    def test_use_user_supplied_proxy_if_valid(self):
        config_settings = [{'proxy': {'https': '192.168.6.1:8080'}}, {'proxy': {'https': '10.254.0.81:2154'}}]
        for config_setting in config_settings:
            self.assertEqual(exp.load_setting_proxy(logger, config_setting), config_setting['proxy']);

if __name__ == '__main__':
    unittest.main()
