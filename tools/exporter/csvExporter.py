import uuid
import time
import json
import requests
import csv

import re


environment = "prod"
url = "http://sync-gateway-internal.%s.safetyculture.io:4985/soter/" % environment
tokens = { 'prod': 'Bearer 90263ab9c6f9b5584b9d532b9222f3c8d503baceedb21eef5c1789641640cffa', 
'sandpit': 'Bearer 90263ab9c6f9b5584b9d532b9222f3c8d503baceedb21eef5c1789641640cffa' }
bearer = tokens[environment]

put_headers = {'Authorization': bearer, 'Content-Type': 'application/json'}


CSV_HEADER_ROW = [
    'Label',
    'Response',
    'Comments / Text',
    'Type',
    'Item Score',
    'Item Max Score',
    'Item Score Percentage',
    'Failed Response',
    'Item ID',
    'Parent ID',
    'Audit Owner',
    'Audit Name',
    'Audit Score',
    'Audit Max Score',
    'Audit Score Percentage',
    'Audit Duration',
    'Date Started',
    'Date Completed',
    'Audit ID'
  ]

LATITUDE_LONGITUDE_REGEX = '\((\-?\d+\.\d+?),\s*(\-?\d+\.\d+?)\)$'

csvFile = open('test.csv', 'wb')
wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)

def getAudit(id): 
	get_doc = requests.get(url + id)
	if get_doc.status_code == 200:
		return get_doc.json()
	else:
		print(get_doc.status_code)

	
	
def generateCsvRowItemData(item):
#   We are outputting 'null' on purpose for absent data.
#   PowerBI can import 'null' and empty string, but not undefined.
	response = ''
	comments = ''
	failed = ''
	score = ''
	maxScore = ''
	scorePercentage = ''
	
	# Determine if the item has failed responses configured and set the boolean accordingly
	if item.get('responses') and 'failed' in item['responses'].keys():
		failed = item['responses']['failed']
		
	# Determine if scoring was calculated for the item and set accordingly
	# Can be either an individual item score or combined score for categories/sections
	if 'scoring' in item.keys() and 'score' in item['scoring'].keys():
		score = item['scoring']['score']
		maxScore = item['scoring']['max_score']
		scorePercentage = item['scoring']['score_percentage']
	elif 'scoring' in item.keys() and 'combined_score' in item['scoring'].keys():
		score = item['scoring']['combined_score']
		maxScore = item['scoring']['combined_max_score']
		scorePercentage = item['scoring']['combined_score_percentage']
		
	# if comments added save that
	if item.get('responses') and item['responses'].get('text'):
		comments = item['responses']['text']
		
		
	if item['type'] == 'section':
		pass
	elif item['type'] == 'category':
		pass
	elif item['type'] == 'text':
		pass
	elif item['type'] == 'textsingle':
		## Already handled above as part of comments
		pass
	elif item['type'] == 'question':
		pass
	elif item['type'] == 'list':
		# We're silently ignoring multi-select lists, ...cbf.
		# Possible solution, duplicate the item across multiple rows, each with
		# a unique selected multiple-choice response.
		# Whether PowerBI can accept data like that is completely untested.
		for response in item['responses']['response']:
			response += str(response) + ','
		#remove trailing comma
		response = response[:-1]
			
		# don't understand this line from JS script
		# response = item['responses']['response'][0]['label'] 
	elif item['type'] == 'address':
		if item['responses'].get('location'):
			# ISSUE: PowerBI needs separate columns for latitude and longitude.
			response = str(item['responses']['location']['geometry']['coordinates'][0]) + ',' + str(item['responses']['location']['geometry']['coordinates'][1])
		#need to understand responses better 
# 		elif 
# 			item['responses'].get('location_text'):
				
	elif item['type'] == 'checkbox':
		pass
	elif item['type'] == 'switch':
		pass
	elif item['type'] == 'slider':
		# convert to string here? 
		response = item['responses']['value']
	elif item['type'] == 'datetime':
		response = item['responses']['datetime']
	else: 
		print 'Unhandled item type: ' + str(item['type'])
	
	return [item['label'], response, comments, item['type'], score, maxScore, scorePercentage, failed, item['item_id'], item['parent_id']]
	
	
def generateCsvRowMetadata(metadata, id):

	metadataArray = []
	
	metadataArray.append(metadata['authorship']['owner']['name'])
	metadataArray.append(metadata['name'])
	metadataArray.append(metadata['score'])
	metadataArray.append(metadata['total_score'])
	metadataArray.append(metadata['score_percentage'])
	metadataArray.append(metadata['duration'])
	metadataArray.append(metadata['date_started'])
	metadataArray.append(metadata['date_completed'])
	metadataArray.append(id)
	
	return metadataArray	
	

def getItemsAndMetadata(id):
	# add try / catch statement here
	audit = getAudit(id) 
	metadata = audit['audit_data']
	items = audit['header'] + audit['items']
	return (metadata, items)

# /**
# * Generate a CSV file from multiple audits with an item per row and each with audit metadata.
# * @param {array} ids The IDs of the audits to process
# * @param {string} bearer The authentication token needed to access SafetyCulture public API
# * @param {string} filePath The path where to output the file (defaults to "./output.csv") [optional]
# * @param {integer} concurrency How many audits to process concurrently (defaults to 3) [optional]
# */
def exportAuditsToCSV(): 
	id = raw_input("audit id: ")
	
	wr.writerow(CSV_HEADER_ROW)
	metadataAndItems = getItemsAndMetadata(id)
	metadata = metadataAndItems[0]
	items = metadataAndItems[1]
	
	metadataArray = generateCsvRowMetadata(metadata, id)
	for item in items:
		itemArray = generateCsvRowItemData(item)
		rowArray = itemArray + metadataArray
		wr.writerow(rowArray)

exportAuditsToCSV()