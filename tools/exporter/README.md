# Audit Exporter Tool
Allows you to export audit data from the SafetyCulture Platform and save them anywhere on your computer.
Supported export formats: PDF, MS WORD (docx), JSON, and CSV. Media and Web Report Link exporting is also supported.

## Installation  
``` 
pip install safetyculture-sdk-python
```

This will install
* SafetyCulture Python SDK -- See top level [README.md](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/README.md) for more information. 
* iAuditor Exporter Tool
* README files


## Initial Setup
IMPORTANT: If you have used previous versions of the exporter tool, you should run it from the same folder you have run the tool from in the past.
Otherwise, the exporter will start exporting from the earliest available audits, rather than from where the last successful export left off. 
The export tool reads and writes to a file named `last_successful.txt` to keep track of what has already been exported. You'll find this file anywhere that you have run the exporter tool before. 
Alternatively, you can move the `last_successful.txt` file if you prefer to export from a different location.

If this is your first time using the exporter tool, follow these steps to get set up: 
1. To automatically create a configuration file (which is needed to run the exporter tool), run:  
```
iauditor_exporter --setup
```
* You will be prompted for an iAuditor username and password which will be used to generate an API token. 
Note that your credentials will not be saved in any capacity.
* A basic configuration file will be auto-generated. A configuration file is necessary to run the Exporter script.
The file will be named `config.yaml` and be placed in a folder named `iAuditor Audit Exports` which will be created in your current directory. 
2. Navigate into the `iauditor_exports_folder` folder just created:
```
cd 'iauditor_exports_folder'
```
3. To start exporting audits in PDF format, run the following command 
```
iauditor_exporter
```
#### Windows Users
The location of `iauditor_exporter.exe` must be included in the system PATH variable in order to execute from the command line without including the full path to the .exe file.  
Find the location of `iauditor_exporter.exe` by running 
```
> where iauditor_exporter
```
Add this path to the system PATH variable. 

Directions on how to update Windows system PATH variable [here](https://www.computerhope.com/issues/ch000549.htm)


## How to run
### Common usage
The API token saved in `config.yaml` provides access to data associated with a single account. Namely, the account used to generate the API token.
Only audits that are owned by or shared with the account associated with the API token in use are available for exporting.
 
All exported data is saved in a folder called  `exports`. The folder will be created in the current working directory if it does not already exist.

To export all completed audits in PDF format, run:
```
iauditor_exporter --config=/path/to/config.yaml
```
  
To enable the exporter to run continuously until interrupted, use the loop command line argument:

```
iauditor_exporter --config=/path/to/config.yaml --loop
```

To specify the export format explicitly run:

```
iauditor_exporter --config=/path/to/config.yaml --format pdf
```

More than one supported formats can be exported at once e.g.

```
iauditor_exporter --config=/path/to/config.yaml --format pdf docx json csv media web-report-link
```

Note:
* Unless you start the tool with the --loop argument, it will sync documents once and terminate (up to 1000 per sync)
* Only completed audits will be exported
* Only audits that are owned by or shared with the iAuditor user account that generated the API token will be exported
* Up to 1000 audits will be exported each time the software checks for new audits. If more than 1000 audits exist they will be retrieved automatically in subsequent sync cycles.

### CSV Export
#### Bulk CSV Export
For an overview of the CSV format used, see [here](https://support.safetyculture.com/integrations/safetyculture-csv-exporter-tool/#format)


Audits built from the same template will be saved in the same CSV file which is named after the templates unique ID number. 
i.e. `TEMPLATE_ID.csv` 

To export Multiple Audits to Bulk CSV file, run the `iauditor_exporter` with the format option set to CSV: 
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

## Export settings

To override default export settings edit config.yaml in this directory.

Things you can configure:

|  Setting | Description  |
|---|---|
| export_path  | absolute or relative path to the directory where to save exported data to  |
| timezone |  an Olson timezone to be used in generated audit reports. If invalid or missing, reports will use the timezone local to the computer running the export tool |
| filename  |  an audit item ID whose response is going to be used to name the files of exported audit reports. Can only be an item with a response type of `text` from the header section of the audit such as Audit Title, Document No., Client / Site, Prepared By, Personnel, or any custom header item which has a 'text' type response |
| export_profiles  | to apply an export profile transformation to particular templates, give here a list of export profile ids
| sync_delay_in_seconds | time in seconds to wait after completing one export run, before running again
| export_inactive_items | This setting only applies when exporting to CSV. Valid values are true (export all items) or false (do not export inactive items). Items that are nested under [Smart Field](https://support.safetyculture.com/templates/smart-fields/) will be 'inactive' if the smart field condition is not satisfied for these items.
| media_sync_offset_in_seconds | time in seconds since an audit has been modified before it will by synced

Here is an example customised config.yaml:

```
API:
    token: YOUR_SAFETYCULTURE_API_TOKEN
export_options:
    export_path: /Users/Monty/Dropbox
    timezone: America/Chicago
    filename: f3245d40-ea77-11e1-aff1-0800200c9a66
    csv:
        export_inactive_items: false
export_profiles:
    template_3E631E46F466411B9C09AD804886A8B4:E15A6525-EFA5-4835-92F0-D11CA9F364F3
    template_3E631E46F466411B9C09AD804886A8B4:E50645A1-2851-4E92-B4EA-60C5CE7981BE
    ...
    ...
sync_delay_in_seconds: 36000
media_sync_offset_in_seconds: 600
```

Note: Templates for which there is no export profile id listed in the config file will be exported without a profile applied

### Naming the exported files

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

## Advanced usage

### How to list available export profile IDs
To list all available export profile IDs and their associated templates:

```
iauditor_exporter --list_export_profiles
```
To list export profile IDs associated with specific templates:
```
iauditor_exporter --list_export_profiles template_3E631E46F466411B9C09AD804886A8B4
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

## Troubleshooting

### Nothing gets exported

Your API key may be missing or has expired. Generate a new API token from the iAuditor web application or using the SafetyCulture API and replace it in the config.yaml file of the top-level directory of this repository. Ensure your API key corresponds to a SafetyCulture account that contains the audits you want to export.

### Some audits failed to transfer

If an audit failed to transfer the export process will not stop, it will simply record the failure in the log file and continue. You can find the log files under the log/ directory. To retry a failed audit export you can reset the export start date as shown in "Setting the export start date" below.

### pdf documents have placeholder images, or docx documents won't open

Sometimes media on an audit can take longer to sync than the rest of the data.  Increasing the value of the media_sync_offset_in_seconds config setting can improve this.

### Re-setting the export start date

Once you have successfully used this tool to extract audit reports, the next time you run it it will only export reports modified or completed since the last time it ran. To reset the export start date edit or delete the file last_successful.txt generated by the exporter tool in this directory. The time is UTC in ISO 8061 format (example: 2016-10-20T05:19:18.352Z).

IMPORTANT: Exporting large numbers of audits in bulk over and over again may result in your account being throttled or your API token revoked.
