import json
from pathlib import Path

from notice_validator.runner import validate, Context

HERE = Path(__file__).resolve()
VALIDATOR = HERE.parents[2]                    # .../validator
SCHEMA = VALIDATOR.parent / "references" / "notice-sidecar-schema.json"
FIX = VALIDATOR / "fixtures"


def _ctx():
    return Context(mode="internal", schema_path=SCHEMA,
                   references_dir=VALIDATOR.parent / "references")


def test_minimal_clean_passes():
    sidecar = json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())
    result = validate(sidecar, _ctx())
    assert result.status in {"passed", "passed_with_warnings"}, [f.to_dict() for f in result.findings]


def test_multi_jurisdiction_localized_passes():
    sidecar = json.loads((FIX / "must_pass" / "multi-jurisdiction-localized.json").read_text())
    result = validate(sidecar, _ctx())
    assert result.status in {"passed", "passed_with_warnings"}, [f.to_dict() for f in result.findings]


def test_missing_notice_type_is_a_rejection_finding_not_an_exception():
    sidecar = json.loads((FIX / "must_fail" / "SCHEMA-1__missing-notice-type.json").read_text())
    result = validate(sidecar, _ctx())   # MUST NOT raise — findings-based
    assert result.status == "failed"
    rejecting = {f.rule_id for f in result.findings if f.severity == "rejection"}
    assert rejecting == {"SCHEMA-1"}, [f.to_dict() for f in result.findings]
