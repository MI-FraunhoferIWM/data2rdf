import pandas as pd
from rdflib import Graph, Namespace

QUDT = Namespace("http://qudt.org/schema/qudt/")
QUDT_UNIT = Namespace("http://qudt.org/vocab/unit/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()

g.parse(
    "https://github.com/qudt/qudt-public-repo/blob/main/vocab/unit/VOCAB_QUDT-UNITS-ALL-v2.1.ttl"
)

unit_query = """
PREFIX qudt: <http://qudt.org/schema/qudt/>
PREFIX qudt_unit: <http://qudt.org/vocab/unit/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?unit ?label
WHERE {
  ?unit rdf:type qudt:Unit .
  ?unit skos:prefLabel ?label .
  FILTER(LANG(?label) = "en")
}
"""
# prefix_query = # there will be no need for a separate query for prefix
# Since QUDT does not use a separate class for prefixes as EMMO does

qres = g.query(unit_query)
unit_df = pd.DataFrame(qres, columns=["Class", "Symbol"])
print(unit_df)


unit_df.to_csv("qudt_units.csv")
