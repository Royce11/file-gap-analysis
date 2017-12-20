from sys import argv
import boto3
import re
import csv
from com.report import Transformation

client = boto3.client('s3')
# s3 = boto3.resource('s3')
# my_bucket = s3.Bucket('idiom-vendor-data')
dict_list = []

def writeToCsv(dictList):
    with open('missingDates.csv', 'a') as f:# Just use 'w' mode in 3.x
        for dictVendor in dict_list:
            for dictObject in dictVendor:
                w = csv.DictWriter(f, dictObject.keys())
                w.writeheader()
                w.writerow(dictObject)

Transformation.initCsv()
# f = open('missingDates.csv', "w+")
# f.close()

for args in argv[1:]:

    # filenamePattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).*)'
    captureArgs = r'.*/(?P<vendor>\w+)/(?P<country>\w+)/(?P<datasource>[A-Za-z0-9_-]+)/(?P<cadence>\w+)/'
    vendor = re.match(captureArgs,args).group(1)
    datasource = re.match(captureArgs,args).group(3)
    country = re.match(captureArgs,args).group(2)
    cadence = re.match(captureArgs,args).group(4)

    metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : country, 'cadence' : cadence}

    response = client.list_objects_v2(Bucket='idiom-vendor-data',Prefix = args,Delimiter = '/')

    dict_list.append(Transformation.getDictListFromResponseCommonPrefixes(response,**metadata))

# writeToCsv(dict_list)
