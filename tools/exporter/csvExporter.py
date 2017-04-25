import unicodecsv as csv
import json
import sys
import os
import copy
from datetime import datetime

CSV_HEADER_ROW = [
    'Item Type',
    'Label',
    'Response',
    'Comment',
    'Media Hypertext Reference',
    'Location Coordinates',
    'Item Score',
    'Item Max Score',
    'Item Score Percentage',
    'Mandatory',
    'Failed Response',
    'Inactive',
    'Item ID',
    'Response ID',
    'Parent ID',
    'Completed',
    'Audit Owner',
    'Audit Author',
    'Audit Name',
    'Audit Score',
    'Audit Max Score',
    'Audit Score Percentage',
    'Audit Duration (seconds)',
    'Date Started',
    'Time Started',
    'Date Completed',
    'Time Completed',
    'Audit ID',
    'Template ID',
    'Template Name',
    'Template Author'
]

# audit item empty response 
EMPTY_RESPONSE = ''

# audit item property constants
LABEL = 'label'
COMMENTS = 'comments'
TYPE = 'type'
FAILED = 'failed'
SCORE = 'score'
MAX_SCORE = 'max_score'
SCORE_PERCENTAGE = 'score_percentage'
COMBINED_SCORE = 'combined_score'
COMBINED_MAX_SCORE = 'combined_max_score'
COMBINED_SCORE_PERCENTAGE = 'combined_score_percentage'
PARENT_ID = 'parent_id'
RESPONSE = 'response'
INACTIVE = 'inactive'
ID = 'item_id'
HREF = 'href'
SIGNATURE = 'signature'
INFORMATION = 'information'
MEDIA = 'media'
RESPONSES = 'responses'

# maps smartfield conditional statement IDs to the corresponding text
smartfield_conditional_id_to_statement_map = {
    # conditional statements for question field
    '3f206180-e4f6-11e1-aff1-0800200c9a66': 'if response selected',
    '3f206181-e4f6-11e1-aff1-0800200c9a66': 'if response not selected',
    '3f206182-e4f6-11e1-aff1-0800200c9a66': 'if response is',
    '3f206183-e4f6-11e1-aff1-0800200c9a66': 'if response is not',
    '3f206184-e4f6-11e1-aff1-0800200c9a66': 'if response is one of',
    '3f206185-e4f6-11e1-aff1-0800200c9a66': 'if response is not one of',
    # conditional statements for list field
    '35f6c130-e500-11e1-aff1-0800200c9a66': 'if response selected',
    '35f6c131-e500-11e1-aff1-0800200c9a66': 'if response not selected',
    '35f6c132-e500-11e1-aff1-0800200c9a66': 'if response is',
    '35f6c133-e500-11e1-aff1-0800200c9a66': 'if response is not',
    '35f6c134-e500-11e1-aff1-0800200c9a66': 'if response is one of',
    '35f6c135-e500-11e1-aff1-0800200c9a66': 'if response is not one of',
    # conditional statements for slider field
    'cda7c330-e500-11e1-aff1-0800200c9a66': 'if slider value is less than',
    'cda7c331-e500-11e1-aff1-0800200c9a66': 'if slider value is less than or equal to',
    'cda7c332-e500-11e1-aff1-0800200c9a66': 'if slider value is equal to',
    'cda7c333-e500-11e1-aff1-0800200c9a66': 'if slider value is not equal to',
    'cda7c334-e500-11e1-aff1-0800200c9a66': 'if slider value is greater than or equal to',
    'cda7c335-e500-11e1-aff1-0800200c9a66': 'if the slider value is greater than',
    'cda7c336-e500-11e1-aff1-0800200c9a66': 'if the slider value is between',
    'cda7c337-e500-11e1-aff1-0800200c9a66': 'if the slider value is not between',
    # conditional statements for checkbox field
    '4e671f40-e4ff-11e1-aff1-0800200c9a66': 'if the checkbox is checked',
    '4e671f41-e4ff-11e1-aff1-0800200c9a66': 'if the checkbox is not checked',
    # conditional statements for switch field
    '3d346f00-e501-11e1-aff1-0800200c9a66': 'if the switch is on',
    '3d346f01-e501-11e1-aff1-0800200c9a66': 'if the switch is off',
    # conditional statements for text field
    '7c441470-e501-11e1-aff1-0800200c9a66': 'if text is',
    '7c441471-e501-11e1-aff1-0800200c9a66': 'if text is not',
    # conditional statements for textsingle field
    '6ff300f0-e501-11e1-aff1-0800200c9a66': 'if text is',
    '6ff300f1-e501-11e1-aff1-0800200c9a66': 'if text is not',
    # conditional statements for signature field
    '831f8ff0-e500-11e1-aff1-0800200c9a66': 'if signature exists',
    '831f8ff1-e500-11e1-aff1-0800200c9a66': 'if the signature does not exist',
    '831f8ff2-e500-11e1-aff1-0800200c9a66': 'if the signature name is',
    '831f8ff3-e500-11e1-aff1-0800200c9a66': 'if the signature name is not',
    # conditional statements for barcode field
    '8259d900-12e3-11e4-9191-0800200c9a66': 'if the scanned barcode is',
    '8259d901-12e3-11e4-9191-0800200c9a66': 'if the scanned barcode is not'
}

