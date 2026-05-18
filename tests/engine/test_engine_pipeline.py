"""End-to-end pipeline tests for :class:`whitebox.engine.Engine`."""

from __future__ import annotations

import json
from datetime import date

import pytest

from whitebox.engine import (
    CTEHarnessSource,
    Engine,
    OverallVerdict,
    RunResult,
    SheetVerdict,
)
from whitebox.engine.mrc_wiring import MRC_VALIDATOR_IDS


def test_run_returns_one_sheet_per_validator(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    assert isinstance(result, RunResult)
    assert len(result.sheets) == len(MRC_VALIDATOR_IDS)
    validator_ids = {s.validator_id for s in result.sheets}
    assert validator_ids == set(MRC_VALIDATOR_IDS)


def test_run_id_is_deterministic(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    a = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    b = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    assert a.run_id == b.run_id
    assert a.source_kind == "cte-harness"


def test_service_fee_validator_runs_clean(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    by_id = {s.validator_id: s for s in result.sheets}
    sfc = by_id["mrc_service_fee_check"]
    assert sfc.verdict in (SheetVerdict.PASS, SheetVerdict.WARN), (
        f"unexpected verdict for service_fee_check: {sfc.verdict}, "
        f"notes={sfc.notes}"
    )


@pytest.mark.parametrize(
    "validator_id",
    [
        "mrc_summary_check",
        "mrc_check_general_info",
        "mrc_check_adv_balance",
        "mrc_other_check",
    ],
)
def test_other_validators_degrade_without_fixtures(
    engine: Engine,
    cte_source: CTEHarnessSource,
    remit_date: date,
    validator_id: str,
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    by_id = {s.validator_id: s for s in result.sheets}
    sheet = by_id[validator_id]
    assert sheet.verdict is SheetVerdict.DEGRADED, (
        f"{validator_id}: expected DEGRADED, got {sheet.verdict} "
        f"notes={sheet.notes}"
    )
    assert sheet.notes  # must explain why


def test_overall_verdict_is_degraded_or_worse(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    # at least 4/5 validators are DEGRADED → roll-up must be DEGRADED or worse
    assert result.overall_verdict in (OverallVerdict.DEGRADED, OverallVerdict.ERROR)


def test_run_result_is_json_serialisable(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    payload = result.to_dict()
    blob = json.dumps(payload)
    round_tripped = json.loads(blob)
    assert round_tripped["run_id"] == result.run_id
    assert round_tripped["overall_verdict"] == result.overall_verdict.value
    assert len(round_tripped["sheets"]) == len(result.sheets)


def test_run_result_carries_source_metadata(
    engine: Engine, cte_source: CTEHarnessSource, remit_date: date
) -> None:
    result = engine.run(servicer="MRC", remit_date=remit_date, source=cte_source)
    assert result.metadata.get("source_kind") == "cte-harness"
    assert result.metadata.get("validator_count") == str(len(MRC_VALIDATOR_IDS))
