import re
from datetime import datetime, timedelta,date
from itertools import tee
from collections import OrderedDict
import csv

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
                if i > date(2017, 1, 1):
                    yield i



def getFormattedDate(dateElement):

    if '-' not in dateElement:
        dateElement = '-'.join(map(str,dateElement[0:3]))

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
    # dictForCsv["File Extension"]= keywords['File Extension']

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

def getDictListForHPEOriginal(response, **regexKeywords):

    dict_list = []
    generalFilePattern = []
    keywords = {}

    for fullFileName in response:
        generalFilePattern.append(pickCorrectRegex(regexKeywords,fullFileName))

    dataSourceDict = createDataSourceDictfromListofFileNameTuples(generalFilePattern)

    for datasourceKey in dataSourceDict:
        keywords['datasource'] = datasourceKey.split('-')[4]
        keywords['vendor'] = datasourceKey.split('-')[0]
        keywords['country'] = datasourceKey.split('-')[2]
        keywords['cadence'] = datasourceKey.split('-')[3]
        # keywords['File Extension'] = datasourceKey.split('-')[5]
        general_missing_list = getMissingDatesSetForDict(dataSourceDict.get(datasourceKey),**keywords) ##init 4
        # general_missing_set = set(general_missing_list)
        general_dict = generateDictForCsv(general_missing_list,**keywords) ##init 6

        dict_list.append(general_dict)

    return dict_list

def pickCorrectRegex(regexIterable,filename):
    for pattern in regexIterable.keys():
        match = re.findall(pattern,filename,flags=re.IGNORECASE)
        if match:
            tempList = list(match[0])
            tempList.insert(len(match[0]),regexIterable.get(pattern))
            match = tuple(tempList)
            break
    return match

def createDataSourceDictfromListofFileNameTuples(fileNamesList):
    dataSourceDict = {}
    for fileTupleElement in fileNamesList:
        if fileTupleElement:
            dataSourceDict.setdefault(str(fileTupleElement[3]),[]).append(fileTupleElement[0:3])
    return dataSourceDict