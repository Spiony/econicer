import re

import pandas as pd


class BankAccount:

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

    def __init__(self, owner, accountNumber, bank, transactions, groupSettings):
        self.owner = owner
        self.accountNumber = accountNumber
        self.bank = bank
        self.transactions = transactions
        self.groupSettings = groupSettings

    def update(self, transactionDataframe):

        self.transactions = pd.concat(
            [self.transactions, transactionDataframe])

        self.transactions = self.transactions.sort_values(
            "date", ascending=False)
        self.transactions = self.transactions.reset_index(drop=True)

        self.transactions.drop_duplicates(
            subset=self.dataframeCols, inplace=True)

        self.groupTransactions()

    def groupTransactions(self):

        # reset groups
        self.transactions.loc[:, "groupID"] = "None"

        groups = self.groupSettings.groups

        for key in self.groupSettings.dbIdentifier:
            for grpName, grpList in reversed(groups.items()):
                searchPat = r"(" + r"|".join(grpList) + ")"
                matches = self.transactions[key].str.extractall(
                    searchPat, re.IGNORECASE)

                if matches.empty:
                    continue

                ids = list(matches.index.droplevel(1).values)
                occupiedIds = list(
                    self.transactions.loc[ids, "groupID"] == "None")
                ids = [i for i, b in zip(ids, occupiedIds) if b]
                self.transactions.loc[ids, "groupID"] = grpName
