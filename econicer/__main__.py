import re
import json
import argparse
import pprint
from pathlib import Path
import pandas as pd
import numpy as np

from econicer.auxiliary import json2Dict
from econicer.account import BankAccount
from econicer.account import writeDefaultConfig
from econicer.report import reportByYear
from econicer.ecoplot import plotBar
from econicer.ecoplot import plotBarYearly
from econicer.ecoplot import plotTimeline
from econicer.ecoplot import plotYearlyBar
from econicer.ecoplot import plotPie
from econicer.ecoplot import plotYearlyBarTotal


def main():

    DEBUG = True

    #class formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
    class formatter(argparse.RawDescriptionHelpFormatter):
        pass

    # define args
    parser = argparse.ArgumentParser(
        description=""
        "   ___  _________  ____  __________  ____\n"
        "  / _ \/ ___/ __ \/ __ \/ / ___/ _ \/ __/\n"
        " /  __/ /__/ /_/ / / / / / /__/  __/ /\n"
        " \___/\___/\____/_/ /_/_/\___/\___/_/\n\n"
        " a perception of economic success",
        formatter_class=formatter)
    # positional args

    # optional args
    parser.add_argument("-i",
                        "--init",
                        metavar='NAME',
                        help="initialize new account",
                        default='')
    parser.add_argument("-c",
                        "--change",
                        metavar='NAME',
                        help="change account or create new",
                        default="")
    parser.add_argument("-a",
                        "--add",
                        metavar='FILE',
                        help="add to current account")
    parser.add_argument("-s",
                        "--search",
                        metavar="KEYWORD",
                        help="Search for specified keyword",
                        default='')
    parser.add_argument("-k",
                        "--category",
                        metavar="CATEGORY",
                        help="Category to search in",
                        nargs="+")
    parser.add_argument("-l",
                        "--listGroup",
                        metavar="GROUP",
                        help="display current settings")
    parser.add_argument("-ls",
                        "--listSettings",
                        help="display current settings",
                        action='store_true')
    parser.add_argument("-n",
                        "--listNoGroup",
                        help="List all transactions withou group",
                        action='store_true')
    parser.add_argument("-g",
                        "--group",
                        help="regroup database",
                        action='store_true')
    parser.add_argument("-p", "--plot", help="make plots", action='store_true')
    parser.add_argument("-r",
                        "--report",
                        help="automated report",
                        action='store_true')
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(indent=4)

    db = Path.cwd() / 'db'

    # list current settings
    if args.listSettings:
        if Path(db / 'settings.json').exists():
            settings = json2Dict(r'db/settings.json')
            print('Current Settings:')
            for k, v in settings.items():
                print(f'  {k}: {v}')
        else:
            print("No settings file found.")
        exit()

    # init new account
    if args.init:
        accPath = Path(db / args.init)
        if accPath.exists():
            print(f"Account with name {args.init} already exists")
        else:
            if not db.exists():
                # create folder for all databases
                db.mkdir()
            # create folder for new account
            accPath.mkdir()

            # update aacount list in settings
            if not Path(db / 'settings.json').exists():
                settings = writeDefaultConfig()
            settings = json2Dict(r'db/settings.json')
            settings["currentAccount"] = args.init
            settings["currentAccountFile"] = str(db / args.init / "hist.csv")
            settings['accountList'] = [
                str(x.name) for x in Path('db').iterdir() if x.is_dir()
            ]
            jsonPath = db / 'settings.json'
            print(jsonPath)
            with open(str(jsonPath), 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Create new account {args.init}")

    # change settings
    if args.change:
        settings = json2Dict(r'db/settings.json')
        if args.change == settings['currentAccount']:
            print(f"Already on {settings['currentAccount']} account")
        elif args.change in settings['accountList']:
            settings['currentAccount'] = args.change
            settings["currentAccountFile"] = str(db / args.change / "hist.csv")
            settings['plotDir'] = str(
                Path('plots') / settings['currentAccount'])
            with open(Path(db / 'settings.json'), 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Set current account to {args.change}")
        else:
            print(f"Unkown account {args.change}")
            print("Available accounts are")
            pp.pprint(settings['accountList'])
        exit()

    # regroup database
    if args.group:
        acc = BankAccount(db / "settings.json")
        acc.groupTransactions()
        writeDB(acc, acc.settings["currentAccountFile"],
                acc.settings["database"])
        exit()

    # list all transactions in current account without group
    if args.listNoGroup:
        acc = BankAccount(db / "settings.json")
        if args.category:
            trans = acc.transactions[args.category[0]]
        else:
            trans = acc.transactions
        noGrp = trans[acc.transactions["group"] == "None"]
        if noGrp.empty:
            print("All transactions are grouped.")
        else:
            print(noGrp)

        exit()

    # list all transactions in current account without group
    if args.listGroup:
        pd.set_option('display.max_rows', None)
        acc = BankAccount(db / "settings.json")
        transFiltered = acc.transactions[acc.transactions["group"] ==
                                         args.listGroup]
        pp.pprint(transFiltered)
        if DEBUG:
            transFiltered.to_csv("debug.csv", sep=";")
        exit()

    # search for keyword in specified categories
    if args.search:
        keyword = fr"({args.search})"

        if args.category is None:
            categories = ["usage"]
        else:
            categories = args.category

        acc = BankAccount(db / "settings.json")

        ids = []
        for cat in categories:
            subDF = acc.transactions[cat]
            matches = subDF.str.extractall(keyword, re.IGNORECASE)
            if not matches.empty:
                tmp = list(matches.index.droplevel(1).values)
                ids = ids + tmp
        if ids:
            ids = np.unique(ids)
            trans = acc.transactions.loc[ids, :]
            print(trans)
            print(f"\n Sum of expanses: {trans.value.sum():.2f}")
        else:
            print("Could not find any matches")
        exit()

    # Add file to account history
    if args.add:
        acc = BankAccount(db / "settings.json")
        if acc.owner == "":
            acc.initDB(Path(args.add))
        else:
            acc.update(Path(args.add))
        writeDB(acc, acc.settings["currentAccountFile"],
                acc.settings["database"])

    # Create plots from current history
    if args.plot:

        acc = BankAccount(db / "settings.json")

        plotDir = Path(acc.settings['plotDir'])
        if not plotDir.exists():
            plotDir.mkdir(parents=True)
        plotYearlyBarTotal(acc)
        plotYearlyBar(acc)
        plotBar(acc)
        plotBarYearly(acc)
        plotTimeline(acc)
        plotPie(acc)

    # print report for year data
    if args.report:

        acc = BankAccount(db / "settings.json")
        reportbyyear(acc)


if __name__ == "__main__":
    main()
