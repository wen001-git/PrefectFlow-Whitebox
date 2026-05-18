"""
tools/compare_validation.py — Round 2 C4 Comparison Orchestrator
=================================================================

Orchestrates the full legacy-vs-new XLSX comparison pipeline.

Python API::

    from tools.compare_validation import orchestrate, build_verdict

CLI — Mode A (manual paths)::

    python tools/compare_validation.py compare \\
        --legacy-xlsx <path> --new-xlsx <path> \\
        --report-dir <dir> \\
        [--legacy-metadata <path>] [--new-metadata <path>] \\
        [--float-tolerance 0.0] \\
        [--ignore-style] [--ignore-format] [--ignore-row-heights] \\
        [--summary-only] [--quiet]

CLI — Mode B (auto, invokes C2 + C3 + C1)::

    python tools/compare_validation.py auto \\
        --servicer mrc --remit-date 2026-04-30 \\
        [--source-repo ../PrefectFlow] \\
        [--new-mode pristine|perturbed|empty] \\
        [--skip-legacy] [--legacy-xlsx <path>] \\
        [--skip-new]    [--new-xlsx <path>] \\
        [--dry-run] \\
        --report-dir <dir> \\
        [--quiet]

Exit codes::

    0 = identical
    1 = minor diffs only
    2 = major diffs
    3 = I/O / run error

Cross-refs:
    plan.md § 9 · plan.md § 9.3 row C4
    docs/stage2/10.0-validation-strategy.{zh,en}.md
    AGENTS.md § 6.11
    tools/docs/compare_validation.md
"""
from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click

# ---------------------------------------------------------------------------
# Make tools/ importable regardless of how the script is invoked
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from xlsx_diff import (  # type: ignore[import]  # noqa: E402
    DiffOptions,
    DiffReport,
    diff_workbooks,
    exit_code_for,
    render_html,
)

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Verdict constants
# ---------------------------------------------------------------------------
VERDICT_PASS = "PASS"
VERDICT_MINOR = "MINOR_DIFFS"
VERDICT_MAJOR = "MAJOR_DIFFS"
VERDICT_ERROR = "ERROR"

