# safetypy (SafetyCulture Python SDK)

Python SDK for interacting with the SafetyCulture API

## How to Install

### Mac
 * Install Python 2.7.x (and the pip package manager if your Python is older than 2.7.9, Python 3 is not supported)
 * Clone this repository to a directory on your computer
 * Go to the cloned directory on your computer
 * Execute the following command from the command line to install the package dependencies:
     * ``pip install -r safetypy/requirements.txt``
 * See ReadMe.md in tools/exporter for a usage example

### Windows
#### Install Python 
 * Install Latest Python 2 Release at https://www.python.org/downloads/windows/
 * Open the download, and start the installation
 * **IMPORTANT: During the Installation Process, when you see the page 'Customize Python', make sure to 'Add python.exe to Path' before clicking Next is set to 'Will be installed on local hard drive'. This will ensure you can run python executable files without including the Path to your Python installation. See [here](http://docs.platformio.org/en/latest/_images/python-installer-add-path.png) for clarification** 
 * Proceed with installation, click 'Finish' when complete.
#### Install SafetyCulture Python SDK and Export tool
 * Open this link in your browser: https://github.com/SafetyCulture/safetyculture-sdk-python
 * Click the green button on the right that says 'Clone or download', this will produce a popdown menu
 * Click 'Download ZIP' from the popdown menu
 * Extract this download and move the folder to an appropriate location
#### Install Requirements
 * Open the Command Prompt (search 'Command Prompt' from the home screen)
 * Open Windoes file explorer and navigate into the safetyculture-sdk-python folder
 * Hold SHIFT and right click within the folder, select 'Open command window here' and pressing Enter
 * In the Command Prompt type `python -m pip install -r safetypy\requirements.txt` and press Enter to install the needed packages for safetypy.py to run
 * Navigate to the tools\exporter directory by typing `cd tools\exporter\` and pressing Enter
 * Type `python -m pip install -r requirements.txt` and press Enter to install the packages needed for exporter.py to run
#### Generate API Token 
 * Open https://app.safetyculture.io/ in your browser
 * Open your personal profile by clicking on the icon on the top of the left hand side menu
 * Click 'Edit details'
 * Scroll to the bottom of the page
 * Enter your SafetyCulture password and click the 'Generate' button 
 * Copy the API access token generated 
 * In the File Explorer open safetyculture-sdk-python\tools\exporter\
 * Right click on config.yaml and open with some text editor
 * Replace YOUR_SAFETYCULTURE_API_TOKEN with your generated API token above
 * Save config.yml and exit the text editor 
#### RUN Exporter.py 
You are now ready to Run the exporter tool
 * In the File Explorer open safetyculture-sdk-python\tools\exporter\
 * Hold SHIFT and right click within the folder, select 'Open command window here' and pressing Enter
 * Type `python exporter.py` to start a bulk export of Audits to PDF files
 * For more information about the exporter tool see https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/tools/exporter/ReadMe.md
 
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
