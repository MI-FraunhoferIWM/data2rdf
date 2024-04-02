import tempfile
import warnings
from functools import lru_cache
from typing import List, Optional

import requests
from rdflib import Graph

from data2rdf.annotation_confs import annotations


def _qudt_sparql(symbol: str) -> str:
    return f"""PREFIX qudt: <http://qudt.org/schema/qudt/>
    SELECT DISTINCT ?unit
        WHERE {{
            ?unit a qudt:Unit .
            {{
                ?unit qudt:symbol "{symbol}" .
            }}
            UNION
            {{
                ?unit qudt:ucumCode "{symbol}"^^qudt:UCUMcs .
            }}
        }}"""


@lru_cache
def _get_qudt_ontology() -> requests.Response:
    url = annotations["qudt_uri"]
    headers = {"Content-Type": "text/turtle; charset=utf-8"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(
            f"Could not download QUDT ontology. Please check URI: {url}"
        )
    return response


def _to_tempfile(content) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ttl", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
    return tmp.name


@lru_cache
def _get_qudt_graph() -> Graph:
    response = _get_qudt_ontology()
    file = _to_tempfile(response.text)

    graph = Graph()
    graph.parse(file, encoding="utf-8")
    return graph


def _get_query_match(symbol: str) -> List[str]:
    graph = _get_qudt_graph()
    query = _qudt_sparql(symbol)
    return [str(row["unit"]) for row in graph.query(query)]


def _check_qudt_mapping(symbol: str) -> Optional[str]:
    if symbol:
        match = _get_query_match(symbol)
        if len(match) == 0:
            warnings.warn(
                f"No QUDT Mapping found for unit with symbol `{symbol}`."
            )
            unit = {}
        elif len(match) > 1:
            warnings.warn(
                f"Multiple QUDT Mappings found for unit with symbol `{symbol}`."
            )
            unit = {"qudt:hasUnit": match}
        else:
            unit = {"qudt:hasUnit": match.pop()}
    else:
        unit = {}
    return unit
