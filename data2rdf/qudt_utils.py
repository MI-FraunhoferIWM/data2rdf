from data2rdf.annotation_confs import annotations
from rdflib import Graph

def _qudt_sparql(symbol: str) -> str:
    return f"""PREFIX qudt: <http://qudt.org/schema/qudt/> 
    SELECT ?unit
        WHERE {{
            ?unit a qudt:Unit .
            ?unit qudt:symbol '{symbol}' .
        }}"""


def _get_query_match(symbol: str) -> list[str]:
    graph = Graph()
    graph.parse(annotations["QudtURI"])

    query = _qudt_sparql(symbol)
    return [row["unit"] for row in graph.query(query)]
