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

COMMENTS = 'comments'
FAILED = 'failed'
SCORE = 'score'
MAX_SCORE = 'maxScore'
SCORE_PERCENTAGE = 'scorePercentage'
PARENT_ID = 'parent_id'
RESPONSE = 'response'
BLANK = ''


class CsvExporter:
    def __init__(self, audit_json):
        self.audit_json = audit_json
        self.audit_id = audit_json['audit_id']
        audit_data_and_items = self.get_items_and_auditdata()
        self.auditdata = audit_data_and_items[0]
        self.items = audit_data_and_items[1]
        self.auditdata_array = self.retrieve_auditdata()
        self.data = self.process_items()

    def process_items(self):
        self.data = []
        for item in self.items:
            item_array = self.generate_csv_row_item_data(item)
            row_array = item_array + self.auditdata_array
            self.data.append(row_array)
        return self.data

    def write(self, path, filename, write_or_append='wb'):
        file_path = os.path.join(path, filename + '.csv')
        if not os.path.isfile(file_path) or write_or_append == 'wb':
            self.data.insert(0, CSV_HEADER_ROW)
        try:
            self.csv_file = open(file_path, write_or_append)
            wr = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)
        except Exception as ex:
            print str(ex) + ': Exception while writing' + filename + ' to file'
        for row in self.data:
            wr.writerow(row)
        self.csv_file.close()

    def path(self, obj, *args):
        """
        Check for the existence of path for a given JSON object
        :param obj:     JSON Object
        :param args:    target path, list of keys
        :return:        if path exists, return value, otherwise return empty string
        """
        for arg in args:
            if isinstance(obj, list) and isinstance(arg, int):
                if len(obj) == 0:
                    return ''
                obj = obj[arg]
            elif arg in obj.keys():
                obj = obj[arg]
            else:
                return ''
        return obj

    # noinspection PyDictCreation
    def generate_csv_row_item_data(self, item):
        """
        Process item JSON data into array that CSV writer can handle
        :param item:    single item in JSON format
        :return:        array of item data, in format that CSV writer can handle
        """

        fields = {
            COMMENTS: BLANK,
            FAILED: BLANK,
            SCORE: BLANK,
            MAX_SCORE: BLANK,
            SCORE_PERCENTAGE: BLANK,
            PARENT_ID: BLANK,
            RESPONSE: BLANK
        }

        # all fields have a parent id, grab this and insert into fields dictionary
        fields[PARENT_ID] = self.path(item, 'parent_id')
        # if failed key exists, insert value into dictionary
        fields[FAILED] = self.path(item, 'responses', 'failed')

        # check if this item has score information. insert data into dictionary
        fields[SCORE] = self.path(item, 'scoring', 'score') or self.path(item, 'scoring', 'combined_score')
        fields[MAX_SCORE] = self.path(item, 'scoring', 'max_score') or self.path(item, 'scoring', 'combined_max_score')
        fields[SCORE_PERCENTAGE] = self.path(item, 'scoring', 'score_percentage') \
                                   or self.path(item, 'scoring', 'combined_score_percentage')

        fields[COMMENTS] = self.path(item, 'responses', 'text')

        if item.get('type') == 'section':
            self.handle_section_field(item, fields)
        elif item.get('type') == 'category':
            self.handle_category_field(item, fields)
        elif item.get('type') == 'text':
            self.handle_text_field(item, fields)
        elif item.get('type') == 'textsingle':
            self.handle_textsingle_field(item, fields)
        elif item.get('type') == 'question':
            self.handle_question_field(item, fields)
        elif item.get('type') == 'list':
            self.handle_list_field(item, fields)
        elif item.get('type') == 'address':
            self.handle_address_field(item, fields)
        elif item.get('type') == 'checkbox':
            self.handle_checkbox_field(item, fields)
        elif item.get('type') == 'switch':
            self.handle_switch_field(item, fields)
        elif item.get('type') == 'slider':
            self.handle_slider_field(item, fields)
        elif item.get('type') == 'drawing':
            self.handle_drawing_field(item, fields)
        elif item.get('type') == 'information':
            self.handle_information_field(item, fields)
        elif item.get('type') == 'media':
            self.handle_media_field(item, fields)
        elif item.get('type') == 'signature':
            self.handle_signature_field(item, fields)
        elif item.get('type') == 'smartfield':
            self.handle_smartfield_field(item, fields)
        elif item.get('type') == 'dynamicfield':
            self.handle_dynamicfield_field(item, fields)
        elif item.get('type') == 'element':
            self.handle_element_field(item, fields)
        elif item.get('type') == 'primeelement':
            self.handle_primeelement_field(item, fields)
        elif item.get('type') == 'datetime':
            self.handle_datetime_field(item, fields)
        elif item.get('type') == 'asset':
            self.handle_asset_field(item, fields)
        elif item.get('type') == 'scanner':
            self.handle_scanner_field(item, fields)
        else:
            print 'Unhandled item type: ' + str(item.get('type')) + ' from ' + self.audit_id + ', ' + item.get(
                'item_id')

        return [item['label'], fields['response'], fields['comments'], item['type'], fields['score'],
                fields['maxScore'],
                fields['scorePercentage'], fields['failed'], item['item_id'], fields['parent_id']]

    def handle_question_field(self, item, fields):
        """
        retrieve information specific to question field, populate fields dictionary with data
        :param item:        single question type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'selected', 0, 'label')

    def handle_list_field(self, item, fields):
        """
        retrieve information specific to list field, populate fields dictionary with data
        :param item:        single list type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        for response in self.path(item, 'responses', 'selected'):
            if response:
                fields['response'] += self.path(response, 'label') + ','
                fields['response'] = fields['response'][:-1]

    def handle_datetime_field(self, item, fields):
        """
        retrieve information specific to datetime field, populate fields dictionary with data
        :param item:        single datetime type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'datetime')

    def handle_slider_field(self, item, fields):
        """
        retrieve information specific to slider field, populate fields dictionary with data
        :param item:        single slider type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'value')

    def handle_drawing_field(self, item, fields):
        """
        retrieve information specific to drawing field, populate fields dictionary with data
        :param item:        single drawing type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'image', 'media_id')

    def handle_checkbox_field(self, item, fields):
        """
        retrieve information specific to checkbox field, populate fields dictionary with data
        :param item:        single checkbox type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'value')

    def handle_switch_field(self, item, fields):
        """
        retrieve information specific to switch field, populate fields dictionary with data
        :param item:        single switch type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'value')

    def handle_address_field(self, item, fields):
        """
        retrieve formatted address information from address field, populate fields dictionary with data
        :param item:        single address type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        for line in self.path(item, 'responses', 'location', 'formatted_address'):
            fields['response'] += ','
            fields['response'] += line
        if fields['response'] != '':
            fields['response'] = fields['response'][1:]

    def handle_signature_field(self, item, fields):
        """
        retrieve information specific to signature field, populate fields dictionary with data
        :param item:        single signature type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'responses', 'image', 'media_id')

    def handle_media_field(self, item, fields):
        """
        retrieve information specific to media field, populate fields dictionary with data
        :param item:        single media type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        for image in self.path(item, 'media'):
            fields['response'] += ','
            fields['response'] += self.path(image, 'media_id')
        if fields['response'] != '':
            fields['response'] = fields['response'][1:]

    def handle_smartfield_field(self, item, fields):
        """
        retrieve information specific to smartfield field, populate fields dictionary with data
        :param item:        single smartfield type item in JSON format
        :param fields:      dictionary of keys whose corresponding data we want to export to CSV
        :return:            fields dic is passed as reference, so updates are global
        """
        fields['response'] = self.path(item, 'evaluation')

    def handle_textsingle_field(self, item, fields):
        pass

    def handle_text_field(self, item, fields):
        pass

    def handle_scanner_field(self, item, fields):
        pass

    def handle_weather_field(self, item, fields):
        pass

    def handle_asset_field(self, item, fields):
        pass

    def handle_section_field(self, item, fields):
        pass

    def handle_category_field(self, item, fields):
        pass

    def handle_information_field(self, item, fields):
        pass

    def handle_dynamic_field(self, item, fields):
        pass

    def handle_element_field(self, item, fields):
        pass

    def handle_primeelement_field(self, item, fields):
        pass

    def handle_dynamicfield_field(self, item, fields):
        pass

    def retrieve_auditdata(self):
        """
        Generate audit_data CSV data, this is appended to every row for a given Audit
        :return:            metdata array in format the csv writer can handle
        """
        auditdata_array = list()
        auditdata_array.append(self.auditdata['authorship']['owner'])
        auditdata_array.append(self.auditdata['name'])
        auditdata_array.append(self.auditdata['score'])
        auditdata_array.append(self.auditdata['total_score'])
        auditdata_array.append(self.auditdata['score_percentage'])
        auditdata_array.append(self.auditdata['duration'])
        auditdata_array.append(self.auditdata['date_started'])
        auditdata_array.append(self.auditdata['date_completed'])
        auditdata_array.append(self.audit_id)
        return auditdata_array

    def get_items_and_auditdata(self):
        """
        Retrieve raw JSON Items and Auditdata list from Audit JSON. This is the data to be processed into CSV format
        :return:        Tuple with auditdata JSON and items JSON
        """
        # add try / catch statement here
        auditdata = self.audit_json['audit_data']
        # items = audit['header'] + audit['items'] -- this works when exported form sync-gateway
        items = self.audit_json['header_items'] + self.audit_json['items']
        return auditdata, items


def main():
    for arg in sys.argv[1:]:
        audit_json = json.load(open(arg, 'r'))
        csv_exporter = CsvExporter(audit_json)
        csv_exporter.write('', audit_json.get('audit_id'))


if __name__ == '__main__':
    main()
