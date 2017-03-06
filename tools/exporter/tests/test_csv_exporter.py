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
        csv_exporter.save_converted_audit_to_file('test 1.csv', allow_overwrite=True)
        self.assertEqual(open('test 1.csv', 'r').read(), open(os.path.join(
            self.path_to_test_files, 'test_convert_single_question_with_standard_yes_no_na_answered_yes_expected_output.csv'), 'r').read())
        os.remove('test 1.csv')

    def test_checkbox_field_checked(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(
            self.path_to_test_files, 'test checkbox field - checked.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 2.csv', allow_overwrite=True)
        self.assertEqual(open('test 2.csv', 'r').read(), open(os.path.join(
            self.path_to_test_files, 'test checkbox field - checked expected output.csv'), 'r').read())
        os.remove('test 2.csv')

    def test_datetime_field(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(
            self.path_to_test_files, 'test datetime field - input date using now button.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 3.csv', allow_overwrite=True)
        self.assertEqual(open('test 3.csv', 'r').read(), open(os.path.join(
            self.path_to_test_files, 'test datetime field - input date using now button expected output.csv'), 'r').read())
        os.remove('test 3.csv')

    def test_single_information_weblink_field(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(
            self.path_to_test_files, 'unit_test_single_information_weblink_field.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 4.csv', allow_overwrite=True)
        self.assertEqual(open('test 4.csv', 'r').read(), open(os.path.join(
            self.path_to_test_files, 'unit_test_single_information_weblink_field_expected_output.csv'), 'r').read())
        os.remove('test 4.csv')

    def test_single_drawing_field_drawn_on_ios(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_drawing_field_drawn_on_ios.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 5.csv', allow_overwrite=True)
        self.assertEqual(open('test 5.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_drawing_field_drawn_on_ios_expected_output.csv'), 'r').read())
        os.remove('test 5.csv')


    def test_single_location_field_input_textually_without_gps(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_location_field_input_textually_without_gps.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 6.csv', allow_overwrite=True)
        self.assertEqual(open('test 6.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_location_field_input_textually_without_gps_expected_output.csv'), 'r').read())
        os.remove('test 6.csv')

    def test_single_media_field_image_taken_on_ios_camera(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_image_taken_on_ios_camera.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 7.csv', allow_overwrite=True)
        self.assertEqual(open('test 7.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_image_taken_on_ios_camera_expected_output.csv'), 'r').read())
        os.remove('test 7.csv')

    def test_single_question_field_custom_response_set_answered_california(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_custom_response_set_answered_california.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 8.csv', allow_overwrite=True)
        self.assertEqual(open('test 8.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_custom_response_set_answered_california_expected_output.csv'), 'r').read())
        os.remove('test 8.csv')

    def test_single_question_field_safe_atRisk_NA_answered_atRisk(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_safe_atRisk_NA_answered_atRisk.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 9.csv', allow_overwrite=True)
        self.assertEqual(open('test 9.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_safe_atRisk_NA_answered_atRisk_expected_output.csv'), 'r').read())
        os.remove('test 9.csv')

    def test_single_question_field_safe_atRisk_NA_answered_safe(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_safe_atRisk_NA_answered_safe.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 10.csv', allow_overwrite=True)
        self.assertEqual(open('test 10.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_field_safe_atRisk_NA_answered_safe_expected_output.csv'), 'r').read())
        os.remove('test 10.csv')

    def test_single_dynamic_field_3_instances(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_dynamic_field_3_instances.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 11.csv', allow_overwrite=True)
        self.assertEqual(open('test 11.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_dynamic_field_3_instances_expected_output.csv'), 'r').read())
        os.remove('test 11.csv')

    def test_single_address_field_used_map__15_Gilbert_St_Dover_Heights_NSW_2030_Australia(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_used_map_-_15_Gilbert_St,_Dover_Heights_NSW_2030,_Australia.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 12.csv', allow_overwrite=True)
        self.assertEqual(open('test 12.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_used_map_-_15_Gilbert_St,_Dover_Heights_NSW_2030,_Australia_expected_output.csv'), 'r').read())
        os.remove('test 12.csv')

    def test_single_multiple_choice__multiple_selection_8_answers_chosen(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_-_multiple_selection_8_answers_chosen.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 13.csv', allow_overwrite=True)
        self.assertEqual(open('test 13.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_-_multiple_selection_8_answers_chosen_expected_output.csv'), 'r').read())
        os.remove('test 13.csv')

    def test_single_multiple_choice_field__single_response_Answered_frog(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_field_-_single_response_Answered_frog.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 14.csv', allow_overwrite=True)
        self.assertEqual(open('test 14.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_field_-_single_response_Answered_frog_expected_output.csv'), 'r').read())
        os.remove('test 14.csv')

    def test_single_question_yes_no_na_answered_no(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes_-_no_-_na_answered_no.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 15.csv', allow_overwrite=True)
        self.assertEqual(open('test 15.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes_-_no_-_na_answered_no_expected_output.csv'), 'r').read())
        os.remove('test 15.csv')

    def test_single_question_yes_no_na_answered_yes(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes_-_no_-_na_answered_yes.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 16.csv', allow_overwrite=True)
        self.assertEqual(open('test 16.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes_-_no_-_na_answered_yes_expected_output.csv'), 'r').read())
        os.remove('test 16.csv')

    def test_single_signature_iOS_signature(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_signature_iOS_signature.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 17.csv', allow_overwrite=True)
        self.assertEqual(open('test 17.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_signature_iOS_signature_expected_output.csv'), 'r').read())
        os.remove('test 17.csv')

    def test_single_media_field_24_images_from_gallery(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_24_images_from_gallery.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 18.csv', allow_overwrite=True)
        self.assertEqual(open('test 18.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_24_images_from_gallery_expected_output.csv'), 'r').read())
        os.remove('test 18.csv')

    def test_single_slider_field_Answered_6(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_slider_field_Answered_6.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 19.csv', allow_overwrite=True)
        self.assertEqual(open('test 19.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_slider_field_Answered_6_expected_output.csv'), 'r').read())
        os.remove('test 19.csv')

    def test_single_text_field_Added_3_lines(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_field_Added_3_lines.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 20.csv', allow_overwrite=True)
        self.assertEqual(open('test 20.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_field_Added_3_lines_expected_output.csv'), 'r').read())
        os.remove('test 20.csv')

    def test_single_switch_field_Switched_off(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_off.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 21.csv', allow_overwrite=True)
        self.assertEqual(open('test 21.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_off_expected_output.csv'), 'r').read())
        os.remove('test 21.csv')

    def test_single_switch_field_Switched_on(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_on.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 22.csv', allow_overwrite=True)
        self.assertEqual(open('test 22.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_on_expected_output.csv'), 'r').read())
        os.remove('test 22.csv')

    def test_single_text_single_line_Single_line_entered(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_Single_line_entered.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 23.csv', allow_overwrite=True)
        self.assertEqual(open('test 23.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_Single_line_entered_expected_output.csv'), 'r').read())
        os.remove('test 23.csv')


if __name__ == '__main__':
    unittest.main()
