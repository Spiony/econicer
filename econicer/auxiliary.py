import json
import datetime
import pandas as pd
import numpy as np


def nextMonth(ts):
    if ts.month <= 11:
        firstDayNextMonth = datetime.datetime(ts.year, ts.month + 1, ts.day)
    else:
        firstDayNextMonth = datetime.datetime(ts.year + 1, 1, 1)
    return np.datetime64(firstDayNextMonth), firstDayNextMonth


def endOfMonth(ts):
    '''Takes a datetime.date and returns the date for the last day in the
    same month.'''
    _, firstDayNextMonth = nextMonth(ts)
    lastDayOfMonth = datetime.datetime.combine(
        firstDayNextMonth - datetime.timedelta(1),
        datetime.datetime.min.time())
    return np.datetime64(lastDayOfMonth), lastDayOfMonth


def nextYear(ts):
    firstDayNextYear = datetime.datetime.combine(
        datetime.datetime(ts.year + 1, 1, 1), datetime.datetime.min.time())
    return np.datetime64(firstDayNextYear), firstDayNextYear


def endOfYear(ts):
    lastDayOfYear = datetime.datetime.combine(
        datetime.datetime(ts.year, 12, 31), datetime.datetime.min.time())
    return np.datetime64(lastDayOfYear), lastDayOfYear


def str2num(stringInput):

    if isinstance(stringInput, float):
        return stringInput

    if isinstance(stringInput, str):
        if "." in stringInput and "," in stringInput:
            stringInput = stringInput.replace('.', '')
            stringInput = stringInput.replace(',', '.')
            return float(stringInput)
        elif "," in stringInput:
            stringInput = stringInput.replace(',', '.')
            return float(stringInput)
        else:
            return float(stringInput)


def json2Dict(filepath):
    jsonFile = open(filepath, encoding='utf-8')
    jsonContent = jsonFile.read()
    return json.loads(jsonContent)
