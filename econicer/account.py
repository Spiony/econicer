import base64
import logging
import re
import hashlib
import pandas as pd
import numpy as np
from dataclasses import dataclass

from econicer.settings import EconicerSettings


def addIdentifier(transactions):
    idComponents = ["date", "customer", "usage", "type", "saldo", "value"]

    idColumns = pd.concat([transactions[col] for col in idComponents], axis=1)
    idColumns["date"] = idColumns["date"].dt.strftime("%Y-%m-%d")

    tuples = idColumns.apply(lambda row: tuple(row), axis=1)
    tuples = tuples.astype(str).str.encode("UTF-8")

    transactions["uid"] = tuples.apply(
        lambda x: base64.b64encode(hashlib.sha1(x).digest()).decode()
    )


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

    def __post_init__(self):
        if not len(self.transactions):
            return
        addIdentifier(self.transactions)

    def checkSaldoTrace(self):
        saldo = self.transactions["saldo"]
        values = self.transactions["value"]

        calcSaldo = values.iloc[::-1].cumsum().iloc[::-1]

        if not saldo.equals(calcSaldo):
            diff = calcSaldo - saldo
            start = diff[diff != 0].index

            t = self.transactions.iloc[start[-1]]
            t2 = self.transactions.iloc[start[-1] + 1]
            print(
                f"Warning! Saldo trace is inconsistent. First inconsistent transaction from {t['date']}"
            )
            print(f"Saldo difference: {diff[start[-1]] / 100}")
            print(t)
            print(t2)
            exit()

    def update(self, transactionDataframe):
        addIdentifier(transactionDataframe)
        if not self.transactions.empty:
            overlapUid = transactionDataframe.iloc[-1]["uid"]
            overlapIndex = self.transactions[
                self.transactions["uid"] == overlapUid
            ].index
            base = self.transactions.drop(range(overlapIndex[0] + 1))
        else:
            base = self.transactions
        mergedDf = pd.concat([transactionDataframe, base])
        mergedDf.reset_index(drop=True, inplace=True)

        self.transactions = mergedDf
        self.checkSaldoTrace()

        self.groupTransactions()
        self.transactions.reset_index(drop=True, inplace=True)

    def groupTransactions(self):
        logger = logging.getLogger()
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
                    logger.info(f"Found no match for {grpList}")
                    continue

                ids = list(matches.index.droplevel(1).values)
                freeIds = list(self.transactions.loc[ids, "groupID"] == "None")
                ids = [i for i, b in zip(ids, freeIds) if b]
                self.transactions.loc[ids, "groupID"] = grpName
                for id in ids:
                    data = self.transactions.loc[id]
                    trans = f'{data["customer"]} \'{data["usage"]}\' {data["value"]} ({data["valuta"]})'
                    logger.info(f"Match {trans} to group: {grpName}")

        addIdentifier(self.transactions)

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
