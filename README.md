# SafetyCulture Python SDK and iAuditor Tools

# Beta Branch
| WARNING: This branch contains beta features for the exporter tool as well as some tweaks to safetypy. We do not currently offer support on the additional features found here. |
| --- |

Features added:

* Initial database support. This is provided by SQLAlchemy and has been tested with SQL and PostgresSQL
* Exporting to a PKL/Pickle
* Exporting only particular templates (Give them as a comma seperated list in the config file)
* Name the template CSV files with the template name inside of the template ID
* last_successful text files are appended with the sql_table parameter to make it easier to manage multiple configurations



Contains:

* The SafetyCulture Python SDK: core functions to interact with the iAuditor API

* The iAuditor Export Tool for exporting audit data to your computer

* The Import Global Response Set (GRS) Tool for importing and updating response sets from a spreadsheet

* The Export Users Tool to export a list of all users and their groups from iAuditor into a spreadsheet

* The Sync Users Tool allows you to use a spreadsheet to keep your users and their group associations up to date and automatically reflect that in iAuditor.

* Examples of how to import individual modules of the SDK into your own scripts.

## iAuditor Export Tool

### First Time Install and Run

You will need to have [Python 2.7 or higher](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installing/) installed on your computer. If you are using Windows, make sure to select the option to "Add Python to PATH" during the installation process. Also, Windows users may need to prepend the following commands with
```
python -m
```
i.e.
```
python -m pip install safetyculture-sdk-python
```

To install the Python SDK, run the following commands from your terminal:

1. Install the SDK and tools
```
pip install safetyculture-sdk-python
```

2. Setup (creates `config.yaml` file in new folder `iauditor_exports_folder`)
```
iauditor_exporter --setup
```

3. Navigate into to the newly created folder
```
cd iauditor_exports_folder
```

4. Run the tool to export PDF reports of all your audits (for other formats see later sections in this tutorial)
```
iauditor_exporter
```

### Upgrading from an Older Version of the Exporter Tool

**Option 1 (re-use existing exports folder)**

Install the latest version of the SDK and Export Tool (you may need to substitute pip with pip3 depending on your configuration):
```
pip install safetyculture-sdk-python
```

If the above command reports that everything is already up to date, run with the force command:
```
pip install safetyculture-sdk-python --force
```



Then navigate into your existing exporter folder. This is located within the cloned repository at `safetyculture-sdk-python/tools/exporter`
and run `iauditor_exporter` from there. Export data will be saved in the existing `exports` folder, and the existing `last_successful.txt` file will
be used to pick up where the last export left off.

**Option 2 (re-use existing exports folder)**

Get the latest version of the code by navigating into `safetyculture-sdk-python` and running
```
git pull
```
Navigate into `safetyculture-sdk-python/tools/exporter`
Run the iAuditor export tool directly:
```
python exporter.py
```

**Option 3 (export audits in new folder)**

Follow the instructions above to start exporting data to the new folder named `iauditor_exports_folder`. The setup script will give you the option to start your exports from the
current date and time, so that you do not have to re-export older audits.


### How to use the iAuditor Export Tool

The API token saved in `config.yaml` provides access to data associated with a single account. Namely, the account used to generate the API token.
Only audits that are accessible to the single iAuditor account associated with the iAuditor API token used are available for exporting.

All exported data is saved in a folder called `exports`. The folder will be created in the current working directory if it does not already exist.

To export all completed audits in PDF format, run
```
iauditor_exporter
```

To enable the exporter to run continuously until interrupted, use the loop command line argument

```
iauditor_exporter --loop
```

To specify the export format explicitly run

```
iauditor_exporter --format pdf
```

More than one supported formats can be exported at once e.g.

```
iauditor_exporter --format  pdf  docx  json  csv  media  web-report-link  actions
```

Note:
* Unless you start the tool with the --loop argument, it will sync documents once and terminate
* Only completed audits will be exported
* Only audits that are owned by or shared with the iAuditor user account that generated the API token will be exported
* Up to 1000 audits will be exported each sync cycle. If more than 1000 audits exist they will be retrieved automatically in subsequent sync cycles

### CSV Export

#### Bulk CSV Export

