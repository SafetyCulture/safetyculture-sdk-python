# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016
import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'SafetyPy'))
import SafetyPy as sp


class SafetyPyTestCase(unittest.TestCase):

    def test_constructor_with_malformed_api_token(self):
        for bad_token in ['123', '111z09cg1e29c43hb77ea0di52ae37988c13f4b7fa6f6f59e9a1649141ef5132', '']:
            with self.assertRaises(SystemExit) as cm:
                sc_client = sp.SafetyCulture(bad_token)
                self.assertEqual(cm.exception.code, 1)

        for bad_token in [None, 123]:
            with self.assertRaises(TypeError):
                sc_client = sp.SafetyCulture(bad_token)

    def test_constructor_with_valid_api_token(self):
        valid_token = '032d09de1ef9c43eb77f56da82ae23588d1564b9fa6f6f59e9a1849191ef1214'
        try:
            sc_client = sp.SafetyCulture(valid_token)
        except:
            self.fail("Encountered an unexpected exception with valid token.")


if __name__ == '__main__':
    unittest.main()