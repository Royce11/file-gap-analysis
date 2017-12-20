import boto3
from com.report import HPEOriginalTransformation
import json
import re

client = boto3.client('s3')

dict_list = []

HPEOriginalTransformation.initCsv()

fileObj = open('/home/osboxes/shared-windows10/hpe_liveramp_target_input.txt','r')
fileList= fileObj.readlines()

pathsList = []
for stripNewLine in fileList:
    pathsList.append(stripNewLine.rstrip())

jsonObj = open('/home/osboxes/shared-windows10/hpe_liveramp_target_cadence.json','r')
hpe_original_filePattern_dict = json.load(jsonObj)

for args in pathsList:
    finalContentList = []

    bucket = args.split('/')[0]
    prefix = args.replace('/','%',1).split('%')[1]

    capturePrefix = r'.*/(?P<vendor>\w+)/clean/(?P<type>\w+)/(?P<datasource>[A-Za-z0-9_-]+)/'
    vendor = re.match(capturePrefix,prefix).group(1)
    type = re.match(capturePrefix,prefix).group(2)
    datasource = re.match(capturePrefix,prefix).group(3)

    metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : 'us', 'type' : type}

    if datasource in hpe_original_filePattern_dict.keys():
        metadata['cadence'] = hpe_original_filePattern_dict.get(datasource)

    response = client.list_objects_v2(Bucket= bucket ,Prefix = prefix,Delimiter = '/')

    dict_list.append(HPEOriginalTransformation.getDictListForHPEOriginal(response,**metadata))