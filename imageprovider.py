
from resourceapi import ResourceApi
from idsapi import IdsApi
import requests
import pprint
import json
import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

providerUrl = "https://provider"
catalog_title = "drone images"
catalog_description = "Example Image Catalog"
representation_type = "jpg"
resource_name = "field image"
resource_description= "Drone image from agricultular field"
resource_keywords = ["agriculture", "flexigrobots","luke","drone"]
provider_link = "https://provider"

## Create new catalog
class IDSImageProvider:
	def __init__(self):
		self.provider = ResourceApi(providerUrl)
		catalogs = self.provider.get_catalogs()
		#print(catalogs["_embedded"]["catalogs"])
		if (len(catalogs["_embedded"]["catalogs"])>0):
			#print(str(len(catalogs["_embedded"]["catalogs"])))
			for cat in catalogs["_embedded"]["catalogs"]:
				if(cat["title"] == catalog_title):
					print("found existing catalog: "+cat["_links"]["self"]["href"])
					self.catalog = cat["_links"]["self"]["href"]
				else:
					print("no catalogs with title: "+catalog_title)
					self.catalog = self.createCatalog(catalog_title, catalog_description)

		else:
			self.catalog = self.createCatalog(catalog_title, catalog_description)
			print(self.catalog)

	def createCatalog(self, title, description=""):
		body = "{\"title\": \""+title+"\",\"description\": \""+description+"\"}"
		return self.provider.create_catalog(json.loads(body))

	def createRepresentation(self,representation):
		print("createRepresentation")
		representations = self.provider.get_representations()
		#print(representations["_embedded"]["representations"])
		if (len(representations["_embedded"]["representations"])>0):
			for rep in representations["_embedded"]["representations"]:
				if(rep["mediaType"] == representation):
					print("found existing representation")
					self.representation = rep["_links"]["self"]["href"]
					return 
		self.representation = self.provider.create_representation(data={"mediaType": representation})
		print("create new representation: self.representation")


	def createResource(self, title):
		print("createResource")
		resources = self.provider.get_catalog_resources(self.catalog)
		#print(str(resources["_embedded"]["resources"]))
		if (len(resources["_embedded"]["resources"])>0):
			for res in resources["_embedded"]["resources"]:
				if(res["title"] == title):
					print("found existing resource: "+res["_links"]["self"]["href"])
					self.offers = res["_links"]["self"]["href"]
				else:
					print("no resource with title: "+title)
					self.offers = self.provider.create_offered_resource(data={"title": title, "description": resource_description, "keywords": resource_keywords, "sovereign": provider_link, "publisher": provider_link})
					self.provider.add_resource_to_catalog(self.catalog, self.offers)
					self.provider.add_representation_to_resource(self.offers, self.representation)
		else:
		## Create image
			self.offers = self.provider.create_offered_resource(data={"title": title, "description": resource_description, "keywords": resource_keywords, "sovereign": provider_link, "publisher": provider_link})
			self.provider.add_resource_to_catalog(self.catalog, self.offers)
			self.provider.add_representation_to_resource(self.offers, self.representation)

	def createOffer(self):
		print("createOffer")
		contract = self.provider.create_contract()
		use_rule = self.provider.create_rule()
		self.provider.add_contract_to_resource(self.offers, contract)
		self.provider.add_rule_to_contract(contract, use_rule)


	def createArtifact(self, path):
		print("Create artifact: "+path)
		name = path.split("/")
		name_str = name[len(name)-1]
		print(name_str)
		artifact = self.provider.create_artifact(data={"value": "","title":name_str})
		in_file = open(path, "rb") # opening for [r]eading as [b]inary
		data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
		in_file.close()
		self.provider.put_data(artifact, data= data)
		self.provider.add_artifact_to_representation(self.representation, artifact)


class FSObserver:
	def __init__(self, path, ids):
		self.path = path
		self.ids = ids

	def on_created(self,event): 
		print(f"hey, {event.src_path} has been created!") 
		self.newfile = event.src_path

	def on_deleted(self,event):
		print(f"what the f**k! Someone deleted {event.src_path}!")

	def on_modified(self,event):
		if (self.newfile == event.src_path):
			historicalSize = -1
			while (historicalSize != os.path.getsize(event.src_path)):
				historicalSize = os.path.getsize(event.src_path)
				time.sleep(1)
			print(f"hey buddy, {event.src_path} has been modified")
			self.ids.createArtifact(event.src_path)
			self.newfile = ""

	def on_moved(self,event):
		print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")


if __name__ == "__main__":
	path = "/var/flexigrobots/assets"

	print("Start Image observer for path: "+path)
	# This creates resource catalog and resource but it should be checked if catalog based on path exist allready and not 
	# create new one on each startup... TBD
	idsconnector = IDSImageProvider()
	idsconnector.createRepresentation(representation_type)
	idsconnector.createResource(resource_name)
	idsconnector.createOffer()

	filemonitor = FSObserver(path, idsconnector)
	patterns = ["*"]
	ignore_patterns = None
	ignore_directories = False
	case_sensitive = True
	my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
	my_event_handler.on_created = filemonitor.on_created
	my_event_handler.on_deleted = filemonitor.on_deleted
	my_event_handler.on_modified = filemonitor.on_modified
	my_event_handler.on_moved = filemonitor.on_moved

	go_recursively = True
	my_observer = Observer()
	my_observer.schedule(my_event_handler, path, recursive=go_recursively)
	my_observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		my_observer.stop()
		my_observer.join()




