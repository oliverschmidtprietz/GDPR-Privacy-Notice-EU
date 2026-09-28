"""CLI tests for --emit-core-artefact (portfolio standard carried gap 5).

Same contract as toms-art32's flag: the emitted artefact is built from the
LIVE validation result, never the sidecar's embedded validation block.
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

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


def test_emit_writes_schema_valid_core_artefact_and_leaves_report_unchanged(tmp_path):
    out = tmp_path / "core.json"
    proc = run_cli(FIXTURE, "--emit-core-artefact", out, "--format", "json")
    assert proc.returncode == 0, proc.stderr
    artefact = json.loads(out.read_text(encoding="utf-8"))
    jsonschema.validate(artefact, ARTEFACT_SCHEMA,
                        format_checker=jsonschema.FormatChecker())
    assert artefact["skill"] == "privacy-notice-eu"
    envelope = json.loads(proc.stdout)
    assert envelope["report_schema_version"] == "2.0"


def test_emit_reflects_live_result_not_embedded_validation_block(tmp_path):
    sidecar = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sidecar["validation"] = {"status": "failed", "findings": []}
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(sidecar), encoding="utf-8")
    out = tmp_path / "core.json"
    proc = run_cli(tampered, "--emit-core-artefact", out)
    assert proc.returncode == 0, proc.stderr
    artefact = json.loads(out.read_text(encoding="utf-8"))
    assert artefact["outcome"]["status"] == "complete"
