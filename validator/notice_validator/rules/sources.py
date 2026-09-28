"""SRC-1 — sources.lock.json manifest coverage and freshness.

Mirrors toms-art32's SRC-1 (skills/toms-art32/validator/toms_validator/rules/sources.py).
One difference: this skill's sources.lock.json declares SOME on-disk reference files at
sub-file granularity (e.g. "references/OTHER_EU.md#ES") because different jurisdiction
sections inside the same physical file (OTHER_EU.md) were re-verified on different dates
(see sources.lock.json's own notes and the adoption brief's honesty requirement) — a whole-
file "last_verified" would either wrongly stamp an unverified section as fresh, or wrongly
flag a verified section as stale. Coverage below therefore treats an on-disk file as covered
if ANY declared key equals its path, or starts with "<path>#".

Two independent checks fire under the single SRC-1 id (findings-based; never raise):
- missing-file: an on-disk references/*.md file has no declared key covering it at all.
- staleness: a declared entry's last_verified is > 365 days before today.
"""
import datetime as _dt
import json
from pathlib import Path

from ..findings import Finding
from ..registry import rule

SPEC = "sources.lock.json#freshness"
_STALE_AFTER_DAYS = 365


def _default_manifest_path(ctx) -> Path:
    return ctx.references_dir.parent / "sources.lock.json"


def _validate_shape(manifest, source_desc):
    if not isinstance(manifest, dict):
        return None, f"{source_desc} is not a JSON object (got {type(manifest).__name__})"
    files = manifest.get("files")
    if files is not None and not isinstance(files, dict):
        return None, f"{source_desc}['files'] is not a JSON object (got {type(files).__name__})"
    return manifest, None


def _load_manifest(ctx):
    override = getattr(ctx, "sources_lock_override", None)
    if override is not None:
        return _validate_shape(override, "ctx.sources_lock_override")
    manifest_path = _default_manifest_path(ctx)
    if not manifest_path.exists():
        return None, f"sources.lock.json not found at {manifest_path}"
    try:
        parsed = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"sources.lock.json at {manifest_path} could not be read/parsed: {exc}"
    return _validate_shape(parsed, str(manifest_path))


def _on_disk_reference_keys(ctx):
    if not ctx.references_dir.exists():
        return set()
    keys = set()
    for path in ctx.references_dir.rglob("*.md"):
        rel = path.relative_to(ctx.references_dir)
        keys.add(f"references/{rel.as_posix()}")
    return keys


def _is_covered(on_disk_key: str, declared_keys) -> bool:
    return on_disk_key in declared_keys or any(
        k.startswith(on_disk_key + "#") for k in declared_keys)


@rule(
    id="SRC-1",
    severity="warning",
    category="freshness",
    description="sources.lock.json must cover every on-disk references/*.md file (whole-file "
                "or per-section keys), and every declared entry's last_verified must be "
                "within the last 12 months.",
    spec_anchor=SPEC,
)
def source_manifest_coverage_and_freshness(sidecar, ctx):
    out = []
    manifest, error = _load_manifest(ctx)
    if manifest is None:
        out.append(Finding(
            rule_id="SRC-1", category="freshness", severity="warning", priority="high",
            message=f"sources.lock.json could not be loaded: {error}",
            spec_anchor=SPEC,
            fix_hint="Author skills/privacy-notice-eu/sources.lock.json covering every "
                     "references/*.md file.",
        ))
        return out

    declared = set((manifest.get("files") or {}).keys())
    on_disk = _on_disk_reference_keys(ctx)

    for missing in sorted(k for k in on_disk if not _is_covered(k, declared)):
        out.append(Finding(
            rule_id="SRC-1", category="freshness", severity="warning", priority="high",
            entry_type="reference_file", entry_id=missing, field="files",
            message=f"{missing} exists on disk but has no entry (or entry section) in "
                     "sources.lock.json.",
            spec_anchor=SPEC,
            fix_hint=f"Add a files['{missing}'] entry to sources.lock.json "
                     "(source_type, jurisdiction, url, last_verified, confidence, owner).",
        ))

    today = _dt.date.today()
    threshold = today - _dt.timedelta(days=_STALE_AFTER_DAYS)
    for path, entry in (manifest.get("files") or {}).items():
        if not isinstance(entry, dict):
            continue
        last_verified = entry.get("last_verified")
        if not isinstance(last_verified, str):
            continue
        try:
            verified_date = _dt.date.fromisoformat(last_verified)
        except ValueError:
            continue
        if verified_date < threshold:
            age_days = (today - verified_date).days
            out.append(Finding(
                rule_id="SRC-1", category="freshness", severity="warning", priority="high",
                entry_type="manifest_entry", entry_id=path, field="last_verified",
                message=(f"sources.lock.json entry '{path}' has last_verified={last_verified} "
                          f"({age_days} days ago, > {_STALE_AFTER_DAYS}-day threshold)."),
                spec_anchor=SPEC,
                fix_hint=f"Re-verify {path} against its source and update sources.lock.json "
                         f"files['{path}'].last_verified.",
            ))

    return out
