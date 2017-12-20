import boto3
from com.report import ComscoreCleanTransformation
import json
import re

client = boto3.client('s3')

dict_list = []

ComscoreCleanTransformation.initCsv()

fileObj = open('/home/osboxes/shared-windows10/comscore_clean_input.txt','r')
fileList= fileObj.readlines()

pathsList = []
for stripNewLine in fileList:
    pathsList.append(stripNewLine.rstrip())

jsonObj = open('/home/osboxes/shared-windows10/comscore_clean_cadence.json','r')
hpe_original_filePattern_dict = json.load(jsonObj)

for args in pathsList:
    finalContentList = []

    bucket = args.split('/')[0]
    prefix = args.replace('/','%',1).split('%')[1]

    capturePrefix = r'vendor-(?P<vendor>\w+)/clean/(?P<datasource>[A-Za-z0-9_-]+)/parquet/country=(?P<country>\w+)/'
    vendor = re.match(capturePrefix,prefix).group(1)
    country = re.match(capturePrefix,prefix).group(3)
    datasource = re.match(capturePrefix,prefix).group(2)

    metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : country}

    if datasource in hpe_original_filePattern_dict.keys():
        metadata['cadence'] = hpe_original_filePattern_dict.get(datasource)

    response = client.list_objects_v2(Bucket= bucket ,Prefix = prefix,Delimiter = '/')

    dict_list.append(ComscoreCleanTransformation.getDictListForHPEOriginal(response,**metadata))