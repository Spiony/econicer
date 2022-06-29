import shutil
from pathlib import Path

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
    print(f"\n Sum of expenses: {transactionDataframe.value.sum():.2f}")


# accuont manager should open the file only once
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

        self.fileIO = FileIO(
            self.settings.currentAccountFile, self.dbSettings
        )

        if Path(self.settings.currentAccountFile).is_file():
            self.account = self.fileIO.readDB(self.groupSettings)
        else:
            self.account = None

        self.plotPaths = {}

    def defineAccountFilepath(self, name):
        return self.db / name / self.dbFileName

    def updateAccountPaths(self, name, filepath):
        self.fileIO.updateFilepath(filepath)
        self.settings.changeAccount(name, filepath)

    def initDB(self, name):
        filepath = self.defineAccountFilepath(name)

        if filepath.is_file():
            print(f"Account {name} already exists")
            return False

        print(f"Initialize empty account for {name}")
        emptyTransactions = pd.DataFrame(columns=BankAccount.dataframeCols)
        self.account = BankAccount(
            name, None, None, emptyTransactions, self.groupSettings
        )

        self.updateAccountPaths(name, filepath)

        self.fileIO.writeDB(self.account)
        self.settings.write()

        return True

    def update(self, filepath):

        self.makeBackup()

        updateFile = FileIO(filepath, self.bankSettings)
        updateAcc = updateFile.readDB(self.groupSettings)

        if not len(self.account.accountNumber):
            self.account.accountNumber = updateAcc.accountNumber

        if not len(self.account.bank):
            self.account.bank = updateAcc.bank

        # compare accounts
        if self.account.accountNumber != updateAcc.accountNumber:
            print("WARNING! Bank account number is mismatching")

        if self.account.bank != updateAcc.bank:
            print("WARNING! Bank institute is mismatching")

        self.account.update(updateAcc.transactions)

        self.fileIO.writeDB(self.account)

    def makeBackup(self):
        undoFile = f"{self.settings.currentAccountFile}.old"
        shutil.copy2(self.settings.currentAccountFile, undoFile)

    def undo(self):
        undoFile = f"{self.settings.currentAccountFile}.old"
        shutil.copy2(undoFile, self.settings.currentAccountFile)

    def regroup(self):
        self.makeBackup()

        self.account.groupTransactions()
        self.fileIO.writeDB(self.account)

    def listNoGroups(self, category=None):

        if category:
            trans = self.account.transactions[category[0]]
        else:
            trans = self.account.transactions
        noGrp = trans[self.account.transactions["groupID"] == "None"]
        if noGrp.empty:
            print("All transactions are grouped.")
        else:
            print(noGrp)
            printSum(noGrp)

    def listGroup(self, group):
        pd.set_option("display.max_rows", None)

        transFiltered = self.account.transactions[self.account.transactions["groupID"] == group]
        print(transFiltered)
        printSum(transFiltered)

    def search(self, search, categories):

        if categories is None:
            categories = ["usage"]

        print(f"Searching for {search} in {categories}")
        result = self.account.search(search, categories)

        if result is not None:
            print(result)
            printSum(result)
        else:
            print("Could not find any matches")

    def createPlots(self):

        plotDir = Path(self.settings.plotDir)
        if not plotDir.exists():
            plotDir.mkdir(parents=True)

        transactions = self.account.transactions

        ep = Ecoplot(str(plotDir))
        """
        ep.plotCategoriesRatioMonthly(transactions)
        ep.plotCategoriesMonthly(transactions)
        """
        ep.plotHbarSplit(transactions)
        ep.plotTimeline(transactions)
        ep.plotPieSplit(transactions)
        ep.plotBars(transactions)
        ep.plotCategories(transactions)
        ep.plotBarsYearly(transactions)
        ep.plotCategoriesYearly(transactions)

        self.plotPaths = ep.plotPaths

    def calculateStatistics(self):
        self.statistics = {}
        # average monthly income; expense; top 5 spending categories
        # yearly average value for each category

    def createReport(self):

        self.createPlots()
        self.calculateStatistics()

        rp = ReportDocument(
            self.account.owner,
            self.account.accountNumber,
            self.account.bank
        )
        rp.addOverallSection(self.plotPaths["overall"])
        rp.addStatisticsSection(self.statistics)
        rp.addYearlyReports(self.plotPaths["years"])
        rp.generatePDF()
