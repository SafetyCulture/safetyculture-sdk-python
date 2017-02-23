import os
import sys
import unittest
import mock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import exporter as exp

logger = exp.configure_logger()

class ShowExportProfilesAndExitTestCase(unittest.TestCase):

	@mock.patch('exporter.sys')
	def test_calls_get_ids_for_all_in_list(self, mock_sys):
		list_export_profiles = [1, 2, 3, 4]
		mock_sc_client = mock.Mock()

		def return_export_profiles(id):
			return {'export_profiles': [{'templates': [ {'name':'x'}], 'name': 'x', 'id': 'x'}]}

		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles
		
		exp.show_export_profiles_and_exit(list_export_profiles, mock_sc_client)
		
		for id in list_export_profiles:
			mock_sc_client.get_export_profile_ids.assert_any_call(id)
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, len(list_export_profiles))
		mock_sys.exit.assert_called()

	@mock.patch('exporter.sys')
	def test_calls_get_ids_returns_none_for_all_in_list(self, mock_sys):
		list_export_profiles = [1, 2, 3, 4]
		mock_sc_client = mock.Mock()

		def return_export_profiles(id):
			return None

		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles
		
		exp.show_export_profiles_and_exit(list_export_profiles, mock_sc_client)
		
		for id in list_export_profiles:
			mock_sc_client.get_export_profile_ids.assert_any_call(id)
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, len(list_export_profiles))
		mock_sys.exit.assert_called()

	@mock.patch('exporter.sys')
	def test_calls_get_ids_returns_empty_for_all_in_list(self, mock_sys):
		list_export_profiles = [1, 2, 3, 4]
		mock_sc_client = mock.Mock()

		def return_export_profiles(id):
			return {'export_profiles': []}
		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles

		exp.show_export_profiles_and_exit(list_export_profiles, mock_sc_client)

		for id in list_export_profiles:
			mock_sc_client.get_export_profile_ids.assert_any_call(id)
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, len(list_export_profiles))
		mock_sys.exit.assert_called

	@mock.patch('exporter.sys')
	def test_call_get_ids_with_no_args(self, mock_sys):
		mock_sc_client = mock.Mock()
		
		def return_export_profiles():
			return {'export_profiles': [{'templates': [ {'name':'x'}], 'name': 'x', 'id': 'x'}]}
		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles
		
		exp.show_export_profiles_and_exit([], mock_sc_client)

		mock_sc_client.get_export_profile_ids.assert_called()
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, 1)
		mock_sys.exit.assert_called()

	@mock.patch('exporter.sys')
	def test_call_get_ids_returns_none_with_no_args(self, mock_sys):
		mock_sc_client = mock.Mock()

		def return_export_profiles():
			return None
		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles

		exp.show_export_profiles_and_exit([], mock_sc_client)

		mock_sc_client.get_export_profile_ids.assert_called()
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, 1)
		mock_sys.exit.assert_called()

	@mock.patch('exporter.sys')
	def test_call_get_ids_returns_empty_with_no_args(self, mock_sys):
		mock_sc_client = mock.Mock()

		def return_export_profiles():
			return {'export_profiles': []}
		mock_sc_client.get_export_profile_ids.side_effect = return_export_profiles

		exp.show_export_profiles_and_exit([], mock_sc_client)

		mock_sc_client.get_export_profile_ids.assert_called()
		self.assertEqual(mock_sc_client.get_export_profile_ids.call_count, 1)
		mock_sys.exit.assert_called()

if __name__ == '__main__':
	unittest.main()