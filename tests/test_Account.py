import unittest
from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
from econicer.account import BankAccount
from econicer.settings import GroupSettings


def getTransactionInfo():
    return [
        ["myCompany", datetime(2021, 2, 25),  "Paycheck", 2000],
        ["Frank", datetime(2021, 2, 17), "Sending your money", 50],
        ["Store", datetime(2021, 2, 11), "Your friendly store nearby", -150],
        ["Gas Station", datetime(2021, 2, 18), "Thank you!", -50],
        ["Landlord", datetime(2021, 2, 1),  "Rent", -500],
        ["myCompany", datetime(2021, 1, 25),  "Paycheck", 2000],
        ["Taxi", datetime(2021, 1, 23), "Thank you for riding the cab", -12],
        ["Book Store", datetime(2020, 12, 31), "Book Order 1234", -25]
    ]


def getTransactionInfoUpdate():
    return [
        ["myCompany", datetime(2021, 3, 28),  "Paycheck", 2000],
        ["Store", datetime(2021, 3, 11), "Your friendly store nearby", -120],
        ["Gas Station", datetime(2021, 3, 6), "Thank you!", -50],
        ["Book Store", datetime(2021, 3, 2), "Book Order 3435", -35],
        ["Landlord", datetime(2021, 3, 1),  "Rent", -500],
    ]


def defineTestDataframe(transactionInfo):

    currency = "EUR"
    transactionType = "transfer"

    customers = [v[0] for v in transactionInfo]
    dates = [v[1] for v in transactionInfo]
    usages = [v[2] for v in transactionInfo]
    transValues = [v[3] for v in transactionInfo]
    transValues.reverse()

    saldo = np.cumsum(transValues).tolist()
    saldo.reverse()

    transValues.reverse()

    length = len(transValues)

    data = {
        "date": dates,
        "valtua": dates,
        "customer": customers,
        "type": [transactionType for x in range(length)],
        "usage": usages,
        "saldo": saldo,
        "saldoCurrency": [currency for x in range(length)],
        "value": transValues,
        "valueCurrency": [currency for x in range(length)],
        "groupID": [-1 for x in range(length)],
    }

    df = pd.DataFrame(data)

    return df


def defineTestAccount():
    owner = "Test"
    accountNumber = 123456789
    bank = "econicer"

    transactionInfo = getTransactionInfo()
    transactions = defineTestDataframe(transactionInfo)

    settingsPath = "tests\\testfiles\\grouping.json"
    groupSettings = GroupSettings(settingsPath)

    acc = BankAccount(owner, accountNumber, bank, transactions, groupSettings)
    return acc


class TestGrouping(unittest.TestCase):

    def test_Update(self):

        acc = defineTestAccount()
        updateDF = defineTestDataframe(getTransactionInfoUpdate())
        acc.update(updateDF)

        initialData = getTransactionInfo()
        updateData = getTransactionInfoUpdate()

        totalLength = len(initialData) + len(updateData)

        (noCol, noRow) = acc.transactions.shape

        # check combination
        self.assertEqual(noCol, totalLength)
        self.assertEqual(acc.transactions["customer"][0], "myCompany")
        self.assertEqual(acc.transactions["customer"].iloc[-1], "Book Store")

        # check sorting
        dates = acc.transactions["date"]

        firstDate = dates[0]
        timeDeltas = [d - firstDate for d in dates]
        self.assertTrue(all([d <= timedelta() for d in timeDeltas]))

    def test_Grouping(self):
        acc = defineTestAccount()
        acc.groupTransactions()

        incomeDF = acc.transactions[acc.transactions["customer"]
                                    == "myCompany"]
        self.assertAlmostEqual(incomeDF["groupID"][0], "income")

        group0 = list(acc.transactions.loc[:, "groupID"] == "income")
        self.assertEqual(group0.count(True), 2)

        group1 = list(acc.transactions.loc[:, "groupID"] == "living")
        self.assertEqual(group1.count(True), 2)

        group3 = list(acc.transactions.loc[:, "groupID"] == "hobby")
        self.assertEqual(group3.count(True), 1)


if __name__ == "__main__":
    unittest.main()
