import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from pathlib import Path
from dataclasses import dataclass

plt.style.use(os.path.join(os.path.dirname(__file__), "glumt.mplrc"))


def nestedSet(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def calcPosNegSums(df):
    posSum = pd.pivot_table(
        df,
        index=df['date'].dt.month,
        columns=df['date'].dt.year,
        values='value',
        aggfunc=lambda x: x[x > 0].sum()
    )
    negSum = pd.pivot_table(
        df,
        index=df['date'].dt.month,
        columns=df['date'].dt.year,
        values='value',
        aggfunc=lambda x: x[x < 0].sum()
    )
    posSum = posSum.rename_axis("month")
    posSum = posSum.rename_axis("year", axis="columns")
    negSum = negSum.rename_axis("month")
    negSum = negSum.rename_axis("year", axis="columns")
    negSum = negSum.apply(np.abs)
    return posSum, negSum


@dataclass
class PlotOptions:
    height: float
    width: float
    formats = ["pdf", "png"]


@dataclass
class Ecoplot:
    plotDir: str
    plotOptions = PlotOptions(3.14, 2.355)
    plotPaths = {"all": {}, "years": {}}

    def saveFig(self, fig, filename):

        fig.set_size_inches(self.plotOptions.height, self.plotOptions.width)
        fig.tight_layout()

        for filetype in self.plotOptions.formats:
            fig.savefig(f"{filename}.{filetype}", dpi=600)

    def plotTimeline(self, transactions):
        timeline = transactions[["date", "saldo"]]
        timeline = timeline.iloc[::-1]

        fig = plt.figure()
        fig.add_subplot(111)
        plt.step(x=timeline["date"], y=timeline["saldo"])
        plt.ylabel("Saldo / EUR")
        plt.xticks(rotation=45)

        filename = Path(self.plotDir) / "ecoTimeline"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["all"].update({"timeline": filename})

    def plotPie(self, transactions, plotName="pie"):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        d = transactions['groupID'].value_counts()
        # sum all neg and pos; subplot for both
        d = transactions.pivot_table(
            index=["groupID"], aggfunc={"value": lambda x: np.sum(np.abs(x))})
        d.plot.pie(y="value", figsize=(5, 5), ax=ax, legend=False)
        plt.ylabel("")

        filename = Path(self.plotDir) / f"ecoPie_{plotName}"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["all"].update({plotName: filename})

    def plotPieSplit(self, transactions):
        ids = transactions["value"] > 0
        incomingTransactions = transactions[ids]
        self.plotPie(incomingTransactions, "pie_income")

        ids = ~ids
        outgoingTransactions = transactions[ids]
        self.plotPie(outgoingTransactions, "pie_outgoing")

    def plotCategories(self, transactions):

        absGroupVal = transactions.pivot_table(
            values=["value"],
            index=["groupID"],
            aggfunc={"value": np.sum}
        )

        fig = plt.figure()
        ax = fig.add_subplot(111)
        absGroupVal.plot.barh(y="value", ax=ax, legend=False)
        plt.xlabel("summation / EUR")
        plt.ylabel("")
        filename = Path(self.plotDir) / "ecoNettoHbarTotal"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["all"].update({"categories": filename})

    def plotBars(self, transactions):
        df = transactions
        posSum, negSum = calcPosNegSums(df)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        yearDF = pd.concat([posSum.sum().rename('in'),
                            negSum.sum().rename('out')],
                           axis=1)
        yearDF.plot.bar(ax=ax)
        plt.ylabel("summation / EUR")
        plt.xticks(rotation=45)
        # ax.set_ylim([minSaldo*1.1, maxSaldo*1.1])
        filename = Path(self.plotDir) / "ecoYearTotal"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["all"].update({"years": filename})

    def splitTransactions(self, transactions):
        ids = transactions["value"] > 0
        incomingTransactions = transactions[ids]
        outgoingTransactions = transactions[~ids]
        return incomingTransactions, outgoingTransactions

    def plotHbarSplit(self, transactions):

        incomingTransactions, outgoingTransactions = self.splitTransactions(
            transactions)

        self.plotHbar(incomingTransactions, "hbar_incoming")
        self.plotHbar(outgoingTransactions, "hbar_outgoing")

    def plotHbar(self, transactions, plotName):
        absGroupVal = transactions.pivot_table(
            values=["value"],
            index=["groupID"],
            aggfunc={"value": np.sum}
        )
        absGroupVal = absGroupVal.sort_values("value")

        fig = plt.figure()
        ax = fig.add_subplot(111)
        absGroupVal.plot.barh(y="value", ax=ax, legend=False)
        plt.xlabel("summation / EUR")
        plt.ylabel("")
        filename = Path(self.plotDir) / f"eco_{plotName}"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["all"].update({plotName: filename})

    def plotBarsYearly(self, transactions):
        """Show total in and out per month over a year"""
        df = transactions
        posSum, negSum = calcPosNegSums(df)

        minSaldo = negSum.min().min()
        maxSaldo = posSum.max().max()

        years = posSum.columns
        for y in years:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            yearDF = pd.concat(
                [posSum.loc[:, y].rename(
                    'in'), negSum.loc[:, y].rename('out')],
                axis=1)
            yearDF.plot.bar(ax=ax)
            ax.set_ylim([minSaldo * 1.1, maxSaldo * 1.1])
            plt.ylabel("summation / EUR")
            filename = Path(self.plotDir) / f"ecoYearTest{y}"
            self.saveFig(fig, filename)
            plt.close(fig)

            nestedSet(self.plotPaths, ["years", f"{y}", "year"], filename)

    def plotCategoriesYearly(self, transactions):

        df = transactions
        yearTrans = pd.pivot_table(
            df,
            index=df['date'].dt.year,
            columns=df['groupID'],
            values='value',
            aggfunc=np.sum
        )

        years = yearTrans.index
        for y in years:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            yearSelected = yearTrans.loc[y, :]
            yearSelected = yearSelected.sort_values()
            yearSelected.plot.barh(y="value", ax=ax)
            plt.xlabel("summation / EUR")
            plt.ylabel("")
            filename = Path(self.plotDir) / f"ecoNettoHbar{y}"
            self.saveFig(fig, filename)
            plt.close(fig)

            nestedSet(self.plotPaths, [
                      "years", f"{y}", "categories"], filename)
