import boto3


finalContentList = []


def getS3Client():
    return boto3.client('s3')

# def __init__(self,response):
#     self.response = response

def getPrefix(commonPrefixList):
    prefixList = []
    for prefixDict in commonPrefixList:
        prefixList.append(prefixDict.get('Prefix'))

    return prefixList

def getFinalContentFromResponse(client,response,bucket):
    if "CommonPrefixes" in response.keys():
        prefixList = getPrefix(response.get('CommonPrefixes'))
        for prefix in prefixList:
            response = client.list_objects_v2(Bucket=bucket,Prefix = prefix,Delimiter = '/')
            getFinalContentFromResponse(client,response,bucket)
    if "Contents" in response.keys():
        for content in response.get('Contents'):
            finalContentList.append(content.get('Key'))

    return finalContentList