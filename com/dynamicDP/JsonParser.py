import json

fileObj = open('/home/osboxes/shared-windows10/rentrak_original_signal_20171120-1034.txt','r')

fileList= fileObj.readlines()

keysList = []

for stripNewLine in fileList:
    keysList.append(stripNewLine.rstrip().replace('s3://digitas-dct-work/',''))

print(keysList)

jsonObj = open('/home/osboxes/shared-windows10/RTDTAdDelivery_6193_20170903.dat._PEL.bz2','r')
parsed_json = json.load(jsonObj)

print(parsed_json)