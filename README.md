# safetypy (SafetyCulture Python SDK)

Python SDK for interacting with the SafetyCulture API

Supports [Python 2](https://www.python.org/downloads/mac-osx/).
This SDK is not compatible with Python 3. 


## Installation
$ `pip install safetyculture-sdk-python`

This will install
* SafetyCulture Python SDK
* SafetyCulture Exporter Script
* README files


### Basic Usage of the SafetyCulture Python SDK
1. Import `safetypy` in a python module: `import safetpy`
2. Create an instance of safetypy.SafetyCulture class: `sc = safetypy.SafetyCulture(YOUR_SAFETYCULTURE_API_TOKEN)`

#### For more information regarding the Python SDK functionality
1. Open the Python interpreter by typing `python`
2. type `import safetypy`
3. type `help(safetypy.SafetyCulture)`

###  Basic Usage of the Exporter script
1. Copy and paste this text into a file named `config.yaml`:
```
API:
    token: YOUR_SAFETYCULTURE_API_TOKEN
export_options:
    export_path:
    timezone:
    filename:
    csv_options:
        export_inactive_items: false
export_profiles:
sync_delay_in_seconds:
media_sync_offset_in_seconds:
```
2. Replace YOUR_SAFETYCULTURE_API_TOKEN with your API Token. See how to generate an API token [here](https://support.safetyculture.com/integrations/how-to-get-an-api-token/).
3. Type the command `safetyculture_audit_exporter --config=/path/to/config.yaml` with the full path to your config.yaml file to start exporting audits in PDF format.
4. See [here](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/INTG-539-pip_install/tools/exporter/ReadMe.md) for more information about how to use the exporter tool.


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
