"""Importing this package populates the rule registry (registry.RULES) by
importing every rule module below — each module's @rule-decorated functions
register themselves as a side effect of import."""
from . import schema_conformance  # noqa: F401
from . import consistency  # noqa: F401
from . import sources  # noqa: F401
