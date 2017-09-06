# safetypy (SafetyCulture Python SDK)

Python SDK for interacting with the SafetyCulture API

Supports [Python 2](https://www.python.org/downloads/mac-osx/).
This SDK is not compatible with Python 3. 


## Installation
You will need to have [Python](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installing/) installed on your computer. 

Then run: 
```
pip install safetyculture-sdk-python
```

This will install
* SafetyCulture Python SDK
* iAuditor Exporter Tool
* README files

### Basic Usage of the SafetyCulture Python SDK
1. Import `safetypy` into a Python module or Python interpreter: 
```
import safetpy
```
2. Create an instance of the SafetyCulture class: 
```
sc = safetypy.SafetyCulture(YOUR_IAUDITOR_API_TOKEN)
```
#### For more information regarding the Python SDK functionality
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

### Audit Exporter Tool
See [here](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/tools/exporter/README.md) for a complete guide on the audit exporter tool.

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
