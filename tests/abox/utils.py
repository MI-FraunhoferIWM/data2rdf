"""data2rdf pytest utilty"""


def remove_ids(metadata: dict) -> dict:
    for section in metadata.get("sections", []):
        section.pop("id")
        for entry in section.get("entries", []):
            entry.pop("id")
    sort_entries(metadata)
    return metadata


def sort_entries(metadata: dict) -> dict:
    for section in metadata.get("sections", []):
        section["entries"].sort(key=lambda x: x["label"])
    return metadata
