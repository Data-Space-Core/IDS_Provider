# USAGE #

Repository contains a Python application if now monitoring folder defined in the imageprovider.py file and adds new artifact to connector when ever new file is added to the folder

## Using provider ##

In imageprovider.py there are configurations to staticaly link to the connector. Configurations are:
````
    providerUrl = <URL to the connecor API>
	catalog_title = <name of the catalog to which data offer is added>
	catalog_description = <description of the catalog to which data offer is added>
	representation_type = <file/data tyoe>
	resource_name = <name of the resource>
	resource_description= <description of the resource>
	resource_keywords = [<list of keywords>]
	provider_link = <link to the provider web>
````

Provider is monitoring file system folder and when file is added there it is added as data artifact automatically. 
````
path = <folder absolute path>
````