For an overview of the CSV format used, see [here](https://support.safetyculture.com/integrations/safetyculture-csv-exporter-tool/#format)

Audits built from the same template will be saved in the same CSV file which is named after the template's unique ID number.
i.e. `TEMPLATE_ID.csv`

To export multiple audits in bulk to a CSV file, run the `iauditor_exporter` with the format option set to CSV:
```
iauditor_exporter --format csv
```
#### The format of the following CSV values do not match the format used by the SafetyCulture API Audit JSON

##### Date/Time field
* JSON: `2017-03-03T03:45:58.090Z`
* CSV:  `03 March 2017 03:45 AM`

##### Checkbox field
* JSON: `1` or `0`
* CSV:  `True` or `False`

##### Media List, Multiple Choice Responses
* JSON: List Object
* CSV:  Newline separated values in single cell

#### Bulk CSV Export Gotchas
* If you update an Audit that has already been exported, it may be appended to the CSV file a second time.
* If you update a template, Audits with the new format will be appended to the same CSV file.

### Media Export
* Running
```
iauditor_exporter --format media
```
will export all audit media files for each audit (images, attachments, signature, and drawings) to a folder named after the audit ID.

### Web Report Link Export
* Running
```
iauditor_exporter --format web-report-link
```
will export your Web Report Links to a CSV file named `web-report-links.csv`.

The CSV file includes five columns: Template ID, Template Name, Audit ID, Audit Name, and Web Report Link.

### Actions Export
Running
```
iauditor_exporter --format actions
```
will export all actions to a file named `iauditor_actions.csv`

The actions export tool reads and writes to a file named `last_successful_actions_export.txt` to keep track of what actions have already been exported.
If it does not already exist, `last_successful_actions_export.txt` is created.

Each time actions are exported, newly created actions are appended to `iauditor_actions.csv`. Additionally, any existing actions that have been modified since the last
time actions were exported will be re-appended to the CSV file.  

`iauditor_actions.csv` consists of the following columns
- actionId
- description
- assignee
- priority
- priorityCode
- status
- statusCode
- due_datetime
- audit
- auditId
- linkedToItem
- linkedToItemId
- creatorName
- creatorId
- createdDatetime
- modifiedDatetime
- completedDatetime

The fields `priorityCode` and `statusCode` are number values. All other fields are string values.  
See [here](https://developer.safetyculture.io/#search-actions) for more information about the status codes and priority codes.

## Export settings

To override default export settings edit config.yaml in this directory.

Things you can configure:

|  Setting | Description  |
|---|---|
| export_path  | absolute or relative path to the directory where to save exported data to  |
| filename  |  an audit item ID whose response is going to be used to name the files of exported audit reports. Can only be an item with a response type of `text` from the header section of the audit such as Audit Title, Document No., Client / Site, Prepared By, Personnel, or any custom header item which has a 'text' type response (doesn't apply when exporting as CSV) |
| preferences  | to apply a preference transformation to particular templates, give here a list of preference ids
| sync_delay_in_seconds | time in seconds to wait after completing one export run, before running again
| export_inactive_items | This setting only applies when exporting to CSV. Valid values are true (export all items) or false (do not export inactive items). Items that are nested under [Smart Field](https://support.safetyculture.com/templates/smart-fields/) will be 'inactive' if the smart field condition is not satisfied for these items.
| media_sync_offset_in_seconds | time in seconds since an audit has been modified before it will by synced

Here is an example customised config.yaml:

```
API:
    token: YOUR_IAUDITOR_API_TOKEN
export_options:
    export_path: /Users/Monty/Dropbox
    filename: f3245d40-ea77-11e1-aff1-0800200c9a66
    csv:
        export_inactive_items: false
preferences:
    template_3E631E46F466411B9C09AD804886A8B4:E15A6525-EFA5-4835-92F0-D11CA9F364F3
    template_3E631E46F466411B9C09AD804886A8B4:E50645A1-2851-4E92-B4EA-60C5CE7981BE
    ...
    ...
sync_delay_in_seconds: 36000
media_sync_offset_in_seconds: 600
```

Note: Templates for which there is no preference id listed in the config file will be exported without a preference applied

### Naming the exported files

(Doesn't apply when exporting as CSV - names are always the template ID.)

Note that when automatic Audit Title rules are set on the template, the Audit will not contain an Audit Title field by default. Regardless, the export filename setting will still work as expected using the automatically generated Audit name.

When configuring a custom filename convention in export settings (in `config.yaml`) you can provide an audit item ID from the ones below to cause all exported audit reports be named after the response of that particular item in the audit.

Here are some standard item IDs

| Item Name| Item ID|
|---|---|
|Audit Title |f3245d40-ea77-11e1-aff1-0800200c9a66|
|Conducted By |f3245d43-ea77-11e1-aff1-0800200c9a66|
|Document No |f3245d46-ea77-11e1-aff1-0800200c9a66|
|Client Site |f3245d41-ea77-11e1-aff1-0800200c9a66|
|Conducted On (Date) |f3245d42-ea77-11e1-aff1-0800200c9a66|
|Conducted At (Location) |f3245d44-ea77-11e1-aff1-0800200c9a66|
|Personnel |f3245d45-ea77-11e1-aff1-0800200c9a66|

or from any other header item of the audit created by the user (a custom header item). Tip: To find the item ID of such custom header items export one audit from the template of interest in JSON format and inspect the contents to identify the item ID of interest in the `header_items` section.


E.g. the following `config.yaml`

```
export_options:
    filename: f3245d40-ea77-11e1-aff1-0800200c9a66
```

will result in all exported files named after the `Audit Title` field.

### How to list available preference IDs
To list all available global preference IDs and their associated templates:

```
iauditor_exporter --list_preferences
```
To list global and template specific preference IDs associated with specific templates:
```
iauditor_exporter --list_preferences template_3E631E46F466411B9C09AD804886A8B4
```

Multiple template IDs can be passed, separated by a space

### How to maintain multiple configurations

You may want to maintain multiple export configurations in different YAML configuration files. To use a specific configuration file (other than config.yaml) do

```
iauditor_exporter --config=/path/to/alternate_config.yaml
```
Note that you can supply a relative or absolute path to an alternate_config.yaml if it is in another directory

Arguments can be combined e.g. -
```
iauditor_exporter --config=alternate_config.yaml --format pdf json
```

### Troubleshooting

#### Nothing gets exported

Your API key may be missing or has expired. Generate a new API token from the iAuditor web application or using the iAuditor API and replace it in the config.yaml file of the top-level directory of this repository. Ensure your API key corresponds to a SafetyCulture account that contains the audits you want to export.

#### Some audits failed to transfer

If an audit failed to transfer the export process will not stop, it will simply record the failure in the log file and continue. You can find the log files under the log/ directory. To retry a failed audit export you can reset the export start date as shown in "Setting the export start date" below.

#### pdf documents have placeholder images, or docx documents won't open

Sometimes media on an audit can take longer to sync than the rest of the data.  Increasing the value of the media_sync_offset_in_seconds config setting can improve this.

#### Re-setting the export start date

Once you have successfully used this tool to extract audit reports, the next time you run it it will only export reports modified or completed since the last time it ran. To reset the export start date edit or delete the file last_successful.txt generated by the exporter tool in this directory. The time is UTC in ISO 8061 format (example: 2016-10-20T05:19:18.352Z).

IMPORTANT: Exporting large numbers of audits in bulk over and over again may result in your account being throttled or your API token revoked.

### The Import Global Response Sets (GRS) tool

This tool helps maintain Global Response Sets up to date by importing them automatically from a Microsoft Excel spreadsheet (xls or xlsx, version 2 or higher).

To import response sets from a spreadsheet file:
```
import_grs --token <YOUR_IAUDITOR_API_TOKEN> --file <FULL_PATH_TO_SPREADSHEET_FILE>
```
Each sheet in the Excel file will correspond to one Global Response Set. Any Global Response Set that exists in your account which has a name that does not match a sheet in the Excel file will not be affected. The name of the sheet will correspond to the name of the Global Response Set.  Please note that if you name a sheet exactly the same as a currently existing Global Response Set, that Global Response Set will be modified - including deletion of any responses that don't exist in the Excel file.

The tool is case-sensitive - if you have 'city names' and 'City Names' as separate sheet names, a new Global Response Set will be created for each. Similarly, if you want to manage an existing Global Response Set, ensure you name the sheet exactly as it appears in the response set, including capitalization.
A single column per sheet is required, each cell in that column will correspond to the label of a response.

To update your Global Response Set, add one or more rows to the spreadsheet. To delete from your Global Response Set, just delete the relevant rows from the spreadsheet. After your changes, save the spreadsheet and run the tool.

Caveat: deleting a response, and then re-adding the same response later will result in iAuditor Analytics dashboard treating these as different responses. This is because the new response will have a different internal identifier than the deleted response had. To update a response while keeping the same internal identifier you will need to use the response set API directly, instead of this tool. See the iAuditor developer portal for more details.

### The Export Users tool

This tool exports a list of users and their groups from iAuditor into a CSV file named `iauditor_users.csv`. To use this tool you need to have Admin permissions in the organisation.

To run it:
Open a command-line terminal and navigate to the directory called `safetyculture-sdk-python/tools/export_users`.
Run the following command:
```
python export_users.py --token <YOUR_IAUDITOR_API_TOKEN>
```
The exported CSV file will be saved in the current working directory. If the file already exists, it is overwritten.

The exported CSV file columns contain the following user information and structure:
- email
- lastname
- firstname
- groups

| email| lastname| firstname| groups|
|---|---|---|---|
|johnsmith@example.com |Smith|John|Group 1, Group 2|
|johndoe@example.com|Doe|John|Group 3|
|jasonR@example.com|R|Jason| |

The field `groups` contains a comma-separated list of all iAuditor groups the user is a member of. All fields are string values.
Note: Group names that contain commas are not supported. If a group name contains a comma, no user will be assigned to it and you may see errors in the logs.

### The Sync Users tool

This tool updates the organisation users in iAuditor from a CSV file. After running this tool, users in iAuditor and their corresponding groups will match the contents of the CSV file. The groups specified in the CSV file must have been created in iAuditor before running the tool. If a group doesn't exist, the user will not be added to that group. To use this tool you need to have Admin permissions in the organisation.

Caveat: Any users added in iAuditor without using this tool which are not listed in the CSV file, will be removed from iAuditor after running this tool. If you want to keep all users, run the Export Users tool and modify the file that is generated to reflect the desired user state.

The input file specified in the command line arguments has the following structure:

| email| lastname| firstname| groups|
|---|---|---|---|
|johnsmith@example.com |Smith|John|Group 1, Group 2|
|johndoe@example.com|Doe|John|Group 3|
|jasonR@example.com|R|Jason| |

The first row must contain the column headings and will be ignored by the tool. See `example_user_listing.csv` in `safetyculture-sdk-python/tools/sync_users` for an example.

Any row that contains more than one groups, must surround the list of groups with double quotes.

To run the tool:
Open a command-line terminal and navigate to the directory called `safetyculture-sdk-python/tools/sync_users`
Run the following command:
```
python sync_users.py --token <YOUR_IAUDITOR_API_TOKEN> --file <FULL_PATH_TO_CSV_FILE>
```
If the user already exists in the organisation in iAuditor, then the user will be added to all the groups in the `groups` field. If the user is not in iAuditor, the user will be added to iAuditor first and then added to the groups listed in the `groups` field. If no groups are specified, the user is only added to the organisation. If the user is not in the CSV file but is present in iAuditor, the user will be deactivated in iAuditor. If a user already belongs to a group, when that group is removed from the list of groups in the relevant CSV field, the user is removed from that group in iAuditor after running the tool.

### Importing SafetyCulture Python SDK Modules into your own scripts

See example scripts in `./examples/`

### Known Limitations:
1. If two or more groups have the same name, the user will be added to only one of those groups.
2. Adding a user in the CSV when that user exists on the server but is deactivated then the user will not be activated.
3. Adding an already invited user will log an error and have no effect.

## SafetyCulture Python SDK
1. Import `safetypy` into a Python module or Python interpreter:
```
import safetypy
```
2. Create an instance of the SafetyCulture class:
```
sc = safetypy.SafetyCulture(YOUR_IAUDITOR_API_TOKEN)
```
### For more information regarding the Python SDK functionality
1. To open the Python interpreter, run
```
python
```
2. From the Python interpreter, import the Python SDK by running
```
import safetypy
```
3. For an overview of available functionality, run
```
help(safetypy.SafetyCulture)
```

## License

Copyright 2017 SafetyCulture Pty Ltd

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
