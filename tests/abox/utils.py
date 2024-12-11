"""data2rdf pytest utilty"""


def remove_ids(metadata: dict) -> dict:
    """
    Remove 'id' keys from metadata sections and entries.

    Modifies the input metadata dictionary directly.

    :param metadata: The metadata dictionary to modify.
    :return: The input metadata dictionary, with 'id' keys removed.
    """
    for section in metadata.get("sections", []):
        section.pop("id")
        for entry in section.get("entries", []):
            entry.pop("id")
    sort_entries(metadata)
    return metadata


def sort_entries(metadata: dict) -> dict:
    """
    Sort entries in metadata by label.

    Modifies the input metadata dictionary directly.
    """
    for section in metadata.get("sections", []):
        section["entries"].sort(key=lambda x: x["label"])
    return metadata


def as_non_dsms_schema(metadata: dict) -> dict:
    """
    Convert DSMS schema to a flat dictionary.

    The input should be metadata in the DSMS schema, i.e. a dictionary
    with a "sections" key. Each section should have an "entries" key with
    a list of dictionaries. Each of these dictionaries should have a
    "label" key.

    The output is a dictionary with the same labels as keys and the same
    dictionaries as values.
    """
    response = {}
    for section in metadata.get("sections", []):
        section["entries"].sort(key=lambda x: x["label"])
        for entry in section.get("entries", []):
            response[entry["label"]] = entry
    return response
