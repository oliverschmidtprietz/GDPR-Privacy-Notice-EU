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


# --- break-it test 2026-10-02: AGE-1 holes (a)/(b)/(c) ---------------------

def test_age_1_fires_for_a_single_covered_jurisdiction():
    # Hole (a): single-jurisdiction notices were never checked at all.
    _assert_only_rule_rejects("AGE-1__single-jurisdiction-wrong-age.json", "AGE-1")


def test_age_1_single_jurisdiction_correct_age_still_passes():
    sidecar = json.loads(
        (FIX / "must_pass" / "AGE-1__single-jurisdiction-correct-age.json").read_text())
    result = validate(sidecar, _ctx())
    assert result.status in {"passed", "passed_with_warnings"}, [f.to_dict() for f in result.findings]
    assert not any(f.rule_id == "AGE-1" for f in result.findings)


def test_age_1_fires_when_localizes_users_is_unset():
    # Hole (b): an unset localizes_users must not silently skip the check — treated
    # conservatively, like localizes_users=false.
    _assert_only_rule_rejects("AGE-1__unset-localizes-wrong-age.json", "AGE-1")


def test_age_1_unset_localizes_users_with_correct_age_still_passes():
    sidecar = json.loads(
        (FIX / "must_pass" / "AGE-1__unset-localizes-correct-age.json").read_text())
    assert "localizes_users" not in sidecar["notice"]
    result = validate(sidecar, _ctx())
    assert result.status in {"passed", "passed_with_warnings"}, [f.to_dict() for f in result.findings]
    assert not any(f.rule_id == "AGE-1" and f.severity == "rejection" for f in result.findings)


def test_age_1_warns_on_a_jurisdiction_outside_the_playbook():
    # Hole (c): a jurisdiction outside _AGE_THRESHOLDS (e.g. PL) must not silently
    # pass when children_data.applicable is true — at least a warning.
    sidecar = json.loads(
        (FIX / "must_pass" / "AGE-1__uncovered-jurisdiction-warning-only.json").read_text())
    result = validate(sidecar, _ctx())
    age_findings = [f for f in result.findings if f.rule_id == "AGE-1"]
    assert len(age_findings) == 1, [f.to_dict() for f in result.findings]
    assert age_findings[0].severity == "warning"
    assert age_findings[0].entry_id == "PL"
    assert result.status != "failed"


# --- break-it test 2026-10-02: CONSIST-1 omission bypass -------------------

def test_consist_1_fires_even_when_compliance_claim_is_omitted():
    _assert_only_rule_rejects(
        "CONSIST-1__unflagged-contested-no-compliance-claim.json", "CONSIST-1")


def test_consist_1_does_not_fire_when_the_contested_item_is_flagged():
    sidecar = json.loads(
        (FIX / "must_pass" / "CONSIST-1__unflagged-claim-irrelevant-when-flagged.json")
        .read_text())
    assert "art13_14_compliant" not in sidecar["notice"]
    result = validate(sidecar, _ctx())
    assert not any(f.rule_id == "CONSIST-1" for f in result.findings)
