import csv
import datetime
from pathlib import Path

import pandas as pd

from econicer.auxiliary import str2num
from econicer.account import BankAccount


class FileIO:

    def __init__(self, filepath, settings, str2numConversion=True):

        self.filepath = filepath
        self.settings = settings
        self.str2numConversion = str2numConversion

    def readHeader(self):
        """extract header account information from database"""
        with open(self.filepath) as csvFile:
            header = [next(csvFile)
                      for x in range(self.settings.beginTable)]

        owner = header[self.settings.owner].split(
            self.settings.delimiter)[1].replace("\n", "")

        accountNumber = header[self.settings.accountNumber].split(
            self.settings.delimiter)[1].replace("\n", "")

        bank = header[self.settings.bank].split(
            self.settings.delimiter)[1].replace("\n", "")

        return owner, accountNumber, bank

    def readBody(self):

        transactionDF = pd.read_csv(
            self.filepath,
            sep=self.settings.delimiter,
            header=self.settings.beginTable,
            skip_blank_lines=False
        )

        transactionDF["date"] = pd.to_datetime(
            transactionDF["date"], format=self.settings.dateFormat)

        transactionDF["valtua"] = pd.to_datetime(
            transactionDF["valtua"], format=self.settings.dateFormat)

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
                quoting=csv.QUOTE_MINIMAL
            )

            # Write header
            csvwriter.writerow(["##ECONICER DATABASE"])
            csvwriter.writerow([
                datetime.datetime.now().strftime(
                    "File created at %Y-%m-%d %H:%M:%S")
            ])
            csvwriter.writerow(["#GENERALINFO"])
            csvwriter.writerow(["owner", account.owner])
            csvwriter.writerow(["account number", account.accountNumber])
            csvwriter.writerow(["bank", account.bank])
            csvwriter.writerow(["#STATS"])
            csvwriter.writerow(["totalSum", "..."])
            csvwriter.writerow(["expanseGroupNames", "..."])
            csvwriter.writerow(["expanseGroupValues", "..."])
            csvwriter.writerow(["#TRANSACTIONS"])

        # write table
        account.transactions.to_csv(
            filepath,
            mode='a',
            sep=self.settings.delimiter,
            index=False,
            date_format=self.settings.dateFormat
        )
