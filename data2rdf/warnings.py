"""DSMS Warnings"""


class MappingMissmatchWarning(UserWarning):
    """A missmatch warning if a value or a concept was not corrently mapped"""


class ParserWarning(UserWarning):
    """A warning raised for a specific context set for a parser"""


class QUDTMappingWarning(UserWarning):
    """A warning raised for a specific context set for a QUDT mapping"""
