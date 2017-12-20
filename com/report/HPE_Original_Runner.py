import boto3
from com.report import TransformHPEOriginal
import json

client = boto3.client('s3')

dict_list = []

TransformHPEOriginal.initCsv()

fileObj = open('/home/osboxes/shared-windows10/hpe_batchwise_input.txt','r')

fileList= fileObj.readlines()

pathsList = []

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


for stripNewLine in fileList:
    pathsList.append(stripNewLine.rstrip())

jsonObj = open('/home/osboxes/shared-windows10/hpe_batchwise_cadence.json','r')
hpe_original_filePattern_dict = json.load(jsonObj)

for args in pathsList:
    finalContentList = []

    bucket = args.split('/')[0]
    prefix = args.replace('/','%',1).split('%')[1]

    response = client.list_objects_v2(Bucket= bucket ,Prefix = prefix,Delimiter = '/')

    finalResponse = getFinalContentFromResponse(response,bucket)

    dict_list.append(TransformHPEOriginal.getDictListForHPEOriginal(finalResponse,**hpe_original_filePattern_dict))

    # while "CommonPrefixes" in response.keys():
    #     if response.get('CommonPrefixes'):
    #         for prefixDict in response.get('CommonPrefixes'):
    #             prefix = prefixDict.get('Prefix')
    #             response = client.list_objects_v2(Bucket='digitas-client-data',Prefix = prefix,Delimiter = '/')