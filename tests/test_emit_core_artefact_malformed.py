"""Malformed-input regression tests for --emit-core-artefact (mirrors
toms-art32's test_toms_emit_core_artefact_malformed.py). The portfolio
standard guarantees the report on stdout and the exit code stay unchanged,
and the artefact is written even when validation fails.
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATE = REPO_ROOT / "skills" / "privacy-notice-eu" / "validator" / "validate.py"
FIXTURE = (REPO_ROOT / "skills" / "privacy-notice-eu" / "validator" / "fixtures"
           / "must_pass" / "minimal-clean.json")
ARTEFACT_SCHEMA = json.loads(
    (REPO_ROOT / "docs" / "standards" / "schemas"
     / "skill-artefact-1.1.schema.json").read_text(encoding="utf-8"))


def run_cli(*argv):
    return subprocess.run(
        [sys.executable, str(VALIDATE), *map(str, argv)],
        capture_output=True, text=True)


def _load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


MUTATIONS = {
    "notice-not-an-object": lambda s: s.__setitem__("notice", 42),
    "confidence-contested-entry-is-null": lambda s: s["confidence"].__setitem__(
        "contested", [None]),
    "generated-at-is-null": lambda s: s.__setitem__("generated_at", None),
}


@pytest.mark.parametrize("name", MUTATIONS)
def test_malformed_sidecar_leaves_report_and_exit_code_unchanged(tmp_path, name):
    sidecar = _load_fixture()
    MUTATIONS[name](sidecar)
    mutated_path = tmp_path / f"{name}.json"
    mutated_path.write_text(json.dumps(sidecar), encoding="utf-8")

    baseline = run_cli(mutated_path, "--format", "json")
    out = tmp_path / "core.json"
    with_flag = run_cli(mutated_path, "--emit-core-artefact", out, "--format", "json")

    assert with_flag.returncode == baseline.returncode
    baseline_report = json.loads(baseline.stdout)
    with_flag_report = json.loads(with_flag.stdout)
    baseline_report["validated_at"] = "<normalised>"
    with_flag_report["validated_at"] = "<normalised>"
    assert with_flag_report == baseline_report
    assert with_flag.stderr == "" or "Traceback" not in with_flag.stderr


@pytest.mark.parametrize("name", MUTATIONS)
def test_malformed_sidecar_still_writes_a_schema_valid_artefact(tmp_path, name):
    sidecar = _load_fixture()
    MUTATIONS[name](sidecar)
    mutated_path = tmp_path / f"{name}.json"
    mutated_path.write_text(json.dumps(sidecar), encoding="utf-8")

    out = tmp_path / "core.json"
    proc = run_cli(mutated_path, "--emit-core-artefact", out, "--format", "json")

    assert out.exists(), f"no artefact written for {name}; stderr={proc.stderr}"
    artefact = json.loads(out.read_text(encoding="utf-8"))
    jsonschema.validate(artefact, ARTEFACT_SCHEMA,
                        format_checker=jsonschema.FormatChecker())

    envelope = json.loads(proc.stdout)
    assert envelope["status"] == "failed"
    assert artefact["outcome"]["status"] == "blocked"
