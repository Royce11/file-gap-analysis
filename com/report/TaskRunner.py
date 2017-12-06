from sys import argv
import boto3
import re
import csv
from com.report import Transformation

client = boto3.client('s3')

dict_list = []

# def writeToCsv(dictList):
#     with open('missingDates.csv', 'a') as f:# Just use 'w' mode in 3.x
#         for dictVendor in dict_list:
#             for dictObject in dictVendor:
#                 w = csv.DictWriter(f, dictObject.keys())
#                 w.writeheader()
#                 w.writerow(dictObject)

Transformation.initCsv()

for args in argv[1:]:

    # filenamePattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).*)'
    captureArgs = r'.*/(?P<vendor>\w+)/(?P<datasource>[A-Za-z0-9_-]+)/(?P<country>\w+)/'
    vendor = re.match(captureArgs,args).group(1)
    datasource = re.match(captureArgs,args).group(2)
    country = re.match(captureArgs,args).group(3)

    metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : country, 'cadence' : 'daily'}

    rentrak_cadence_dict = {'ad-delivery' : 'daily', 'ad-metadata' : 'monthly', 'features' : 'monthly', 'program-metadata' : 'monthly', 'program-tunein' : 'daily', 'reporting' : 'monthly', 'roster' : 'monthly', 'series-genre' : 'monthly'}
    comscore_cadence_dict = {'census-ip' : 'daily', 'search-entity-map' : 'weekly', 'search' : 'weekly', 'traffic' : 'daily', 'pel-xref' : 'monthly'}

    if vendor == 'rentrak':
        if datasource in rentrak_cadence_dict:
            metadata['cadence'] = rentrak_cadence_dict.get(datasource)

    if vendor == 'comscore':
        if datasource in comscore_cadence_dict:
            metadata['cadence'] = comscore_cadence_dict.get(datasource)

    response = client.list_objects_v2(Bucket='idiom-vendor-data',Delimiter = '/',Prefix = args)

    dict_list.append(Transformation.getDictListFromResponseContents(response,**metadata))

# writeToCsv(dict_list)
