import sys
import os
import json

sys.path.append('/Users/tonyoreglia/safetyculture-sdk-python/safetypy/')
import safetypy as spi


sys.path.append('/Users/tonyoreglia/safetyculture-sdk-python/tools/exporter/')
import csvExporter as csv_e
sc_sdk = spi.SafetyCulture('e40c9502d89c63796b41dfe1e32b550b2237be9dbfdd5eec1172e1314c6d483f')

def get_test_number():
    count = 0
    with open('test_csv_exporter.py', 'r') as script:
        lines = script.readlines()
    for line in lines:
        if line.strip(' ').startswith('def'):
            count += 1
    script.close()
    return count

def remove_existing_csv_files():
    files = os.listdir('csv_test_files/')
    for file in files:
        if file.endswith('.csv'):
            os.remove('csv_test_files/' + file)


def update_argv_with_all_json_test_files():
    argv = []
    files = os.listdir("csv_test_files/")
    for file in files:
        if file.endswith('.json'):
            argv.append(file)
    return argv

def clean(config):
    response = raw_input("are you sure you want to remake all test files? ")
    if response in ['yes', 'y', 'Yes', 'Y']:
        remove_existing_csv_files()
        argv = update_argv_with_all_json_test_files()
        config['use_existing_unittest'] = True
        config['auto_create_name'] = True
        config['cleaning'] = True
        return argv
    else:
        print 'OK, exiting now'
        quit()

def update_config_settings(arg, config):
    if arg == 'auto_create_name':
        config['auto_create_name'] = True
    elif arg == 'use_existing_unittest':
        config['use_existing_unittest'] = True
    elif arg.endswith('.json'):
        config['is_json'] = True
        config['audit_json'] = json.load(open('csv_test_files/' + arg, 'rb'))
        config['auto_create_name'] = True
    elif arg.startswith('audit_'):
        config['is_audit_id'] = True
        config['audit_json'] = sc_sdk.get_audit(arg)
    else:
        print 'bad arg: ' + arg
        exit()

def set_unit_test_name(arg, config):
    if config['auto_create_name'] and config['is_audit_id']:
        name = config['audit_json']['template_data']['metadata']['name'] + '_' + config['audit_json']['audit_data'][
            'name']
        name = name.replace(' ', '_').replace('-', '_').replace(',', '_').replace(':','').replace('___', '_').replace('__', '_')
        name = 'unit_test_' + name
    elif config['is_json']: # json must use autocreate name
        name = os.path.splitext(arg)[0]
    else:
        name = raw_input('What do you want to name the json file for ' + arg + ': ')
        name = os.path.splitext(name)[0]
        name = name.replace(' ', '_').replace('-', '_').replace(',', '_').replace('___', '_').replace('__', '_')
    config['name_root'] = name
    config['unit_test_name'] = 'test_' + name

def write_unit_test(config):
    if not config['use_existing_unittest']:
        test_number = str(get_test_number() + 1)
        read_existing_test_code = open('test_csv_exporter.py', 'r')
        lines = read_existing_test_code.readlines()
        lines = lines[:-3]
        read_existing_test_code.close()
        lines.append('    def ' + config['unit_test_name'] + '(self):\n')
        lines.append(
            '        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, ' + "'" + config['json_name'] + "'), 'r')))\n")
        lines.append(
            "        csv_exporter.save_converted_audit_to_file('test " + test_number + ".csv', allow_overwrite=True)\n")
        lines.append(
            "        self.assertEqual(open('test " + test_number + ".csv', 'r').read(), open(os.path.join(self.path_to_test_files, '" + config['csv_name'] + "'), 'r').read())\n")
        lines.append("        os.remove('test " + test_number + ".csv')\n\n\n")
        lines.append("if __name__ == '__main__':\n")
        lines.append("    unittest.main()\n")
        write_code = open('test_csv_exporter.py', 'w')
        write_code.writelines(lines)
        write_code.close()

def reset_config_settings(config):
    config['is_json'] = False
    config['is_audit_id'] = False
    config['audit_json'] = None
    config['name_root'] = None
    config['unit_test_name'] = None
    config['json_name'] = None
    config['csv_name'] = None

def main():
    """
    Takes an audit_id and builds all necessary code and resources files for a unit test
    * writes JSON file to csv_test_files directory
    * writes CSV file to csv_test_files directory
    * writes unit test to test_csv_exporter.py, unless use_existing_unit_test specified as argument
    """
    config = {
    'auto_create_name' : False,
    'use_existing_unittest' : False,
    'is_audit_id' : False,
    'is_json' : False,
    'cleaning' : False,
    'audit_json': None,
    'name_root': None,
    'unit_test_name': None,
    'json_name': None,
    'csv_name': None
    }

    if sys.argv[1] == 'CLEAN':
        argv = clean(config)
    else:
        argv = sys.argv[1:]
        if len(argv) == 1:
            print 'No arguments given'

    for arg in argv:
        reset_config_settings(config)
        update_config_settings(arg, config)
        if arg in ['auto_create_name', 'use_existing_unittest']:
            continue
        set_unit_test_name(arg, config)

        config['json_name'] = config['name_root'] + '.json'
        config['csv_name'] = config['name_root'] + '_expected_output.csv'

        # write csv file
        csv_sdk = csv_e.CsvExporter(config['audit_json'])
        csv_sdk.save_converted_audit_to_file('csv_test_files/' + config['csv_name'], allow_overwrite=True)

        if config['cleaning']:
            continue

        if not config['is_json']:
            with open('csv_test_files/' + config['json_name'], 'wb') as json_path_to_file:
                json.dump(config['audit_json'], json_path_to_file, indent=4)

        if not config['use_existing_unittest']:
            write_unit_test(config)


if __name__ == '__main__':
    main()
