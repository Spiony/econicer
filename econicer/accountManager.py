import shutil
from pathlib import Path

import pandas as pd

from econicer.account import BankAccount
from econicer.ecoplot import EcoPlot
from econicer.fileIO import FileIO
from econicer.report import ReportDocument
from econicer.settings import BankFileSettings
from econicer.settings import DatabaseSettings
from econicer.settings import EconicerSettings
from econicer.settings import GroupSettings


def printSum(transactionDataframe):
    print(f"\n Sum of expenses: {transactionDataframe.value.sum():.2f}")


# account manager should open the file only once
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

        self.fileIO = FileIO(self.settings.currentAccountFile, self.dbSettings)

        if Path(self.settings.currentAccountFile).is_file():
            self.account = self.fileIO.readDB(self.groupSettings)
            self.account.checkSaldoTrace()

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

        startDate = updateAcc.transactions["date"].iloc[-1]
        endDate = updateAcc.transactions["date"].iloc[0]
        print(f"adding transaction data from {startDate} to {endDate}")

        if not self.account.transactions.empty:
            startDateHistory = self.account.transactions["date"].iloc[-1]
            endDateHistory = self.account.transactions["date"].iloc[0]
            if startDate > endDateHistory:
                print(
                    "Warning! New dataset does not start in the known date range. There might be a gap in the datasets"
                )
            if endDateHistory > endDate:
                print(
                    "The date timestamps indicate that the dataset is already included. The program will stop now"
                )
                exit()
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

    def printTransactions(self, transactions):
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_colwidth", None)
        print(transactions[["date", "customer", "usage", "saldo", "value", "groupID"]])
        printSum(transactions)

    def listNoGroups(self, category=None):
        if category:
            trans = self.account.transactions[category[0]]
        else:
            trans = self.account.transactions
        noGrp = trans[self.account.transactions["groupID"] == "None"]
        if noGrp.empty:
            print("All transactions are grouped.")
        else:
            self.printTransactions(noGrp)

    def listGroup(self, group):
        transFiltered = self.account.transactions[
            self.account.transactions["groupID"] == group
        ]
        self.printTransactions(transFiltered)

    def search(self, search, categories):
        if categories is None:
            categories = ["usage"]

        print(f"Searching for {search} in {categories}")
        result = self.account.search(search, categories)

        if result is not None:
            self.printTransactions(result)
        else:
            print("Could not find any matches")

    def createPlots(self):
        plotDir = Path(self.settings.plotDir)
        if not plotDir.exists():
            plotDir.mkdir(parents=True)

        transactions = self.account.transactions.copy()
        transactions["value"] = transactions["value"] / 100
        transactions["saldo"] = transactions["saldo"] / 100

        ep = EcoPlot(plotDir)
        """
        ep.plotCategoriesRatioMonthly(transactions)
        ep.plotCategoriesMonthly(transactions)
        """
        ep.plotCategoriesFlow(transactions)
        ep.sankeyPlot(transactions)
        ep.plotHbarSplit(transactions)
        ep.plotTimeline(transactions)
        ep.plotPieSplit(transactions)
        ep.plotBars(transactions)
        ep.plotCategories(transactions)
        ep.plotBarsYearly(transactions, self.groupSettings.groupTypes)
        ep.plotCategoriesYearly(transactions)

        # self.plotPaths = ep.plotPaths
        return ep.reg

    def calculateStatistics(self):
        self.statistics = {}
        # average monthly income; expense; top 5 spending categories
        # yearly average value for each category

    def createReport(self):
        reg = self.createPlots()
        self.calculateStatistics()

        rp = ReportDocument(
            self.account.owner, self.account.accountNumber, self.account.bank, reg
        )
        rp.addOverallSection()
        rp.addStatisticsSection(self.statistics)

        transactions = self.account.transactions.copy()
        transactions["value"] = transactions["value"] / 100
        transactions["saldo"] = transactions["saldo"] / 100
        rp.addYearlyReports(transactions)
        rp.addFlowSection()

        rp.generatePDF()
