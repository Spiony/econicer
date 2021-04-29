import unittest
from pathlib import Path

from econicer.fileIO import FileIO
from econicer.settings import DatabaseSettings
from econicer.settings import GroupSettings

from test_Account import defineTestAccount


class TestFileIO(unittest.TestCase):

    def test_fileIO(self):
        dbSettings = DatabaseSettings()
        testFile = Path("tests\\test.csv")
        dataIO = FileIO(str(testFile), dbSettings)

        account = defineTestAccount()
        dataIO.writeDB(account)

        settingsPath = "tests\\testfiles\\grouping.json"
        groupSettings = GroupSettings(settingsPath)
        accFromFile = dataIO.readDB(groupSettings)

        compare = account.transactions == accFromFile.transactions
        self.assertTrue(all(compare))

        testFile.unlink()


if __name__ == "__main__":
    unittest.main()
