# safetypy (SafetyCulture Python SDK)

Python SDK for interacting with the SafetyCulture API

Supports [Python 2](https://www.python.org/downloads/mac-osx/).
This SDK is not compatible with Python 3. 


## Installation
$ `pip install safetyculture-sdk-python`

This will install
* SafetyCulture Python SDK
* iAuditor Exporter Script
* README.md files

### Basic Usage of the SafetyCulture Python SDK
1. Import `safetypy` in a python module: `import safetpy`
2. Create an instance of safetypy.SafetyCulture class: `sc = safetypy.SafetyCulture(YOUR_IAUDITOR_API_TOKEN)`

#### For more information regarding the Python SDK functionality
1. Open the Python interpreter by typing 
```
$ python
```
2. Import the Python SDK by running
```
$ import safetypy
```
3. For an overview of available functionality, run
 ```
$ help(safetypy) 
$ help(safetypy.SafetyCulture)
```

###  Basic Usage of the Exporter script
1. To initialize a basic configuration file, type:  
```
$ safetyculture_audit_exporter --setup
```
* You will be prompted for a iAuditor username and password which will be used to generate an API token. 
Note that your credentials will not be saved in any capacity.
* A basic configuration file will be auto-generated. A configuration file is necessary to run the Exporter script.
The configuration file will be named `config.yaml` and be placed in a folder named `iAuditor Audit Exports`
2. Navigate into the `iAuditor Audit Exporter` folder
3. To start exporting audits in PDF format, run the following command 
```
$ safetyculture_audit_exporter
```
4. See [here](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/INTG-539-pip_install/tools/exporter/ReadMe.md) for more information about how to use the exporter tool.

#### Windows Users
The location of `safetyculture_audit_exporter.exe` must be included in the system PATH variable in order to execute.  
Find the location of `safetyculture_audit_exporter.exe` by running 
```
> where safetyculture_audit_exporter
```
Add this path to the system PATH variable. 

Directions on how to update Windows system PATH variable [here](http://windowsitpro.com/systems-management/how-can-i-add-new-folder-my-system-path)


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
