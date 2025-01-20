"""data2rdf pytest utilty"""
import random
import string
import time


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


def dsms_schema(metadata: dict) -> dict:
    """
    Convert a flat dictionary to a DSMS schema.

    The input should be a dictionary with each key-value pair representing
    a metadata entry. The output is a dictionary in the DSMS schema, with
    a single section named "General", containing the given metadata entries.

    :param metadata: The metadata dictionary to convert.
    :return: A dictionary in the DSMS schema.
    """
    if metadata:
        for metadatum in metadata:
            metadatum["id"] = generate_id()
        metadata = {
            "sections": [
                {
                    "id": generate_id(),
                    "name": "General",
                    "entries": metadata,
                }
            ]
        }
    else:
        metadata = {}

    return metadata


def generate_id(prefix: str = "id") -> str:
    # Generate a unique part using time and random characters
    """
    Generates a unique id using a combination of the current time and 6 random characters.

    Args:
    prefix (str): The prefix to use for the generated id. Defaults to "id".

    Returns:
    str: The generated id.
    """
    unique_part = f"{int(time.time() * 1000)}"  # Milliseconds since epoch
    random_part = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=6)  # nosec
    )
    # Combine prefix, unique part, and random part
    generated_id = f"{prefix}{unique_part}{random_part}"
    return generated_id
