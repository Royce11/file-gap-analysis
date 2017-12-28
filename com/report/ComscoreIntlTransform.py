import re
from datetime import datetime, timedelta,date
from itertools import tee
from collections import OrderedDict
import csv
import collections

def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T

def writeToCsv(dictObject):
    with open('missingDates.csv', 'a') as f:# Just use 'w' mode in 3.x
        w = csv.DictWriter(f, dictObject.keys())
        w.writerow(dictObject)

def initCsv():
    f = open('missingDates.csv', "w+")
    fieldnames = ['vendor','datasource','country','cadence','Year-Month','Missing Dates','Missing Count']
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    f.close()

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b)
    return zip(a, b)

def missing_dates(dates,timeDeltaParam):
    if dates:
        dates.append(date.today())
        for prev, curr in pairwise(sorted(dates)):
            i = prev
            while i + timedelta(timeDeltaParam) < curr:
                i += timedelta(timeDeltaParam)
                if i > date(2015, 12, 31):
                    yield i


def getFormattedDate(dateElement):

    if '-' not in dateElement:
        dateElement = '-'.join(map(str,dateElement[0:3]))

    # dateFormat = datetime.date(datetime.strptime(dateElement,'%W'))
    dateFormat = datetime.date(datetime.strptime(dateElement,'%Y-%m-%d'))

    return dateFormat

def d_range(d1,d2):
    delta = d2 - d1 #assumes second date is always after first
    return [d1 + timedelta(days=i) for i in range(delta.days + 1)]

def getAvailableDates(datesList):
    finaldateTupleList = []
    if len(datesList):
        for dateElement in datesList:
            try:
                finaldateTupleList.append(getFormattedDate(dateElement))
            except ValueError:
                pass

    return finaldateTupleList

def getMissingDatesSetForDict(fileNamesList, **keywords):
    # missing_dates_set = set()
    missing_dates_list = []
    timeDeltaParam_dict = {'daily' : 1, 'weekly' : 10, 'monthly' : 45}
    timeDeltaParam = timeDeltaParam_dict.get(keywords.get('cadence'))

    if len(fileNamesList):
        availableDatesList = getAvailableDates(fileNamesList)
        for missing in missing_dates(availableDatesList,timeDeltaParam):
            missing_dates_list.append(missing)
            # my_range = d_range(min(availableDatesList), max(availableDatesList))
            # missing_dates_set = sorted(set(my_range).difference(set(availableDatesList)))
    return missing_dates_list
    # return missing_dates_set

def generateDictForCsv(missing_dates_set,**keywords):
    dictForCsv = OrderedDict()
    dictForCsv["vendor"]= keywords['vendor']
    dictForCsv["datasource"]= keywords['datasource']
    dictForCsv["country"]= keywords['country']
    dictForCsv["cadence"]= keywords['cadence']

    tempDict = OrderedDict()

    if 'hisp' in keywords:
        if keywords['hisp'] == 'Y':
            dictForCsv["datasource"] = keywords['datasource'] + ' hispanic'

    if len(missing_dates_set):
        for missing_date_key in missing_dates_set:
            tempDict.setdefault(str(missing_date_key.year) + '-' + str(missing_date_key.month),[]).append(missing_date_key.day)

        for key,value in tempDict.items():
            dictForCsv["Year-Month"] = key
            dictForCsv["Missing Dates"] = value
            dictForCsv["Missing Count"] = len(value)
            writeToCsv(dictForCsv)

    return dictForCsv

def rentrakFileHandler(response,test):
    generalFilePattern = []
    hispFilePattern = []

    for fullFileName in response:
        if "hisp" in fullFileName:
            hispanicExtractedDate=getListofDates(test,fullFileName)
            if hispanicExtractedDate:
                hispFilePattern.append(getFormattedDate(hispanicExtractedDate))
        else:
            extractedDate=getListofDates(test,fullFileName)
            if extractedDate:
                generalFilePattern.append(getFormattedDate(extractedDate))

    return set(generalFilePattern)

def getDictListForHPEOriginal(response,**args):

    dict_list = []
    generalFilePattern = []
    hispFilePattern = []
    keywords = {}
    test =args.get('regex')

    FilePattern = namedtuple_with_defaults('FilePattern', 'general hispanic')


    if args.get('cleanFlag') == True:
        if "CommonPrefixes" in response.keys():
            for prefixDictElement in response.get('CommonPrefixes'):
                generalFilePattern.append(getFormattedDate(prefixDictElement.get('Prefix').split('/')[5].strip("dt=")))

    if args.get('cleanFlag') == False:
        for fullFileName in response:
            extractedDate=getListofDates(test,fullFileName)
            if extractedDate:
                if "hisp" in fullFileName:
                    args['type'] = 'hispanic'
                    hispFilePattern.append(getFormattedDate(extractedDate))
                else:
                    args['type'] = 'non-hispanic'
                    generalFilePattern.append(getFormattedDate(extractedDate))

    if args.get('vendor') == 'rentrak':
        return FilePattern(set(generalFilePattern),set(hispFilePattern))
    else:
        return FilePattern(set(generalFilePattern))

    dataSourceDict = createDataSourceDictfromListofFileNameTuples(generalFilePattern)


    for datasourceKey in dataSourceDict:
        keywords['datasource'] = datasourceKey.split('-')[4]
        keywords['vendor'] = datasourceKey.split('-')[0]
        keywords['country'] = datasourceKey.split('-')[2]
        keywords['cadence'] = datasourceKey.split('-')[3]
        general_missing_set = getMissingDatesSetForDict(dataSourceDict.get(datasourceKey),**keywords) ##init 4
        general_dict = generateDictForCsv(general_missing_set,**keywords) ##init 6
        # keywords['hisp'] = "N"
        dict_list.append(general_dict)


def insertDay(tupleElement):
    tempList = list(tupleElement)
    tempList.insert(len(tupleElement),'01')
    tupleElement = tuple(tempList)
    return tupleElement

def getListofDates(comscore_conf,filename):
    for pattern in comscore_conf:
        match = re.findall(pattern,filename)
        if match:
            if int(match[0][0]) > 2015:
                if len(match[0]) < 3:
                    match = insertDay(match[0])
                    return match
                return match[0]

def createDataSourceDictfromListofFileNameTuples(fileNamesList):
    dataSourceDict = {}
    for fileTupleElement in fileNamesList:
        dataSourceDict.setdefault(str(fileTupleElement[4])+str(fileTupleElement[5]),[]).append(fileTupleElement[0:4])
    return dataSourceDict