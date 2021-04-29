import pprint
import re
from pathlib import Path

import pandas as pd
import numpy as np

from econicer.account import BankAccount
from econicer.fileIO import FileIO
from econicer.settings import BankFileSettings
from econicer.settings import DatabaseSettings
from econicer.settings import EconicerSettings
from econicer.settings import GroupSettings
from econicer import ecoplot

pp = pprint.PrettyPrinter(indent=4)


class AccountManager:

    dbFileName = "history.csv"

    def __init__(self, databasePath=".db", settingsPath=".db//settings.json"):

        self.db = Path(databasePath)
        self.settingsPath = Path(settingsPath)

        # load general settings from file
        self.settings = EconicerSettings(self.settingsPath)

        # assign database definition class
        self.dbSettings = DatabaseSettings()

        # load input file settings from file
        self.bankSettings = BankFileSettings(self.settings.inputType)

        self.groupSettings = GroupSettings(self.settings.group)

    def initDB(self, name):

        emptyTransactions = pd.DataFrame(columns=BankAccount.dataframeCols)
        acc = BankAccount(name, None, None, emptyTransactions, {})

        filepath = self.db / name / self.dbFileName
        dbFile = FileIO(filepath, self.dbSettings)
        dbFile.writeDB(acc)

    def update(self, filepath):

        updateFile = FileIO(filepath, self.bankSettings)
        updateAcc = updateFile.readDB(self.groupSettings)
        # updateAcc.groupTransactions()

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        # compare accounts
        if dbAcc.owner != updateAcc.owner:
            print("WARNING! Owner is missmatching")

        if dbAcc.accountNumber != updateAcc.accountNumber:
            print("WARNING! Bank account number is missmatching")

        if dbAcc.bank != updateAcc.bank:
            print("WARNING! Bank institute is missmatching")

        dbAcc.update(updateAcc.transactions)

        dbFile.writeDB(dbAcc)

    def regroup(self):
        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)
        dbAcc.groupTransactions()
        dbFile.writeDB(dbAcc)

    def listNoGroups(self, category=None):

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        if category:
            trans = dbAcc.transactions[category[0]]
        else:
            trans = dbAcc.transactions
        noGrp = trans[dbAcc.transactions["groupID"] == "None"]
        if noGrp.empty:
            print("All transactions are grouped.")
        else:
            print(noGrp)

    def listGroup(self, group):
        pd.set_option("display.max_rows", None)

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        transFiltered = dbAcc.transactions[dbAcc.transactions["groupID"] == group]
        pp.pprint(transFiltered)

    def search(self, search, category):
        print(search, category)

        keyword = fr"({search})"

        if category is None:
            categories = ["usage"]
        else:
            categories = category

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        ids = []
        for cat in categories:
            subDF = dbAcc.transactions[cat]
            matches = subDF.str.extractall(keyword, re.IGNORECASE)
            if not matches.empty:
                tmp = list(matches.index.droplevel(1).values)
                ids = ids + tmp
        if ids:
            ids = np.unique(ids)
            trans = dbAcc.transactions.loc[ids, :]
            print(trans)
            print(f"\n Sum of expanses: {trans.value.sum():.2f}")
        else:
            print("Could not find any matches")

    def createPlots(self):

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        plotDir = Path(self.settings.plotDir)
        if not plotDir.exists():
            plotDir.mkdir(parents=True)

        transactions = dbAcc.transactions

        ecoplot.plotYearlyBarTotal(plotDir, transactions)
        ecoplot.plotYearlyBar(plotDir, transactions)
        ecoplot.plotBar(plotDir, transactions)
        ecoplot.plotBarYearly(plotDir, transactions)
        ecoplot.plotTimeline(plotDir, transactions)
        ecoplot.plotPie(plotDir, transactions)
