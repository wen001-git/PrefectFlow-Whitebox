#!/usr/bin/env python3
"""
tools/run_legacy_mrc.py — Operator-invoked legacy MRC validation runner.

Loads Vault credentials from .env, invokes the legacy remit_validation_check
flow against live Redshift, captures the output XLSX, and writes a JSON sidecar
with run metadata.

Usage:
    python tools/run_legacy_mrc.py \\
        --servicer mrc \\
        --remit-date 2026-04-30 \\
        --out-dir runs/legacy/<timestamp>/ \\
        [--source-repo ../PrefectFlow] \\
        [--dry-run]

Exit codes:
    0 = success, XLSX produced
    1 = legacy run failed
    2 = creds/env problem
    3 = source repo not found or entrypoint missing
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

TOOL_VERSION = "1.0.0"

DEFAULT_SOURCE_REPO = Path(__file__).parent.parent / ".." / "PrefectFlow"
DEFAULT_VAULT_REDSHIFT_PATH = "prefect-secret/db/redshift"

# Relative path from source repo root to the top-level flow entrypoint.
# Discovered by reading PrefectFlow/flow/remit_validation/remit_validation.py:
#   - @flow(name="remit_validation_check") at line 66
#   - accepts: remit_date: datetime.date, email: bool, to_new_redshift: bool, to_mysql: bool
MRC_ENTRYPOINT_RELPATH = "flow/remit_validation/remit_validation.py"
MRC_FUNCTION_NAME = "remit_validation_check"

# MRC-specific task keys populated in VALIDATION_TABLE_MAP by the flow
_MRC_DATASET_KEYS = [
    "mrc_summary_check",
    "mrc_general_check",
    "mrc_adv_check",
    "mrc_service_fee_check",
    "mrc_adv_info",
]

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Pure helpers (no side-effects; importable without legacy deps installed)
# ──────────────────────────────────────────────────────────────────────────────


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha(repo: Path) -> tuple[str, bool]:
    """Return (sha, dirty) for the given repo. Falls back gracefully."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(repo),
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return sha, bool(status.strip())
    except Exception:
        return "unknown", False


