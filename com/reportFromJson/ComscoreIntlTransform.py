import re
from datetime import datetime, timedelta,date
from itertools import tee


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

def getDictListForHPEOriginal(response,**args):

    dict_list = []
    generalFilePattern = []
    hispFilePattern = []
    keywords = {}
    test =args.get('regex')


    if args.get('cleanFlag') == True:
        if "CommonPrefixes" in response.keys():
            for prefixDictElement in response.get('CommonPrefixes'):
                generalFilePattern.append(getFormattedDate(prefixDictElement.get('Prefix').split('/')[5].strip("dt=")))

    if args.get('cleanFlag') == False:
        for fullFileName in response:
            extractedDate=getListofDates(test,fullFileName)
            if extractedDate:
                generalFilePattern.append(getFormattedDate(extractedDate))

    return set(generalFilePattern)

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