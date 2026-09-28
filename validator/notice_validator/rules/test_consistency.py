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


def _assert_only_rule_rejects(fixture_name, rule_id):
    sidecar = json.loads((FIX / "must_fail" / fixture_name).read_text())
    result = validate(sidecar, _ctx())   # MUST NOT raise — findings-based
    assert result.status == "failed"
    rejecting = {f.rule_id for f in result.findings if f.severity == "rejection"}
    assert rejecting == {rule_id}, [f.to_dict() for f in result.findings]


def test_consist_1_compliant_claim_with_unflagged_contested_item_is_rejected():
    _assert_only_rule_rejects("CONSIST-1__compliant-with-unflagged-contested.json", "CONSIST-1")


def test_age_1_lowest_threshold_regression_is_rejected():
    # The exact pre-v1.6 bug (CHANGELOG.md Finding 7): a multi-jurisdiction notice that
    # cannot localise users must apply the HIGHEST applicable Art. 8 threshold, never the
    # lowest. Regression guard.
    _assert_only_rule_rejects("AGE-1__lowest-threshold-regression.json", "AGE-1")


def test_age_1_per_market_threshold_wrong_is_rejected():
    _assert_only_rule_rejects("AGE-1__per-market-threshold-wrong.json", "AGE-1")


def test_age_1_does_not_fire_when_children_data_not_applicable():
    sidecar = json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())
    assert sidecar["children_data"]["applicable"] is False
    result = validate(sidecar, _ctx())
    assert not any(f.rule_id == "AGE-1" for f in result.findings)
