"""CLI fail-closed regression tests for bad sidecar input (break-it test
2026-10-02, ledger cross-cutting X1): a missing file, an unreadable file,
invalid UTF-8, invalid JSON, or a non-object top-level JSON must never crash
validate.py with a raw traceback at the file-read step — they are reported as
an ordinary rejection finding (rule INPUT-0), exit code 1, same as any other
blocked run.
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATE = REPO_ROOT / "skills" / "privacy-notice-eu" / "validator" / "validate.py"
ARTEFACT_SCHEMA = json.loads(
    (REPO_ROOT / "docs" / "standards" / "schemas"
     / "skill-artefact-1.1.schema.json").read_text(encoding="utf-8"))


def run_cli(*argv):
    return subprocess.run(
        [sys.executable, str(VALIDATE), *map(str, argv)],
        capture_output=True, text=True)


def _assert_fails_closed(proc):
    assert proc.returncode == 1, proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr


def test_missing_file_fails_closed_json(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    proc = run_cli(missing, "--format", "json")
    _assert_fails_closed(proc)
    report = json.loads(proc.stdout)
    assert report["status"] == "failed"
    assert any(f["rule_id"] == "INPUT-0" for f in report["findings"])


def test_missing_file_fails_closed_human(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    proc = run_cli(missing)
    _assert_fails_closed(proc)
    assert "status: failed" in proc.stdout


def test_invalid_json_syntax_fails_closed(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"not": "valid json"', encoding="utf-8")  # probe12
    proc = run_cli(bad, "--format", "json")
    _assert_fails_closed(proc)
    report = json.loads(proc.stdout)
    assert report["status"] == "failed"
    assert any(f["rule_id"] == "INPUT-0" for f in report["findings"])


def test_invalid_utf8_fails_closed(tmp_path):
    bad = tmp_path / "bad-utf8.json"
    bad.write_bytes(b'{"notice": {"notice_type": "\xff\xfe"}}')
    proc = run_cli(bad, "--format", "json")
    _assert_fails_closed(proc)
    report = json.loads(proc.stdout)
    assert report["status"] == "failed"
    assert any(f["rule_id"] == "INPUT-0" for f in report["findings"])


def test_non_object_top_level_json_fails_closed(tmp_path):
    arr = tmp_path / "array.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")  # probe07
    proc = run_cli(arr, "--format", "json")
    _assert_fails_closed(proc)
    report = json.loads(proc.stdout)
    assert report["status"] == "failed"
    assert any(f["rule_id"] == "INPUT-0" for f in report["findings"])


@pytest.mark.parametrize("make_bad_file", [
    lambda p: p.write_text("[1, 2, 3]", encoding="utf-8"),
    lambda p: p.write_text('{"not": "valid json"', encoding="utf-8"),
])
def test_bad_input_with_emit_core_artefact_still_writes_a_blocked_schema_valid_artefact(
        tmp_path, make_bad_file):
    bad = tmp_path / "bad.json"
    make_bad_file(bad)
    out = tmp_path / "core.json"
    proc = run_cli(bad, "--emit-core-artefact", out, "--format", "json")
    _assert_fails_closed(proc)
    assert out.exists(), f"no artefact written; stderr={proc.stderr}"
    artefact = json.loads(out.read_text(encoding="utf-8"))
    jsonschema.validate(artefact, ARTEFACT_SCHEMA, format_checker=jsonschema.FormatChecker())
    assert artefact["outcome"]["status"] == "blocked"
    envelope = json.loads(proc.stdout)
    assert envelope["status"] == "failed"


def test_valid_sidecar_is_unaffected_by_the_loader_change(tmp_path):
    clean = (REPO_ROOT / "skills" / "privacy-notice-eu" / "validator" / "fixtures"
             / "must_pass" / "minimal-clean.json")
    proc = run_cli(clean, "--format", "json")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["status"] in {"passed", "passed_with_warnings"}
    assert not any(f["rule_id"] == "INPUT-0" for f in report["findings"])
