#Exporter tools

Exporter tools for interacting with the Public API export capabilities

**Note**:
  Exporter tools are written in Python 2.7.x
  Other versions of Python are likely to generate errors

**Instructions**:
  - Follow the instructions in the top-level ReadMe.md
  - Execute the following command from terminal (from this directory):

    ``pip install -r requirements.txt``
  - Edit pdf_config.yaml to customize export settings


Example configuration of pdf_config.yaml:
```
export_options:
    export_path: /Users/Monty/Dropbox
    timezone: America/Chicago
export_profiles:
    template_3E631E46F466411B9C09AD804886A8B4:E15A6525-EFA5-4835-92F0-D11CA9F364F3
    template_3E631E46F466411B9C09AD804886A8B4:E50645A1-2851-4E92-B4EA-60C5CE7981BE
    ...
    ...
```

Definition of config parameters:

*export_path*:     absolute or relative path to export directory

*timezone*   :     must be a valid Olson timezone, if invalid or missing, will default to local timezone

*export_profiles*: For every template which should have an export profile applied, an export profile id must be supplied
                   This id can be obtained via the Public API
                   Templates for which there is no export profile id listed will be exported without a profile applied

To run the export, either double-click pdf_exporter.py or execute `python pdf_exporter.py` from terminal

Supported command-line arguments:
```
  Argument    Example

  config      python pdf_exporter.py --config=alternate_config.yaml
```
