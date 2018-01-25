import re
from datetime import datetime, timedelta,date
from itertools import tee
from isoweek import Week
from dateutil.rrule import rrule, MONTHLY
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

def getFilteredDates(datesSet,start_date,end_date):

     datesList = list(datesSet)
     indices_to_be_removed = []

     if datesList:
         for idxCount, dateElement in enumerate(datesList):
             if dateElement < start_date or dateElement > end_date:
                 indices_to_be_removed.append(idxCount)

         datesList = [i for j, i in enumerate(datesList) if j not in indices_to_be_removed]

     return set(datesList)


def d_range(d1,d2):
    delta = d2 - d1 #assumes second date is always after first
    return [d1 + timedelta(days=i) for i in range(delta.days + 1)]

def getWeekFromDate(dateElement):
    return Week.withdate(dateElement)

def getWeeksSet(datesList):
    weeksList = []
    if datesList:
        for dateElement in datesList:
            weeksList.append(getWeekFromDate(dateElement))
    return set(weeksList)

def w_range(start_date,end_date=None):
    weeks_list = []
    startWeek = Week.withdate(start_date)
    if end_date:
        endWeek = Week.withdate(end_date)
    else:
        endWeek = Week.thisweek()
    int_week = startWeek
    while int_week < endWeek:
        int_week = int_week + 1
        weeks_list.append(int_week)
    return weeks_list

def getMonthsSet(datesList):
    monthsList = []
    if datesList:
        for dateElement in datesList:
            if dateElement.day > 16:
                dateElement = dateElement+timedelta(days=15)
            monthsList.append(datetime.strftime(dateElement,'%Y-%m'))
    return monthsList

def getMonthsRange(start_date,end_date=None):
    monthsList = []
    if end_date is None:
        end_date = date.today()
    for dt in rrule(MONTHLY, dtstart=start_date, until=end_date):
        monthsList.append(datetime.strftime(dt.date(),'%Y-%m'))
    return monthsList

def getAvailableDates(datesList):
    finaldateTupleList = []
    if len(datesList):
        for dateElement in datesList:
            try:
                finaldateTupleList.append(getFormattedDate(dateElement))
            except ValueError:
                pass

    return finaldateTupleList

def insertDay(tupleElement):
    tempList = list(tupleElement)
    tempList.insert(len(tupleElement),'01')
    tupleElement = tuple(tempList)
    return tupleElement

def extractDate(regex_from_json,filename):
    for pattern in regex_from_json:
        match = re.findall(pattern,filename)
        if match:
            if int(match[0][0]) > 2015:
                if len(match[0]) < 3:
                    match = insertDay(match[0])
                    return match
                return match[0]

def extractDateAndDatasource(regex_from_json,filename):
    for pattern in regex_from_json:
        match = re.findall(pattern,filename,flags=re.IGNORECASE)
        if match:
            if int(match[0][1]) > 2016:
                return {match[0][0]:match[0][1:4]}

def getStartDate(dateElement):
    return max(dateElement,date(2016,1,1))

def getEndDate(dateElement):
    return min(dateElement,date.today())

def prefixBuilder(prefix,**subs_value):
    prefix_with_country =  re.sub(r'\${country}',subs_value.get('country'),prefix)
    prefix_with_country_year = re.sub(r'\${year}',subs_value.get('year'),prefix_with_country)
    prefix_with_country_year_month = re.sub(r'\${month}',subs_value.get('month'),prefix_with_country_year)

    return prefix_with_country_year_month