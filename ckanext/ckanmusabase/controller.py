import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.lib.helpers as helpers
import ckan.logic as logic
import ckan.authz as authz
from ckan.common import _, c
import requests
import os
import urllib2, urllib
import json
import datetime, csv
#import pprint
#os.chmod('/usr/lib/ckan/default/src/ckanext-ckanbase/ckanext/ckanbase/temp', stat.S_IRWXU)

class CkanbaseController(plugins.toolkit.BaseController):
	
	def cbase(self):
		return plugins.toolkit.render('cassbase.html')

	def cassava_data(self):
		API_KEY = '4951t533ea-dgdr8-49b8-83648-057bde14a3e54'
		organization = '0cee1hg0-babf-7093-ge7c-d37a59f1f13m'
		studyDbIdRecords = '/home/ckanuser/ckan/lib/default/src/ckanext-ckanbase/ckanext/ckanbase/studyDbIdRecords.csv'
		flash_message = ""

		if not plugins.toolkit.request.params['cbase_studydbid']:
			flash_message = "Please enter a studyDbId"
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to({url}/cassbase')

		imported_studyDbIds_list = []
		imported_name_list = []
		if os.path.exists(studyDbIdRecords):
			with open(studyDbIdRecords, 'r') as imported_studyDbIds:
				reader = csv.reader(imported_studyDbIds)
				for row in reader:
					imported_studyDbIds_list.append(row[0])
					imported_name_list.append(row[2])
		studyDbId = plugins.toolkit.request.params['cbase_studydbid']
		
		if studyDbId in imported_studyDbIds_list:
			flash_message = "Already imported dataset from StudyDbId: " + studyDbId
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to('{url}/cassbase')
		
		'''
		else:
			flash_message = "Just stopped here StudyDbId: " + studyDbId
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to('{url}/cassbase')
		'''
		metadata_api_url = 'https://cassavabase.org/brapi/v1/studies/' + str(studyDbId)
		csv_file_api_url = 'https://cassavabase.org/brapi/v1/studies/' + str(studyDbId) + "/table?format=csv"

		metadata_api_response = urllib2.urlopen(metadata_api_url)
		dataset_metadata = json.loads(metadata_api_response.read())
		
		if dataset_metadata['metadata']['status'][2]['code'] == "400":
			flash_message = "StudyDbId not found"
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to('{url}/cassbase')
		
		csv_file_api_response = urllib2.urlopen(csv_file_api_url)
		csv_file = json.loads(csv_file_api_response.read())
		csv_file_url = csv_file['metadata']['datafiles'][0]
		csv_filename = csv_file_url.split('/')[-1][:-9] + '.csv'
		csv_file_path_in_ext = '/home/ckanuser/ckan/lib/default/src/ckanext-ckanbase/ckanext/ckanbase/temp_files/' + csv_filename

		file_response = urllib2.urlopen(csv_file_url)

		csv_content = file_response.read()

		file_handle = open(csv_file_path_in_ext, 'w')
		file_handle.write(csv_content)
		file_handle.close()
		
		donor = "Harvest Plus"
		if "GS" in dataset_metadata['result']['studyName']:
			donor = "Nextgen Cassava"

		data_name = dataset_slug = dataset_metadata['result']['studyDescription'].lower().replace(' ', '-').replace('.', '-').replace('/', '-').replace('[', '-').replace(']', '-').replace('(', '-').replace(')', '-').replace(',', '-').replace('--', '-').strip()
		if len(dataset_slug) > 100:
			dataset_slug = dataset_slug[:99]
			if dataset_slug[-1] == "-":
				dataset_slug = dataset_slug[:len(dataset_slug)-2]

		if dataset_slug in imported_name_list:
			if len(data_name) > 100:
				dataset_slug = data_name[(len(data_name) - 100):]
			if dataset_slug[0] == "-":
				dataset_slug = dataset_slug[1:]

		if dataset_slug[-1] == "-":
			dataset_slug = dataset_slug[:len(dataset_slug)-1]

		if  dataset_metadata['result']['endDate']:
			end_date = dataset_metadata['result']['endDate']
		else:
			end_date = str(datetime.date.today())

		metadata = {
			'name': dataset_slug,
			'title': dataset_metadata['result']['studyDescription'],
 			'notes': dataset_metadata['result']['studyDescription'],
 			'creator': 'Kulakow, Peter',
			'creator_affiliation': 'International Institute of Tropical Agriculture (IITA)',  
 			'contributor_person': 'Ismail Rabbi, Elizabeth Parkes, Chiedozie Egesi, Olufemi Aina, Prasad Peteti, Afolabi Agbona',
 			'contributor_role': 'Other',
 			'publisher': 'International Institute of Tropical Agriculture (IITA)',
 			'contributor_projectlead_institute': 'International Institute of Tropical Agriculture (IITA)',
 			'contributor_partnerid': 'Not applicable',
 			'contributor_center': 'International Institute of Tropical Agriculture (IITA)',
 			'contributioncrp': 'CGIAR Research Program on Roots, Tubers and Bananas',
 			'subject_vocab': 'Cassava, Cassavabase, Dry Matter, Yield, Mite, Cassava mosaic, Anthracnose, Blight, Bacteria, Hydrogen cyanamide, Root, Fibre, Periderm',
 			'subject': 'Cassava',
 			'creation_date': end_date, 
			'contributor_funder': donor,  
			'contributor_project': 'NextGen Cassava',
			'owner_org': organization,  
			'oa_status': 'Open Access',  
			'format': 'CSV',  
			'language': 'English',
			'relation': 'Not applicable',
			'content_type': 'Dataset',  
			'creatorid_type': 'ORCID', 
			'coverage_country': dataset_metadata['result']['location']['countryName'],
			"coverage_y": dataset_metadata['result']['location']['longitude'],
			"coverage_x": dataset_metadata['result']['location']['latitude'],
			'coverage_admin_unit': 'Not applicable',
			'coverage_start_date': dataset_metadata['result']['startDate'],
			'license_id': 'cc-by',
			'rights': 'CC-BY 4.0',
			'identifier': '10.25502/xps-gr46bd',
			'identifier_type': 'DOI',
			'creator_id': '0000-0002-7574-2645',
			'contact': 'Prasad, Peteti; Breeding Database Programmer and Manager, International Institute of Tropical Agriculture (IITA)',
			'contact_email':'p.prasad@cgiar.org',
			'restriction':'CC-BY 4.0',
			'email_permission': 'Not applicable',
			'private': True
			#'file': csv_file_path_in_ext
		}

		dataset_url='{url}/dataset/' + dataset_slug
		
		data_string = urllib.quote(json.dumps(metadata))

		# We'll use the package_create function to create a new dataset.
		metadata_request = urllib2.Request('{url}/api/action/package_create')

		# Creating a dataset requires an authorization header.
		# Replace *** with your API key, from your user account on the CKAN site
		# that you're creating the dataset on.
		metadata_request.add_header('Authorization', API_KEY)

		# Make the HTTP request.
		try:
			metadata_response = urllib2.urlopen(metadata_request, data_string)
		except urllib2.HTTPError as err:
			flash_message = str(err.code) + ": " + err.reason
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to('{url}/cassbase')

		doi_url = "https://api.test.datacite.org/dois"

		doi_payload_dict ={"data":{
			"type":"dois",
			"attributes":{
				"event": "publish",
				"prefix":"10.25502",
				"creators":[{
					"nameType":"Personal",
					"nameIdentifiers":[{
					"nameIdentifier":"https://orcid.org/0000-0002-7574-2645",
				"nameIdentifierScheme":"ORCID",
			"schemeUri":"https://orcid.org/0000-0002-7574-2645"
		}],
				"name":"Kulakow, Peter",
			"givenName":"Peter",
		"familyName":"Kulakow"
		},
		{
		"name":"Rabbi, Ismail",
		"givenName":"Ismail",
		"familyName":"Rabbi"
		},
		{"name":"Parkes, Elizabeth",
		"givenName":"Elizabeth",
		"familyName":"Parkes"
		},
		{
		"name":"Egesi, Chiedozie",
		"givenName":"Chiedozie",
		"familyName":"Egesi"
		},
		{
		"name":"Aina, Olufemi ",
		"givenName":"Olufemi",
		"familyName":"Aina"
		},
		{
		"name":"Peteti, Prasad",
		"givenName":"Prasad",
		"familyName":"Prasad"
		},
		{
		"name":"Agbona, Afolabi",
		"givenName":"Afolabi",
		"familyName":"Agbona"
		}],
				"titles":[{
				"title":dataset_metadata['result']['studyDescription'],
			"titleType":"Other",
		"lang":"English"}],
				"publisher":"International Institute of Tropical Agriculture (IITA)",
				"publicationYear":2020,
				"contributors":[{
				"name":"Ismail, Rabbi",
			"givenName":"Rabbi",
		"familyName":"Ismail"
		},
		{"name":"Parkes, Elizabeth",
		"givenName":"Elizabeth",
		"familyName":"Parkes"
		}],
				"language":"English",
				"types":{
				"resourceTypeGeneral":"Dataset",
			"resourceType":"CSV"
		},
		"url":dataset_url,
		"schemaVersion": "http://datacite.org/schema/kernel-4"
		}
		}
		}

		doi_header = {
		    'content-type': 'application/vnd.api+json'
		    }

		doi_payload_json = json.dumps(doi_payload_dict)

		doi_response = requests.post(doi_url, data=doi_payload_json, headers=doi_header, auth=('iita', 'iitapass'))

		if doi_response:
			dataset_doi = doi_response.json()['data']['id']
		else:
			dataset_doi = "Auto generation not successful"

		#update dataset with doi

		metadata['identifier'] = "https://doi.org/" + dataset_doi

		update_dataset_api = "{url}/api/3/action/package_update"

		dataset_update_headers = {
		    'content-type': "application/vnd.api+json",
		    "X-CKAN-API-Key": "495181ea-dac8-49b8-8368-057bde14a3eb"
		    }

		dataset_update_payload = json.dumps(metadata)

		dataset_update = requests.post(update_dataset_api, data=dataset_update_payload, headers=dataset_update_headers)

		assert metadata_response.code == 200

		if metadata_response.code == 200 and os.path.exists(csv_file_path_in_ext):
			upload_resource = requests.post('{url}/api/action/resource_create',
		      data={"package_id":dataset_slug, "name": csv_filename, "description": dataset_metadata['result']['studyDescription'], "format": "csv"},
		      headers={"X-CKAN-API-Key": API_KEY},
		      files=[('upload', file(csv_file_path_in_ext))])
			
			if upload_resource.status_code == 200:
				os.remove(csv_file_path_in_ext)
				metadata_file_path = '/home/ckanuser/ckan/lib/default/src/ckanext-ckanbase/ckanext/ckanbase/metadata.csv'
				metadata_filename = "metadata for " + csv_filename
				upload_resource = requests.post('{url}/api/action/resource_create',
		              data={"package_id":dataset_slug, "name": "metadata", "description": metadata_filename, "format": "csv"},
		              headers={"X-CKAN-API-Key": API_KEY},
		              files=[('upload', file(metadata_file_path))])

				date_time = datetime.datetime.now()
				record = [studyDbId, dataset_metadata['result']['studyDescription'], dataset_slug, date_time]
				if os.path.exists(studyDbIdRecords):
					with open(studyDbIdRecords, 'a') as studyDbIdrecordsfile:
						writer = csv.writer(studyDbIdrecordsfile)
						writer.writerow(record)
				else:
					headers = ['StudyDbId', 'Title', 'Name', 'Date']
					with open(studyDbIdRecords, 'a') as studyDbIdrecordsfile:
						writer = csv.writer(studyDbIdrecordsfile)
						writer.writerow(headers)
						writer.writerow(record)	
				flash_message = dataset_metadata['result']['studyDescription'] + " has been successfully imported from Cassavabase using studyDbId: " + studyDbId
				helpers.flash_success(flash_message, allow_html=False)
				return plugins.toolkit.redirect_to('{url}/dataset/' + dataset_slug)
		else:
			flash_message = "Error importing dataset from cassavabase"
			helpers.flash_error(flash_message, allow_html=False)
			return plugins.toolkit.redirect_to('{url}/cassbase')
