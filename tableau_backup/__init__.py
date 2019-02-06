import tableauserverclient as TSC
import json
import datetime
import os, errno
import logging
import zipfile
import shutil
import boto3
from argparse import ArgumentParser
import sys

project_children = {}
projects = {}
project_paths = {}

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def folder_builder(root_id):
	for project_id in project_children[root_id]:
		folder_name = projects[project_id].name
		folder_path = project_paths[root_id] + "/" + folder_name
		project_paths[project_id] = folder_path
		try:
		    os.makedirs(folder_path)
		except OSError as e:
			pass
		if project_id in project_children:
			folder_builder(project_id)

def main():
	parser = ArgumentParser()
	parser.add_argument("-c", "--config", dest="config_file_path",
	                    help="path to config file to be used", metavar="CONFIG")

	args = parser.parse_args()

	if not args.config_file_path:
		print('You must include a config file path')
		sys.exit(1)  # abort because of error
	#Get configs
	with open(args.config_file_path) as json_file:
		json_data = json.load(json_file)

	USERNAME = json_data['username']
	PASSWORD = json_data['password']
	SITE = json_data['site']
	SERVER = json_data['server']
	BACKUP_ROOT = json_data['backup_directory']
	BUCKET_NAME = json_data['bucket_name']

	#Log to backup root
	logging.basicConfig(filename=BACKUP_ROOT + '/' +'backup.log',level=logging.INFO)
	logging.info("Starting at: " + str(datetime.datetime.today()))

	#Create Backup Directory
	backup_date = datetime.datetime.today().strftime('%Y-%m-%d')
	backup_directory = BACKUP_ROOT + "/" + backup_date

	try:
	    os.makedirs(backup_directory)
	except OSError as e:
	    pass

	#Set up auth and server object
	tableau_auth = TSC.TableauAuth(USERNAME, PASSWORD, site_id=SITE)
	server = TSC.Server(SERVER, use_server_version=True)

	#Get Projects
	
	

	server.auth.sign_in(tableau_auth)

	for project in TSC.Pager(server.projects):
		projects[project.id] = project
		if project.parent_id in project_children:
			project_children[project.parent_id].append(project.id)
		else:
			project_children[project.parent_id] = [project.id]

	#Start Building
	#Root at None
	project_paths[None] = backup_directory
	folder_builder(None)

	logging.info('Folder structure built')

	#Iterate through workbooks
	for workbook in TSC.Pager(server.workbooks):
		#Get project location
		location = project_paths[workbook.project_id]
		#Download workbook without Extract to location
		server.workbooks.download(workbook.id, filepath=location, no_extract=True)

	logging.info('Workbooks downloaded')
	server.auth.sign_out()

	#Create zipfile
	backup_name = 'tableau-backup-' + backup_date + '.zip'
	backup_zip = BACKUP_ROOT + '/' + backup_name
	zipf = zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED)
	zipdir(backup_directory, zipf)
	zipf.close()

	#Remove directory
	try:
	    shutil.rmtree(backup_directory)
	except OSError as e:
	    logging.error("Error: %s - %s." % (e.filename, e.strerror))

	#upload to s3

	s3 = boto3.resource('s3')
	data = open(backup_zip, 'rb')
	s3.Bucket(BUCKET_NAME).put_object(Key=backup_name, Body=data)
	logging.info('Uploaded ' + backup_name + ' to S3 bucket ' + BUCKET_NAME)

	#Remove ZIP
	os.remove(backup_zip)
	logging.info("Ended at: " + str(datetime.datetime.today()))

if __name__ == "__main__":
    main()