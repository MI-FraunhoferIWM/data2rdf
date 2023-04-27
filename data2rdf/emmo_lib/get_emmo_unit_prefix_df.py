# add func that matches EMMO units !
import os

import pandas as pd
from rdflib import Graph

# EMMO_ONTOLOGY = "https://emmo-repo.github.io/versions/1.0.0-alpha2/emmo.ttl"

g = Graph()

# try:
# 	g.parse(EMMO_ONTOLOGY, format="ttl")
# except:

# in order to filter for specific classes, the inferred EMMO needs to be used !
g.parse(os.path.join("..", "emmo", "emmo-inferred.ttl"), format="ttl")

unit_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX csvw: <http://www.w3.org/ns/csvw#>
PREFIX perc: <http://emmo.info/emmo/middle/perceptual#>
PREFIX siunits: <http://emmo.info/emmo/middle/siunits#>
PREFIX metro: <http://emmo.info/emmo/middle/metrology#>

SELECT ?unit ?unit_symbol
WHERE {
?unit_class rdfs:subClassOf* metro:EMMO_216f448e_cdbc_4aeb_a529_7a5fe7fc38bb . #property path query to filter for all subclasses of UnitSymbol
?unit rdfs:subClassOf ?x .
?unit rdfs:subClassOf ?unit_class . #get only subclasses of UnitSymbol
?x rdf:type owl:Restriction .
?x owl:onProperty perc:EMMO_23b579e1_8088_45b5_9975_064014026c42 .
?x owl:hasValue ?unit_symbol .
}
"""

qres = g.query(unit_query)
unit_df = pd.DataFrame(qres, columns=["Class", "Symbol"])
print(unit_df)

prefix_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX csvw: <http://www.w3.org/ns/csvw#>
PREFIX perc: <http://emmo.info/emmo/middle/perceptual#>
PREFIX siunits: <http://emmo.info/emmo/middle/siunits#>

SELECT ?unit ?unit_symbol
WHERE {
?unit rdfs:subClassOf ?x .
?unit rdfs:subClassOf siunits:EMMO_471cb92b_edca_4cf9_bce8_a75084d876b8 . #get only subclasses of SIMetricPrefix
?x rdf:type owl:Restriction .
?x owl:onProperty perc:EMMO_23b579e1_8088_45b5_9975_064014026c42 .
?x owl:hasValue ?unit_symbol .
}
"""

qres = g.query(prefix_query)
prefix_df = pd.DataFrame(qres, columns=["Class", "Symbol"])
print(prefix_df)

unit_df.to_csv("emmo_units.csv")
prefix_df.to_csv("emmo_unit_prefixes.csv")
