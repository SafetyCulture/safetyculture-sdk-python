#Exporter tools

Exporter tools for interacting with the Public API export capabilities.  Download audit reports in pdf, docx, and/or json format,
and save them anywhere on your drive. Apply export profiles to your exports by modifying config file (illustrated below).
Set the application to run on a recurring schedule with Task Scheduler or cron to keep up to date with all of your audit reports.

**Note**:
  Exporter tools are written in Python 2.7.x
  Other versions of Python are likely to generate errors

**Instructions**:
  - Follow the instructions in the top-level ReadMe.md
  - Execute the following command from command line (from this directory):

    ``pip install -r requirements.txt``
  - Edit config.yaml to customize export settings


Example configuration of config.yaml:
```
export_options:
    export_path: /Users/Monty/Dropbox
    timezone: America/Chicago
    filename: f3245d40-ea77-11e1-aff1-0800200c9a66
export_profiles:
    template_3E631E46F466411B9C09AD804886A8B4:E15A6525-EFA5-4835-92F0-D11CA9F364F3
    template_3E631E46F466411B9C09AD804886A8B4:E50645A1-2851-4E92-B4EA-60C5CE7981BE
    ...
    ...
```

Definition of config parameters:

*export_path*:     absolute or relative path to export directory

*timezone*   :     must be a valid Olson timezone, if invalid or missing, will default to local timezone

*filename*   :     must be a valid item_id of a header item with a 'text' response.  Currently supported fields are Audit Title, Document No., Client / Site, Prepared By, Personnel, or any custom header item which has a 'text' type response

*export_profiles*: For every template which should have an export profile applied, an export profile id must be supplied
                   This id can be obtained via the Public API.

Templates for which there is no export profile id listed will be exported without a profile applied



To run the export, either double-click exporter.py or execute `python exporter.py` from the command line.

Supported command-line arguments:
```
  Argument    Example

  config      python exporter.py --config=alternate_config.yaml
  format      python exporter.py --formats pdf json docx

  *Arguments can be combined e.g. - `python exporter.py --config=alternate_config.yaml --formats pdf json docx`*
```
