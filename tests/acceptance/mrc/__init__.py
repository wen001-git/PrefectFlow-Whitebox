"""MRC cell-identity acceptance harness (v9.1 acceptance gate).

The suite operates in three independent modes; each mode is the
authority for a different question:

1. **Self-consistency** (:mod:`.test_renderer_determinism`,
   :mod:`.test_self_consistency`) — runs the engine twice and asserts
   that two independent runs produce byte-identical XLSX output. Always
   runs; a failure here is a real bug (non-determinism in the engine
   or renderer).
2. **Baseline diff** (:mod:`.test_against_baseline`) — diffs one
   engine run against a captured legacy baseline XLSX
   (``baselines/mrc/2026-04-30/validation_report.xlsx``). Skips
   cleanly when the baseline is absent (waiting on G2a).
3. **Live legacy diff** (:mod:`.test_against_legacy_live`) — runs the
   real legacy flow + the new engine in the same window and diffs the
   two XLSX. Skips when Redshift / Vault credentials are unavailable.

The meta-test in :mod:`.test_acceptance_gate` aggregates the three
modes into a single verdict (PASS / MINOR_DIFFS / MAJOR_DIFFS /
SKIPPED) and is what the :mod:`tools.acceptance_gate` CLI mirrors.
"""
