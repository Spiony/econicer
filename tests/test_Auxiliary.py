import unittest
import datetime
import econicer.auxiliary as aux


class TestGrouping(unittest.TestCase):

    def test_Str2Num(self):
        self.assertEqual(aux.str2num("5.0"), 5.0)
        self.assertEqual(aux.str2num("1,0"), 1.0)
        self.assertEqual(aux.str2num("5.000,0"), 5000.0)

        self.assertEqual(aux.str2num(1.0), 1.0)

        with self.assertRaises(ValueError):
            aux.str2num("asd")

    def test_NextMonth(self):
        ts = datetime.datetime(2000, 1, 5)
        _, nm = aux.nextMonth(ts)
        self.assertEqual(nm, datetime.datetime(2000, 2, 1))

    def test_EndOfMonth(self):
        ts = datetime.datetime(2000, 1, 5)
        _, nm = aux.endOfMonth(ts)
        self.assertEqual(nm, datetime.datetime(2000, 1, 31))

    def test_NextYear(self):
        ts = datetime.datetime(2000, 1, 5)
        _, nm = aux.nextYear(ts)
        self.assertEqual(nm, datetime.datetime(2001, 1, 1))

    def test_EndOfYear(self):
        ts = datetime.datetime(2000, 1, 5)
        _, nm = aux.endOfYear(ts)
        self.assertEqual(nm, datetime.datetime(2000, 12, 31))


if __name__ == "__main__":
    unittest.main()
