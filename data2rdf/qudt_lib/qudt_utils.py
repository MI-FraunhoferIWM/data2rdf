import os

import pandas as pd

qudt_units_df = pd.read_csv(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "qudt_units.csv"),
    index_col=0,
)


def qudt_unit_lookup(parsed_unit):
    """
    Function that looks up QUDT unit classes for a parsed unit.
    QUDT defines prefixed units as unique entities, so we can look them up directly.
    example:
        unit:KiloGM
        qudt:symbol "kg"
        URI: https://qudt.org/2.1/vocab/unit/vocab/KiloGM #TODO to be double-checked
    Args:
        parsed_unit (str): Parsed unit from the data (e.g., "kg")

    Returns:
        unit_class (str): The QUDT class URI of the unit (or None if not found)
    """

    # Look up the unit in the DataFrame
    unit_match = qudt_units_df.loc[
        qudt_units_df["Symbol"] == parsed_unit, "URI"
    ]

    if not unit_match.empty:
        unit_class = unit_match.iloc[0]
    else:
        unit_class = None

    return unit_class


def generate_unit_individuals_qudt(parsed_unit, row_id):
    """
    Generates the json-ld representation of the individuals generated from a parsed unit using QUDT Logic

    Args:
        parsed_unit (str): Parsed unit from the data (e.g., kg)
        row_id (int): ID assigned to the individuals. In the pipeline, each individual gets an incremental ID

    Returns:
        unit_json (json): json-ld representation of the individuals, can be added in a json-ld syntax
    """

    unit_class_uri = qudt_unit_lookup(parsed_unit)

    if unit_class_uri:
        unit_json = {
            "@id": f"fileid:unit-{row_id}",
            "@type": unit_class_uri,
        }
    else:
        # if the unit cannot be parsed, store the string as literal to a
        # UnparseableUnit individual
        # Fallback for an unrecognized or unparseable unit
        # TODO: aadjust to QUDT
        raise NotImplementedError

    return unit_json
