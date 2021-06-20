import json
import pprint
from abc import ABC
from pathlib import Path

from econicer.auxiliary import json2Dict

pp = pprint.PrettyPrinter()


class Settings(ABC):

    _settingsName = ""

    def listCurrentSettings(self):
        """Print all attributes"""
        print(f"Current {self._settingsName} settings:")
        out = self.getSettingsDict()
        pp.pprint(out)

    def getSettingsDict(self):
        out = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        for k, v in out.items():
            if isinstance(v, Path):
                out[k] = str(v)
        return out

    def write(self):
        out = self.getSettingsDict()

        outPath = Path(".db\\settings.json")
        outPath.parent.mkdir(parents=True, exist_ok=True)
        with open(Path(str(outPath)), "w") as f:
            json.dump(out, f, indent=4)


class DatabaseSettings(Settings):

    _settingsName = "Database Settings"

    delimiter = ";"
    owner = 3
    accountNumber = 4
    bank = 5
    beginTable = 11
    dateFormat = "%d.%m.%Y"
    table = [
        "date",
        "valtua",
        "customer",
        "type",
        "usage",
        "saldo",
        "saldoCurrency",
        "value",
        "valueCurrency",
        "groupID"
    ]


class ExternalSettings(Settings):
    """Abstract class which defines settings behavior"""

    _defaultFile = ""

    def __init__(self, filename="", verbose=True):

        if filename == "":
            self._filename = self._defaultFile
        else:
            self._filename = filename
        settingsPath = Path(self._filename)

        if settingsPath.is_file():

            settDict = json2Dict(settingsPath)

            for k, v in self.__class__.__dict__.items():

                if k.startswith("_"):
                    continue

                if callable(v):
                    continue

                if k in settDict.keys():
                    setattr(self, k, settDict[k])
                else:
                    setattr(self, k, v)
        else:
            if verbose:
                print(
                    f"Could not find settings file for {self._settingsName}. Use default parameters")

            for k, v in self.__class__.__dict__.items():
                # add attribute checking
                if k.startswith("_"):
                    continue

                if callable(v):
                    continue

                setattr(self, k, v)


class EconicerSettings(ExternalSettings):
    """Define parameters for the econicer app"""

    _settingsName = "Econicer"

    currentAccount = ""
    currentAccountFile = ""
    accountList = []
    inputType = Path(r"config\bank.json")
    group = Path(r"config\grouping.json")
    # database = Path(r"config\database.json")
    plotDir = Path("plots")

    def changeAccount(self, accountName, accountFile):
        if accountName == self.currentAccount:
            print(f"Already on {self.currentAccount} account")
        elif accountName in self.accountList:
            self.currentAccount = accountName
            self.currentAccountFile = accountFile
            self.plotDir = str(Path("plots") / self.currentAccount)
            print(f"Set current account to {self.currentAccount}")
        else:
            print(f"Unknown account {accountName}")
            print("Available accounts are:")
            pp.pprint(self.accountList)

    def updateAccountList(self):

        if not self._filename:
            accList = []
        else:
            basePath = Path(self._filename).parent
            accList = [p.stem for p in basePath.iterdir() if p.is_dir()]

        self.accountList = accList

        # files = [x for x in p if x.is_file()]


class GroupSettings(ExternalSettings):
    """Define grouping settings for transaction analysis"""

    _settingsName = "transaction grouping"

    dbIdentifier = []
    groups = {}


class BankFileSettings(ExternalSettings):
    """Define read parameters for transaction file from some Bank"""

    _settingsName = "bank transaction file"

    delimiter = ""
    beginTable = -1
    accountNumber = -1
    bank = -1
    owner = -1
    dateFormat = r""
    table = {}


if __name__ == "__main__":

    sdb = EconicerSettings(".db\\settings.json")
    sdb.updateAccountList()
    sdb.write()
    sdb.listCurrentSettings()
    print(sdb.accountList)

    sdb = EconicerSettings()
    print(sdb.accountList)
