import re
from datetime import datetime, timedelta
from itertools import tee
from collections import OrderedDict


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b)
    return zip(a, b)

def missing_dates(dates,timeDeltaParam):
    if dates:
        for prev, curr in pairwise(sorted(dates)):
            i = prev
            while i + timedelta(timeDeltaParam) < curr:
                i += timedelta(timeDeltaParam)
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

    if 'hisp' in keywords:
        if keywords['hisp'] == 'Y':
            dictForCsv["datasource"] = keywords['datasource'] + ' hispanic'

    if len(missing_dates_set):
        for missing_date_key in missing_dates_set:
            dictForCsv.setdefault(str(missing_date_key.year) + '-' + str(missing_date_key.month),[]).append(missing_date_key.day)

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

    filenamePattern = r'.*/(?P<filename>.*(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).*)'

    for key in response.keys():
        for data in response[key]:
            content = data.get("Key")
            finalContentList.append(''.join(map(str, content)))
        for element in finalContentList:
            generalFilePattern += re.findall(filenamePattern,element)

        general_missing_set = getMissingDatesSetForDict(generalFilePattern,**keywords) ##init 4
        general_dict = generateDictForCsv(general_missing_set,**keywords) ##init 6
        keywords['hisp'] = "N"
        dict_list.append(general_dict)


    return dict_list