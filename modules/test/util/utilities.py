import datetime as dt
import unittest
import modules.main.util.utilities as utilities


class TestSparseConfigsValidation(unittest.TestCase):


    def test_extract_year_from_date(self):
        """Test extract_year_from_date()."""
        
        # Date strings properly formatted as YYYY-MM-DD should match expectations.
        dates_and_expectations = [
            ("2018-01-01", 2018),
            (" 2019-01-02", 2019),
            ("1986-01-03 ", 1986),
            ("  1999-01-04", 1999),
            ("2000-01-05  ", 2000),
            ("   2001-01-06   ", 2001)
        ]
        for date, year in dates_and_expectations:
            self.assertEqual(utilities.extract_year_from_date(date), year)

        # Date strings improperly formatted should raise ValueError.
        for date, _ in dates_and_expectations:
            with self.assertRaises(ValueError):
                utilities.extract_year_from_date("a" + date)


    def test_get_seconds_since_datetime(self):
        """Test get_seconds_since_datetime()."""

        t0 = dt.datetime.now()
        # Time difference should be nearly zero since we're checking right after setting t0.
        self.assertAlmostEqual(
            first=utilities.get_seconds_since_datetime(t0), 
            second=0.0, 
            places=4
        )


if __name__ == '__main__':
    unittest.main()
    