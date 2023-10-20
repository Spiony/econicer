import base64
import re
import hashlib
import pandas as pd
import numpy as np
from dataclasses import dataclass

from econicer.settings import EconicerSettings


@dataclass
class BankAccount:
    owner: str
    accountNumber: str
    bank: str
    transactions: pd.DataFrame
    groupSettings: EconicerSettings

    dataframeCols = [
        "date",
        "valuta",
        "customer",
        "type",
        "usage",
        "saldo",
        "saldoCurrency",
        "value",
        "valueCurrency",
    ]

    def update(self, transactionDataframe):
        self.transactions = pd.concat([self.transactions, transactionDataframe])

        self.transactions = self.transactions.sort_values("date", ascending=False)
        self.groupTransactions()

        self.transactions.drop_duplicates(subset=["uid"], inplace=True)
        self.transactions.reset_index(drop=True, inplace=True)

    def groupTransactions(self):
        # reset groups
        self.transactions.loc[:, "groupID"] = "None"

        groups = self.groupSettings.groups

        for key in self.groupSettings.dbIdentifier:
            for grpName, grpList in groups.items():
                searchPat = r"(" + r"|".join(grpList) + ")".lower()
                matches = self.transactions[key].str.extractall(
                    searchPat, re.IGNORECASE
                )

                if matches.empty:
                    continue

                ids = list(matches.index.droplevel(1).values)
                occupiedIds = list(self.transactions.loc[ids, "groupID"] == "None")
                ids = [i for i, b in zip(ids, occupiedIds) if b]
                self.transactions.loc[ids, "groupID"] = grpName

        self.addIdentifier()

    def addIdentifier(self):
        idComponents = ["date", "customer", "usage", "type", "value"]

        idColumns = pd.concat([self.transactions[col] for col in idComponents], axis=1)
        idColumns["date"] = idColumns["date"].dt.strftime("%Y-%m-%d")

        tuples = idColumns.apply(lambda row: tuple(row), axis=1)
        tuples = tuples.astype(str).str.encode("UTF-8")

        self.transactions["uid"] = tuples.apply(
            lambda x: base64.b64encode(hashlib.sha1(x).digest()).decode()
        )

    def search(self, search, categories):
        keyword = rf"({search})"

        ids = []
        for cat in categories:
            subDF = self.transactions[cat]
            matches = subDF.str.extractall(keyword, re.IGNORECASE)
            if not matches.empty:
                tmp = list(matches.index.droplevel(1).values)
                ids = ids + tmp

        if ids:
            return self.transactions.loc[np.unique(ids), :]
        else:
            return None
