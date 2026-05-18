"""Smoke test for the ``python -m whitebox.engine`` CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cli_smoke(tmp_path: Path) -> None:
    out_dir = tmp_path / "engine-out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "whitebox.engine",
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--source",
            "cte-harness",
            "--output",
            str(out_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"CLI failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    xlsx = out_dir / "validation_report.xlsx"
    js = out_dir / "RunResult.json"
    assert xlsx.exists() and xlsx.stat().st_size > 0
    assert js.exists()
    payload = json.loads(js.read_text(encoding="utf-8"))
    assert payload["servicer"] == "MRC"
    assert payload["remit_date"] == "2026-04-30"
    assert payload["source_kind"] == "cte-harness"
    assert len(payload["sheets"]) == 5
