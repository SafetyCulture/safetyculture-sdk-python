# safetypy (SafetyCulture Python SDK)

Python SDK for interacting with the SafetyCulture API

## How to Install

### Mac
#### Install Python 
 1. Download and install the latest Python 2 release at https://www.python.org/downloads/mac-osx/
#### Install SafetyCulture Python SDK and Export tool
 2. Open this link in your browser: https://github.com/SafetyCulture/safetyculture-sdk-python
 3. Click the green button on the right that says 'Clone or download', this will produce a popdown menu
 4. Click 'Download ZIP' from the popdown menu
 5. Extract this download and move the folder to an appropriate location
#### Install Requirements
 6. Open the Terminal
 7. Navigate into the safetyculture-sdk-python folder using [cd command](http://guides.macrumors.com/cd)
 8. In ther Terminal type `pip install -r safetypy/requirements.txt` and press Enter to install the needed packages for safetypy.py to run
 9. Navigate to the tools/exporter directory by typing `cd tools/exporter/` and pressing Enter
 10. Type `pip install -r requirements.txt` and press Enter to install the packages needed for exporter.py to run
#### Generate API Token 
 11. See [Generate API Token](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/ReadMe.md#generate-api-token-2) section below
#### RUN Exporter.py 
You are now ready to Run the exporter tool
 12. Open Terminal to the tools/exporter/ folder. Type `python exporter.py` to start a bulk export of Audits to PDF files
 13. For more information about the exporter tool see https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/tools/exporter/ReadMe.md

### Windows
#### Install Python 
 1. Download latest Python 2 release at https://www.python.org/downloads/windows/
 2. Open the download, and start the installation
 3. **IMPORTANT: During the Installation Process, when you see the page 'Customize Python', make sure to 'Add python.exe to Path'  before clicking Next is set to 'Will be installed on local hard drive'. This will ensure you can run python executable files without including the Path to your Python installation. See [here](http://docs.platformio.org/en/latest/_images/python-installer-add-path.png) for clarification** 
 4. Proceed with installation, click 'Finish' when complete.
#### Install SafetyCulture Python SDK and Export tool
 5. Open this link in your browser: https://github.com/SafetyCulture/safetyculture-sdk-python
 6. Click the green button on the right that says 'Clone or download', this will produce a popdown menu
 7. Click 'Download ZIP' from the popdown menu
 8. Extract this download and move the folder to an appropriate location
#### Install Requirements
 9. Open the Command Prompt (search 'Command Prompt' from the home screen)
 10. Open Windoes file explorer and navigate into the safetyculture-sdk-python folder
 11. Hold SHIFT and right click within the folder, select 'Open command window here' and pressing Enter
 12. In the Command Prompt type `python -m pip install -r safetypy\requirements.txt` and press Enter to install the needed packages for safetypy.py to run
 13. Navigate to the tools\exporter directory by typing `cd tools\exporter\` and pressing Enter
 14. Type `python -m pip install -r requirements.txt` and press Enter to install the packages needed for exporter.py to run
#### Generate API Token 
 15. See [Generate API Token](https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/ReadMe.md#generate-api-token-2) section below
#### RUN Exporter.py 
 16. In the File Explorer open safetyculture-sdk-python\tools\exporter\
 17. Hold SHIFT and right click within the folder, select 'Open command window here' and pressing Enter
 18. Type `python exporter.py` to start a bulk export of Audits to PDF files
 19. For more information about the exporter tool see https://github.com/SafetyCulture/safetyculture-sdk-python/blob/master/tools/exporter/ReadMe.md
 

### Generate API Token 
 1. Open https://app.safetyculture.io/ in your browser
 2. Open your personal profile by clicking on the icon on the top of the left hand side menu
 3. Click 'Edit details'
 4. Scroll to the bottom of the page
 5. Enter your SafetyCulture password and click the 'Generate' button 
 6. Copy the API access token generated 
 7. In the File Explorer open safetyculture-sdk-python/tools/exporter/
 8. Right click on config.yaml and open with some text editor
 9. Replace YOUR_SAFETYCULTURE_API_TOKEN with your generated API token above
 10. Save config.yml and exit the text editor 

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
