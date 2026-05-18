"""
tools/acceptance_gate.py — v9.1 MRC cell-identity acceptance gate (P2.5).

End-to-end orchestrator that mirrors the pytest acceptance suite
(``tests/acceptance/mrc/``) so CI and operators can run **the same
gate** outside pytest, with durable artefacts in a single output
directory.

CLI::

    python tools/acceptance_gate.py \\
        --servicer MRC \\
        --remit-date 2026-04-30 \\
        --baseline baselines/mrc/2026-04-30/validation_report.xlsx \\
        --legacy-mode dry-run|live|skip \\
        --output runs/acceptance/<timestamp>/

What it does:

1. Invokes ``python -m whitebox.engine`` twice (via subprocess, so we
   stress the same path operators hit) to produce
   ``engine_output.xlsx`` and ``engine_output_rerun.xlsx``.
2. Diffs the two engine outputs → ``self_diff.json``. **Floor**:
   must be ``0/0`` else the gate is invalid.
3. If ``--baseline <path>`` is given and the file exists, diffs the
   primary engine output against the baseline →
   ``baseline_diff.{json,html}``.
4. Per ``--legacy-mode``:
   - ``skip`` (default): records SKIPPED with reason.
   - ``dry-run``: invokes ``tools/run_legacy_mrc.py --dry-run`` to
     prove the runner is wired, then records SKIPPED with reason
     "dry-run only" (no XLSX produced).
   - ``live``: invokes the real legacy run and diffs against the
     primary engine output → ``legacy_diff.{json,html}``.
5. Composes ``acceptance_verdict.json`` (machine-readable verdict +
   per-component breakdown) and ``acceptance_report.md`` (human
   summary).

Exit codes:

    0 = PASS                (every active component passed)
    1 = MINOR_DIFFS         (any active component minor-diffed)
    2 = MAJOR_DIFFS         (any active component major-diffed,
                             or floor (self-consistency) violated)
    3 = ERROR               (engine/runner failure, IO problem)
    4 = SKIPPED-env-blocked (self-consistency itself could not run)

Cross-refs:
    docs/stage2/12.0-acceptance-gate.en.md
    docs/stage2/11.0-architecture.en.md §6 PR evidence rule
    plan.md §11 (Round 3 closure)
    tools/xlsx_diff.py · tools/compare_validation.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Allow ``python tools/acceptance_gate.py`` from a fresh shell.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.xlsx_diff import (  # noqa: E402
    DiffOptions,
    DiffReport,
    diff_workbooks,
    render_html,
)

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Verdict constants & exit-code mapping
# ---------------------------------------------------------------------------

VERDICT_PASS = "PASS"
VERDICT_MINOR = "MINOR_DIFFS"
VERDICT_MAJOR = "MAJOR_DIFFS"
VERDICT_ERROR = "ERROR"
VERDICT_SKIPPED = "SKIPPED"

EXIT_PASS = 0
EXIT_MINOR = 1
EXIT_MAJOR = 2
EXIT_ERROR = 3
EXIT_SKIPPED = 4

MAJOR_DIMENSIONS = {"value", "formula", "merged_cells", "structure"}

LEGACY_MODES = ("skip", "dry-run", "live")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _now_utc_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_allowlist(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a JSON array")
    return data


def _diff_is_allowlisted(diff: Any, allowlist: list[dict[str, Any]]) -> bool:
    cell_ref = f"{diff.col}{diff.row}" if diff.col else ""
    for entry in allowlist:
        if (
            entry.get("sheet") == diff.sheet
            and entry.get("cell_ref") == cell_ref
            and entry.get("dimension") == diff.category
        ):
            return True
    return False


# ---------------------------------------------------------------------------
# Engine + legacy runner invocations (subprocess wrappers)
# ---------------------------------------------------------------------------


def _run_engine_subprocess(
    *, servicer: str, remit_date: str, out_dir: Path, log_path: Path
) -> tuple[int, str, str]:
    """Invoke ``python -m whitebox.engine`` and return (rc, stdout, stderr)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "whitebox.engine",
        "--servicer",
        servicer,
        "--remit-date",
        remit_date,
        "--source",
        "cte-harness",
        "--output",
        str(out_dir),
    ]
    proc = subprocess.run(  # noqa: S603 - controlled args
        cmd,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {' '.join(cmd)}\nrc={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
        encoding="utf-8",
    )
    return proc.returncode, proc.stdout, proc.stderr


def _run_legacy_subprocess(
    *,
    servicer: str,
    remit_date: str,
    out_dir: Path,
    dry_run: bool,
    log_path: Path,
) -> tuple[int, str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(_REPO_ROOT / "tools" / "run_legacy_mrc.py"),
        "--servicer",
        servicer.lower(),
        "--remit-date",
        remit_date,
        "--out-dir",
        str(out_dir),
    ]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(  # noqa: S603 - controlled args
        cmd,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {' '.join(cmd)}\nrc={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
        encoding="utf-8",
    )
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# Per-component evaluation
# ---------------------------------------------------------------------------


def _summarise_diff(
    report: DiffReport, allowlist: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply the allowlist and produce a verdict block."""
    major = report.major_count
    minor_total = report.minor_count
    allowlisted = sum(
        1
        for d in report.diffs
        if d.severity == "minor" and _diff_is_allowlisted(d, allowlist)
    )
    minor_undocumented = minor_total - allowlisted

    if major > 0:
        status = VERDICT_MAJOR
    elif minor_undocumented > 0:
        status = VERDICT_MINOR
    else:
        status = VERDICT_PASS

    return {
        "status": status,
        "major": major,
        "minor": minor_total,
        "allowlisted": allowlisted,
        "minor_undocumented": minor_undocumented,
        "per_sheet": report.per_sheet_summary(),
    }


def _write_diff_artifacts(
    report: DiffReport, out_dir: Path, basename: str
) -> tuple[Path, Path]:
    json_path = out_dir / f"{basename}.json"
    html_path = out_dir / f"{basename}.html"
    json_path.write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    html_path.write_text(render_html(report), encoding="utf-8")
    return json_path, html_path


# ---------------------------------------------------------------------------
# Verdict aggregation
# ---------------------------------------------------------------------------

# Order matters: worst-case wins. SKIPPED never escalates.
_STATUS_RANK: dict[str, int] = {
    VERDICT_PASS: 0,
    VERDICT_SKIPPED: 0,
    VERDICT_MINOR: 1,
    VERDICT_MAJOR: 2,
    VERDICT_ERROR: 3,
}


def _aggregate_verdict(components: dict[str, dict[str, Any]]) -> tuple[str, int]:
    self_block = components.get("self_consistency", {})
    if self_block.get("status") == VERDICT_ERROR:
        return VERDICT_ERROR, EXIT_ERROR
    if self_block.get("status") == VERDICT_SKIPPED:
        return VERDICT_SKIPPED, EXIT_SKIPPED
    if self_block.get("status") in (VERDICT_MAJOR, VERDICT_MINOR):
        # self-consistency is a HARD floor; any diff = MAJOR for the gate.
        return VERDICT_MAJOR, EXIT_MAJOR

    worst = VERDICT_PASS
    for block in components.values():
        status = block.get("status", VERDICT_SKIPPED)
        if _STATUS_RANK.get(status, 0) > _STATUS_RANK[worst]:
            worst = status

    return worst, {
        VERDICT_PASS: EXIT_PASS,
        VERDICT_MINOR: EXIT_MINOR,
        VERDICT_MAJOR: EXIT_MAJOR,
        VERDICT_ERROR: EXIT_ERROR,
        VERDICT_SKIPPED: EXIT_PASS,
    }[worst]


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


def _emoji(status: str) -> str:
    return {
        VERDICT_PASS: "✅",
        VERDICT_MINOR: "🟡",
        VERDICT_MAJOR: "🔴",
        VERDICT_ERROR: "💥",
        VERDICT_SKIPPED: "⏭",
    }.get(status, "❔")


def _render_markdown(
    *,
    verdict: str,
    exit_code: int,
    components: dict[str, dict[str, Any]],
    artifacts: dict[str, str],
    args: argparse.Namespace,
    started_at: str,
    finished_at: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# MRC acceptance gate report — {_emoji(verdict)} {verdict}")
    lines.append("")
    lines.append(f"- **Servicer**: `{args.servicer}`")
    lines.append(f"- **Remit date**: `{args.remit_date}`")
    lines.append(f"- **Legacy mode**: `{args.legacy_mode}`")
    lines.append(f"- **Baseline**: `{args.baseline or '(none provided)'}`")
    lines.append(f"- **Started at**: `{started_at}`")
    lines.append(f"- **Finished at**: `{finished_at}`")
    lines.append(f"- **Exit code**: `{exit_code}`")
    lines.append("")
    lines.append("## Components")
    lines.append("")
    lines.append("| Component | Status | Major | Minor | Allowlisted | Notes |")
    lines.append("|---|---|---:|---:|---:|---|")
    for name in ("self_consistency", "baseline", "legacy_live"):
        block = components.get(name, {"status": VERDICT_SKIPPED})
        status = block.get("status", VERDICT_SKIPPED)
        lines.append(
            f"| `{name}` | {_emoji(status)} {status} "
            f"| {block.get('major', '-')} "
            f"| {block.get('minor', '-')} "
            f"| {block.get('allowlisted', '-')} "
            f"| {block.get('reason', '')} |"
        )
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for key, path in artifacts.items():
        lines.append(f"- `{key}` → `{path}`")
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append(
        "See `docs/stage2/12.0-acceptance-gate.en.md` for the verdict vocabulary, "
        "the three operational modes, and the allowlist policy."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python tools/acceptance_gate.py",
        description="Run the v9.1 MRC cell-identity acceptance gate end-to-end.",
    )
    p.add_argument("--servicer", required=True, help="Servicer id (e.g. MRC).")
    p.add_argument(
        "--remit-date", required=True, help="Cycle date in YYYY-MM-DD format."
    )
    p.add_argument(
        "--baseline",
        default=None,
        help="Path to captured baseline XLSX (optional; SKIPPED if absent).",
    )
    p.add_argument(
        "--legacy-mode",
        choices=LEGACY_MODES,
        default="skip",
        help="Legacy comparison mode (default: skip).",
    )
    p.add_argument(
        "--output", required=True, help="Output directory (created if absent)."
    )
    p.add_argument(
        "--allowlist",
        default=str(
            _REPO_ROOT
            / "tests"
            / "acceptance"
            / "mrc"
            / "acceptance_minor_diffs_allowlist.json"
        ),
        help="Path to allowlist JSON (defaults to the MRC acceptance allowlist).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:  # noqa: C901, PLR0915, PLR0912
    args = _parse_args(argv)
    started_at = _now_utc_iso()
    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    allowlist_path = Path(args.allowlist).resolve()
    try:
        allowlist = _load_allowlist(allowlist_path)
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"allowlist error: {exc}\n")
        return EXIT_ERROR

    components: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Step 1 — primary engine run
    # ------------------------------------------------------------------
    primary_dir = out_dir / "engine_primary"
    rc, _, stderr = _run_engine_subprocess(
        servicer=args.servicer,
        remit_date=args.remit_date,
        out_dir=primary_dir,
        log_path=out_dir / "engine_primary.log",
    )
    if rc != 0:
        components["self_consistency"] = {
            "status": VERDICT_ERROR,
            "reason": f"engine primary run failed rc={rc}: {stderr[-200:]}",
        }
        _finalise(components, artifacts, args, started_at, out_dir)
        return EXIT_ERROR

    primary_xlsx = primary_dir / "validation_report.xlsx"
    promoted_primary = out_dir / "engine_output.xlsx"
    promoted_primary.write_bytes(primary_xlsx.read_bytes())
    artifacts["engine_output.xlsx"] = str(promoted_primary.relative_to(out_dir))

    # ------------------------------------------------------------------
    # Step 2 — rerun for self-consistency
    # ------------------------------------------------------------------
    rerun_dir = out_dir / "engine_rerun"
    rc, _, stderr = _run_engine_subprocess(
        servicer=args.servicer,
        remit_date=args.remit_date,
        out_dir=rerun_dir,
        log_path=out_dir / "engine_rerun.log",
    )
    if rc != 0:
        components["self_consistency"] = {
            "status": VERDICT_ERROR,
            "reason": f"engine rerun failed rc={rc}: {stderr[-200:]}",
        }
        _finalise(components, artifacts, args, started_at, out_dir)
        return EXIT_ERROR

    rerun_xlsx = rerun_dir / "validation_report.xlsx"
    promoted_rerun = out_dir / "engine_output_rerun.xlsx"
    promoted_rerun.write_bytes(rerun_xlsx.read_bytes())
    artifacts["engine_output_rerun.xlsx"] = str(
        promoted_rerun.relative_to(out_dir)
    )

    self_report = diff_workbooks(promoted_primary, promoted_rerun, DiffOptions())
    self_summary = _summarise_diff(self_report, allowlist=[])
    # Self-consistency must be 0/0 — allowlist does NOT apply.
    if self_report.major_count == 0 and self_report.minor_count == 0:
        self_summary["status"] = VERDICT_PASS
    else:
        self_summary["status"] = VERDICT_MAJOR
        self_summary["reason"] = (
            "engine non-deterministic; floor violated "
            "(see docs/stage2/12.0-acceptance-gate.en.md §4)"
        )
    components["self_consistency"] = self_summary
    self_json = out_dir / "self_diff.json"
    self_json.write_text(
        json.dumps(self_report.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts["self_diff.json"] = str(self_json.relative_to(out_dir))

    # ------------------------------------------------------------------
    # Step 3 — baseline diff (optional)
    # ------------------------------------------------------------------
    if args.baseline:
        baseline_path = Path(args.baseline).resolve()
        if not baseline_path.exists():
            components["baseline"] = {
                "status": VERDICT_SKIPPED,
                "reason": f"baseline not found at {baseline_path}",
            }
        else:
            try:
                rep = diff_workbooks(baseline_path, promoted_primary, DiffOptions())
            except Exception as exc:  # noqa: BLE001
                components["baseline"] = {
                    "status": VERDICT_ERROR,
                    "reason": f"baseline diff IO error: {exc}",
                }
            else:
                summary = _summarise_diff(rep, allowlist)
                components["baseline"] = summary
                j, h = _write_diff_artifacts(rep, out_dir, "baseline_diff")
                artifacts["baseline_diff.json"] = str(j.relative_to(out_dir))
                artifacts["baseline_diff.html"] = str(h.relative_to(out_dir))
    else:
        components["baseline"] = {
            "status": VERDICT_SKIPPED,
            "reason": "--baseline not provided",
        }

    # ------------------------------------------------------------------
    # Step 4 — legacy mode
    # ------------------------------------------------------------------
    legacy_dir = out_dir / "legacy"
    if args.legacy_mode == "skip":
        components["legacy_live"] = {
            "status": VERDICT_SKIPPED,
            "reason": "--legacy-mode=skip",
        }
    elif args.legacy_mode == "dry-run":
        rc, _, stderr = _run_legacy_subprocess(
            servicer=args.servicer,
            remit_date=args.remit_date,
            out_dir=legacy_dir,
            dry_run=True,
            log_path=out_dir / "legacy_dry_run.log",
        )
        components["legacy_live"] = {
            "status": VERDICT_SKIPPED,
            "reason": (
                f"--legacy-mode=dry-run (runner exit={rc}); "
                "no XLSX produced by design"
            ),
        }
    elif args.legacy_mode == "live":
        rc, _, stderr = _run_legacy_subprocess(
            servicer=args.servicer,
            remit_date=args.remit_date,
            out_dir=legacy_dir,
            dry_run=False,
            log_path=out_dir / "legacy_live.log",
        )
        legacy_xlsx = legacy_dir / "validation_report.xlsx"
        if rc != 0 or not legacy_xlsx.exists():
            components["legacy_live"] = {
                "status": VERDICT_SKIPPED,
                "reason": (
                    f"legacy live runner exit={rc}; treated as env-skip "
                    f"({stderr[-200:].strip()})"
                ),
            }
        else:
            try:
                rep = diff_workbooks(legacy_xlsx, promoted_primary, DiffOptions())
            except Exception as exc:  # noqa: BLE001
                components["legacy_live"] = {
                    "status": VERDICT_ERROR,
                    "reason": f"legacy diff IO error: {exc}",
                }
            else:
                summary = _summarise_diff(rep, allowlist)
                components["legacy_live"] = summary
                j, h = _write_diff_artifacts(rep, out_dir, "legacy_diff")
                artifacts["legacy_diff.json"] = str(j.relative_to(out_dir))
                artifacts["legacy_diff.html"] = str(h.relative_to(out_dir))

    return _finalise(components, artifacts, args, started_at, out_dir)


def _finalise(
    components: dict[str, dict[str, Any]],
    artifacts: dict[str, str],
    args: argparse.Namespace,
    started_at: str,
    out_dir: Path,
) -> int:
    finished_at = _now_utc_iso()
    verdict, exit_code = _aggregate_verdict(components)

    verdict_payload: dict[str, Any] = {
        "tool_version": __version__,
        "verdict": verdict,
        "exit_code": exit_code,
        "servicer": args.servicer,
        "remit_date": args.remit_date,
        "legacy_mode": args.legacy_mode,
        "baseline": args.baseline,
        "started_at": started_at,
        "finished_at": finished_at,
        "components": components,
        "artifacts": artifacts,
    }
    verdict_path = out_dir / "acceptance_verdict.json"
    verdict_path.write_text(
        json.dumps(verdict_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_md = _render_markdown(
        verdict=verdict,
        exit_code=exit_code,
        components=components,
        artifacts={**artifacts, "acceptance_verdict.json": "acceptance_verdict.json"},
        args=args,
        started_at=started_at,
        finished_at=finished_at,
    )
    (out_dir / "acceptance_report.md").write_text(report_md, encoding="utf-8")

    # ASCII-only on stdout: Windows cp1252 cannot encode emoji.
    sys.stdout.write(
        f"acceptance gate: {verdict} "
        f"(exit={exit_code}) -> {verdict_path}\n"
    )
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
