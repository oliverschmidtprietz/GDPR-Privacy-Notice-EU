"""Project a native privacy-notice-eu sidecar into the portfolio core artefact.

A PROJECTION, not a rewrite (D-WS3-06): the native sidecar is never modified
or restructured. Structure and signature — `to_core_artefact(sidecar, *,
skill_version) -> dict` — mirror toms-art32's adapter
(skills/toms-art32/validator/toms_validator/core_artefact.py), but not the
mapping logic, which is this skill's own.

Field grounding, against notice-sidecar-schema.json:
  - subject: the notice being drafted, per the brief
    (docs/projects/gdpr-skills-marathon/SIX-SKILL-ADOPTION-BRIEF-2026-09-24.md
    section 5). Neither an organisation record nor a single processing
    activity, so subject.type is "other". id/label derive from
    notice.controller_name — the only human-meaningful identity a notice
    carries; slugified so the same controller yields the same id across
    repeated projections (mirrors toms-art32's org_slug/legal_name fallback).
  - outcome: notice_type + jurisdictions + the settled/assumed/contested
    tag counts, per the brief's "outcome" bullet.
  - gaps[]: BOTH the live validator's own diagnostics (deterministic, gate
    vocabulary rejection|warning|info) AND every confidence.contested[] item
    (substantive: a [TO CONFIRM WITH COUNSEL] flag is itself a drafting gap
    in this skill's domain, per the brief's "gaps = every [TO CONFIRM WITH
    COUNSEL: ...] flag"). An unflagged contested item under a compliant claim
    is exactly what CONSIST-1 rejects — both paths agree, they are not
    re-labelling one vocabulary as the other (D-WS3-03 governs the
    validator's own diagnostics about the sidecar; a contested item's
    severity here is this skill's own substantive judgement of how blocking
    the open question is).
  - sources[]: not hard-coded empty (the exact defect the standard calls out
    in ropa and toms-art32) — populated from sources.lock.json, filtered to
    the entries actually relevant to notice.jurisdictions plus EU_COMMON
    (always loaded per SKILL.md Step 1).
  - handoffs[]/unknowns[]: driven by the `dpia` block SKILL.md Group G
    produces. Indicators >=2 and not yet routed -> handoff to dpia-sentinel
    (SKILL.md:213-231,410, the skill's one named sibling). No `dpia` block at
    all -> unknown (the topic never came up in this run). Same treatment for
    `notice.localizes_users` when children's data is applicable.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ARTEFACT_SCHEMA_VERSION = "1.1"
SKILL_NAME = "privacy-notice-eu"
_UNKNOWN_SUBJECT_ID = "unknown-controller"

# skills/privacy-notice-eu/ — three parents up from validator/notice_validator/core_artefact.py
_SKILL_ROOT = Path(__file__).resolve().parents[2]
_SOURCES_LOCK_PATH = _SKILL_ROOT / "sources.lock.json"

_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

_OUTCOME_BY_VALIDATION_STATUS = {
    "passed": "complete",
    "passed_with_warnings": "provisional",
    "passed_with_override": "provisional",
    "failed": "blocked",
}

# Which sources.lock.json file keys are relevant to a given jurisdiction code.
# OTHER_EU.md carries several jurisdictions under one physical file, each
# re-verified independently (v1.6 only touched the ES section — see
# sources.lock.json's own per-jurisdiction entries and honesty note).
_JURISDICTION_FILE_KEYS = {
    "DE": ["references/DE.md"],
    "FR": ["references/FR.md"],
    "AT": ["references/OTHER_EU.md#AT"],
    "IT": ["references/OTHER_EU.md#IT"],
    "ES": ["references/OTHER_EU.md#ES"],
    "NL": ["references/OTHER_EU.md#NL"],
    "BE": ["references/OTHER_EU.md#BE"],
    "IE": ["references/OTHER_EU.md#IE"],
    "UK": ["references/OTHER_EU.md#UK"],
}
_ALWAYS_LOADED_FILE_KEYS = ["references/EU_COMMON.md"]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or _UNKNOWN_SUBJECT_ID


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _generated_at(sidecar: dict) -> str:
    value = sidecar.get("generated_at") if isinstance(sidecar, dict) else None
    if isinstance(value, str) and _DATETIME_RE.match(value):
        return value
    return _now_iso()


def _notice(sidecar: dict) -> dict:
    notice = sidecar.get("notice") if isinstance(sidecar, dict) else None
    return notice if isinstance(notice, dict) else {}


def _confidence(sidecar: dict) -> dict:
    confidence = sidecar.get("confidence") if isinstance(sidecar, dict) else None
    return confidence if isinstance(confidence, dict) else {}


def _subject(sidecar: dict) -> dict:
    notice = _notice(sidecar)
    controller_name = notice.get("controller_name")
    if isinstance(controller_name, str) and controller_name.strip():
        return {"id": _slugify(controller_name), "label": controller_name, "type": "other"}
    return {"id": _UNKNOWN_SUBJECT_ID, "label": "unknown controller", "type": "other"}


def _outcome_summary(sidecar: dict) -> str:
    notice = _notice(sidecar)
    confidence = _confidence(sidecar)
    notice_type = notice.get("notice_type", "unknown-type")
    jurisdictions = notice.get("jurisdictions")
    jurisdictions_str = ",".join(jurisdictions) if isinstance(jurisdictions, list) else "unknown"
    settled = confidence.get("settled_count", 0)
    assumed = confidence.get("assumed")
    contested = confidence.get("contested")
    assumed_n = len(assumed) if isinstance(assumed, list) else 0
    contested_n = len(contested) if isinstance(contested, list) else 0
    return (f"{notice_type} notice ({jurisdictions_str}): {settled} settled, "
            f"{assumed_n} assumed, {contested_n} contested")


def _contested_gaps(sidecar: dict) -> list:
    """Every confidence.contested[] item is a drafting gap in this skill's
    domain (brief: "gaps = every [TO CONFIRM WITH COUNSEL: ...] flag"). An
    item whose flag was never actually emitted is a rejection-severity gap —
    the same defect CONSIST-1 rejects at the validator level; a properly
    flagged item is a legitimate, non-blocking handback to counsel."""
    out = []
    confidence = _confidence(sidecar)
    contested = confidence.get("contested")
    if not isinstance(contested, list):
        return out
    for item in contested:
        if not isinstance(item, dict):
            continue
        flagged = item.get("confirm_with_counsel_flag_emitted")
        out.append({
            "id": item.get("id") or "contested-item",
            "severity": "warning" if flagged else "rejection",
            "message": item.get("description") or "(no description on this contested item)",
        })
    return out


def _validator_gaps(validation_findings) -> list:
    if not isinstance(validation_findings, list):
        return []
    out = []
    for f in validation_findings:
        if not isinstance(f, dict):
            continue
        out.append({
            "id": f.get("entry_id") or f.get("rule_id") or "gap",
            "severity": f.get("severity") or "rejection",
            "message": f.get("message") or "(no message on this finding)",
        })
    return out


def _load_sources_lock() -> dict:
    try:
        return json.loads(_SOURCES_LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sources(sidecar: dict) -> list:
    """sources[] = the sources.lock.json entries actually relied on for this
    run: EU_COMMON.md (always loaded per SKILL.md Step 1) plus every
    jurisdiction file key for a jurisdiction this notice actually names.
    Never a hard-coded empty list (the standard's carried gap 8)."""
    lock = _load_sources_lock()
    files = lock.get("files") if isinstance(lock, dict) else None
    if not isinstance(files, dict):
        return []
    notice = _notice(sidecar)
    jurisdictions = notice.get("jurisdictions")
    jurisdictions = jurisdictions if isinstance(jurisdictions, list) else []
    keys = list(_ALWAYS_LOADED_FILE_KEYS)
    for j in jurisdictions:
        keys.extend(_JURISDICTION_FILE_KEYS.get(j, []))
    out = []
    for key in keys:
        entry = files.get(key)
        if not isinstance(entry, dict):
            continue
        url = entry.get("url")
        citation = url or entry.get("notes") or entry.get("source_type") or key
        last_verified = entry.get("last_verified")
        if not isinstance(last_verified, str):
            continue
        out.append({"id": key, "citation": citation, "last_verified": last_verified})
    return out


def _handoffs_and_unknowns(sidecar: dict) -> tuple:
    """Driven by real input, per the brief: emit handoffs[] when a sibling
    topic actually came up in this run/document; emit unknowns[] when it's an
    open question with no sibling data available. Never a hard-coded []."""
    handoffs, unknowns = [], []
    notice = _notice(sidecar)
    children = sidecar.get("children_data") if isinstance(sidecar, dict) else None
    children = children if isinstance(children, dict) else {}
    dpia = sidecar.get("dpia") if isinstance(sidecar, dict) else None

    if isinstance(dpia, dict):
        indicators = dpia.get("indicators_flagged")
        routed = dpia.get("routed_to_dpia_sentinel")
        if isinstance(indicators, int) and indicators >= 2 and not routed:
            handoffs.append({
                "sibling_skill": "dpia-sentinel",
                "reason": (f"{indicators} WP248 rev.01 DPIA indicators flagged in Group G — "
                           "SKILL.md:230 routes the full Art. 35 threshold assessment and "
                           "drafting to dpia-sentinel; this skill only drafts the notice."),
            })
    else:
        unknowns.append({
            "id": "dpia-screening-not-run",
            "question": "Have the WP248 rev.01 DPIA indicators (SKILL.md Group G) been "
                        "screened for this processing at all?",
            "blocking": False,
        })

    if children.get("applicable") is True and notice.get("localizes_users") is None:
        unknowns.append({
            "id": "localisation-capability-unknown",
            "question": "Can this service reliably localise which target market a user is "
                        "in, for the purpose of applying the correct per-Member-State Art. 8 "
                        "age threshold (EU_COMMON.md 'Multi-jurisdiction rule')?",
            "blocking": True,
        })

    return handoffs, unknowns


def to_core_artefact(sidecar: dict, *, skill_version: str) -> dict:
    if not isinstance(sidecar, dict):
        sidecar = {}
    validation = sidecar.get("validation")
    validation = validation if isinstance(validation, dict) else {}
    validation_findings = validation.get("findings")
    handoffs, unknowns = _handoffs_and_unknowns(sidecar)
    return {
        "artefact_schema_version": ARTEFACT_SCHEMA_VERSION,
        "skill": SKILL_NAME,
        "skill_version": skill_version,
        "generated_at": _generated_at(sidecar),
        "subject": _subject(sidecar),
        "outcome": {
            "status": _OUTCOME_BY_VALIDATION_STATUS.get(
                validation.get("status", "passed"), "provisional"),
            "summary": _outcome_summary(sidecar),
        },
        "gaps": _validator_gaps(validation_findings) + _contested_gaps(sidecar),
        "sources": _sources(sidecar),
        "handoffs": handoffs,
        "unknowns": unknowns,
    }


def blocked_artefact(*, skill_version: str, reason: str) -> dict:
    """Minimal, always schema-valid artefact for when `to_core_artefact`
    itself raises despite the guards above (defence in depth, mirrors
    toms_validator.core_artefact.blocked_artefact)."""
    return {
        "artefact_schema_version": ARTEFACT_SCHEMA_VERSION,
        "skill": SKILL_NAME,
        "skill_version": skill_version,
        "generated_at": _now_iso(),
        "subject": {"id": _UNKNOWN_SUBJECT_ID, "label": "unknown controller", "type": "other"},
        "outcome": {
            "status": "blocked",
            "summary": f"Core artefact adapter failed: {reason}",
        },
        "gaps": [{
            "id": "core-artefact-adapter-error",
            "severity": "rejection",
            "message": f"to_core_artefact raised: {reason}",
        }],
        "sources": [],
        "handoffs": [],
        "unknowns": [],
    }
