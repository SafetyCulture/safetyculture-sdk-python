import unicodecsv as csv
import json
import sys
import os
import copy

CSV_HEADER_ROW = [
    'Label',
    'Response',
    'Comments / Text',
    'Type',
    'Inactive',
    'Item Score',
    'Item Max Score',
    'Item Score Percentage',
    'Failed Response',
    'Item ID',
    'Parent ID',
    'Audit Owner',
    'Audit Name',
    'Audit Score',
    'Audit Max Score',
    'Audit Score Percentage',
    'Audit Duration',
    'Date Started',
    'Date Completed',
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
FAILED = 'failed'
SCORE = 'score'
MAX_SCORE = 'max_score'
SCORE_PERCENTAGE = 'score_percentage'
COMBINED_SCORE = 'combined_score'
COMBINED_MAX_SCORE = 'combined_max_score'
COMBINED_SCORE_PERCENTAGE = 'combined_score_percentage'
PARENT_ID = 'parent_id'
RESPONSE = 'response'

smartfield_conditional_id_to_statement_map = {
    # conditional statements for question item
    '3f206180-e4f6-11e1-aff1-0800200c9a66': 'if response selected',
    '3f206181-e4f6-11e1-aff1-0800200c9a66': 'if response not selected',
    '3f206182-e4f6-11e1-aff1-0800200c9a66': 'if response is',
    '3f206183-e4f6-11e1-aff1-0800200c9a66': 'if response is not',
    '3f206184-e4f6-11e1-aff1-0800200c9a66': 'if response is one of',
    '3f206185-e4f6-11e1-aff1-0800200c9a66': 'if response is not one of',
    # conditional statements for list item
    '35f6c130-e500-11e1-aff1-0800200c9a66': 'if response selected',
    '35f6c131-e500-11e1-aff1-0800200c9a66': 'if response not selected',
    '35f6c132-e500-11e1-aff1-0800200c9a66': 'if response is',
    '35f6c133-e500-11e1-aff1-0800200c9a66': 'if response is not',
    '35f6c134-e500-11e1-aff1-0800200c9a66': 'if response is one of',
    '35f6c135-e500-11e1-aff1-0800200c9a66': 'if resonse is not one of',
    # conditional statements for slider item
    'cda7c330-e500-11e1-aff1-0800200c9a66': 'if slider value is less than',
    'cda7c331-e500-11e1-aff1-0800200c9a66': 'if slider value is less than or equal to',
    'cda7c332-e500-11e1-aff1-0800200c9a66': 'if slider value is equal to',
    'cda7c333-e500-11e1-aff1-0800200c9a66': 'if slider value is not equal to',
    'cda7c334-e500-11e1-aff1-0800200c9a66': 'if slider value is greater than or equal to',
    'cda7c335-e500-11e1-aff1-0800200c9a66': 'if the slider value is greater than',
    'cda7c336-e500-11e1-aff1-0800200c9a66': 'if the slider value is between',
    'cda7c337-e500-11e1-aff1-0800200c9a66': 'if the slider value is not between',
    # conditional statements for checkbox item
    '4e671f40-e4ff-11e1-aff1-0800200c9a66': 'if the checkbox is checked',
    '4e671f41-e4ff-11e1-aff1-0800200c9a66': 'if the checkbox is not checked',
    # conditional statements for switch item
    '3d346f00-e501-11e1-aff1-0800200c9a66': 'if the switch is on',
    '3d346f01-e501-11e1-aff1-0800200c9a66': 'if the switch is off',
    # conditional statements for text item
    '7c441470-e501-11e1-aff1-0800200c9a66': 'text is',
    '7c441471-e501-11e1-aff1-0800200c9a66': 'text is not',
    # conditional statements for textsingle item
    '6ff300f0-e501-11e1-aff1-0800200c9a66': 'text is',
    '6ff300f1-e501-11e1-aff1-0800200c9a66': 'text is not',
    # conditional statements for signature item
    '831f8ff0-e500-11e1-aff1-0800200c9a66': 'if signature exists',
    '831f8ff1-e500-11e1-aff1-0800200c9a66': 'if the signature does not exist',
    '831f8ff2-e500-11e1-aff1-0800200c9a66': 'if the signature name is',
    '831f8ff3-e500-11e1-aff1-0800200c9a66': 'if the signature name is not'
}

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
            for response in custom_response_sets[response_set]['responses']:
                audit_custom_response_id_to_label_map[response['id']] = response['label']
        return audit_custom_response_id_to_label_map

    def common_audit_data(self):
        """
        :return:    Selected sub-properties of the audit_data property of the audit JSON as a list
        """
        audit_data_property = self.audit_json['audit_data']
        template_data_property = self.audit_json['template_data']
        audit_data_as_list = list()
        audit_data_as_list.append(audit_data_property['authorship']['owner'])
        audit_data_as_list.append(audit_data_property['name'])
        audit_data_as_list.append(audit_data_property[SCORE])
        audit_data_as_list.append(audit_data_property['total_score'])
        audit_data_as_list.append(audit_data_property[SCORE_PERCENTAGE])
        audit_data_as_list.append(audit_data_property['duration'])
        audit_data_as_list.append(audit_data_property['date_started'])
        audit_data_as_list.append(audit_data_property['date_completed'])
        audit_data_as_list.append(self.audit_id())
        audit_data_as_list.append(self.audit_json['template_id'])
        audit_data_as_list.append(template_data_property['metadata']['name'])
        audit_data_as_list.append(template_data_property['authorship']['author'])

        return audit_data_as_list

    def convert_audit_to_table(self):
        """
        Collects all audit item responses, appends common audit data and returns
        as a 2-dimensional list.

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

        :param output_csv_path:  The full path to the file to save
        """
        if os.path.isfile(output_csv_path) and not allow_overwrite:
            sys.exit(
                'File already exists at ' + output_csv_path +
                '\nPlease set allow_overwrite to True in confil.yaml file. See ReadMe.md for further instruction')
        elif os.path.isfile(output_csv_path) and allow_overwrite:
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
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for row in self.audit_table:
                wr.writerow(row)
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
                    return ''
                obj = obj[arg]
            elif (isinstance(obj, object) or isinstance(obj, dict)) and arg in obj.keys():
                obj = obj[arg]
            else:
                return ''
        return obj

    def get_item_response(self, item):
        """
        :param item:    single item in JSON format
        :return:        response property
        """
        response = ''
        if item.get('type') == 'question':
            response = self.get_json_property(item, 'responses', 'selected', 0, 'label')
        elif item.get('type') == 'list':
            for single_response in self.get_json_property(item, 'responses', 'selected'):
                if single_response:
                    response += self.get_json_property(single_response, 'label') + ','
            response = response[:-1]
        elif item.get('type') == 'address':
            for line in self.get_json_property(item, 'responses', 'location', 'formatted_address'):
                response += ','
                response += line
            if response != '':
                response = response[1:]
        elif item.get('type') == 'checkbox':
            response = self.get_json_property(item, 'responses', 'value')
        elif item.get('type') == 'switch':
            response = self.get_json_property(item, 'responses', 'value')
        elif item.get('type') == 'slider':
            response = self.get_json_property(item, 'responses', 'value')
        elif item.get('type') == 'drawing':
            response = self.get_json_property(item, 'responses', 'image', 'media_id')
        elif item.get('type') == 'media':
            for image in self.get_json_property(item, 'media'):
                response += ','
                response += self.get_json_property(image, 'media_id')
            if response != '':
                response = response[1:]
        elif item.get('type') == 'signature':
            response = self.get_json_property(item, 'responses', 'image', 'media_id')
        elif item.get('type') == 'smartfield':
            response = self.get_json_property(item, 'evaluation')
        elif item.get('type') == 'datetime':
            response = self.get_json_property(item, 'responses', 'datetime')
        elif item.get('type') in ['dynamicfield', 'element', 'primeelement', 'asset', 'scanner', 'category', 'text',
                                  'textsingle', 'section', 'information']:
            pass
        else:
            print 'Unhandled item type: ' + str(item.get('type')) + ' from ' + \
                  self.audit_id() + ', ' + item.get('item_id')
        return response

    def get_item_score(self, item, score_property_to_retrieve, combined_score_property_to_retrieve):
        """
        retrieve score property from item. There are three score properties for a given item,
        each of which may be either combined (score for multiple items, e.g. a section type item) or
        singular (score representing a single item, e.g. a question field)
            1. score and combined_score
            2. max_score or combined_max_score
            3. score_percentage or combined_score_percentage
        :param item:    single item in JSON format
        :param score_property_to_retrieve:  score property to retrieve it it exists
        :param combined_score_property_to_retrieve: combined_score property to retrieve it it exists
        :return:    score property or empty string if property does not exist
        """
        if isinstance(self.get_json_property(item, 'scoring', score_property_to_retrieve), int):
            return self.get_json_property(item, 'scoring', score_property_to_retrieve)
        elif isinstance(self.get_json_property(item, 'scoring', combined_score_property_to_retrieve), int):
            return self.get_json_property(item, 'scoring', combined_score_property_to_retrieve)
        else:
            return ''

    def get_item_label(self, item):
        """
        retrieve item label property

        :param item:    single item in JSON format
        :return:        label property
        """
        if self.get_json_property(item, 'type') == 'smartfield':
            custom_response_id_to_label_map = self.audit_custom_response_id_to_label_map()
            label = copy.deepcopy(
                smartfield_conditional_id_to_statement_map[self.get_json_property(item, 'options', 'condition')])
            for value in self.get_json_property(item, 'options', 'values'):
                label += '|'
                if value in standard_response_id_map.keys():
                    label += standard_response_id_map[value]
                elif value in custom_response_id_to_label_map.keys():
                    label += custom_response_id_to_label_map[value]
                label += '|'
            return label
        else:
            return self.get_json_property(item, LABEL)

    def item_properties_as_list(self, item):
        """
        Returns selected properties of the audit item JSON as a list

        :param item:    single item in JSON format
        :return:        array of item data, in format that CSV writer can handle
        """

        item_properties = {
            LABEL: self.get_item_label(item),
            COMMENTS: self.get_json_property(item, 'responses', 'text'),
            FAILED: self.get_json_property(item, 'responses', FAILED),
            SCORE: self.get_item_score(item, SCORE, COMBINED_SCORE),
            MAX_SCORE: self.get_item_score(item, MAX_SCORE, COMBINED_MAX_SCORE),
            SCORE_PERCENTAGE: self.get_item_score(item, SCORE_PERCENTAGE, COMBINED_SCORE_PERCENTAGE),
            PARENT_ID: self.get_json_property(item, PARENT_ID),
            RESPONSE: self.get_item_response(item)
        }

        return [item_properties[LABEL], item_properties[RESPONSE], item_properties[COMMENTS], item['type'],
                item_properties[SCORE],
                item_properties[MAX_SCORE], item_properties[SCORE_PERCENTAGE], item_properties[FAILED], item['item_id'],
                item_properties[PARENT_ID]]


def main():
    """
    Processes the audit JSON file givon on the command line and saves the converted CSV file to a file with the same
    name with CSV extension

    :param arg:     path to audit json file
    """
    for arg in sys.argv[1:]:
        audit_json = json.load(open(arg, 'r'))
        csv_exporter = CsvExporter(audit_json)
        csv_exporter.save_converted_audit_to_file(str(audit_json['audit_id']) + '.csv')


if __name__ == '__main__':
    main()
