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

def main():
    for arg in sys.argv[1:]:
        audit_json = sc_sdk.get_audit(arg)
        # name = raw_input('What do you want to name the json file: ')
        name = audit_json['template_data']['metadata']['name'] + '_' + audit_json['audit_data']['name']
        name = name.replace(' ', '_')
        test_number = str(get_test_number() + 1)
        name_root = os.path.splitext(name)[0]
        unit_test_fxn_name = 'test_' + name_root
        json_name = 'unit_test_' + name_root + '.json'
        with open ('csv_test_files/' + json_name, 'wb') as outfile:
            json.dump(audit_json, outfile, indent = 4)
        csv_name = 'unit_test_' + name_root + '_expected_output.csv'
        csv_sdk = csv_e.CsvExporter(audit_json)
        csv_sdk.save_converted_audit_to_file('csv_test_files/' + csv_name, allow_overwrite=True)
        read_existing_test_code = open('test_csv_exporter.py', 'r')
        lines = read_existing_test_code.readlines()
        lines = lines[:-3]
        read_existing_test_code.close()
        lines.append('    def ' + unit_test_fxn_name + '(self):\n')
        lines.append('        csv_exporter = csv.CsvExporter(json.load(open(os.path.join(self.path_to_test_files, ' + "'" + json_name + "'), 'r')))\n")
        lines.append("        csv_exporter.save_converted_audit_to_file('test " + test_number + ".csv', allow_overwrite=True)\n")
        lines.append("        self.assertEqual(open('test " + test_number + ".csv', 'r').read(), open(os.path.join(self.path_to_test_files, '" + csv_name + "'), 'r').read())\n")
        lines.append("        os.remove('test " + test_number + ".csv')\n\n\n")
        lines.append("if __name__ == '__main__':\n")
        lines.append("    unittest.main()\n")
        write_code = open('test_csv_exporter.py', 'w')
        write_code.writelines(lines)
        write_code.close()


if __name__ == '__main__':
    main()
