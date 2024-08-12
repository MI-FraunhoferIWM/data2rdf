"""Test DSMS utilities"""

import pytest

mappings = [
    ("http://qudt.org/vocab/unit/PER-MilliM", "mm-1"),
    ("http://qudt.org/vocab/unit/MegaPA", "MPa"),
    ("http://qudt.org/vocab/unit/MilliM-PER-BAR", "mm/bar"),
    ("http://qudt.org/vocab/unit/MilliM-PER-BAR", "mm.bar-1"),
    ("http://qudt.org/vocab/unit/MilliM2", "mm²"),
    ("http://qudt.org/vocab/unit/DEG_C", "°C"),
]


@pytest.mark.parametrize("iri,symbol", mappings)
def test_unit_retrieval(iri, symbol) -> None:
    from data2rdf import Config
    from data2rdf.qudt.utils import _get_query_match

    config = Config()

    assert [iri] == _get_query_match(symbol, config.qudt_units)
