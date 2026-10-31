"""Shared test support for privacy-notice-eu/tests/.

``find_schema`` resolves a shared portfolio schema (docs/standards/schemas/)
by walking UP from this file's own location. That works identically in both
layouts a skill's bundled tests can run from:

* inside the monorepo, where docs/standards/schemas/ lives at the repo root
  (an ancestor of skills/privacy-notice-eu/tests/); and
* inside a flat public copy (built by scripts/stage-public-copy.sh), where
  the same schemas are staged at docs/standards/schemas/ relative to the
  public repo root (an ancestor of tests/ there too).

Neither caller needs to know which layout it is running in.
"""
from pathlib import Path


def find_schema(name: str) -> Path:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "docs" / "standards" / "schemas" / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"schema {name!r} not found in any ancestor of {here} — expected at "
        "docs/standards/schemas/ at the monorepo root or the public repo root"
    )
