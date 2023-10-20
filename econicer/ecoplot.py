import matplotlib.pyplot as plt
from cycler import cycler
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
        index=df["date"].dt.month,
        columns=df["date"].dt.year,
        values="value",
        aggfunc=lambda x: x[x > 0].sum(),
    )
    negSum = pd.pivot_table(
        df,
        index=df["date"].dt.month,
        columns=df["date"].dt.year,
        values="value",
        aggfunc=lambda x: x[x < 0].sum(),
    )
    posSum = posSum.rename_axis("month")
    posSum = posSum.rename_axis("year", axis="columns")
    negSum = negSum.rename_axis("month")
    negSum = negSum.rename_axis("year", axis="columns")
    negSum = negSum.apply(np.abs)
    return posSum, negSum


@dataclass
class PlotOptions:
    width: float
    height: float
    formats = ["pdf", "png"]


@dataclass
class Ecoplot:
    plotDir: str
    plotOptions = PlotOptions(3.14, 2.355)
    plotPaths = {"overall": {}, "years": {}}

    def saveFig(self, fig, filename, width=None, height=None, skipTight=False):
        if not width:
            width = self.plotOptions.width

        if not height:
            height = self.plotOptions.height

        fig.set_size_inches(width, height)
        if not skipTight:
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

        self.plotPaths["overall"].update({"timeline": filename})

    def plotPie(self, transactions, plotName="pie"):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        d = transactions["groupID"].value_counts()
        # sum all neg and pos; subplot for both
        d = transactions.pivot_table(
            index=["groupID"], aggfunc={"value": lambda x: np.sum(np.abs(x))}
        )
        d.plot.pie(y="value", figsize=(5, 5), ax=ax, legend=False)
        plt.ylabel("")

        filename = Path(self.plotDir) / f"ecoPie_{plotName}"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["overall"].update({plotName: filename})

    def plotPieSplit(self, transactions):
        ids = transactions["value"] > 0
        incomingTransactions = transactions[ids]
        self.plotPie(incomingTransactions, "pie_income")

        ids = ~ids
        outgoingTransactions = transactions[ids]
        self.plotPie(outgoingTransactions, "pie_outgoing")

    def plotCategories(self, transactions):
        absGroupVal = transactions.pivot_table(
            values=["value"], index=["groupID"], aggfunc={"value": np.sum}
        )

        fig = plt.figure()
        ax = fig.add_subplot(111)
        absGroupVal.plot.barh(y="value", ax=ax, legend=False)
        plt.xlabel("summation / EUR")
        plt.ylabel("")
        filename = Path(self.plotDir) / "ecoNettoHbarTotal"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["overall"].update({"categories": filename})

    def plotBars(self, transactions):
        df = transactions
        posSum, negSum = calcPosNegSums(df)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        yearDF = pd.concat(
            [posSum.sum().rename("in"), negSum.sum().rename("out")], axis=1
        )
        yearDF.plot.bar(ax=ax)
        plt.ylabel("summation / EUR")
        plt.xticks(rotation=45)
        # ax.set_ylim([minSaldo*1.1, maxSaldo*1.1])
        filename = Path(self.plotDir) / "ecoYearTotal"
        self.saveFig(fig, filename)
        plt.close(fig)

        self.plotPaths["overall"].update({"years": filename})

    def splitTransactions(self, transactions):
        ids = transactions["value"] > 0
        incomingTransactions = transactions[ids]
        outgoingTransactions = transactions[~ids]
        return incomingTransactions, outgoingTransactions

    def plotHbarSplit(self, transactions):
        incomingTransactions, outgoingTransactions = self.splitTransactions(
            transactions
        )

        self.plotHbar(incomingTransactions, "hbar_incoming")
        self.plotHbar(outgoingTransactions, "hbar_outgoing")

    def plotHbar(self, transactions, plotName):
        absGroupVal = transactions.pivot_table(
            values=["value"], index=["groupID"], aggfunc={"value": np.sum}
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

        self.plotPaths["overall"].update({plotName: filename})

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
                [posSum.loc[:, y].rename("in"), negSum.loc[:, y].rename("out")], axis=1
            )
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
            index=df["date"].dt.year,
            columns=df["groupID"],
            values="value",
            aggfunc=np.sum,
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

            nestedSet(self.plotPaths, ["years", f"{y}", "categories"], filename)

    def plotCategoriesRatioMonthly(self, transactions):
        """Calculate ratio of monthly expense and create line plot for each month"""
        df = transactions
        years = list(set(df["date"].dt.year))
        monthTrans = pd.pivot_table(
            df,
            index=df["date"].dt.strftime("%Y-%m"),
            columns=df["groupID"],
            values="value",
            aggfunc=np.sum,
        )

        monthTrans.index = pd.to_datetime(monthTrans.index)

        legendCreated = False
        for year in years:
            transInYear = monthTrans[f"{year}-01-01":f"{year}-12-31"]
            selector = (transInYear.columns != "income") & (
                transInYear.columns != "saving"
            )
            transInYear = transInYear.loc[:, selector]

            fig = plt.figure()
            ax = fig.add_subplot(111)
            colorcycle = cycler(color=plt.rcParams["axes.prop_cycle"].by_key()["color"])
            linecycle = cycler("linestyle", ["-", "--", ":", "-."])
            plt.gca().set_prop_cycle(linecycle * colorcycle)
            transInYear.plot.line(ax=ax, legend=False, marker="o", ms=2, rot=45)
            ax.set_yscale("symlog")
            plt.ylabel("value / EUR")
            plt.xlabel("")

            filename = Path(self.plotDir) / f"ecoMonth{year}"
            self.saveFig(fig, filename)
            plt.close(fig)

            nestedSet(self.plotPaths, ["years", f"{year}", "monthly"], filename)

            if not legendCreated:
                handles, labels = ax.get_legend_handles_labels()

                legFig = plt.figure()
                leg = legFig.legend(handles=handles, labels=labels, loc="center")

                leg.figure.canvas.draw()
                bb = leg.get_window_extent()
                width = (bb.x1 - bb.x0) / 100 + 2 * leg.borderaxespad * plt.rcParams[
                    "font.size"
                ] / 72
                height = (bb.y1 - bb.y0) / 100

                filename = Path(self.plotDir) / "ecoMonth_Legend"
                self.saveFig(legFig, filename, width=width, height=height)
                plt.close(legFig)
                legendCreated = True
                nestedSet(
                    self.plotPaths, ["years", f"{year}", "monthly_legend"], filename
                )

    def plotCategoriesMonthly(self, transactions):
        df = transactions
        years = list(set(df["date"].dt.year))
        monthTrans = pd.pivot_table(
            df,
            index=df["date"].dt.strftime("%Y-%m"),
            columns=df["groupID"],
            values="value",
            aggfunc=np.sum,
        )

        monthTrans.index = pd.to_datetime(monthTrans.index)

        for year in years:
            transInYear = monthTrans[f"{year}-01-01":f"{year}-12-31"]

            """
            fig = plt.figure()
            ax = fig.add_subplot(111)
            """
            axes = transInYear.plot.bar(subplots=True, legend=False, rot=45)
            fig = axes[0].get_figure()
            # clearing axis tick labels
            for x in axes:
                x.set_xticklabels("")
                x.set_title("")
                x.set_xlabel("")
            xlabels = [
                pandas_datetime.strftime("%Y-%m")
                for pandas_datetime in transInYear.index
            ]
            axes[-1].set_xticklabels(xlabels)
            lines = []
            labels = []
            for x in axes:
                Line, Label = x.get_legend_handles_labels()
                lines.extend(Line)
                labels.extend(Label)

            # rotating x-axis labels of last sub-plot
            fig.legend(lines, labels, loc="upper center", ncol=5)

            plt.subplots_adjust(top=0.90)

            filename = Path(self.plotDir) / f"ecoCat_{year}"
            self.saveFig(fig, filename, 8, 11, True)
            plt.close(fig)

            nestedSet(self.plotPaths, ["years", f"{year}", "monthlyCat"], filename)

    def plotCategoriesFlow(self, transactions: pd.DataFrame):
        df = transactions

        categories = set(df["groupID"])
        catDatas = {}
        for cat in categories:
            catData = df[df["groupID"] == cat]
            catData = catData.set_index("date")
            catData = catData.iloc[::-1]
            catData = catData["value"].cumsum()
            catDatas[cat] = catData

        catDatas = {
            k: v for k, v in sorted(catDatas.items(), key=lambda item: item[1][-1])
        }

        for cat, catData in catDatas.items():
            fig = plt.figure()
            ax = fig.add_subplot(111)

            plt.step(x=catData.index, y=catData)
            plt.xlabel("")
            plt.ylabel("value / EUR")
            plt.xticks(rotation=45)
            plt.title(cat)
            filename = Path(self.plotDir) / f"ecoCat_{cat}"
            self.saveFig(fig, filename)
            plt.close(fig)

            nestedSet(self.plotPaths, ["flow", cat], filename)
