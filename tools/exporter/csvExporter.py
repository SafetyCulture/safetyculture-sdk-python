import unicodecsv as csv

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

def path(obj, *args):
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


def generateCsvRowItemData(item):
    """
    :param item:
    :return:
    """

    fields = {
        'comments': '',
        'failed' : '',
        'score' : '',
        'maxScore' : '',
        'scorePercentage' : '',
        'parent_id' : '',
        'response' : ''
    }

    fields['parent_id'] = path(item, 'parent_id')
    fields['failed'] = path(item, 'responses', 'failed')

    fields['score'] = path(item, 'scoring', 'score')
    fields['maxScore'] = path(item, 'scoring', 'max_score')
    fields['scorePercentage'] = path(item, 'scoring', 'score_percentage')

    if fields['score'] == '':
        fields['score'] = path(item, 'scoring', 'combined_score')
        fields['maxScore'] = path(item, 'scoring', 'combined_max_score')
        fields['scorePercentage'] = path(item, 'scoring', 'combined_score_percentage')

    fields['comments'] = path(item, 'responses', 'text')

    if item['type'] == 'section':
        handle_section_field(item, fields)
    elif item['type'] == 'category':
        handle_category_field(item, fields)
    elif item['type'] == 'text':
        handle_text_field(item, fields)
    elif item['type'] == 'textsingle':
        handle_textsingle_field(item, fields)
    elif item['type'] == 'question':
        handle_question_field(item, fields)
    elif item['type'] == 'list':
        handle_list_field(item, fields)
    elif item['type'] == 'address':
        handle_address_field(item, fields)
    elif item['type'] == 'checkbox':
        handle_checkbox_field(item, fields)
    elif item['type'] == 'switch':
        handle_switch_field(item, fields)
    elif item['type'] == 'slider':
        handle_slider_field(item, fields)
    elif item['type'] == 'drawing':
        handle_drawing_field(item, fields)
    elif item['type'] == 'information':
        handle_information_field(item, fields)
    elif item['type'] == 'media':
        handle_media_field(item, fields)
    elif item['type'] == 'signature':
        handle_signature_field(item, fields)
    elif item['type'] == 'smartfield':
        handle_smartfield_field(item, fields)
    elif item['type'] == 'dynamicfield':
        handle_dynamicfield_field(item, fields)
    elif item['type'] == 'element':
        handle_element_field(item, fields)
    elif item['type'] == 'primeelement':
        handle_primeelement_field(item, fields)
    elif item['type'] == 'datetime':
        handle_datetime_field(item, fields)
    elif item['type'] == 'asset':
        handle_asset_field(item, fields)
    elif item['type'] == 'scanner':
        handle_scanner_field(item, fields)
    else:
        print 'Unhandled item type: ' + str(item['type'])

    return [item['label'], fields['response'], fields['comments'], item['type'], fields['score'], fields['maxScore'],
            fields['scorePercentage'], fields['failed'], item['item_id'], fields['parent_id']]


def handle_question_field(item, fields):
    fields['response'] = path(item, 'responses', 'selected', 0, 'label')
def handle_list_field(item, fields):
    for response in path(item, 'responses', 'selected'):
        if response:
            fields['response'] += str(path(response, 'label')) + ','
            fields['response'] = fields['response'][:-1]
def handle_textsingle_field(item, fields):
    pass
def handle_text_field(item, fields):
    pass
def handle_datetime_field(item, fields):
    fields['response'] = path(item, 'responses', 'datetime')
def handle_slider_field(item, fields):
    fields['response'] = path(item, 'responses', 'value')
def handle_drawing_field(item, fields):
    fields['response'] = path(item, 'responses', 'image', 'media_id')
def handle_checkbox_field(item, fields):
    fields['response'] = path(item, 'responses', 'value')
def handle_switch_field(item, fields):
    fields['response'] = path(item, 'responses', 'value')
def handle_address_field(item, fields):
    # longitude, latitude approach
    # fields['response'] = str(path(item, 'responses', 'location', 'geometry', 'coordinates', 0)) + ',' + \
    # str(path(item, 'responses', 'location', 'geometry', 'coordinates', 1))
    # if fields['response'] == ',':
    #     fields['responses'] = ''
    for line in path(item, 'responses', 'location', 'formatted_address'):
        fields['response'] += ','
        fields['response'] += line
    if fields['response'] != '':
            fields['response'] = fields['response'][1:]
def handle_signature_field(item, fields):
    fields['response'] = path(item, 'responses', 'image', 'media_id')
def handle_media_field(item, fields):
    for image in path(item, 'media'):
        fields['response'] += ','
        fields['response'] += path(image, 'media_id')
    if fields['response'] != '':
        fields['response'] = fields['response'][1:]
def handle_scanner_field(item, fields):
    pass
def handle_weather_field(item, fields):
    pass
def handle_asset_field(item, fields):
    pass
def handle_section_field(item, fields):
    pass
def handle_category_field(item, fields):
    pass
def handle_information_field(item, fields):
    pass
def handle_dynamic_field(item, fields):
    pass
def handle_smartfield_field(item, fields):
    fields['response'] = path(item, 'evaluation')
def handle_element_field(item, fields):
    pass
def handle_primeelement_field(item, fields):
    pass
def handle_dynamicfield_field(item, fields):
    pass

def generateCsvRowMetadata(metadata, id):
    """
    :param metadata:
    :param id:
    :return:
    """
    metadataArray = []
    metadataArray.append(metadata['authorship']['owner'])
    metadataArray.append(metadata['name'])
    metadataArray.append(metadata['score'])
    metadataArray.append(metadata['total_score'])
    metadataArray.append(metadata['score_percentage'])
    metadataArray.append(metadata['duration'])
    metadataArray.append(metadata['date_started'])
    metadataArray.append(metadata['date_completed'])
    metadataArray.append(id)
    return metadataArray


def getItemsAndMetadata(audit):
    """

    :param audit:
    :return:
    """
    # add try / catch statement here
    metadata = audit['audit_data']
    # items = audit['header'] + audit['items'] -- this works when exported form sync-gateway
    items = audit['header_items'] + audit['items']
    return (metadata, items)


def create_file(file_name):
    """
    :return:
    """
    csvFile = open(file_name, 'wb')
    wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
    return wr

def remove_newline(rowArray):
    i = 0
    for cell in rowArray:
        if isinstance(cell, basestring):
            cell = cell.replace('\n', ',')
        rowArray[i] = cell
        i += 1

def exportAuditsToCSV(audit_json):
    """
    generate a CSV file from multiple audits with an item per row and each with audit metadata.

    :param audit_json:	audit data to export as CSV
    """
    wr = create_file('temp.csv')
    id = audit_json['audit_id']
    metadataAndItems = getItemsAndMetadata(audit_json)
    metadata = metadataAndItems[0]
    items = metadataAndItems[1]
    metadataArray = generateCsvRowMetadata(metadata, id)

    for item in items:
        itemArray = generateCsvRowItemData(item)
        rowArray = itemArray + metadataArray
        remove_newline(rowArray)
        wr.writerow(rowArray)


def add_header(data):
    header_string = ''
    for item in CSV_HEADER_ROW:
        header_string = header_string + item + ','
    header_string = header_string[:-1]
    header_string += '\n'
    return header_string + data