"""SRC-1 — sources.lock.json manifest coverage and freshness (sources.py).

Mirrors toms-art32's test_sources.py pattern (findings-based registry rule,
never raise). Fixture manifests are synthetic inline dicts injected via
ctx.sources_lock_override, with ctx.references_dir pointed at the real
references/ directory so the on-disk .md set is real.
"""
import json
from pathlib import Path

from notice_validator.runner import validate, Context

HERE = Path(__file__).resolve()
VALIDATOR = HERE.parents[2]                    # .../validator
SKILL_ROOT = VALIDATOR.parent                  # .../privacy-notice-eu
SCHEMA = SKILL_ROOT / "references" / "notice-sidecar-schema.json"
REFERENCES_DIR = SKILL_ROOT / "references"
REAL_MANIFEST = SKILL_ROOT / "sources.lock.json"
FIX = VALIDATOR / "fixtures"


def _ctx(sources_lock_override=None):
    return Context(mode="internal", schema_path=SCHEMA, references_dir=REFERENCES_DIR,
                   sources_lock_override=sources_lock_override)


def _minimal_sidecar():
    return json.loads((FIX / "must_pass" / "minimal-clean.json").read_text())


def _src1_findings(result):
    return [f for f in result.findings if f.rule_id == "SRC-1"]


def test_src_1_missing_manifest_entry_is_flagged():
    # A manifest that omits a real on-disk reference file (templates.md is real and
    # committed; deliberately left out here).
    override = {
        "schema_version": "1.0",
        "generated_at": "2026-09-24",
        "files": {
            "references/EU_COMMON.md": {
                "source_type": "primary-law", "jurisdiction": "EU", "url": None,
                "last_verified": "2026-09-15", "confidence": "high",
                "owner": "oliverschmidtprietz",
            },
        },
    }
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=override))
    findings = _src1_findings(result)
    assert findings, "SRC-1 must fire when an on-disk references/*.md file has no manifest entry"
    assert any("templates.md" in f.message for f in findings), [f.to_dict() for f in findings]
    for f in findings:
        assert f.severity == "warning"


def test_src_1_per_section_key_covers_the_physical_file():
    # OTHER_EU.md is declared as several "#<jurisdiction>" sub-entries, never a bare
    # "references/OTHER_EU.md" key — coverage must still recognise the physical file as
    # covered via the "#" prefix match, not flag it as missing.
    override = {
        "schema_version": "1.0",
        "generated_at": "2026-09-24",
        "files": {
            "references/OTHER_EU.md#AT": {
                "source_type": "primary-law", "jurisdiction": "AT", "url": None,
                "last_verified": "2026-08-21", "confidence": "high",
                "owner": "oliverschmidtprietz",
            },
        },
    }
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=override))
    findings = _src1_findings(result)
    assert not any("OTHER_EU.md" in f.message and "exists on disk" in f.message for f in findings)


def test_src_1_stale_manifest_entry_is_flagged():
    override = {
        "schema_version": "1.0",
        "generated_at": "2026-09-24",
        "files": {
            "references/EU_COMMON.md": {
                "source_type": "primary-law", "jurisdiction": "EU", "url": None,
                "last_verified": "2024-01-01", "confidence": "high",
                "owner": "oliverschmidtprietz",
            },
        },
    }
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=override))
    findings = _src1_findings(result)
    stale = [f for f in findings if "EU_COMMON.md" in f.message and "2024-01-01" in f.message]
    assert stale, [f.to_dict() for f in findings]
    for f in findings:
        assert f.severity == "warning"


def test_src_1_bare_list_manifest_is_flagged_without_raising():
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=[]))   # MUST NOT raise
    findings = _src1_findings(result)
    assert findings, "a malformed (non-object) manifest must be flagged, not silently skipped"
    assert not any(f.severity == "rejection" for f in result.findings), \
        "a malformed manifest must never surface as a build-failing rejection"


def test_src_1_real_manifest_produces_zero_findings():
    # GREEN case: the real, honest, complete sources.lock.json (no override) must satisfy
    # SRC-1 with no findings at all.
    assert REAL_MANIFEST.exists(), "skills/privacy-notice-eu/sources.lock.json must exist"
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=None))
    findings = _src1_findings(result)
    assert findings == [], [f.to_dict() for f in findings]


def test_src_1_is_never_rejection_severity():
    override = {"schema_version": "1.0", "generated_at": "2026-09-24", "files": {}}
    result = validate(_minimal_sidecar(), _ctx(sources_lock_override=override))
    findings = _src1_findings(result)
    assert findings, "expected findings to check severity on"
    for f in findings:
        assert f.severity == "warning", f.to_dict()