# maps default answer IDs to corresponding Text
standard_response_id_map = {
    '8bcfbf00-e11b-11e1-9b23-0800200c9a66': 'Yes',
    '8bcfbf01-e11b-11e1-9b23-0800200c9a66': 'No',
    '8bcfbf02-e11b-11e1-9b23-0800200c9a66': 'N/A',
    'b5c92350-e11b-11e1-9b23-0800200c9a66': 'Safe',
    'b5c92351-e11b-11e1-9b23-0800200c9a66': 'At Risk',
    'b5c92352-e11b-11e1-9b23-0800200c9a66': 'N/A'
}


class CsvExporter:
    """
    provides tools to convert single json audit to CSV

    Attributes:
        audit_json(json): audit to be converted to CSV
        audit_table(list): the audit data converted to a table
    """

    def __init__(self, audit_json):
        """
        Constructor

        :param audit_json:      audit in JSON format to be converted to CSV
        """
        self.audit_json = audit_json
        self.audit_table = self.convert_audit_to_table()

    def audit_id(self):
        """
        :return:    The audit ID
        """
        return self.audit_json['audit_id']

    def audit_items(self):
        """
        :return:    All audit items, including header and non-header items
        """
        return self.audit_json['header_items'] + self.audit_json['items']

    def audit_custom_response_id_to_label_map(self):
        """
        :return:     dictionary mapping custom response_id's to their label
        """
        custom_response_sets = self.audit_json['template_data']['response_sets']
        audit_custom_response_id_to_label_map = dict()
        for response_set in custom_response_sets.keys():
            for response in custom_response_sets[response_set][RESPONSES]:
                audit_custom_response_id_to_label_map[response['id']] = response[LABEL]
        return audit_custom_response_id_to_label_map

    def common_audit_data(self):
        """
        :return:    Selected sub-properties of the audit_data property of the audit JSON as a list
        """
        audit_data_property = self.audit_json['audit_data']
        template_data_property = self.audit_json['template_data']
        audit_date_completed = audit_data_property['date_completed']
        audit_data_as_list = list()
        audit_data_as_list.append(True if audit_date_completed else False)
        audit_data_as_list.append(audit_data_property['authorship']['owner'])
        audit_data_as_list.append(audit_data_property['authorship']['author'])
        audit_data_as_list.append(audit_data_property['name'])
        audit_data_as_list.append(audit_data_property[SCORE])
        audit_data_as_list.append(audit_data_property['total_score'])
        audit_data_as_list.append(audit_data_property[SCORE_PERCENTAGE])
        audit_data_as_list.append(audit_data_property['duration'])
        audit_data_as_list.append(self.format_date(audit_data_property['date_started']))
        audit_data_as_list.append(self.format_time(audit_data_property['date_started']))
        audit_data_as_list.append(self.format_date(audit_date_completed))
        audit_data_as_list.append(self.format_time(audit_date_completed))
        audit_data_as_list.append(self.audit_id())
        audit_data_as_list.append(self.audit_json['template_id'])
        audit_data_as_list.append(template_data_property['metadata']['name'])
        audit_data_as_list.append(template_data_property['authorship']['author'])
        return audit_data_as_list

    @staticmethod
    def format_date(date):
        """
        :param date:    date in the format: 2017-03-03T03:45:58.090Z
        :return:        date in the format: '03 March 2017',
        """
        if date:
            date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = date_object.strftime('%d %B %Y')
            return formatted_date
        else:
            return ''

    @staticmethod
    def format_time(date):
        """
        :param date:    date in the format: 2017-03-03T03:45:58.090Z
        :return:        time in the format '03:45AM'
        """
        if date:
            date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_time = date_object.strftime('%I:%M%p')
            return formatted_time
        else:
            return ''

    def convert_audit_to_table(self):
        """
        Collects all audit item responses, appends common audit data and returns a 2-dimensional list.

        :return:    2 dimensional list, each list is a single item, which corresponds to a single row
        """
        self.audit_table = []
        for item in self.audit_items():
            row_array = self.item_properties_as_list(item) + self.common_audit_data()
            self.audit_table.append(row_array)
        return self.audit_table

    def append_converted_audit_to_bulk_export_file(self, output_csv_path):
        """
        Appends audit data table to bulk export file at output_csv_path

        :param output_csv_path: The full path to the file to save
        """
        if not os.path.isfile(output_csv_path) and self.audit_table[0] != CSV_HEADER_ROW:
            self.audit_table.insert(0, CSV_HEADER_ROW)
        self.write_file(output_csv_path, 'ab')

    def save_converted_audit_to_file(self, output_csv_path, allow_overwrite):
        """
        Saves audit data table to a file at output_csv_path

        :param output_csv_path:     The full path to the file to save
        :param allow_overwrite:     if True, allow function to overwrite existing file
        """
        file_exists = os.path.isfile(output_csv_path)
        if file_exists and not allow_overwrite:
            sys.exit(
                'File already exists at ' + output_csv_path +
                '\nPlease set allow_overwrite to True in config.yaml file. See ReadMe.md for further instruction')
        elif file_exists and allow_overwrite:
            print 'Overwriting file at ' + output_csv_path
        elif self.audit_table[0] != CSV_HEADER_ROW:
            self.audit_table.insert(0, CSV_HEADER_ROW)
        self.write_file(output_csv_path, 'wb')

    def write_file(self, output_csv_path, mode):
        """
        Saves audit data table to a file at 'path'

        :param output_csv_path: the full path to file to save
        :param mode:    write ('wb') or append ('ab') mode
        """
        try:
            csv_file = open(output_csv_path, mode)
            wr = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_ALL)
            wr.writerows(self.audit_table)
            csv_file.close()
        except Exception as ex:
            print str(ex) + ': Error saving audit_table to ' + output_csv_path

    @staticmethod
    def get_json_property(obj, *args):
        """
        Returns json property if it exists. If it does not exist, returns an empty string
        :param obj:     JON Object
        :param args:    target path, list of keys
        :return:        if path exists, return value, otherwise return empty string
        """
        for arg in args:
            if isinstance(obj, list) and isinstance(arg, int):
                if len(obj) == 0:
                    return EMPTY_RESPONSE
                obj = obj[arg]
            elif isinstance(obj, dict) and arg in obj.keys():
                obj = obj[arg]
            else:
                return EMPTY_RESPONSE
        return obj if obj is not None else EMPTY_RESPONSE

    def get_item_response(self, item):
        """
        :param item:    single item in JSON format
        :return:        response property
        """
        response = EMPTY_RESPONSE
        item_type = self.get_json_property(item, TYPE)
        if item_type == 'question':
            response = self.get_json_property(item, RESPONSES, 'selected', 0, LABEL)
        elif item_type == 'list':
            for single_response in self.get_json_property(item, RESPONSES, 'selected'):
                if single_response:
                    response += self.get_json_property(single_response, LABEL) + '\n'
            response = response[:-1]
        elif item_type == 'address':
            response = self.get_json_property(item, RESPONSES, 'location_text')
        elif item_type == 'checkbox':
            response = bool(self.get_json_property(item, RESPONSES, 'value'))
        elif item_type == 'switch':
            response = self.get_json_property(item, RESPONSES, 'value')
        elif item_type == 'slider':
            response = self.get_json_property(item, RESPONSES, 'value')
        elif item_type == 'drawing':
            response = self.get_json_property(item, RESPONSES, 'image', 'media_id')
        elif item_type == MEDIA:
            for image in self.get_json_property(item, MEDIA):
                response += '\n' + self.get_json_property(image, 'media_id')
            if response:
                response = response[1:]
        elif item_type == SIGNATURE:
            response = self.get_json_property(item, RESPONSES, 'name')
        elif item_type == 'smartfield':
            response = self.get_json_property(item, 'evaluation')
        elif item_type == 'datetime':
            response = self.format_date(self.get_json_property(item, RESPONSES, 'datetime'))
            response = response + ' at ' + self.format_time(self.get_json_property(item, RESPONSES, 'datetime'))
        elif item_type == 'text' or item_type == 'textsingle':
            response = self.get_json_property(item, RESPONSES, 'text')
        elif item_type == INFORMATION and self.get_json_property(item, 'options', TYPE) == 'link':
            response = self.get_json_property(item, 'options', 'link')
        elif item_type in ['dynamicfield', 'element', 'primeelement', 'asset', 'scanner', 'category', 'section',
                           INFORMATION]:
            pass
        else:
            print 'Unhandled item type: ' + str(item_type) + ' from ' + \
                  self.audit_id() + ', ' + item.get(ID)
        return response

    def get_item_response_id(self, item):
        """
        :param item:    single item in JSON format
        :return:        response id property
        """
        response_id = EMPTY_RESPONSE
        item_type = self.get_json_property(item, TYPE)
        if item_type == 'question':
            response_id = self.get_json_property(item, RESPONSES, 'selected', 0, 'id')
        elif item_type == 'list':
            for single_response in self.get_json_property(item, RESPONSES, 'selected'):
                if single_response:
                    response_id += self.get_json_property(single_response, 'id') + '\n'
            response_id = response_id[:-1]
        return response_id

    def get_item_score(self, item):
        """
        retrieve score property from item

        :param item:    single item in JSON format
        :return:        score property or empty string if property does not exist
        """
        if isinstance(self.get_json_property(item, 'scoring', SCORE), int):
            return self.get_json_property(item, 'scoring', SCORE)
        elif isinstance(self.get_json_property(item, 'scoring', COMBINED_SCORE), int):
            return self.get_json_property(item, 'scoring', COMBINED_SCORE)
        else:
            return EMPTY_RESPONSE

    def get_item_max_score(self, item):
        """
        retrieve max score property from item

        :param item:    single item in JSON format
        :return:        max score property or empty string if property does not exist
        """
        if isinstance(self.get_json_property(item, 'scoring', MAX_SCORE), int):
            return self.get_json_property(item, 'scoring', MAX_SCORE)
        elif isinstance(self.get_json_property(item, 'scoring', COMBINED_MAX_SCORE), int):
            return self.get_json_property(item, 'scoring', COMBINED_MAX_SCORE)
        else:
            return EMPTY_RESPONSE

    def get_item_score_percentage(self, item):
        """
        retrieve score percentage property from item

        :param item:    single item in JSON format
        :return:        score percentage property or empty string if property does not exist
        """
        if isinstance(self.get_json_property(item, 'scoring', SCORE_PERCENTAGE), int):
            return self.get_json_property(item, 'scoring', SCORE_PERCENTAGE)
        elif isinstance(self.get_json_property(item, 'scoring', COMBINED_SCORE_PERCENTAGE), int):
            return self.get_json_property(item, 'scoring', COMBINED_SCORE_PERCENTAGE)
        else:
            return EMPTY_RESPONSE

    def get_item_label(self, item):
        """
        retrieve item label property

        :param item:    single item in JSON format
        :return:        label property
        """
        label = EMPTY_RESPONSE
        item_type = self.get_json_property(item, TYPE)
        if item_type == 'smartfield':
            custom_response_id_to_label_map = self.audit_custom_response_id_to_label_map()
            conditional_id = self.get_json_property(item, 'options', 'condition')
            if conditional_id:
                label = copy.deepcopy(smartfield_conditional_id_to_statement_map[conditional_id])
            for value in self.get_json_property(item, 'options', 'values'):
                label += '|'
                if value in standard_response_id_map.keys():
                    label += standard_response_id_map[value]
                elif value in custom_response_id_to_label_map.keys():
                    label += custom_response_id_to_label_map[value]
                else:
                    label += str(value)
                label += '|'
            return label
        else:
            return self.get_json_property(item, LABEL)

    def get_item_type(self, item):
        """
        :param item:    single item in JSON format
        :return:        item type property
        """
        item_type = self.get_json_property(item, TYPE)
        if item_type == INFORMATION:
            item_type += ' - ' + self.get_json_property(item, 'options', TYPE)
        return item_type

    def get_item_media(self, item):
        """
        :param item:    single item in JSON format
        :return:        item media href links
        """
        item_type = self.get_json_property(item, TYPE)
        if item_type == INFORMATION and self.get_json_property(item, 'options', TYPE) == MEDIA:
            media_href = self.get_json_property(item, 'options', MEDIA, HREF)
        elif item_type in ['drawing', SIGNATURE]:
            media_href = self.get_json_property(item, RESPONSES, 'image', HREF)
        else:
            media_href = '\n'.join(image[HREF] for image in self.get_json_property(item, MEDIA))
        return media_href

    def get_item_location_coordinates(self, item):
        """

        :param item:    single item in JSON format
        :return:        comma separated longitude and latitude coordinates
        """
        item_type = self.get_json_property(item, TYPE)
        if item_type == 'address':
            location_coordinates = self.get_json_property(item, 'responses', 'location', 'geometry', 'coordinates')
            if isinstance(location_coordinates, list):
                return str(location_coordinates).strip('[]')
        return EMPTY_RESPONSE

    def item_properties_as_list(self, item):
        """
        Returns selected properties of the audit item JSON as a list

        :param item:    single item in JSON format
        :return:        array of item data, in format that CSV writer can handle
        """
        return [
            self.get_item_type(item),
            self.get_item_label(item),
            self.get_item_response(item),
            self.get_json_property(item, RESPONSES, 'text') if item.get(TYPE) not in ['text',
                                                                                      'textsingle'] else EMPTY_RESPONSE,
            self.get_item_media(item),
            self.get_item_location_coordinates(item),
            self.get_item_score(item),
            self.get_item_max_score(item),
            self.get_item_score_percentage(item),
            self.get_json_property(item, 'options', 'is_mandatory'),
            self.get_json_property(item, RESPONSES, FAILED),
            self.get_json_property(item, INACTIVE),
            self.get_json_property(item, ID),
            self.get_item_response_id(item),
            self.get_json_property(item, PARENT_ID)
        ]


def main():
    """
    saves JSON file as CSV. Path to JSON file provided as command line argument
    """
    for arg in sys.argv[1:]:
        audit_json = json.load(open(arg, 'r'))
        csv_exporter = CsvExporter(audit_json)
        csv_exporter.save_converted_audit_to_file(os.path.splitext(arg.split('/')[-1])[0] + '.csv',
                                                  allow_overwrite=True)


if __name__ == '__main__':
    main()
