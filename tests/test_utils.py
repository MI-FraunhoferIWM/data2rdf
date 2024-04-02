import unittest

from data2rdf.qudt_utils import _get_query_match


class TestQudtMatch(unittest.TestCase):
    def test_per_mm(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/PER-MilliM"]
            == _get_query_match("mm-1")
        )

    def test_mpa(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MegaPA"] == _get_query_match("MPa")
        )

    def test_mm_per_bar_slash(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM-PER-BAR"]
            == _get_query_match("mm/bar")
        )

    def test_mm_per_bar(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM-PER-BAR"]
            == _get_query_match("mm.bar-1")
        )

    def test_square_mm(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/MilliM2"] == _get_query_match("mm²")
        )

    def test_deg_cel(self):
        self.assertTrue(
            ["http://qudt.org/vocab/unit/DEG_C"] == _get_query_match("°C")
        )


if __name__ == "__main__":
    unittest.main()
