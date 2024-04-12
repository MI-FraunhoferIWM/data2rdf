import json
import tempfile
import warnings
from functools import lru_cache
from typing import List, Optional, Union

import requests
from pydantic import AnyUrl
from rdflib import Graph

from data2rdf.config import config


def make_qudt_quantity(
    oclass: str,
    value: Union[float, int],
    unit: Optional[str] = None,
    iri: AnyUrl = config.base_iri,
    separator: str = config.separator,
    graph_identifier: str = config.base_iri,
    suffix: Optional[str] = None,
) -> Graph:
    graph = Graph(identifier=str(graph_identifier))
    if not suffix:
        suffix = oclass.split(separator)[-1]
    if not str(iri).endswith(separator):
        prefix = str(iri) + separator
    else:
        prefix = str(iri)
    model = {
        "@context": {
            "fileid": prefix,
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "qudt": "http://qudt.org/schema/qudt/",
        },
        "@id": f"fileid:{suffix}",
        "@type": oclass,
        "qudt:value": {
            "@type": "xsd:float",
            "@value": value,
        },
        **_check_qudt_mapping(unit),
    }
    graph.parse(data=json.dumps(model), format="json-ld")
    return graph


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
    url = config.qudt_units
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            f"Could not download QUDT ontology. Please check URI: {url}"
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
