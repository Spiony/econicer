import argparse
import sys
from pathlib import Path
import logging

from econicer.accountManager import AccountManager
from econicer.settings import EconicerSettings


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename="app.log",
        filemode="w",
        format="%(name)s - %(levelname)s: %(message)s",
    )

    # command line arguments
    parser = argparse.ArgumentParser(
        description=""
        "   ___  _________  ____  __________  ____\n"
        "  / _ \\/ ___/ __ \\/ __ \\/ / ___/ _ \\/ __/\n"
        " /  __/ /__/ /_/ / / / / / /__/  __/ /\n"
        " \\___/\\___/\\____/_/ /_/_/\\___/\\___/_/\n\n"
        " a perception of economic success",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i", "--init", metavar="NAME", help="initialize new account", default=""
    )
    parser.add_argument(
        "-c",
        "--change",
        metavar="NAME",
        help="change account or create new",
        default="",
    )
    parser.add_argument("-a", "--add", metavar="FILE", help="add to current account")
    parser.add_argument(
        "-s",
        "--search",
        metavar="KEYWORD",
        help="Search for specified keyword in category 'usage' and lists sum of expenses",
        default="",
    )
    parser.add_argument(
        "-k",
        "--category",
        metavar="CATEGORY",
        help="Categories to search in",
        nargs="+",
    )
    parser.add_argument(
        "-l", "--listGroup", metavar="GROUP", help="display current settings"
    )
    parser.add_argument(
        "-ls", "--listSettings", help="display current settings", action="store_true"
    )
    parser.add_argument(
        "-n",
        "--listNoGroup",
        help="List all transactions without a group",
        action="store_true",
    )
    parser.add_argument(
        "-u", "--undo", help="Undo last change on database", action="store_true"
    )
    parser.add_argument("-g", "--group", help="regroup database", action="store_true")
    parser.add_argument("-p", "--plot", help="make plots", action="store_true")
    parser.add_argument("-r", "--report", help="automated report", action="store_true")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # display help message when no args are passed.
        parser.print_help()
        exit()

    # Path objects to database and settings file
    db = Path.cwd() / ".db"
    settingsPath = Path(db / "settings.json")

    # check if db folder exists
    if not db.is_dir():
        print("No database folder found. Creating new database folder")
        db.mkdir(parents=True)

    if not settingsPath.is_file():
        print("No database settings file found. Creating default settings")
        ecoSettings = EconicerSettings(verbose=False)
        ecoSettings.write()

        print("Please edit the settings file to your preferences")

    ecoSettings = EconicerSettings(settingsPath, verbose=True)
    ecoSettings.updateAccountList()

    # list current settings
    if args.listSettings:
        ecoSettings.listCurrentSettings()
        exit()

    # change settings
    if args.change:
        accPath = db / "//".join([args.change, AccountManager.dbFileName])
        ecoSettings.changeAccount(args.change, accPath)
        ecoSettings.write()
        exit()

    if args.undo:
        accountMan = AccountManager()
        accountMan.undo()
        exit()

    # init new account
    if args.init:
        accountMan = AccountManager()
        initSuccess = accountMan.initDB(args.init)

        if not initSuccess:
            exit()

    # Add file to account history
    if args.add:
        accountMan = AccountManager()
        accountMan.update(args.add)

    # regroup database
    if args.group:
        accountMan = AccountManager()
        accountMan.regroup()

    # list all transactions in current account without group
    if args.listNoGroup:
        accountMan = AccountManager()
        accountMan.listNoGroups(args.category)

    # list all transactions in current account without group
    if args.listGroup:
        accountMan = AccountManager()
        accountMan.listGroup(args.listGroup)

    # search for keyword in specified categories
    if args.search:
        accountMan = AccountManager()
        accountMan.search(args.search, args.category)

    # Create plots from current history
    if args.plot:
        accountMan = AccountManager()
        accountMan.createPlots()

    # print report for all account data
    if args.report:
        accountMan = AccountManager()
        if not len(accountMan.plotPaths):
            accountMan.createPlots()
        accountMan.createReport()
