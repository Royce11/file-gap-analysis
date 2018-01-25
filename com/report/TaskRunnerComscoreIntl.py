import boto3
import re
from com.report import Transformation
import json

client = boto3.client('s3')

dict_list = []

Transformation.initCsv()

fileObj = open('/home/osboxes/shared-windows10/comscore_intl_input_2018.txt','r')

fileList= fileObj.readlines()

pathsList = []

for stripNewLine in fileList:
    pathsList.append(stripNewLine.rstrip())

for args in pathsList:

    captureArgs = r'(?P<vendor>[A-Za-z0-9_-]+)/raw/original/(?P<country>\w+)/(?P<datasource>[A-Za-z0-9_-]+)/'
    vendor = re.match(captureArgs,args).group(1).replace('vendor-','')
    datasource = re.match(captureArgs,args).group(3)
    country = re.match(captureArgs,args).group(2)

    metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : country, 'cadence' : 'daily'}


    jsonObj = open('/home/osboxes/shared-windows10/comscore_intl_cadence.json','r')
    comscore_intl_cadence_dict = json.load(jsonObj)

    if vendor == 'comscore':
        if datasource in comscore_intl_cadence_dict:
            metadata['cadence'] = comscore_intl_cadence_dict.get(datasource)

    response = client.list_objects_v2(Bucket='idiom-vendor-data',Prefix = args)

    dict_list.append(Transformation.getDictListForComscoreIntl(response,**metadata))

