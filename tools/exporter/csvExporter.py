import uuid
import time
import json
import requests
import csv

import re

import sys
from io import BytesIO


# TOKEN  = "fb31b33411b59481a2fe44769de1c89df9baa81300f4b5ed1ee8c568d999cd4a" 
# TIMEZONE = "Australia/Melbourne"
# AUTH_HEADER = {'Authorization': 'Bearer ' + TOKEN}
# TYPE_HEADER = {"Content-Type": "application/json"}
# URL = "https://api.safetyculture.io/audits/audit_893A10D909AC493CA8310552CF190A6B"

# id = raw_input("audit id: ")
# URL = URL + id
# put_headers = {'Authorization': bearer, 'Content-Type': 'application/json'}


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

csvFile = open('temp.csv', 'wb')
wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)

# def get_audit(id):
#     print "Getting audits based off " + str(id)
#     audit_dictionary = requests.get(URL, headers= AUTH_HEADER)
#     if audit_dictionary.status_code != 200:
#         print "Failed to retrieve Audits from " + id
#         print "STATUS CODE: " + str(audit_dictionary.status_code)
#         quit()
#     return audit_dictionary.json() 


def generateCsvRowItemData(item):
#   We are outputting 'null' on purpose for absent data.
#   PowerBI can import 'null' and empty string, but not undefined.
	response = ''
	comments = ''
	failed = ''
	score = ''
	maxScore = ''
	scorePercentage = ''
	parent_id = ''
	
	
	if 'parent_id' in item.keys():
		parent_id = item['parent_id']
	
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
		for _response in item['responses']['selected']:
			response += str(_response['label']) + ','
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
	
	return [item['label'], response, comments, item['type'], score, maxScore, scorePercentage, failed, item['item_id'], parent_id]
	
	
def generateCsvRowMetadata(metadata, id):
	metadataArray = []
	
# 	metadataArray.append(metadata['authorship']['owner']['name']) -- this works when exported form sync-gateway
	metadataArray.append(metadata['authorship']['owner'])
	metadataArray.append(metadata['name'])
	metadataArray.append(metadata['score'])
	metadataArray.append(metadata['total_score'])
	metadataArray.append(metadata['score_percentage'])
	metadataArray.append(metadata['duration'])
	metadataArray.append(metadata['date_started'])
	metadataArray.append(metadata['date_completed'])
	metadataArray.append(id)
	
	return metadataArray	
	

def getItemsAndMetadata(audit):
	# add try / catch statement here
	metadata = audit['audit_data']
	# items = audit['header'] + audit['items'] -- this works when exported form sync-gateway
	items = audit['header_items'] + audit['items']
	return (metadata, items)


def exportAuditsToCSV(audit_json): 
  	"""
  	enerate a CSV file from multiple audits with an item per row and each with audit metadata.
  	
  	:param audit_json:	audit data to export as CSV
  	"""
	
	wr.writerow(CSV_HEADER_ROW)
	metadataAndItems = getItemsAndMetadata(audit_json)
	metadata = metadataAndItems[0]
	items = metadataAndItems[1]
	
	metadataArray = generateCsvRowMetadata(metadata, id)
	for item in items:
		itemArray = generateCsvRowItemData(item)
		rowArray = itemArray + metadataArray
		wr.writerow(rowArray)
		

exportAuditsToCSV()

