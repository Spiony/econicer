import json
import datetime
import numpy as np


def nextMonth(date):
    """returns datetime object of first day of next month"""
    if date.month <= 11:
        firstDayNextMonth = datetime.datetime(date.year, date.month + 1, 1)
    else:
        firstDayNextMonth = datetime.datetime(date.year + 1, 1, 1)
    return np.datetime64(firstDayNextMonth), firstDayNextMonth


def endOfMonth(date):
    """returns datetime object of last day of next month"""
    _, firstDayNextMonth = nextMonth(date)
    lastDayOfMonth = datetime.datetime.combine(
        firstDayNextMonth - datetime.timedelta(1), datetime.datetime.min.time()
    )
    return np.datetime64(lastDayOfMonth), lastDayOfMonth


def nextYear(date):
    """returns datetime object of beginning of next year"""
    firstDayNextYear = datetime.datetime.combine(
        datetime.datetime(date.year + 1, 1, 1), datetime.datetime.min.time()
    )
    return np.datetime64(firstDayNextYear), firstDayNextYear


def endOfYear(date):
    """returns datetime object for the end of this year"""
    lastDayOfYear = datetime.datetime.combine(
        datetime.datetime(date.year, 12, 31), datetime.datetime.min.time()
    )
    return np.datetime64(lastDayOfYear), lastDayOfYear


def str2num(stringInput):
    if isinstance(stringInput, int):
        return stringInput * 100

    if isinstance(stringInput, float):
        return int(stringInput * 100)

    if isinstance(stringInput, str):
        mult = 1
        if "-" in stringInput:
            stringInput = stringInput.replace("-", "")
            mult = -1

        if "." in stringInput and "," in stringInput:
            stringInput = stringInput.replace(".", "")
            stringInput = stringInput.replace(",", ".")
            a, b = stringInput.split(".")
            v = 100 * int(a) + int(b)
        elif "," in stringInput:
            stringInput = stringInput.replace(",", ".")
            a, b = stringInput.split(".")
            v = 100 * int(a) + int(b)
        else:
            v = int(stringInput)

        return mult * v


def json2Dict(filepath):
    with open(str(filepath), "r", encoding="utf-8") as jsonFile:
        jsonContent = jsonFile.read()
    return json.loads(jsonContent)
