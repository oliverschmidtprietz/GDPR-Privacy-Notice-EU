"""Finding dataclass — a single validator output entry.

Severity is the GATE ("does this stop the job?"); priority is an optional risk
grading that never affects the gate (D-WS3-02). This is the deterministic
validator's own diagnostics about the sidecar file — never applied to a
substantive legal judgement (D-WS3-03). This skill has no separate substantive
severity register today (unlike toms-art32's Article 32 findings[]), so no
migration table is needed here.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(frozen=True)
class Finding:
    rule_id: str
    category: str
    severity: str             # "rejection" | "warning" | "info"
    message: str
    spec_anchor: str
    priority: Optional[str] = None      # "high" | "medium" | "low"
    entry_type: Optional[str] = None
    entry_id: Optional[str] = None
    field: Optional[str] = None
    fix_hint: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}
