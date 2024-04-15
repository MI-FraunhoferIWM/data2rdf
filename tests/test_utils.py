import unittest

from data2rdf import Config
from data2rdf.qudt.utils import _get_query_match

config = Config()


class TestQudtMatch(unittest.TestCase):
    def test_per_mm(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/PER-MilliM"]
            == _get_query_match("mm-1", config.qudt_units)
        )

    def test_mpa(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MegaPA"]
            == _get_query_match("MPa", config.qudt_units)
        )

    def test_mm_per_bar_slash(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM-PER-BAR"]
            == _get_query_match("mm/bar", config.qudt_units)
        )

    def test_mm_per_bar(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM-PER-BAR"]
            == _get_query_match("mm.bar-1", config.qudt_units)
        )

    def test_square_mm(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM2"]
            == _get_query_match("mm²", config.qudt_units)
        )

    def test_deg_cel(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/DEG_C"]
            == _get_query_match("°C", config.qudt_units)
        )


if __name__ == "__main__":
    unittest.main()
