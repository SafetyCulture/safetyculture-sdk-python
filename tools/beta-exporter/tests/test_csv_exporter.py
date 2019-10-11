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

    def test_single_checkbox_checked(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_checkbox_checked.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 2.csv', allow_overwrite=True)
        self.assertEqual(open('test 2.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_checkbox_checked_expected_output.csv'), 'r').read())
        os.remove('test 2.csv')

    def test_single_date_time_field_input_date_using_now_button(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_date_time_field_input_date_using_now_button.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 3.csv', allow_overwrite=True)
        self.assertEqual(open('test 3.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_date_time_field_input_date_using_now_button_expected_output.csv'), 'r').read())
        os.remove('test 3.csv')

    def test_single_information_field___weblink__Nothing_to_do_here(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_information_field___weblink__Nothing_to_do_here.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 4.csv', allow_overwrite=True)
        self.assertEqual(open('test 4.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_information_field___weblink__Nothing_to_do_here_expected_output.csv'), 'r').read())
        os.remove('test 4.csv')

    def test_single_drawing_field_Drawing_done_in_iOS_device(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_drawing_field_Drawing_done_in_iOS_device.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 5.csv', allow_overwrite=True)
        self.assertEqual(open('test 5.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_drawing_field_Drawing_done_in_iOS_device_expected_output.csv'), 'r').read())
        os.remove('test 5.csv')

    def test_single_address_field_textually_input_address(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_textually_input_address.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 6.csv', allow_overwrite=True)
        self.assertEqual(open('test 6.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_textually_input_address_expected_output.csv'), 'r').read())
        os.remove('test 6.csv')

    def test_single_media_field_Single_image_taken_with_camera(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_Single_image_taken_with_camera.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 7.csv', allow_overwrite=True)
        self.assertEqual(open('test 7.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_Single_image_taken_with_camera_expected_output.csv'), 'r').read())
        os.remove('test 7.csv')

    def test_single_question_custom_response_set_answered_california(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_custom_response_set_answered_california.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 8.csv', allow_overwrite=True)
        self.assertEqual(open('test 8.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_custom_response_set_answered_california_expected_output.csv'), 'r').read())
        os.remove('test 8.csv')

    def test_single_question_safe___at_risk___na_answered_safe(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_safe___at_risk___na_answered_safe.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 9.csv', allow_overwrite=True)
        self.assertEqual(open('test 9.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_safe___at_risk___na_answered_safe_expected_output.csv'), 'r').read())
        os.remove('test 9.csv')


    def test_single_question_safe___at_risk___na_answered_at_risk(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_safe___at_risk___na_answered_at_risk.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 11.csv', allow_overwrite=True)
        self.assertEqual(open('test 11.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_safe___at_risk___na_answered_at_risk_expected_output.csv'), 'r').read())
        os.remove('test 11.csv')

    def test_SafetyCulture_iAuditor___The_Smartest_Checklist_App_(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_SafetyCulture_iAuditor___The_Smartest_Checklist_App_.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 12.csv', allow_overwrite=True)
        self.assertEqual(open('test 12.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_SafetyCulture_iAuditor___The_Smartest_Checklist_App__expected_output.csv'), 'r').read())
        os.remove('test 12.csv')

    def test_single_text_single_line_double_quotes_within_text(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_double_quotes_within_text.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 13.csv', allow_overwrite=True)
        self.assertEqual(open('test 13.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_double_quotes_within_text_expected_output.csv'), 'r').read())
        os.remove('test 13.csv')

    def test_single_text_single_line_mathematical_symbols_in_text(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_mathematical_symbols_in_text.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 14.csv', allow_overwrite=True)
        self.assertEqual(open('test 14.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_mathematical_symbols_in_text_expected_output.csv'), 'r').read())
        os.remove('test 14.csv')

    def test_single_text_single_line_Single_line_entered(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_Single_line_entered.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 16.csv', allow_overwrite=True)
        self.assertEqual(open('test 16.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_single_line_Single_line_entered_expected_output.csv'), 'r').read())
        os.remove('test 16.csv')

    def test_single_text_field_Added_3_lines(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_text_field_Added_3_lines.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 17.csv', allow_overwrite=True)
        self.assertEqual(open('test 17.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_text_field_Added_3_lines_expected_output.csv'), 'r').read())
        os.remove('test 17.csv')

    def test_single_switch_field_Switched_on(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_on.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 18.csv', allow_overwrite=True)
        self.assertEqual(open('test 18.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_on_expected_output.csv'), 'r').read())
        os.remove('test 18.csv')

    def test_single_switch_field_Switched_off(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_off.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 19.csv', allow_overwrite=True)
        self.assertEqual(open('test 19.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_switch_field_Switched_off_expected_output.csv'), 'r').read())
        os.remove('test 19.csv')

    def test_single_slider_field_Answered_6(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_slider_field_Answered_6.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 20.csv', allow_overwrite=True)
        self.assertEqual(open('test 20.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_slider_field_Answered_6_expected_output.csv'), 'r').read())
        os.remove('test 20.csv')

    def test_single_signature_iOS_signature(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_signature_iOS_signature.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 21.csv', allow_overwrite=True)
        self.assertEqual(open('test 21.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_signature_iOS_signature_expected_output.csv'), 'r').read())
        os.remove('test 21.csv')

    def test_single_question_yes___no___na_answered_yes(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_answered_yes.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 22.csv', allow_overwrite=True)
        self.assertEqual(open('test 22.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_answered_yes_expected_output.csv'), 'r').read())
        os.remove('test 22.csv')

    def test_single_question_yes___no___na_answered_no(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_answered_no.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 23.csv', allow_overwrite=True)
        self.assertEqual(open('test 23.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_answered_no_expected_output.csv'), 'r').read())
        os.remove('test 23.csv')

    def test_single_multiple_choice_field___single_response_Answered_frog(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_field___single_response_Answered_frog.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 24.csv', allow_overwrite=True)
        self.assertEqual(open('test 24.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice_field___single_response_Answered_frog_expected_output.csv'), 'r').read())
        os.remove('test 24.csv')

    def test_single_multiple_choice___multiple_selection_8_answers_chosen(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice___multiple_selection_8_answers_chosen.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 25.csv', allow_overwrite=True)
        self.assertEqual(open('test 25.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_multiple_choice___multiple_selection_8_answers_chosen_expected_output.csv'), 'r').read())
        os.remove('test 25.csv')

    def test_single_multi_line_text_field_500_unicode_characters__on_5_lines(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_multi_line_text_field_500_unicode_characters__on_5_lines.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 26.csv', allow_overwrite=True)
        self.assertEqual(open('test 26.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_multi_line_text_field_500_unicode_characters__on_5_lines_expected_output.csv'), 'r').read())
        os.remove('test 26.csv')

    def test_single_media_field_24_images_from_gallery(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_24_images_from_gallery.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 27.csv', allow_overwrite=True)
        self.assertEqual(open('test 27.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_media_field_24_images_from_gallery_expected_output.csv'), 'r').read())
        os.remove('test 27.csv')

    def test_single_question_as_mandatory_field_answered_mandatory_field(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_as_mandatory_field_answered_mandatory_field.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 28.csv', allow_overwrite=True)
        self.assertEqual(open('test 28.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_as_mandatory_field_answered_mandatory_field_expected_output.csv'), 'r').read())
        os.remove('test 28.csv')

    def test_single_information_field___media_(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_information_field___media_.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 29.csv', allow_overwrite=True)
        self.assertEqual(open('test 29.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_information_field___media__expected_output.csv'), 'r').read())
        os.remove('test 29.csv')

    def test_single_dynamic_field_3_instances(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_dynamic_field_3_instances.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 30.csv', allow_overwrite=True)
        self.assertEqual(open('test 30.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_dynamic_field_3_instances_expected_output.csv'), 'r').read())
        os.remove('test 30.csv')

    def test_single_address_field_used_map___15_Gilbert_St__Dover_Heights_NSW_2030__Australia(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_used_map___15_Gilbert_St__Dover_Heights_NSW_2030__Australia.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 31.csv', allow_overwrite=True)
        self.assertEqual(open('test 31.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_address_field_used_map___15_Gilbert_St__Dover_Heights_NSW_2030__Australia_expected_output.csv'), 'r').read())
        os.remove('test 31.csv')

    def test_Rugby_Union_Contest_Self_Assessment_(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'null_date_test.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 32.csv', allow_overwrite=True)
        self.assertEqual(open('test 32.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'null_date_test_expected_output.csv'), 'r').read())
        os.remove('test 32.csv')

    def test_failed_response_test_(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_failed_response_test_.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 33.csv', allow_overwrite=True)
        self.assertEqual(open('test 33.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_failed_response_test__expected_output.csv'), 'r').read())
        os.remove('test 33.csv')

    def test_failed_response_test_failed_response_not_chosen(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_failed_response_test_failed_response_not_chosen.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 34.csv', allow_overwrite=True)
        self.assertEqual(open('test 34.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_failed_response_test_failed_response_not_chosen_expected_output.csv'), 'r').read())
        os.remove('test 34.csv')

    def test_single_question_yes___no___na_comment_and_images_added_to_question(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_comment_and_images_added_to_question.json'), 'r')))
        csv_exporter.save_converted_audit_to_file('test 35.csv', allow_overwrite=True)
        self.assertEqual(open('test 35.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'unit_test_single_question_yes___no___na_comment_and_images_added_to_question_expected_output.csv'), 'r').read())
        os.remove('test 35.csv')

    def test_export_inactive_fields_true(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'export_inactive_fields_true.json'), 'r')), True)
        csv_exporter.save_converted_audit_to_file('test 36.csv', allow_overwrite=True)
        self.assertEqual(open('test 36.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'export_inactive_fields_true_expected_output.csv'), 'r').read())
        os.remove('test 36.csv')

    def test_do_not_export_inactive_fields(self):
        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, 'do_not_export_inactive_fields.json'), 'r')), False)
        csv_exporter.save_converted_audit_to_file('test 37.csv', allow_overwrite=True)
        self.assertEqual(open('test 37.csv', 'r').read(), open(os.path.join(self.path_to_test_files, 'do_not_export_inactive_fields_expected_output.csv'), 'r').read())
        os.remove('test 37.csv')


if __name__ == '__main__':
    unittest.main()
