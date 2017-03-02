import unicodecsv as csv
import json
import sys
import os

CSV_HEADER_ROW = [
    'Label',
    'Response',
    'Comments / Text',
    'Type',
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
    'Audit ID'
]

# audit item empty response 
EMPTY_RESPONSE = ''

# audit item property constants
COMMENTS = 'comments'
FAILED = 'failed'
SCORE = 'score'
MAX_SCORE = 'max_score'
SCORE_PERCENTAGE = 'score_percentage'
PARENT_ID = 'parent_id'
RESPONSE = 'response'


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

    def common_audit_data(self):
        """
        :return:    Selected sub-properties of the audit_data property of the audit JSON as a list
        """
        audit_data_property = self.audit_json['audit_data']
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

        :param path_to_export_file: The full path to the file to save
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
            sys.exit('File already exists at ' + output_csv_path + '\nPlease set allow_overwrite to True in confil.yaml file. See ReadMe.md for further instruction')
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
        :param item:    audit item JSON
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

    def item_properties_as_list(self, item):
        """
        Returns selected properties of the audit item JSON as a list

        :param item:    single item in JSON format
        :return:        array of item data, in format that CSV writer can handle
        """
        item_properties = {
            COMMENTS: self.get_json_property(item, 'responses', 'text'),
            FAILED: self.get_json_property(item, 'responses', FAILED),
            SCORE: self.get_json_property(item, 'scoring', SCORE) or self.get_json_property(item, 'scoring',
                                                                                            'combined_score'),
            MAX_SCORE: self.get_json_property(item, 'scoring', MAX_SCORE) or self.get_json_property(item, 'scoring',
                                                                                                    'combined_max_score'),
            SCORE_PERCENTAGE: self.get_json_property(item, 'scoring', SCORE_PERCENTAGE) \
                              or self.get_json_property(item, 'scoring', 'combined_score_percentage'),
            PARENT_ID: self.get_json_property(item, PARENT_ID),
            RESPONSE: self.get_item_response(item)}

        return [item['label'], item_properties[RESPONSE], item_properties[COMMENTS], item['type'],
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