_EXIT_TO_VERDICT = {0: VERDICT_PASS, 1: VERDICT_MINOR, 2: VERDICT_MAJOR, 3: VERDICT_ERROR}
_VERDICT_TO_EMOJI = {
    VERDICT_PASS: "✅ PASS",
    VERDICT_MINOR: "🟡 MINOR_DIFFS",
    VERDICT_MAJOR: "🔴 MAJOR_DIFFS",
    VERDICT_ERROR: "💥 ERROR",
}

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def _configure_logging(log_path: Path, quiet: bool) -> logging.Logger:
    """Set up a logger that writes to file and (if not quiet) stdout."""
    logger = logging.getLogger("compare_validation")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

    fh = logging.FileHandler(str(log_path), encoding="utf-8", mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    if not quiet:
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    return logger


# ---------------------------------------------------------------------------
# SHA-256 helper
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Metadata loading
# ---------------------------------------------------------------------------

def _load_metadata(meta_path: Path | None) -> dict[str, Any]:
    """Load run_metadata.json sidecar; return {} if unavailable."""
    if meta_path is None or not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Warning detection
# ---------------------------------------------------------------------------

def _build_warnings(
    legacy_meta: dict[str, Any],
    new_meta: dict[str, Any],
    report: DiffReport | None,
    new_mode: str | None,
    ignore_style: bool,
) -> list[str]:
    warnings: list[str] = []

    # Dirty legacy repo
    if legacy_meta.get("source_repo_dirty") is True:
        warnings.append(
            "legacy repo had uncommitted changes; result may not be reproducible"
        )

    # Time gap > 1 hour
    leg_started = legacy_meta.get("started_at") or legacy_meta.get("run", {}).get("started_at")
    new_started = new_meta.get("started_at") or new_meta.get("run", {}).get("started_at")
    if leg_started and new_started:
        try:
            from datetime import datetime as _dt
            leg_ts = _dt.fromisoformat(leg_started.rstrip("Z"))
            new_ts = _dt.fromisoformat(new_started.rstrip("Z"))
            gap = abs((new_ts - leg_ts).total_seconds())
            if gap > 3600:
                warnings.append(
                    f"Redshift may have drifted between runs "
                    f"(gap = {int(gap // 60)} min between legacy and new run)"
                )
        except Exception:
            pass

    if report is not None:
        # pristine + no major diffs → self-test note
        if new_mode == "pristine" and report.major_count == 0:
            warnings.append("harness self-test passed (pristine mode, no major diffs)")

        # perturbed → check all 4 perturbation categories
        if new_mode == "perturbed":
            expected_ids = {"value_diff", "font_diff", "missing_row", "extra_sheet"}
            pert_meta = new_meta.get("perturbations", [])
            if isinstance(pert_meta, list):
                found_ids = {p.get("id") for p in pert_meta if isinstance(p, dict)}
                missing = expected_ids - found_ids
                if missing:
                    warnings.append(
                        f"harness may have missed expected perturbations: {sorted(missing)}"
                    )
            # Detect via diff categories too
            detected_cats = {d.category for d in report.diffs}
            cat_map = {"value": "value_diff", "structure": "extra_sheet / missing_row"}
            missing_cat_hints = []
            if "value" not in detected_cats:
                missing_cat_hints.append("value")
            if "structure" not in detected_cats:
                missing_cat_hints.append("structure")
            if missing_cat_hints:
                warnings.append(
                    f"diff report missing expected categories: {missing_cat_hints}; "
                    "check --ignore-style / --ignore-format flags"
                )

    if ignore_style:
        warnings.append(
            "--ignore-style was used; font/fill/border/alignment diffs are suppressed"
        )

    return warnings


# ---------------------------------------------------------------------------
# Next-steps hints
# ---------------------------------------------------------------------------

def _build_next_steps(
    verdict: str,
    report: DiffReport | None,
    ignore_style: bool,
) -> list[str]:
    steps: list[str] = []

    if verdict == VERDICT_PASS:
        steps.append("Cell-identity confirmed. Safe to ship.")
    elif verdict == VERDICT_MINOR:
        steps.append(
            "Review HTML report; minor style diffs may be acceptable depending on "
            "ch 1.6 § baseline contract clauses."
        )
        if ignore_style:
            steps.append(
                "--ignore-style was used; rerun without it to see full style diff picture."
            )
    elif verdict == VERDICT_MAJOR:
        if report is not None:
            cats = {d.category for d in report.diffs if d.severity == "major"}
            if "value" in cats or "formula" in cats:
                steps.append(
                    "Investigate engine/transform; cite ch 1.4 / 1.5 for expected behavior."
                )
            if "structure" in cats:
                steps.append(
                    "Sheet missing/extra → check sheet renderer registration."
                )
            if not cats:
                steps.append(
                    "Investigate engine/transform; cite ch 1.4 / 1.5 for expected behavior."
                )
        else:
            steps.append(
                "Investigate engine/transform; cite ch 1.4 / 1.5 for expected behavior."
            )
    elif verdict == VERDICT_ERROR:
        steps.append(
            "Read comparison_report.log; verify creds and source-repo path."
        )

    return steps


# ---------------------------------------------------------------------------
# Verdict builder
# ---------------------------------------------------------------------------

def build_verdict(
    *,
    report: DiffReport | None,
    exit_code: int,
    servicer: str | None,
    remit_date: str | None,
    legacy_meta: dict[str, Any],
    new_meta: dict[str, Any],
    new_mode: str | None,
    ignore_style: bool = False,
    error_message: str | None = None,
) -> dict[str, Any]:
    """Assemble the top-level verdict.json payload."""
    now = datetime.now(timezone.utc).isoformat()
    verdict_str = _EXIT_TO_VERDICT.get(exit_code, VERDICT_ERROR)

    # Legacy run block
    leg_out = legacy_meta.get("output", {})
    leg_run: dict[str, Any] = {
        "path": leg_out.get("xlsx_path", legacy_meta.get("xlsx_path")),
        "sha256": leg_out.get("sha256", legacy_meta.get("sha256")),
        "source_repo_sha": legacy_meta.get("source_repo_sha"),
        "started_at": legacy_meta.get("started_at"),
    }

    # New run block
    new_out = new_meta.get("output", {})
    new_run: dict[str, Any] = {
        "path": new_out.get("xlsx_path", new_meta.get("xlsx_path")),
        "sha256": new_out.get("sha256", new_meta.get("sha256")),
        "mode": new_meta.get("mode", new_mode),
        "started_at": new_meta.get("started_at"),
    }

    # Summary from diff report
    if report is not None:
        summary: dict[str, Any] = {
            "identical": report.identical,
            "major_diff_count": report.major_count,
            "minor_diff_count": report.minor_count,
            "per_sheet": report.per_sheet_summary(),
        }
    else:
        summary = {
            "identical": False,
            "major_diff_count": -1,
            "minor_diff_count": -1,
            "per_sheet": [],
        }

    warnings = _build_warnings(legacy_meta, new_meta, report, new_mode, ignore_style)
    next_steps = _build_next_steps(verdict_str, report, ignore_style)
    if error_message:
        warnings.insert(0, f"run error: {error_message}")

    v: dict[str, Any] = {
        "exit_code": exit_code,
        "generated_at": now,
        "legacy_run": leg_run,
        "new_run": new_run,
        "next_steps": next_steps,
        "remit_date": remit_date,
        "servicer": servicer,
        "summary": summary,
        "tool_version": __version__,
        "verdict": verdict_str,
        "warnings": warnings,
    }
    return v


# ---------------------------------------------------------------------------
# Core orchestrate function (importable)
# ---------------------------------------------------------------------------

def orchestrate(
    *,
    legacy_xlsx: Path,
    new_xlsx: Path,
    report_dir: Path,
    legacy_metadata: Path | None = None,
    new_metadata: Path | None = None,
    float_tolerance: float = 0.0,
    ignore_style: bool = False,
    ignore_format: bool = False,
    ignore_row_heights: bool = False,
    summary_only: bool = False,
    servicer: str | None = None,
    remit_date: str | None = None,
    new_mode: str | None = None,
    quiet: bool = False,
) -> int:
    """
    Run the comparison between two XLSX files, write all output artifacts to
    ``report_dir``, and return an exit code (0–3).

    This is the shared implementation used by both the ``compare`` and ``auto``
    subcommands (after auto has resolved XLSX paths).
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    log_path = report_dir / "comparison_report.log"
    log = _configure_logging(log_path, quiet)

    log.info("compare_validation.py v%s", __version__)
    log.info("legacy XLSX : %s", legacy_xlsx)
    log.info("new XLSX    : %s", new_xlsx)
    log.info("report dir  : %s", report_dir)

    # Validate inputs
    if not legacy_xlsx.exists():
        log.error("Legacy XLSX not found: %s", legacy_xlsx)
        _write_error_verdict(report_dir, 3, servicer, remit_date, new_mode, {}, {},
                             f"legacy XLSX not found: {legacy_xlsx}")
        return 3
    if not new_xlsx.exists():
        log.error("New XLSX not found: %s", new_xlsx)
        _write_error_verdict(report_dir, 3, servicer, remit_date, new_mode, {}, {},
                             f"new XLSX not found: {new_xlsx}")
        return 3

    legacy_meta = _load_metadata(legacy_metadata)
    new_meta = _load_metadata(new_metadata)

    # Run diff (C1)
    opts = DiffOptions(
        float_tolerance=float_tolerance,
        ignore_style=ignore_style,
        ignore_format=ignore_format,
        ignore_row_heights=ignore_row_heights,
        summary_only=summary_only,
    )
    log.info(
        "running diff: float_tol=%.6g ignore_style=%s ignore_format=%s ignore_row_heights=%s",
        float_tolerance, ignore_style, ignore_format, ignore_row_heights,
    )

    try:
        report: DiffReport = diff_workbooks(legacy_xlsx, new_xlsx, opts)
    except Exception as exc:  # noqa: BLE001
        log.error("diff_workbooks failed: %s", exc)
        _write_error_verdict(
            report_dir, 3, servicer, remit_date, new_mode, legacy_meta, new_meta,
            f"diff_workbooks failed: {exc}",
        )
        return 3

    diff_exit = exit_code_for(report)
    log.info(
        "diff complete: major=%d minor=%d identical=%s exit=%d",
        report.major_count, report.minor_count, report.identical, diff_exit,
    )

    # Enrich HTML with metadata context at the top
    html_body = render_html(report)
    html_body = _prepend_metadata_banner(html_body, legacy_meta, new_meta, servicer, remit_date)
    html_out = report_dir / "comparison_report.html"
    html_out.write_text(html_body, encoding="utf-8")
    log.info("HTML report : %s", html_out)

    # Enriched JSON (C1 report + embedded run metadata)
    report_dict = report.to_dict()
    report_dict["legacy_run"] = legacy_meta
    report_dict["new_run"] = new_meta
    json_out = report_dir / "comparison_report.json"
    json_out.write_text(json.dumps(report_dict, indent=2, sort_keys=True), encoding="utf-8")
    log.info("JSON report : %s", json_out)

    # Verdict
    verdict = build_verdict(
        report=report,
        exit_code=diff_exit,
        servicer=servicer,
        remit_date=remit_date,
        legacy_meta=legacy_meta,
        new_meta=new_meta,
        new_mode=new_mode,
        ignore_style=ignore_style,
    )
    verdict_out = report_dir / "verdict.json"
    verdict_out.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
    log.info("verdict     : %s", verdict_out)

    # One-line summary to stdout (safe encoding for Windows cp1252 terminals)
    verdict_str = verdict["verdict"]
    major = report.major_count
    minor = report.minor_count
    emoji_line = _VERDICT_TO_EMOJI.get(verdict_str, verdict_str)
    if verdict_str in (VERDICT_MINOR, VERDICT_MAJOR):
        emoji_line += f" (major={major}, minor={minor})"
    try:
        print(emoji_line)
    except UnicodeEncodeError:
        print(emoji_line.encode(sys.stdout.encoding or "ascii", errors="replace").decode(
            sys.stdout.encoding or "ascii"
        ))

    if verdict["warnings"]:
        for w in verdict["warnings"]:
            log.warning("WARN: %s", w)

    return diff_exit


def _prepend_metadata_banner(
    html: str,
    legacy_meta: dict[str, Any],
    new_meta: dict[str, Any],
    servicer: str | None,
    remit_date: str | None,
) -> str:
    """Insert a run-context banner at the top of the C1 HTML body."""
    rows = []
    if servicer:
        rows.append(f"<tr><th>Servicer</th><td>{servicer}</td></tr>")
    if remit_date:
        rows.append(f"<tr><th>Remit date</th><td>{remit_date}</td></tr>")
    if legacy_meta.get("started_at"):
        rows.append(f"<tr><th>Legacy run started</th><td>{legacy_meta['started_at']}</td></tr>")
    if new_meta.get("started_at"):
        rows.append(f"<tr><th>New run started</th><td>{new_meta['started_at']}</td></tr>")
    mode = new_meta.get("mode")
    if mode:
        rows.append(f"<tr><th>New-system mode</th><td>{mode}</td></tr>")
    if legacy_meta.get("source_repo_sha"):
        rows.append(
            f"<tr><th>Legacy source SHA</th><td><code>{legacy_meta['source_repo_sha']}</code></td></tr>"
        )

    if not rows:
        return html

    banner = (
        "<div style='background:#f0f6ff;border:1px solid #c8daed;padding:.8em 1em;"
        "border-radius:4px;margin-bottom:1.5em'>"
        "<strong>Run context</strong>"
        "<table style='border-collapse:collapse;margin-top:.5em'>"
        + "".join(rows)
        + "</table></div>"
    )
    return html.replace("<h1>xlsx_diff Report</h1>", "<h1>xlsx_diff Report</h1>\n" + banner, 1)


def _write_error_verdict(
    report_dir: Path,
    exit_code: int,
    servicer: str | None,
    remit_date: str | None,
    new_mode: str | None,
    legacy_meta: dict[str, Any],
    new_meta: dict[str, Any],
    error_message: str,
) -> None:
    """Write a minimal verdict.json when an error prevents the full diff."""
    report_dir.mkdir(parents=True, exist_ok=True)
    verdict = build_verdict(
        report=None,
        exit_code=exit_code,
        servicer=servicer,
        remit_date=remit_date,
        legacy_meta=legacy_meta,
        new_meta=new_meta,
        new_mode=new_mode,
        error_message=error_message,
    )
    (report_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Auto-mode helpers: subprocess invocation of C2/C3
# ---------------------------------------------------------------------------

def _invoke_c2_legacy(
    *,
    servicer: str,
    remit_date: str,
    out_dir: Path,
    source_repo: Path | None,
    dry_run: bool,
    log: logging.Logger,
) -> tuple[Path, Path | None]:
    """Invoke run_legacy_mrc.py via subprocess. Returns (xlsx_path, meta_path)."""
    c2 = _TOOLS_DIR / "run_legacy_mrc.py"
    cmd: list[str] = [
        sys.executable, str(c2),
        "--servicer", servicer,
        "--remit-date", remit_date,
        "--out-dir", str(out_dir),
    ]
    if source_repo:
        cmd += ["--source-repo", str(source_repo)]
    if dry_run:
        cmd += ["--dry-run"]

    log.info("C2 cmd: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    log.info("C2 stdout: %s", result.stdout.strip())
    if result.stderr.strip():
        log.warning("C2 stderr: %s", result.stderr.strip())
    if result.returncode != 0:
        raise RuntimeError(f"run_legacy_mrc.py exited {result.returncode}: {result.stderr}")

    xlsx = out_dir / "validation_report.xlsx"
    meta = out_dir / "run_metadata.json"
    return xlsx, meta if meta.exists() else None


def _invoke_c3_new(
    *,
    servicer: str,
    remit_date: str,
    out_dir: Path,
    mode: str,
    dry_run: bool,
    log: logging.Logger,
) -> tuple[Path, Path | None]:
    """Invoke run_newsystem_mrc.py via subprocess. Returns (xlsx_path, meta_path)."""
    c3 = _TOOLS_DIR / "run_newsystem_mrc.py"
    cmd: list[str] = [
        sys.executable, str(c3),
        "--servicer", servicer,
        "--remit-date", remit_date,
        "--out-dir", str(out_dir),
        "--mode", mode,
    ]
    log.info("C3 cmd: %s", " ".join(cmd))
    if dry_run:
        # dry-run: don't actually run
        return out_dir / "validation_report.xlsx", None

    result = subprocess.run(cmd, capture_output=True, text=True)
    log.info("C3 stdout: %s", result.stdout.strip())
    if result.stderr.strip():
        log.warning("C3 stderr: %s", result.stderr.strip())
    if result.returncode != 0:
        raise RuntimeError(f"run_newsystem_mrc.py exited {result.returncode}: {result.stderr}")

    xlsx = out_dir / "validation_report.xlsx"
    meta = out_dir / "run_metadata.json"
    return xlsx, meta if meta.exists() else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
def cli() -> None:
    """compare_validation.py — Round 2 C4 comparison orchestrator.

    Produces verdict.json + HTML + JSON reports comparing legacy vs new-system
    MRC validation reports.
    """


# ── compare subcommand ─────────────────────────────────────────────────────

@cli.command("compare")
@click.option(
    "--legacy-xlsx", "legacy_xlsx",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path to legacy validation_report.xlsx.",
)
@click.option(
    "--new-xlsx", "new_xlsx",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path to new-system validation_report.xlsx.",
)
@click.option(
    "--legacy-metadata", "legacy_metadata",
    type=click.Path(dir_okay=False, path_type=Path), default=None,
    help="Path to legacy run_metadata.json sidecar.",
)
@click.option(
    "--new-metadata", "new_metadata",
    type=click.Path(dir_okay=False, path_type=Path), default=None,
    help="Path to new-system run_metadata.json sidecar.",
)
@click.option("--report-dir", "report_dir", required=True,
              type=click.Path(path_type=Path), help="Output directory for reports.")
@click.option("--float-tolerance", "float_tolerance", type=float, default=0.0, show_default=True,
              help="Tolerance for float comparisons.")
@click.option("--ignore-style", "ignore_style", is_flag=True, default=False,
              help="Suppress font/fill/border/alignment diffs.")
@click.option("--ignore-format", "ignore_format", is_flag=True, default=False,
              help="Suppress number-format diffs.")
@click.option("--ignore-row-heights", "ignore_row_heights", is_flag=True, default=False,
              help="Suppress row-height diffs.")
@click.option("--summary-only", "summary_only", is_flag=True, default=False,
              help="Omit per-cell diff details from JSON/HTML.")
@click.option("--servicer", "servicer", default=None, help="Servicer code (for verdict context).")
@click.option("--remit-date", "remit_date", default=None, help="Remit date (for verdict context).")
@click.option("--new-mode", "new_mode", default=None,
              help="New-system mode (pristine/perturbed/empty) for warning logic.")
@click.option("--quiet", "quiet", is_flag=True, default=False, help="Suppress stdout logging.")
def compare_cmd(
    legacy_xlsx: Path,
    new_xlsx: Path,
    legacy_metadata: Path | None,
    new_metadata: Path | None,
    report_dir: Path,
    float_tolerance: float,
    ignore_style: bool,
    ignore_format: bool,
    ignore_row_heights: bool,
    summary_only: bool,
    servicer: str | None,
    remit_date: str | None,
    new_mode: str | None,
    quiet: bool,
) -> None:
    """Compare two XLSX files directly (Mode A — manual paths)."""
    rc = orchestrate(
        legacy_xlsx=legacy_xlsx,
        new_xlsx=new_xlsx,
        report_dir=report_dir,
        legacy_metadata=legacy_metadata,
        new_metadata=new_metadata,
        float_tolerance=float_tolerance,
        ignore_style=ignore_style,
        ignore_format=ignore_format,
        ignore_row_heights=ignore_row_heights,
        summary_only=summary_only,
        servicer=servicer,
        remit_date=remit_date,
        new_mode=new_mode,
        quiet=quiet,
    )
    sys.exit(rc)


# ── auto subcommand ────────────────────────────────────────────────────────

@cli.command("auto")
@click.option("--servicer", "servicer", required=True, help="Servicer code (e.g. mrc).")
@click.option("--remit-date", "remit_date", required=True, help="Remit date (YYYY-MM-DD).")
@click.option("--source-repo", "source_repo", type=click.Path(path_type=Path), default=None,
              help="Path to source PrefectFlow repo (for C2).")
@click.option("--new-mode", "new_mode",
              type=click.Choice(["pristine", "perturbed", "empty"]), default="pristine",
              show_default=True, help="New-system stub mode.")
@click.option("--skip-legacy", "skip_legacy", is_flag=True, default=False,
              help="Reuse existing --legacy-xlsx instead of invoking C2.")
@click.option("--legacy-xlsx", "legacy_xlsx",
              type=click.Path(dir_okay=False, path_type=Path), default=None,
              help="Existing legacy XLSX (used with --skip-legacy).")
@click.option("--skip-new", "skip_new", is_flag=True, default=False,
              help="Reuse existing --new-xlsx instead of invoking C3.")
@click.option("--new-xlsx", "new_xlsx",
              type=click.Path(dir_okay=False, path_type=Path), default=None,
              help="Existing new-system XLSX (used with --skip-new).")
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="Print orchestration plan; do not invoke C2/C3.")
@click.option("--report-dir", "report_dir", required=True,
              type=click.Path(path_type=Path), help="Output directory for reports.")
@click.option("--float-tolerance", "float_tolerance", type=float, default=0.0, show_default=True)
@click.option("--ignore-style", "ignore_style", is_flag=True, default=False)
@click.option("--ignore-format", "ignore_format", is_flag=True, default=False)
@click.option("--ignore-row-heights", "ignore_row_heights", is_flag=True, default=False)
@click.option("--summary-only", "summary_only", is_flag=True, default=False)
@click.option("--quiet", "quiet", is_flag=True, default=False, help="Suppress stdout logging.")
def auto_cmd(  # noqa: C901
    servicer: str,
    remit_date: str,
    source_repo: Path | None,
    new_mode: str,
    skip_legacy: bool,
    legacy_xlsx: Path | None,
    skip_new: bool,
    new_xlsx: Path | None,
    dry_run: bool,
    report_dir: Path,
    float_tolerance: float,
    ignore_style: bool,
    ignore_format: bool,
    ignore_row_heights: bool,
    summary_only: bool,
    quiet: bool,
) -> None:
    """Full auto mode: invoke C2 + C3 then compare (Mode B)."""
    report_dir = Path(report_dir)
    legacy_out_dir = report_dir / "legacy"
    new_out_dir = report_dir / "newsystem"

    # Dry-run: print plan and exit
    if dry_run:
        _print_dry_run_plan(
            servicer=servicer,
            remit_date=remit_date,
            source_repo=source_repo,
            new_mode=new_mode,
            skip_legacy=skip_legacy,
            legacy_xlsx=legacy_xlsx,
            skip_new=skip_new,
            new_xlsx=new_xlsx,
            report_dir=report_dir,
            legacy_out_dir=legacy_out_dir,
            new_out_dir=new_out_dir,
            float_tolerance=float_tolerance,
            ignore_style=ignore_style,
            ignore_format=ignore_format,
            ignore_row_heights=ignore_row_heights,
        )
        sys.exit(0)

    # Validate skip-legacy / skip-new constraints
    if skip_legacy and legacy_xlsx is None:
        click.echo("ERROR: --skip-legacy requires --legacy-xlsx", err=True)
        sys.exit(3)
    if skip_new and new_xlsx is None:
        click.echo("ERROR: --skip-new requires --new-xlsx", err=True)
        sys.exit(3)

    report_dir.mkdir(parents=True, exist_ok=True)
    log_path = report_dir / "comparison_report.log"
    log = _configure_logging(log_path, quiet)

    log.info("=== auto mode start ===")
    log.info("servicer=%s remit_date=%s new_mode=%s", servicer, remit_date, new_mode)

    resolved_legacy_xlsx: Path
    resolved_new_xlsx: Path
    legacy_metadata_path: Path | None = None
    new_metadata_path: Path | None = None

    # --- Step 1: resolve legacy XLSX ---
    if skip_legacy and legacy_xlsx is not None:
        resolved_legacy_xlsx = Path(legacy_xlsx)
        # look for sidecar next to the provided XLSX
        sidecar = resolved_legacy_xlsx.parent / "run_metadata.json"
        if sidecar.exists():
            legacy_metadata_path = sidecar
        log.info("skip-legacy: reusing %s", resolved_legacy_xlsx)
    else:
        log.info("invoking C2 → %s", legacy_out_dir)
        try:
            resolved_legacy_xlsx, legacy_metadata_path = _invoke_c2_legacy(
                servicer=servicer,
                remit_date=remit_date,
                out_dir=legacy_out_dir,
                source_repo=source_repo,
                dry_run=False,
                log=log,
            )
        except RuntimeError as exc:
            log.error("C2 failed: %s", exc)
            _write_error_verdict(
                report_dir, 3, servicer, remit_date, new_mode, {}, {}, str(exc)
            )
            print("💥 ERROR")
            sys.exit(3)

    # --- Step 2: resolve new XLSX ---
    if skip_new and new_xlsx is not None:
        resolved_new_xlsx = Path(new_xlsx)
        sidecar = resolved_new_xlsx.parent / "run_metadata.json"
        if sidecar.exists():
            new_metadata_path = sidecar
        log.info("skip-new: reusing %s", resolved_new_xlsx)
    else:
        log.info("invoking C3 (mode=%s) → %s", new_mode, new_out_dir)
        try:
            resolved_new_xlsx, new_metadata_path = _invoke_c3_new(
                servicer=servicer,
                remit_date=remit_date,
                out_dir=new_out_dir,
                mode=new_mode,
                dry_run=False,
                log=log,
            )
        except RuntimeError as exc:
            log.error("C3 failed: %s", exc)
            _write_error_verdict(
                report_dir, 3, servicer, remit_date, new_mode, {}, {}, str(exc)
            )
            print("💥 ERROR")
            sys.exit(3)

    # --- Step 3: compare ---
    rc = orchestrate(
        legacy_xlsx=resolved_legacy_xlsx,
        new_xlsx=resolved_new_xlsx,
        report_dir=report_dir,
        legacy_metadata=legacy_metadata_path,
        new_metadata=new_metadata_path,
        float_tolerance=float_tolerance,
        ignore_style=ignore_style,
        ignore_format=ignore_format,
        ignore_row_heights=ignore_row_heights,
        summary_only=summary_only,
        servicer=servicer,
        remit_date=remit_date,
        new_mode=new_mode,
        quiet=quiet,
    )
    sys.exit(rc)


def _print_dry_run_plan(
    *,
    servicer: str,
    remit_date: str,
    source_repo: Path | None,
    new_mode: str,
    skip_legacy: bool,
    legacy_xlsx: Path | None,
    skip_new: bool,
    new_xlsx: Path | None,
    report_dir: Path,
    legacy_out_dir: Path,
    new_out_dir: Path,
    float_tolerance: float,
    ignore_style: bool,
    ignore_format: bool,
    ignore_row_heights: bool,
) -> None:
    """Print orchestration plan for dry-run mode."""
    click.echo("=== compare_validation DRY-RUN PLAN ===")
    click.echo(f"  servicer      : {servicer}")
    click.echo(f"  remit_date    : {remit_date}")
    click.echo(f"  report_dir    : {report_dir}")
    click.echo("")
    click.echo("Step 1 — legacy XLSX")
    if skip_legacy and legacy_xlsx:
        click.echo(f"  [SKIP] reuse existing: {legacy_xlsx}")
    else:
        c2 = _TOOLS_DIR / "run_legacy_mrc.py"
        cmd = [sys.executable, str(c2),
               "--servicer", servicer, "--remit-date", remit_date,
               "--out-dir", str(legacy_out_dir)]
        if source_repo:
            cmd += ["--source-repo", str(source_repo)]
        click.echo(f"  [RUN C2] {' '.join(str(x) for x in cmd)}")
        click.echo(f"  output XLSX  : {legacy_out_dir / 'validation_report.xlsx'}")
        click.echo(f"  output meta  : {legacy_out_dir / 'run_metadata.json'}")
    click.echo("")
    click.echo("Step 2 — new-system XLSX")
    if skip_new and new_xlsx:
        click.echo(f"  [SKIP] reuse existing: {new_xlsx}")
    else:
        c3 = _TOOLS_DIR / "run_newsystem_mrc.py"
        cmd3 = [sys.executable, str(c3),
                "--servicer", servicer, "--remit-date", remit_date,
                "--out-dir", str(new_out_dir), "--mode", new_mode]
        click.echo(f"  [RUN C3] {' '.join(str(x) for x in cmd3)}")
        click.echo(f"  output XLSX  : {new_out_dir / 'validation_report.xlsx'}")
        click.echo(f"  output meta  : {new_out_dir / 'run_metadata.json'}")
    click.echo("")
    click.echo("Step 3 — diff (C1 import)")
    click.echo(f"  float_tolerance   = {float_tolerance}")
    click.echo(f"  ignore_style      = {ignore_style}")
    click.echo(f"  ignore_format     = {ignore_format}")
    click.echo(f"  ignore_row_heights= {ignore_row_heights}")
    click.echo("")
    click.echo("Outputs (inside report_dir):")
    click.echo(f"  {report_dir / 'comparison_report.html'}")
    click.echo(f"  {report_dir / 'comparison_report.json'}")
    click.echo(f"  {report_dir / 'verdict.json'}")
    click.echo(f"  {report_dir / 'comparison_report.log'}")
    click.echo("")
    click.echo("Plan is coherent. Exit 0 (dry-run).")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
