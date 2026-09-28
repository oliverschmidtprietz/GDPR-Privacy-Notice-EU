"""Tests for notice_validator.core_artefact.to_core_artefact."""
import json
from pathlib import Path

import jsonschema

from notice_validator.core_artefact import to_core_artefact, blocked_artefact

_ARTEFACT_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[4] / "docs" / "standards" / "schemas"
     / "skill-artefact-1.1.schema.json").read_text(encoding="utf-8")
)


def _native() -> dict:
    return {
        "sidecar_schema_version": "1.0",
        "generated_at": "2026-09-24T09:00:00Z",
        "notice": {
            "notice_type": "website_app",
            "controller_name": "Musterfirma GmbH",
            "jurisdictions": ["DE"],
            "localizes_users": True,
            "art13_14_compliant": True,
        },
        "confidence": {
            "settled_count": 12,
            "assumed": [{"id": "assume-1", "description": "Marketing runs on consent."}],
            "contested": [],
        },
        "children_data": {"applicable": False},
        "dpia": {"indicators_flagged": 0, "routed_to_dpia_sentinel": False},
        "validation": {"status": "passed", "findings": []},
    }


def test_projection_is_schema_valid():
    jsonschema.validate(to_core_artefact(_native(), skill_version="1.7"), _ARTEFACT_SCHEMA)


def test_subject_is_derived_from_controller_name():
    doc = to_core_artefact(_native(), skill_version="1.7")
    assert doc["subject"] == {"id": "musterfirma-gmbh", "label": "Musterfirma GmbH", "type": "other"}


def test_subject_id_is_a_placeholder_when_controller_name_is_absent():
    native = _native()
    del native["notice"]["controller_name"]
    doc = to_core_artefact(native, skill_version="1.7")
    assert doc["subject"]["id"] == "unknown-controller"


def test_native_artefact_is_not_mutated():
    native = _native()
    before = json.dumps(native, sort_keys=True)
    to_core_artefact(native, skill_version="1.7")
    assert json.dumps(native, sort_keys=True) == before


def test_outcome_status_maps_from_live_validation_status():
    native = _native()
    native["validation"] = {"status": "failed", "findings": []}
    doc = to_core_artefact(native, skill_version="1.7")
    assert doc["outcome"]["status"] == "blocked"


def test_contested_item_with_flag_emitted_is_a_warning_gap_not_a_rejection():
    native = _native()
    native["confidence"]["contested"] = [
        {"id": "contested-1", "description": "Genuinely unsettled point.",
         "confirm_with_counsel_flag_emitted": True}
    ]
    doc = to_core_artefact(native, skill_version="1.7")
    assert doc["gaps"] == [{"id": "contested-1", "severity": "warning",
                            "message": "Genuinely unsettled point."}]


def test_contested_item_without_flag_emitted_is_a_rejection_gap():
    native = _native()
    native["confidence"]["contested"] = [
        {"id": "contested-2", "description": "Smoothed over.",
         "confirm_with_counsel_flag_emitted": False}
    ]
    doc = to_core_artefact(native, skill_version="1.7")
    assert doc["gaps"] == [{"id": "contested-2", "severity": "rejection",
                            "message": "Smoothed over."}]


def test_live_validation_findings_also_project_into_gaps():
    native = _native()
    native["validation"] = {
        "status": "failed",
        "findings": [{"rule_id": "SCHEMA-1", "severity": "rejection",
                      "message": "Schema violation."}],
    }
    doc = to_core_artefact(native, skill_version="1.7")
    assert {"id": "SCHEMA-1", "severity": "rejection", "message": "Schema violation."} in doc["gaps"]


def test_no_dpia_block_at_all_emits_an_unknown_not_a_hardcoded_empty_list():
    native = _native()
    del native["dpia"]
    doc = to_core_artefact(native, skill_version="1.7")
    assert any(u["id"] == "dpia-screening-not-run" for u in doc["unknowns"])
    assert doc["handoffs"] == []


def test_two_plus_dpia_indicators_not_yet_routed_emits_a_handoff():
    native = _native()
    native["dpia"] = {"indicators_flagged": 3, "routed_to_dpia_sentinel": False}
    doc = to_core_artefact(native, skill_version="1.7")
    assert doc["handoffs"] == [{
        "sibling_skill": "dpia-sentinel",
        "reason": ("3 WP248 rev.01 DPIA indicators flagged in Group G — SKILL.md:230 "
                   "routes the full Art. 35 threshold assessment and drafting to "
                   "dpia-sentinel; this skill only drafts the notice."),
    }]


def test_sources_are_populated_from_the_real_lock_file_not_hardcoded_empty():
    doc = to_core_artefact(_native(), skill_version="1.7")
    assert doc["sources"], "sources[] must not be a hard-coded empty list"
    ids = {s["id"] for s in doc["sources"]}
    assert "references/EU_COMMON.md" in ids
    assert "references/DE.md" in ids


def test_blocked_artefact_is_schema_valid():
    doc = blocked_artefact(skill_version="1.7", reason="boom")
    jsonschema.validate(doc, _ARTEFACT_SCHEMA)
    assert doc["outcome"]["status"] == "blocked"
