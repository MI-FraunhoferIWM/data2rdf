# add func that matches EMMO units !
import os

import pandas as pd

unit_df = pd.read_csv(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "emmo_units.csv"),
    index_col=0,
)
prefix_df = pd.read_csv(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "emmo_unit_prefixes.csv"
    ),
    index_col=0,
)


def simple_unit_lookup(parsed_unit):
    """
        Very simple function that assignes EMMO unit classes for the prefix and the unit for a parsed
        unit. Assuming, that the prefix and unit match the EMMO annotation, that follows SI standards.
        Could be improved using unit matching libs like pint.

    Args:
        parsed_unit (str): Parsed unit from the data (e.g. mm)

    Returns:

        prefix_class (str): The EMMO class of the prefix (or none)
        unit_class (str): The EMMO class of the unit (or none)

    """

    if not isinstance(parsed_unit, str):
        prefix_class = None
        unit_class = None

        return (prefix_class, unit_class)

    if len(parsed_unit) == 0:
        prefix_class = None
        unit_class = None

        return (prefix_class, unit_class)

    prefix, unit = parsed_unit[0], parsed_unit[1:]

    prefix_match = prefix_df.loc[(prefix_df["Symbol"] == prefix), :]
    unit_match = unit_df.loc[(unit_df["Symbol"] == unit), :]

    # assuming, that prefix and unit are there
    if not prefix_match.empty and not unit_match.empty:
        prefix_class = prefix_match["Class"].to_list()[0]
        unit_class = unit_match["Class"].to_list()[0]

    else:
        # if either prefix or unti cannot be matched, try only the unit
        unit = parsed_unit
        unit_match = unit_df.loc[(unit_df["Symbol"] == unit), :]

        if not unit_match.empty:
            prefix_class = None
            unit_class = unit_match["Class"].to_list()[0]

        # Neither can be matched
        else:
            prefix_class = None
            unit_class = None

    return (prefix_class, unit_class)


def generate_unit_individuals(parsed_unit, row_id):
    """
        Generates the json-ld representation of the individuals generated from a parsed unit using EMMO Logic
        A figure describing the schema is shown in unit_assignment_scheme.drawio

    Args:
        parsed_unit (str): Parsed unit from the data (e.g. mm)
        row_id (int): ID assigned to the individuals. In the pipeline each individuals gets an incremental ID

    Returns:

        unit_json: (json): json-ld representation of the individuals, can be added in a json-ld syntax

    """

    prefix_class, unit_class = simple_unit_lookup(parsed_unit)

    if prefix_class and unit_class:
        unit_json = {
            "@id": f"fileid:unit-{row_id}",
            "@type": "http://emmo.info/emmo/middle/metrology#EMMO_c6d4a5e0_7e95_44df_a6db_84ee0a8bbc8e",  # PrefixedUnit
            "http://emmo.info/emmo/middle/reductionistic#EMMO_b2282816_b7a3_44c6_b2cb_3feff1ceb7fe": [  # hasSpatialDirectPart
                {
                    "@id": f"fileid:MetricPrefix-{row_id}",
                    "@type": prefix_class,
                },
                {
                    "@id": f"fileid:UnitSymbol-{row_id}",
                    "@type": unit_class,
                },
            ],
        }

    if not prefix_class and unit_class:
        unit_json = {
            "@id": f"fileid:unit-{row_id}",
            "@type": unit_class,  # a NonPrefixedUnit
        }

    # if the unit cannot be parsed, store the string as literal to a
    # UnparseableUnit individual
    if not prefix_class and not unit_class:
        unit_json = {
            "@id": f"fileid:unit-{row_id}",
            # TODO add to sd or emmo UnparseableUnit !!
            "@type": "http://www.example.de#UnparseableUnit",
            "http://emmo.info/emmo/middle/perceptual#EMMO_23b579e1_8088_45b5_9975_064014026c42": {
                "@value": parsed_unit,
                "@type": "xsd:string",
            },
        }

    return unit_json


# example_unit = "mPa"
# print(simple_unit_lookup(example_unit))
# unit_json = generate_unit_individuals(example_unit, row_id = 1)
# print(unit_json)

# from pint import UnitRegistry
# ureg = UnitRegistry()

# parsed_unit = ureg(example_unit)
# print(ureg.get_symbol(str(parsed_unit.units)))

# print(parsed_unit._units.items())
# print(ureg.get_symbol(parsed_unit))
# exit()
# for attr in dir(parsed_unit):
# 	try:
# 		print(attr, getattr(parsed_unit, attr))
# 	except:
# 		pass
