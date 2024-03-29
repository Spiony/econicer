import csv
import datetime
from pathlib import Path
from typing import List

import pandas as pd

from econicer.auxiliary import str2num
from econicer.account import BankAccount


def countKeys(inDict, key):
    count = sum([1 for k in inDict.keys() if k.split(".")[0] == key])
    return count


def invertDict(singleLayerDict):
    invertedDict = {}
    for k, v in singleLayerDict.items():
        if v in invertedDict:
            count = countKeys(invertedDict, v)

            v = f"{v}.{count}"

        invertedDict[v] = k

    return invertedDict


def getKeywordValue(lines: List[str], keyword: str, sep: str):
    for line in lines:
        if not len(line):
            continue

        data = line.split(sep)

        if data[0] == keyword:
            value = data[1].strip()
            return value

    return None


class FileIO:
    def __init__(self, filepath, settings, str2numConversion=True):
        self.filepath = filepath
        self.settings = settings
        self.str2numConversion = str2numConversion

    def updateFilepath(self, filepath):
        self.filepath = filepath

    def readHeader(self):
        """extract header account information from database"""
        with open(self.filepath) as csvFile:
            header = [next(csvFile) for x in range(20)]

        sep = self.settings.delimiter

        owner = getKeywordValue(header, self.settings.owner, sep)
        accountNumber = getKeywordValue(header, self.settings.accountNumber, sep)
        bank = getKeywordValue(header, self.settings.bank, sep)

        return owner, accountNumber, bank

    def readBody(self):
        with open(self.filepath, "r") as f:
            noSeps = []
            for _ in range(20):
                linedata = f.readline()
                noSeps.append(linedata.count(";"))
        noHeaderLines = noSeps.index(max(noSeps))

        transactionDF = pd.read_csv(
            self.filepath,
            sep=self.settings.delimiter,
            header=noHeaderLines,
            skip_blank_lines=False,
            encoding=self.settings.encoding,
        )

        if isinstance(self.settings.table, dict):
            renameTable = invertDict(self.settings.table)
            transactionDF = transactionDF.rename(columns=renameTable)

        transactionDF["date"] = pd.to_datetime(
            transactionDF["date"], format=self.settings.dateFormat
        )

        transactionDF["valuta"] = pd.to_datetime(
            transactionDF["valuta"], format=self.settings.dateFormat
        )

        if self.str2numConversion:
            transactionDF["value"] = transactionDF["value"].apply(str2num)
            transactionDF["saldo"] = transactionDF["saldo"].apply(str2num)

        return transactionDF

    def readDB(self, groupSettings):
        owner, accountNumber, bank = self.readHeader()
        transactionDF = self.readBody()

        return BankAccount(owner, accountNumber, bank, transactionDF, groupSettings)

    def writeDB(self, account):
        """Write all account inforrmation to database"""

        filepath = Path(self.filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(
                csvfile,
                delimiter=self.settings.delimiter,
                quotechar="'",
                quoting=csv.QUOTE_MINIMAL,
            )

            # Write header
            csvwriter.writerow(["##ECONICER DATABASE"])
            csvwriter.writerow(
                [datetime.datetime.now().strftime("File created at %Y-%m-%d %H:%M:%S")]
            )
            csvwriter.writerow(["#GENERALINFO"])
            csvwriter.writerow(["owner", account.owner])
            csvwriter.writerow(["account number", account.accountNumber])
            csvwriter.writerow(["bank", account.bank])
            csvwriter.writerow(["#STATS"])
            csvwriter.writerow(["totalSum", "..."])
            csvwriter.writerow(["expenseGroupNames", "..."])
            csvwriter.writerow(["expenseGroupValues", "..."])
            csvwriter.writerow(["#TRANSACTIONS"])

        # write table
        account.transactions.to_csv(
            filepath,
            mode="a",
            sep=self.settings.delimiter,
            index=False,
            date_format=self.settings.dateFormat,
        )
