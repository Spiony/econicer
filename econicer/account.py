"""

"""
import re
import csv
import json
import datetime

from pathlib import Path
import pandas as pd

from econicer.auxiliary import json2Dict
from econicer.auxiliary import str2num


def writeDefaultConfig():
    defaultConfig = {
        "currentAccount": "",
        "currentAccountFile": "",
        "accountList": [],
        "inputType": r"cfg\\ing.json",
        "group": r"cfg\grouping.json",
        "database": r"cfg\database.json",
        "plotDir": r"plot"
    }
    with open(r"db\settings.json", "w") as jsonFile:
        json.dump(defaultConfig, jsonFile)


def readHeader(filepath, cfg):
    """extract header information from database"""
    with open(filepath) as csvFile:
        header = [next(csvFile) for x in range(cfg["beginTable"] - 1)]
    owner = header[cfg["owner"]].split(cfg["delimiter"])[1].replace("\n", "")
    accountNumber = header[cfg["accountNumber"]].split(
        cfg["delimiter"])[1].replace("\n", "")
    bank = header[cfg["bank"]].split(cfg["delimiter"])[1].replace("\n", "")
    return owner, accountNumber, bank


class BankAccount:
    def __init__(self, settingsPath=""):

        # check if db folder exists
        dbPath = Path(r"db")
        if not dbPath.is_dir():
            print("No database folder found. Creating new database folder.")
            dbPath.mkdir()

        # load settings from db
        settingsPath = Path(settingsPath)
        if not settingsPath.exists():
            print("No settings found. Created initial settings file.")
            writeDefaultConfig()
        self.settings = json2Dict(settingsPath)

        cfgPath = self.settings["database"]
        filepath = Path(self.settings["currentAccountFile"])

        if not filepath.exists():
            print("No database found. Account initialized.")
            self.owner = ""
            self.accountNumber = ""
            self.bank = ""
            self.transactions = []
        else:
            self.readDB(filepath, cfgPath)

        #owner, accountNumber, bank, transactionDF = readDB(filepath, cfgPath)
        #self.owner = owner
        #self.accountNumber = accountNumber
        #self.bank = bank
        #self.transactions = transactionDF

    def initDB(self, filepath, cfgPath=""):

        if cfgPath == "":
            cfgPath = self.settings["inputType"]

        if filepath == "":
            filepath = self.settings["currentAccountFile"]

        cfgIn = json2Dict(cfgPath)
        self.owner, self.accountNumber, self.bank = readHeader(filepath, cfgIn)

        transactionDF = pd.read_csv(filepath,
                                    sep=cfgIn["delimiter"],
                                    header=cfgIn["beginTable"],
                                    encoding='mbcs')
        transactionDF = transactionDF.rename(columns=cfgIn["table"])
        self.transactions = transactionDF

        self.transactions["valtua"] = pd.to_datetime(
            self.transactions["valtua"], format=cfgIn["dateFormat"])
        self.transactions["date"] = pd.to_datetime(self.transactions["date"],
                                                   format=cfgIn["dateFormat"])

        self.transactions["value"] = self.transactions["value"].apply(str2num)
        self.transactions["saldo"] = self.transactions["saldo"].apply(str2num)

        self.groupTransactions()

    def readDB(self, filepath, cfgPath):
        """Read data from database and create BankAccount"""

        cfg = json2Dict(cfgPath)

        self.owner, self.accountNumber, self.bank = readHeader(filepath, cfg)

        transactionDF = pd.read_csv(filepath,
                                    sep=cfg["delimiter"],
                                    header=cfg["beginTable"])
        transactionDF["date"] = pd.to_datetime(transactionDF["date"],
                                               format=cfg["dateFormat"])
        transactionDF["valtua"] = pd.to_datetime(transactionDF["valtua"],
                                                 format=cfg["dateFormat"])
        self.transactions = transactionDF

    def writeDB(self, filepath, cfgPath):
        """Write bankAccount content to database"""

        filepath = Path(filepath)
        filepath.parents[0].mkdir(parents=True, exist_ok=True)

        cfg = json2Dict(cfgPath)
        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile,
                                   delimiter=cfg["delimiter"],
                                   quotechar="'",
                                   quoting=csv.QUOTE_MINIMAL)

            # Write header
            csvwriter.writerow(["##ECONICER DATABASE"])
            csvwriter.writerow([
                datetime.datetime.now().strftime(
                    "File created at %Y-%m-%d %H:%M:%S")
            ])
            csvwriter.writerow(["#GENERALINFO"])
            csvwriter.writerow(["owner", self.owner])
            csvwriter.writerow(["account number", self.accountNumber])
            csvwriter.writerow(["bank", self.bank])
            csvwriter.writerow(["#STATS"])
            csvwriter.writerow(["totalSum", "..."])
            csvwriter.writerow(["expanseGroupNames", "..."])
            csvwriter.writerow(["expanseGroupValues", "..."])
            csvwriter.writerow(["#TRANSACTIONS"])

        # write table
        self.transactions.to_csv(filepath,
                                 mode='a',
                                 sep=cfg["delimiter"],
                                 index=False,
                                 date_format=cfg["dateFormat"])

    def update(self, filepath, cfgPath=""):

        if cfgPath == "":
            cfgPath = self.settings["inputType"]

        cfgIn = json2Dict(cfgPath)
        owner, accountNumber, bank = readHeader(filepath, cfgIn)
        if self.owner != owner:
            print("WARNING! Owner is missmatching")

        if self.accountNumber != accountNumber:
            print("WARNING! Bank account number is missmatching")

        if self.bank != bank:
            print("WARNING! Bank institute is missmatching")

        transactionDF = pd.read_csv(filepath,
                                    sep=cfgIn["delimiter"],
                                    header=cfgIn["beginTable"],
                                    encoding='mbcs')
        transactionDF = transactionDF.rename(columns=cfgIn["table"])
        transactionDF["valtua"] = pd.to_datetime(transactionDF["valtua"],
                                                 format=cfgIn["dateFormat"])
        transactionDF["date"] = pd.to_datetime(transactionDF["date"],
                                               format=cfgIn["dateFormat"])

        self.transactions = pd.concat([self.transactions, transactionDF])

        self.transactions["value"] = self.transactions["value"].apply(str2num)
        self.transactions["saldo"] = self.transactions["saldo"].apply(str2num)

        self.transactions = self.transactions.sort_values("date",
                                                          ascending=False)
        self.transactions = self.transactions.reset_index(drop=True)

        self.transactions.drop_duplicates(subset=[
            "date", "customer", "type", "usage", "saldo", "saldoCurrency",
            "value", "valueCurrency"
        ],
                                          inplace=True)

        # check if data is consistent
        self.groupTransactions()

    def groupTransactions(self, groupCfg=""):

        self.transactions.loc[:, "group"] = "None"

        if groupCfg == "":
            groupCfg = json2Dict(self.settings["group"])

        groups = groupCfg["groups"]
        #groupId = {k: int(i) for i, k in enumerate(groups.keys())}

        for key in groupCfg['dbIdentifier']:
            #for grpName, grpList in groups.items():
            for grpName, grpList in reversed(groups.items()):
                searchPat = r"(" + r"|".join(grpList) + ")"
                matches = self.transactions[key].str.extractall(
                    searchPat, re.IGNORECASE)
                if not matches.empty:
                    ids = list(matches.index.droplevel(1).values)
                    occupiedIds = list(
                        self.transactions.loc[ids, "group"] == "None")
                    ids = [i for i, b in zip(ids, occupiedIds) if b]
                    self.transactions.loc[ids, "group"] = grpName
