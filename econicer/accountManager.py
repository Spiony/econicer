import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from econicer.account import BankAccount
from econicer.ecoplot import Ecoplot
from econicer.fileIO import FileIO
from econicer.report import ReportDocument
from econicer.settings import BankFileSettings
from econicer.settings import DatabaseSettings
from econicer.settings import EconicerSettings
from econicer.settings import GroupSettings


def printSum(transactionDataframe):
    print(f"\n Sum of expanses: {transactionDataframe.value.sum():.2f}")


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
        filepath = self.db / name / self.dbFileName

        if filepath.is_file():
            print(f"Account {name} already exitsts")
            return False

        print(f"Initialize empty account for {name}")
        emptyTransactions = pd.DataFrame(columns=BankAccount.dataframeCols)
        acc = BankAccount(name, None, None, emptyTransactions, {})

        dbFile = FileIO(filepath, self.dbSettings)
        dbFile.writeDB(acc)

        return True

    def update(self, filepath):

        self.makeBackup()

        updateFile = FileIO(filepath, self.bankSettings)
        updateAcc = updateFile.readDB(self.groupSettings)
        # updateAcc.groupTransactions()

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        if not len(dbAcc.accountNumber):
            dbAcc.accountNumber = updateAcc.accountNumber

        if not len(dbAcc.bank):
            dbAcc.bank = updateAcc.bank

        # compare accounts
        if dbAcc.accountNumber != updateAcc.accountNumber:
            print("WARNING! Bank account number is missmatching")

        if dbAcc.bank != updateAcc.bank:
            print("WARNING! Bank institute is missmatching")

        dbAcc.update(updateAcc.transactions)

        dbFile.writeDB(dbAcc)

    def makeBackup(self):
        undoFile = f"{self.settings.currentAccountFile}.old"
        shutil.copy2(self.settings.currentAccountFile, undoFile)

    def undo(self):
        undoFile = f"{self.settings.currentAccountFile}.old"
        shutil.copy2(undoFile, self.settings.currentAccountFile)

    def regroup(self):
        self.makeBackup()

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
        print(transFiltered)
        printSum(transFiltered)

    def search(self, search, category):
        keyword = fr"({search})"

        if category is None:
            categories = ["usage"]
        else:
            categories = category

        print(f"Seaching for {search} in {categories}")

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
            printSum(trans)
        else:
            print("Could not find any matches")

    def createPlots(self):

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        plotDir = Path(self.settings.plotDir)
        if not plotDir.exists():
            plotDir.mkdir(parents=True)

        transactions = dbAcc.transactions

        ep = Ecoplot(str(plotDir))
        ep.plotTimeline(transactions)
        ep.plotPie(transactions)
        ep.plotBars(transactions)
        ep.plotCategories(transactions)
        ep.plotBarsYearly(transactions)
        ep.plotCategoriesYearly(transactions)

        self.plotPaths = ep.plotPaths

    def createReport(self):

        self.createPlots()

        dbFile = FileIO(self.settings.currentAccountFile, self.dbSettings)
        dbAcc = dbFile.readDB(self.groupSettings)

        rp = ReportDocument(dbAcc.owner, dbAcc.accountNumber, dbAcc.bank)
        rp.addOverallSection(self.plotPaths["all"])
        rp.addYearlyReports(self.plotPaths["years"])
        rp.generatePDF()
