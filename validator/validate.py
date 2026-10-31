#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["jsonschema>=4.21"]
# ///
"""privacy-notice-eu validator CLI — structural tier.

  uv run skills/privacy-notice-eu/validator/validate.py <notice-sidecar.json> [--mode internal|submission] [--format human|json]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from notice_validator.runner import validate, Context, Result, to_findings_json  # noqa: E402
from notice_validator.core_artefact import to_core_artefact, blocked_artefact  # noqa: E402
from notice_validator.findings import Finding  # noqa: E402
from notice_validator import rules  # noqa: E402,F401  (populates the registry)

DEFAULT_SCHEMA = HERE.parent / "references" / "notice-sidecar-schema.json"
DEFAULT_REFS = HERE.parent / "references"


def _skill_version() -> str:
    """Read the live version from SKILL.md frontmatter — never hard-code it (CLAUDE.md)."""
    skill_md = Path(__file__).resolve().parents[1] / "SKILL.md"
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("SKILL.md has no version: field")


def _load_sidecar(path: Path):
    """Read and parse `path` as the notice sidecar JSON (break-it test
    2026-10-02, ledger X1). A missing file, an unreadable file, invalid
    UTF-8, invalid JSON, or a non-object top level is bad input, not a
    program bug: return (None, <one-line message>) instead of letting any of
    FileNotFoundError / OSError / UnicodeDecodeError / json.JSONDecodeError
    propagate as a raw traceback. On success, return (sidecar_dict, None)."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"sidecar file not found: {path}"
    except OSError as exc:
        return None, f"sidecar file could not be read: {exc}"
    except UnicodeDecodeError as exc:
        return None, f"sidecar file is not valid UTF-8: {exc}"
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"sidecar is not valid JSON: {exc}"
    if not isinstance(parsed, dict):
        return None, (f"sidecar must be a JSON object at the top level, got "
                       f"{type(parsed).__name__}")
    return parsed, None


def _input_error_result(error: str, *, mode: str, artefact_path: str) -> Result:
    """A Result carrying a single rejection finding for bad input, built the
    same way RUNNER-0 is built (status 'failed', the runner's own vocabulary)
    so the CLI's downstream report/exit-code code path needs no special case."""
    finding = Finding(
        rule_id="INPUT-0", category="input", severity="rejection",
        message=f"Could not load the sidecar: {error}.",
        spec_anchor="validator/validate.py#input-loading",
        fix_hint="Point the sidecar argument at a readable, UTF-8-encoded, "
                 "valid-JSON file whose top level is a JSON object.",
    )
    return Result(
        status="failed",
        summary={"rejections": 1, "warnings": 0, "info": 0, "rules_evaluated": 0},
        findings=[finding],
        mode=mode,
        artefact_path=artefact_path,
        validated_at=datetime.now(timezone.utc)
            .isoformat(timespec="seconds").replace("+00:00", "Z"),
    )


def main(argv=None):
    p = argparse.ArgumentParser(prog="privacy-notice-eu-validator")
    p.add_argument("sidecar", type=Path)
    p.add_argument("--mode", choices=["internal", "submission"], default="internal")
    p.add_argument("--format", choices=["human", "json"], default="human")
    p.add_argument("--schema-path", type=Path, default=DEFAULT_SCHEMA)
    p.add_argument("--references-dir", type=Path, default=DEFAULT_REFS)
    p.add_argument(
        "--emit-core-artefact",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "After validation, write the portfolio core artefact "
            "(skill-artefact-1.1 schema) projection of THIS run's result to PATH. "
            "Built from the live validation result, never the sidecar's "
            "embedded validation block. Report and exit code unchanged."
        ),
    )
    args = p.parse_args(argv)

    sidecar, load_error = _load_sidecar(args.sidecar)
    if load_error is not None:
        # Fail closed (break-it test 2026-10-02, ledger X1): bad input is reported
        # the same way any other rejection is, never as a raw traceback.
        result = _input_error_result(load_error, mode=args.mode,
                                      artefact_path=str(args.sidecar))
    else:
        ctx = Context(mode=args.mode, schema_path=args.schema_path,
                      references_dir=args.references_dir)
        result = validate(sidecar, ctx)
        result.artefact_path = str(args.sidecar)

    if args.emit_core_artefact is not None:
        if load_error is not None:
            artefact = blocked_artefact(skill_version=_skill_version(), reason=load_error)
        else:
            live_sidecar = {**sidecar, "validation": {
                "status": result.status,
                "findings": [f.to_dict() for f in result.findings],
            }}
            try:
                artefact = to_core_artefact(live_sidecar,
                                            skill_version=_skill_version())
            except Exception as exc:  # adapter must never crash the run — mirrors
                # runner.validate()'s per-rule guard: the report on stdout and the
                # exit code stay exactly as they would be without this flag, and a
                # minimal, schema-valid, blocked artefact is written instead of a
                # traceback (docs/standards/PORTFOLIO-STANDARD.md ~line 129).
                artefact = blocked_artefact(
                    skill_version=_skill_version(),
                    reason=f"{type(exc).__name__}: {exc}")
        args.emit_core_artefact.write_text(
            json.dumps(artefact, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(to_findings_json(result, skill_version=_skill_version()), indent=2))
    else:
        print(f"status: {result.status}  ({len(result.findings)} findings)")
        for f in result.findings:
            print(f"  [{f.severity}] {f.rule_id}: {f.message}")
    return 1 if result.status == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
