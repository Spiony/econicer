import argparse
import sys
from pathlib import Path

from econicer.accountManager import AccountManager
from econicer.report import reportByYear
from econicer.settings import EconicerSettings


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
    parser.add_argument(
        "-i",
        "--init",
        metavar="NAME",
        help="initialize new account",
        default=""
    )
    parser.add_argument(
        "-c",
        "--change",
        metavar="NAME",
        help="change account or create new",
        default=""
    )
    parser.add_argument(
        "-a",
        "--add",
        metavar="FILE",
        help="add to current account"
    )
    parser.add_argument(
        "-s",
        "--search",
        metavar="KEYWORD",
        help="Search for specified keyword",
        default=""
    )
    parser.add_argument(
        "-k",
        "--category",
        metavar="CATEGORY",
        help="Category to search in",
        nargs="+"
    )
    parser.add_argument(
        "-l",
        "--listGroup",
        metavar="GROUP",
        help="display current settings"
    )
    parser.add_argument(
        "-ls",
        "--listSettings",
        help="display current settings",
        action="store_true"
    )
    parser.add_argument(
        "-n",
        "--listNoGroup",
        help="List all transactions withou group",
        action="store_true"
    )
    parser.add_argument(
        "-g",
        "--group",
        help="regroup database",
        action="store_true"
    )
    parser.add_argument(
        "-p",
        "--plot",
        help="make plots",
        action="store_true"
    )
    parser.add_argument(
        "-r",
        "--report",
        help="automated report",
        action="store_true"
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # display help message when no args are passed.
        parser.print_help()
        sys.exit(1)

    # Path objects to database and settings file
    db = Path.cwd() / ".db"
    settingsPath = Path(db / "settings.json")

    # check if db folder exists
    if not db.is_dir():
        print("No database folder found. Creating new database folder.")
        db.mkdir(parents=True)

    if not settingsPath.is_file():
        print("No database settings file found. Creating default settings.")
        ecoSettings = EconicerSettings(verbose=False)
        ecoSettings.write()

        print("Please edit the settings file to your preferences.")

        exit()

    ecoSettings = EconicerSettings(settingsPath, verbose=False)

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

    # init new account
    if args.init:
        accountMan = AccountManager()
        accountMan.initDB(args.init)

        ecoSettings.updateAccountList()
        ecoSettings.write()
        exit()

    # Add file to account history
    if args.add:
        accountMan = AccountManager()
        accountMan.update(args.add)
        exit()

    # regroup database
    if args.group:
        accountMan = AccountManager()
        accountMan.regroup()
        exit()

    # list all transactions in current account without group
    if args.listNoGroup:
        accountMan = AccountManager()
        accountMan.listNoGroups(args.category)

        exit()

    # list all transactions in current account without group
    if args.listGroup:
        accountMan = AccountManager()
        accountMan.listGroup(args.listGroup)
        exit()

    # search for keyword in specified categories
    if args.search:
        accountMan = AccountManager()
        accountMan.search(args.search, args.category)
        exit()

    # Create plots from current history
    if args.plot:
        accountMan = AccountManager()
        accountMan.createPlots()
        exit()

    # print report for year data
    if args.report:
        raise NotImplementedError("Reports will be implemented.")


if __name__ == "__main__":
    main()
