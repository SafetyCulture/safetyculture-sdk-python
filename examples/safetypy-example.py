# This script is compatible with Python 3
# Note: pipenv is recommended for isolating python environments and handling dependencies.
# Once safetyculture-sdk-python is installed in the environment, safeypy module can be imported
import safetypy as sp

api_token = input('Please enter your API token: ')

if not api_token: 
  exit()

# SafetyPy Authentication 
sc_client = sp.SafetyCulture(api_token)

# SafetyPy Search Audits
response = sc_client.discover_audits()

audits = response['audits']
total_audits = response['total']


print("This account has access to " + str(total_audits) + " audits.")

# SafetyPy Retrieve Templates
response = sc_client.discover_templates()
templates = response['templates']
template_cnt = response['total']

print("This account has access to " + str(template_cnt) + " templates.")
