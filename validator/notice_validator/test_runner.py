"""Runner-level guards.

An embedder who imports only notice_validator.runner gets an empty rule
registry — validate() must fail loudly in that state, never return a green
result for arbitrary input (mirrors toms-art32's RUNNER-0 test).
"""
import json
from pathlib import Path

import jsonschema

from notice_validator.findings import Finding
from notice_validator.runner import validate, Context, Result, to_findings_json

HERE = Path(__file__).resolve()
VALIDATOR = HERE.parents[1]                    # .../validator
SCHEMA = VALIDATOR.parent / "references" / "notice-sidecar-schema.json"
FIX = VALIDATOR / "fixtures"


def _ctx():
    return Context(mode="internal", schema_path=SCHEMA,
                   references_dir=VALIDATOR.parent / "references")


def test_empty_rule_registry_fails_closed(monkeypatch):
    monkeypatch.setattr("notice_validator.runner.RULES", {})
    sidecar = json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())
    result = validate(sidecar, _ctx())
    assert result.status == "failed"
    assert any(f.rule_id == "RUNNER-0" and f.severity == "rejection"
               for f in result.findings), [f.to_dict() for f in result.findings]


def test_populated_registry_still_passes_clean_fixture():
    import notice_validator.rules  # noqa: F401 — populates the registry
    sidecar = json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())
    result = validate(sidecar, _ctx())
    assert result.status in {"passed", "passed_with_warnings"}, \
        [f.to_dict() for f in result.findings]


def test_runner0_early_return_reports_the_real_mode_and_validated_at(monkeypatch):
    monkeypatch.setattr("notice_validator.runner.RULES", {})
    sidecar = json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())
    ctx = Context(mode="submission", schema_path=SCHEMA,
                  references_dir=VALIDATOR.parent / "references")
    result = validate(sidecar, ctx)
    assert result.status == "failed"
    assert result.mode == "submission"
    assert result.validated_at != ""


# --- Portfolio findings-report 2.0 ---------------------------------

_REPORT_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[4] / "docs" / "standards" / "schemas"
     / "findings-report-2.0.schema.json").read_text(encoding="utf-8")
)


def _sample_result() -> Result:
    return Result(
        status="passed_with_warnings",
        summary={"rejections": 0, "warnings": 1, "info": 0, "rules_evaluated": 4},
        findings=[Finding(
            rule_id="SRC-1", category="freshness", severity="warning", priority="high",
            message="references/NOTICE_TYPES.md exists on disk but has no entry in "
                     "sources.lock.json.",
            spec_anchor="sources.lock.json#freshness",
        )],
        mode="internal",
        artefact_path="notice.json",
        validated_at="2026-09-24T09:12:00Z",
    )


def test_report_validates_against_the_portfolio_schema():
    jsonschema.validate(to_findings_json(_sample_result(), skill_version="1.7"),
                        _REPORT_SCHEMA)


def test_report_is_self_describing():
    report = to_findings_json(_sample_result(), skill_version="1.7")
    assert report["report_schema_version"] == "2.0"
    assert report["skill"] == "privacy-notice-eu"
    assert report["skill_version"] == "1.7"
    assert set(report["summary"]) == {"rejections", "warnings", "info", "rules_evaluated"}
