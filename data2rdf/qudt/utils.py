"""Data2RDF utils"""
import tempfile
import warnings
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests
from rdflib import Graph

from data2rdf.warnings import QUDTMappingWarning


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
def _get_qudt_ontology(qudt_iri: str) -> requests.Response:
    response = requests.get(qudt_iri)
    if response.status_code != 200:
        raise RuntimeError(
            f"Could not download QUDT ontology. Please check URI: {qudt_iri}"
        )
    response.encoding = "utf-8"
    return response


def _to_tempfile(content) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ttl", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
    return tmp.name


@lru_cache
def _get_qudt_graph(qudt_iri: str) -> Graph:
    response = _get_qudt_ontology(qudt_iri)
    file = _to_tempfile(response.text)

    graph = Graph()
    graph.parse(file, encoding="utf-8")
    return graph


def _get_query_match(symbol: str, qudt_iri: str) -> List[str]:
    graph = _get_qudt_graph(qudt_iri)
    query = _qudt_sparql(symbol)
    return [str(row["unit"]) for row in graph.query(query)]


def _check_qudt_mapping(symbol: Optional[str]) -> Optional[str]:
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
            unit = {
                "qudt:hasUnit": [
                    {"@value": uri, "@type": "xsd:anyURI"} for uri in match
                ]
            }
        else:
            unit = {
                "qudt:hasUnit": {"@value": match.pop(), "@type": "xsd:anyURI"}
            }
    else:
        unit = {}
    return unit


def _get_qudt_label_and_symbol(
    iri: str, qudt_iri: str, language: str
) -> Dict[str, Any]:
    graph = _get_qudt_graph(qudt_iri)
    gen_query = f"""PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?label ?symbol
    WHERE {{
        <{iri}> qudt:symbol ?symbol .
        OPTIONAL {{
            <{iri}> rdfs:label ?label .
            FILTER (LANG(?label) = "{language}")
        }}
        OPTIONAL {{
            <{iri}> rdfs:label ?label_no_lang .
            FILTER (LANG(?label_no_lang) = "")
        }}
        BIND(COALESCE(?label, ?label_no_lang) AS ?label)
    }}"""
    match = [
        {"label": str(row["label"]), "symbol": str(row["symbol"])}
        for row in graph.query(gen_query)
    ]
    if len(match) == 0:
        warnings.warn(
            f"No QUDT label and symbol found for unit with iri `{iri}`.",
            QUDTMappingWarning,
        )
        unit = {}
    elif len(match) > 1:
        warnings.warn(
            f"Multiple QUDT symbols and labels found for unit with iri `{iri}`.",
            QUDTMappingWarning,
        )
        unit = match[0]
    else:
        unit = match.pop()
    return unit
