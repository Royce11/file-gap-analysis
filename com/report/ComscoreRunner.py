import boto3
from com.report import ComscoreIntlTransform
import json

client = boto3.client('s3')

dict_list = []

ComscoreIntlTransform.initCsv()

def getPrefix(commonPrefixList):
    prefixList = []
    for prefixDict in commonPrefixList:
        prefixList.append(prefixDict.get('Prefix'))

    return prefixList

def getFinalContentFromResponse(response,bucket):
    if "CommonPrefixes" in response.keys():
        prefixList = getPrefix(response.get('CommonPrefixes'))
        for prefix in prefixList:
            response = client.list_objects_v2(Bucket=bucket,Prefix = prefix,Delimiter = '/')
            getFinalContentFromResponse(response,bucket)
    if "Contents" in response.keys():
        for content in response.get('Contents'):
            finalContentList.append(content.get('Key'))

    return finalContentList

fileObj = open('/home/osboxes/shared-windows10/comscore_intl_batchwise_input.txt','r')
fileList= fileObj.readlines()

pathsList = []
for stripNewLine in fileList:
    pathsList.append(stripNewLine.rstrip())

jsonObj = open('/home/osboxes/shared-windows10/comscore_raw_cadence.json','r')
hpe_original_filePattern_dict = json.load(jsonObj)

for args in pathsList:
    finalContentList = []

    bucket = args.split('/')[0]
    prefix = args.replace('/','%',1).split('%')[1]

    # capturePrefix = r'.*/(?P<vendor>\w+)/clean/(?P<type>\w+)/(?P<datasource>[A-Za-z0-9_-]+)/'
    # vendor = re.match(capturePrefix,prefix).group(1)
    # type = re.match(capturePrefix,prefix).group(2)
    # datasource = re.match(capturePrefix,prefix).group(3)

    # metadata = {'vendor' : vendor, 'datasource' : datasource, 'country' : 'us', 'type' : type}

    # if datasource in hpe_original_filePattern_dict.keys():
    #     metadata['cadence'] = hpe_original_filePattern_dict.get(datasource)

    response = client.list_objects_v2(Bucket= bucket ,Prefix = prefix,Delimiter = '/')

    finalResponse = getFinalContentFromResponse(response,bucket)

    dict_list.append(ComscoreIntlTransform.getDictListForHPEOriginal(finalResponse,**hpe_original_filePattern_dict))