def _load_dotenv(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a dict; returns {} if file missing."""
    if not env_path.exists():
        return {}
    result: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def _mask(val: str | None) -> str:
    """Mask a secret value for display."""
    if not val:
        return "<not-set>"
    if len(val) <= 4:
        return "****"
    return val[:2] + "****"


def _write_metadata(out_dir: Path, meta: dict[str, Any]) -> None:
    (out_dir / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, default=str), encoding="utf-8"
    )


class _TeeStream:
    """Forwards writes to both an original stream and a log file."""

    def __init__(self, stream: Any, logfile_path: Path) -> None:
        self._stream = stream
        self._logfile = logfile_path.open("a", encoding="utf-8")

    def write(self, data: str) -> int:
        self._stream.write(data)
        self._logfile.write(data)
        return len(data)

    def flush(self) -> None:
        self._stream.flush()
        self._logfile.flush()

    def close(self) -> None:
        self._logfile.close()

    def fileno(self) -> int:
        return self._stream.fileno()  # type: ignore[no-any-return]

    @property
    def encoding(self) -> str:
        return getattr(self._stream, "encoding", "utf-8")  # type: ignore[no-any-return]

    @property
    def errors(self) -> str:
        return getattr(self._stream, "errors", "replace")  # type: ignore[no-any-return]


# ──────────────────────────────────────────────────────────────────────────────
# Core run logic
# ──────────────────────────────────────────────────────────────────────────────


def run(
    servicer: str,
    remit_date: datetime.date,
    out_dir: Path,
    source_repo: Path,
    dry_run: bool,
    env_file: Path,
) -> int:
    """Execute the legacy MRC validation flow and write outputs to out_dir.

    Returns an exit code:
      0 = success
      1 = legacy run failed
      2 = creds/env problem
      3 = source repo not found or entrypoint missing
    """
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    t_start = time.monotonic()

    # ── Resolve paths ──────────────────────────────────────────────────────────
    source_repo = source_repo.resolve()
    entrypoint_file = source_repo / MRC_ENTRYPOINT_RELPATH
    mrc_validation_file = source_repo / "flow" / "remit_validation" / "mrc_validation.py"

    # ── 1. Check source repo (exit 3) ─────────────────────────────────────────
    if not source_repo.exists():
        print(
            f"ERROR: Source repo not found: {source_repo}\n"
            "  Pass --source-repo <path> pointing to the PrefectFlow checkout.",
            file=sys.stderr,
        )
        return 3

    # ── 2. Load .env and env vars ─────────────────────────────────────────────
    env_vars = _load_dotenv(env_file)
    vault_addr = env_vars.get("VAULT_ADDR") or os.environ.get("VAULT_ADDR", "")
    vault_token = env_vars.get("VAULT_TOKEN") or os.environ.get("VAULT_TOKEN", "")
    vault_redshift_path = (
        env_vars.get("VAULT_REDSHIFT_PATH")
        or os.environ.get("VAULT_REDSHIFT_PATH", DEFAULT_VAULT_REDSHIFT_PATH)
    )
    buildenv = env_vars.get("BUILDENV") or os.environ.get("BUILDENV", "prod")

    # ── 3. Dry-run: print plan and exit ───────────────────────────────────────
    if dry_run:
        if not env_file.exists():
            print(
                f"  WARNING: .env not found at {env_file} — "
                "copy .env.example to .env before a real run.",
            )
        date_path = "".join(str(remit_date).split("-"))
        expected_xlsx = out_dir / "validation_report.xlsx"
        print("=== DRY-RUN MODE — no Redshift contact ===")
        print(f"  .env loaded from       : {env_file} ({'found' if env_file.exists() else 'MISSING'})")
        print(f"  VAULT_ADDR             : {vault_addr or '<not set>'}")
        print(f"  VAULT_REDSHIFT_PATH    : {vault_redshift_path}")
        print(f"  BUILDENV               : {buildenv}")
        print(f"  Vault token (masked)   : {_mask(vault_token)}")
        print(f"  Source repo            : {source_repo}")
        print(f"  Entrypoint file        : {entrypoint_file}")
        print(f"  remit_date             : {remit_date}")
        print(f"  Entrypoint function    : {MRC_FUNCTION_NAME}(")
        print(f"                               remit_date=datetime.date({remit_date.year}, {remit_date.month}, {remit_date.day}),")
        print( "                               email=False, to_new_redshift=True, to_mysql=False)")
        print(f"  date_path              : {date_path}")
        print(f"  servicer               : {servicer}")
        print(f"  out_dir                : {out_dir}")
        print(f"  Output XLSX            : {expected_xlsx}")
        print(f"  Run log                : {out_dir / 'run.log'}")
        print(f"  Metadata sidecar       : {out_dir / 'run_metadata.json'}")
        return 0

    # ── 4. (Non-dry-run) Validate .env ────────────────────────────────────────
    if not env_file.exists():
        print(
            f"ERROR: .env file not found at {env_file}\n"
            "  Copy .env.example to .env and fill in VAULT_ADDR and VAULT_TOKEN.",
            file=sys.stderr,
        )
        return 2

    if not vault_addr or not vault_token:
        print(
            "ERROR: VAULT_ADDR and VAULT_TOKEN must be set in .env (or environment).\n"
            f"  Checked: {env_file}",
            file=sys.stderr,
        )
        return 2

    # ── 5. Check source repo entrypoint files (exit 3) ────────────────────────
    if not mrc_validation_file.exists():
        print(
            f"ERROR: mrc_validation.py not found in source repo:\n"
            f"  Expected: {mrc_validation_file}",
            file=sys.stderr,
        )
        return 3

    if not entrypoint_file.exists():
        print(
            f"ERROR: Flow entrypoint not found in source repo:\n"
            f"  Expected: {entrypoint_file}",
            file=sys.stderr,
        )
        return 3

    # ── 6. Create output directory ────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 7. Set up log capture ─────────────────────────────────────────────────
    log_path = out_dir / "run.log"
    tee_out = _TeeStream(sys.stdout, log_path)
    tee_err = _TeeStream(sys.stderr, log_path)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = tee_out  # type: ignore[assignment]
    sys.stderr = tee_err  # type: ignore[assignment]

    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # ── 8. Prepare metadata skeleton ──────────────────────────────────────────
    meta: dict[str, Any] = {
        "tool_version": TOOL_VERSION,
        "started_at": started_at,
        "finished_at": None,
        "duration_sec": None,
        "servicer": servicer,
        "remit_date": str(remit_date),
        "source_repo_path": str(source_repo),
        "source_repo_sha": None,
        "source_repo_dirty": None,
        "python_version": sys.version,
        "platform": platform.platform(),
        "redshift": {
            "vault_path": vault_redshift_path,
            "user": "<masked>",
            "cluster": "<masked>",
        },
        "output": None,
        "datasets": [],
        "exit_code": 1,
    }

    try:
        sha, dirty = _git_sha(source_repo)
        meta["source_repo_sha"] = sha
        meta["source_repo_dirty"] = dirty

        # ── 9. Vault pre-check (for masked metadata) ──────────────────────────
        try:
            import hvac  # noqa: PLC0415  # type: ignore[import-untyped]

            client = hvac.Client(url=vault_addr, token=vault_token)
            if not client.is_authenticated():
                raise RuntimeError("Vault authentication failed — check VAULT_TOKEN.")
            parts = vault_redshift_path.split("/", 1)
            mount = parts[0] if len(parts) > 1 else "secret"
            secret_path = parts[1] if len(parts) > 1 else vault_redshift_path
            secret = client.secrets.kv.v1.read_secret(
                path=secret_path, mount_point=mount
            )
            cred_data: dict[str, str] = secret.get("data", {})
            meta["redshift"]["user"] = _mask(cred_data.get("sql-user", ""))
            meta["redshift"]["cluster"] = _mask(cred_data.get("hostname", ""))
        except ImportError:
            print(
                "WARNING: hvac not installed — Vault pre-check skipped.\n"
                "  Install with: pip install hvac",
                file=sys.stderr,
            )
        except Exception as vault_err:
            print(
                f"WARNING: Vault pre-check failed: {vault_err}\n"
                "  Proceeding — legacy code will attempt its own Vault connection.",
                file=sys.stderr,
            )

        # ── 10. Inject env vars for legacy credential loading ─────────────────
        # cred/__init__.py reads PREFECT_VAULT_TOKEN as fallback; env-specific
        # tokens (PROD_PREFECT_VAULT_TOKEN, TEST_PREFECT_VAULT_TOKEN) take priority.
        os.environ["PREFECT_VAULT_TOKEN"] = vault_token
        os.environ.setdefault("BUILDENV", buildenv)
        if buildenv == "prod":
            os.environ.setdefault("PROD_PREFECT_VAULT_TOKEN", vault_token)
        elif buildenv in ("uat", "test"):
            os.environ.setdefault("TEST_PREFECT_VAULT_TOKEN", vault_token)

        # ── 11. Add source repo to sys.path and import entrypoint ─────────────
        if str(source_repo) not in sys.path:
            sys.path.insert(0, str(source_repo))

        # Import is deferred to here so dry-run + tests work without legacy deps.
        import flow.remit_validation.remit_validation as rv_mod  # noqa: PLC0415  # type: ignore[import-untyped]

        # ── 12. Patch VALIDATION_REPORT_ROUTE to capture XLSX in out_dir ──────
        # remit_validation.py references this module-level name inside the flow
        # function; patching the module attribute redirects XLSX output to our
        # controlled location.
        date_path = "".join(str(remit_date).split("-"))
        xlsx_subdir = out_dir / "xlsx_output" / date_path
        xlsx_subdir.mkdir(parents=True, exist_ok=True)
        patched_route = str(out_dir / "xlsx_output") + "/"
        original_route = rv_mod.VALIDATION_REPORT_ROUTE
        rv_mod.VALIDATION_REPORT_ROUTE = patched_route
        expected_xlsx = xlsx_subdir / f"{remit_date}_validation_report.xlsx"

        print(f"[run_legacy_mrc] Calling {MRC_FUNCTION_NAME}(remit_date={remit_date})")
        print(f"[run_legacy_mrc] XLSX expected at: {expected_xlsx}")

        try:
            rv_mod.remit_validation_check(  # type: ignore[attr-defined]
                remit_date=remit_date,
                email=False,
                to_new_redshift=True,
                to_mysql=False,
            )
        finally:
            rv_mod.VALIDATION_REPORT_ROUTE = original_route

        # ── 13. Collect dataset row counts from VALIDATION_TABLE_MAP ──────────
        vtm = getattr(rv_mod, "VALIDATION_TABLE_MAP", {})
        datasets: list[dict[str, Any]] = []
        for key in _MRC_DATASET_KEYS:
            df = vtm.get(key)
            if df is not None:
                try:
                    row_count = len(df)
                except Exception:
                    row_count = -1
                datasets.append({"name": key, "row_count": row_count, "query_sec": None})
        meta["datasets"] = datasets

        # ── 14. Locate and copy produced XLSX ────────────────────────────────
        if expected_xlsx.exists():
            source_xlsx = expected_xlsx
        else:
            found = sorted(out_dir.rglob("*.xlsx"))
            source_xlsx = found[0] if found else None

        if source_xlsx and source_xlsx.exists():
            final_xlsx = out_dir / "validation_report.xlsx"
            shutil.copy2(str(source_xlsx), str(final_xlsx))
            meta["output"] = {
                "xlsx_path": str(final_xlsx),
                "sha256": _sha256_file(final_xlsx),
                "size_bytes": final_xlsx.stat().st_size,
            }
            meta["exit_code"] = 0
            print(f"[run_legacy_mrc] SUCCESS — XLSX at {final_xlsx}")
        else:
            print(
                f"ERROR: Expected XLSX not produced at {expected_xlsx}",
                file=sys.stderr,
            )
            meta["exit_code"] = 1

    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        meta["exit_code"] = 1

    except Exception as exc:
        import traceback

        print(f"ERROR: Legacy run failed: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        meta["exit_code"] = 1

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        tee_out.close()
        tee_err.close()
        root_logger.removeHandler(file_handler)
        file_handler.close()

        finished_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        meta["finished_at"] = finished_at
        meta["duration_sec"] = round(time.monotonic() - t_start, 2)
        _write_metadata(out_dir, meta)

    return int(meta["exit_code"])


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Operator-invoked legacy MRC validation runner.\n\n"
            "Loads Vault creds from .env, runs the legacy remit_validation_check\n"
            "flow against live Redshift, and writes XLSX + JSON sidecar to --out-dir."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--servicer", default="mrc", help="Servicer tag recorded in metadata (default: mrc)"
    )
    parser.add_argument(
        "--remit-date",
        required=True,
        metavar="YYYY-MM-DD",
        help="Remittance date — must be the last day of a calendar month",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        metavar="PATH",
        help="Directory to write validation_report.xlsx, run.log, run_metadata.json",
    )
    parser.add_argument(
        "--source-repo",
        default=str(DEFAULT_SOURCE_REPO),
        metavar="PATH",
        help=f"Path to the PrefectFlow source repo (default: {DEFAULT_SOURCE_REPO})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without touching Redshift; exit 0 if plan is coherent",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        metavar="PATH",
        help="Path to .env file (default: .env in CWD)",
    )

    args = parser.parse_args()

    try:
        remit_date = datetime.date.fromisoformat(args.remit_date)
    except ValueError:
        print(
            f"ERROR: Invalid --remit-date '{args.remit_date}' — expected YYYY-MM-DD",
            file=sys.stderr,
        )
        sys.exit(2)

    exit_code = run(
        servicer=args.servicer,
        remit_date=remit_date,
        out_dir=Path(args.out_dir),
        source_repo=Path(args.source_repo),
        dry_run=args.dry_run,
        env_file=Path(args.env_file),
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
