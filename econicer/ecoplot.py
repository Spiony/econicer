import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from pathlib import Path

from econicer.auxiliary import json2Dict
from econicer.auxiliary import nextMonth
from econicer.auxiliary import nextYear
from econicer.auxiliary import endOfMonth
from econicer.auxiliary import endOfYear

plt.style.use(os.path.join(os.path.dirname(__file__), "glumt.mplrc"))


def plotTimeline(acc):
    timeline = acc.transactions[["date", "saldo"]]
    timeline = timeline.iloc[::-1]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    timeline.plot(x="date", y="saldo", ax=ax)

    filename = Path(acc.settings["plotDir"]) / "ecoTimeline.png"
    fig.savefig(filename)
    plt.close(fig)
    # add timeDelta for plot separation


def calcPosNegSums(df):
    posSum = pd.pivot_table(df,
                            index=df['date'].dt.month,
                            columns=df['date'].dt.year,
                            values='value',
                            aggfunc=lambda x: x[x > 0].sum())
    negSum = pd.pivot_table(df,
                            index=df['date'].dt.month,
                            columns=df['date'].dt.year,
                            values='value',
                            aggfunc=lambda x: x[x < 0].sum())
    posSum = posSum.rename_axis("month")
    posSum = posSum.rename_axis("year", axis="columns")
    negSum = negSum.rename_axis("month")
    negSum = negSum.rename_axis("year", axis="columns")
    negSum = negSum.apply(np.abs)
    return posSum, negSum


def plotYearlyBarTotal(acc):
    df = acc.transactions
    posSum, negSum = calcPosNegSums(df)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    yearDF = pd.concat([posSum.sum().rename('in'),
                        negSum.sum().rename('out')],
                       axis=1)
    yearDF.plot.bar(ax=ax)
    #ax.set_ylim([minSaldo*1.1, maxSaldo*1.1])
    filename = Path(acc.settings["plotDir"]) / "ecoYearTotal.png"
    fig.savefig(filename)
    plt.close(fig)


def plotYearlyBar(acc):
    """Show total in and out per month over a year"""
    df = acc.transactions
    posSum, negSum = calcPosNegSums(df)

    minSaldo = negSum.min().min()
    maxSaldo = posSum.max().max()

    years = posSum.columns
    for y in years:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        yearDF = pd.concat(
            [posSum.loc[:, y].rename('in'), negSum.loc[:, y].rename('out')],
            axis=1)
        yearDF.plot.bar(ax=ax)
        ax.set_ylim([minSaldo * 1.1, maxSaldo * 1.1])
        filename = Path(acc.settings["plotDir"]) / f"ecoYearTest{y}.png"
        fig.savefig(filename)
        plt.close(fig)


def plotPie(acc):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    d = acc.transactions['group'].value_counts()
    # sum all neg and pos; subplot for both
    d = acc.transactions.pivot_table(
        index=["group"], aggfunc={"value": lambda x: np.sum(np.abs(x))})
    d.plot.pie(y="value", figsize=(5, 5), ax=ax)
    filename = Path(acc.settings["plotDir"]) / "ecoPie.png"
    fig.savefig(filename)
    plt.close(fig)


def plotBar(acc):

    absGroupVal = acc.transactions.pivot_table(values=["value"],
                                               index=["group"],
                                               aggfunc={"value": np.sum})

    fig = plt.figure()
    ax = fig.add_subplot(111)
    absGroupVal.plot.barh(y="value", ax=ax)
    filename = Path(acc.settings["plotDir"]) / "ecoNettoHbarTotal.png"
    fig.savefig(filename)
    plt.close(fig)


def plotBarYearly(acc):

    df = acc.transactions
    yearTrans = pd.pivot_table(df,
                               index=df['date'].dt.year,
                               columns=df['group'],
                               values='value',
                               aggfunc=np.sum)

    years = yearTrans.index
    for y in years:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        yearTrans.loc[y, :].plot.barh(y="value", ax=ax)
        filename = Path(acc.settings["plotDir"]) / f"ecoNettoHbar{y}.png"
        fig.savefig(filename)
        plt.close(fig)
