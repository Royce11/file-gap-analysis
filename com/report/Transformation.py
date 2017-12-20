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
                if i > date(2016, 1, 1):
                    yield i


def getFormattedDate(dateElement):

    if '-' not in dateElement:
        dateElement = '-'.join(map(str,dateElement[1:4]))

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


def getDictListFromResponseContents(response, **keywords):

    dict_list = []
    generalFilePattern = []
    finalContentList = []
    hispFilePattern = []

    filenamePattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).*)'
    for key in response.keys():
        if key == "Contents":
            for data in response[key]:
                content = data.get("Key")
                finalContentList.append(''.join(map(str, content))) ## init 3
            for element in finalContentList:
                if '_hisp.' in element:
                    hispFilePattern += re.findall(filenamePattern,element)  ##init 2
                else:
                    generalFilePattern += re.findall(filenamePattern,element) ##init 1

            general_missing_set = getMissingDatesSetForDict(generalFilePattern,**keywords) ##init 4
            general_dict = generateDictForCsv(general_missing_set,**keywords) ##init 6
            keywords['hisp'] ="N"
            dict_list.append(general_dict)

            if hispFilePattern:
                keywords['hisp'] ="Y"
                hisp_missing_set = getMissingDatesSetForDict(hispFilePattern,**keywords) ##init 5
                hisp_dict =  generateDictForCsv(hisp_missing_set,**keywords)  ##init 7
                dict_list.append(hisp_dict)


    return dict_list

def getDictListFromResponseCommonPrefixes(response, **keywords):

    finalContentList = []
    dict_list = []
    for key in response.keys():
        if key == 'CommonPrefixes':
            for data in response[key]:
                content = data.get("Prefix")
                finalContentList.append(content.split("/")[-2])

    general_missing_set = getMissingDatesSetForDict(finalContentList,**keywords)
    general_dict = generateDictForCsv(general_missing_set,**keywords)
    dict_list.append(general_dict)

    return dict_list

def getDictListForComscoreIntl(response, **keywords):

    finalContentList = []
    dict_list = []
    generalFilePattern = []
    personDemosFilePattern = []
    machineDemosFilePattern = []
    personDemosFileLists = []
    machineDemosFileLists = []

    filenamePattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).*)'
    demosPattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2}).*)'

    for key in response.keys():
        if key == "Contents":
            for data in response[key]:
                content = data.get("Key")
                finalContentList.append(''.join(map(str, content)))
            for element in finalContentList:
                if 'Demographic' in element:
                    if "PersonDemographic" in re.match(demosPattern,element).group(1):
                        personDemosFilePattern += re.findall(demosPattern,element)
                    if "MachineDemographic" in re.match(demosPattern,element).group(1):
                        machineDemosFilePattern += re.findall(demosPattern,element)
                else:
                    generalFilePattern += re.findall(filenamePattern,element)

            general_missing_set = getMissingDatesSetForDict(generalFilePattern,**keywords) ##init 4
            general_dict = generateDictForCsv(general_missing_set,**keywords) ##init 6
            keywords['hisp'] = "N"
            dict_list.append(general_dict)

            if personDemosFilePattern:
                keywords['datasource'] = "person-demographic"
                for tupleElement in personDemosFilePattern:
                    personDemosFileLists.append(insertDay(tupleElement))

                personDemosMissingSet = getMissingDatesSetForDict(personDemosFileLists,**keywords)
                personDemos_dict = generateDictForCsv(personDemosMissingSet,**keywords)
                dict_list.append(personDemos_dict)


            if machineDemosFilePattern:
                keywords['datasource'] = "machine-demographic"
                for tupleElement in machineDemosFilePattern:
                    machineDemosFileLists.append(insertDay(tupleElement))

                machineDemosMissingSet = getMissingDatesSetForDict(machineDemosFileLists,**keywords)
                machineDemos_dict = generateDictForCsv(machineDemosMissingSet,**keywords)
                dict_list.append(machineDemos_dict)

    return dict_list

def insertDay(tupleElement):
    tempList = list(tupleElement)
    tempList.insert(len(tupleElement)-1,'01')
    tupleElement = tuple(tempList)
    return tupleElement

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
        general_missing_set = getMissingDatesSetForDict(dataSourceDict.get(datasourceKey),**keywords) ##init 4
        general_dict = generateDictForCsv(general_missing_set,**keywords) ##init 6
        # keywords['hisp'] = "N"
        dict_list.append(general_dict)

def pickCorrectRegex(regexIterable,filename):
    match = ()
    for pattern in regexIterable.keys():
        match = re.findall(pattern,filename)
        if match:
            tempList = list(match[0])
            tempList.insert(len(match[0]),regexIterable.get(pattern))
            match = tuple(tempList)
            break
    return match

def createDataSourceDictfromListofFileNameTuples(fileNamesList):
    dataSourceDict = {}
    for fileTupleElement in fileNamesList:
        dataSourceDict.setdefault(str(fileTupleElement[4])+str(fileTupleElement[5]),[]).append(fileTupleElement[0:4])
    return dataSourceDict