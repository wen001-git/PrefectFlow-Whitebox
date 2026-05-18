"""Acceptance test suites.

Each subpackage (e.g. :mod:`tests.acceptance.mrc`) is a per-servicer
end-to-end acceptance gate. These suites run the **real engine**
through the **real renderer** and diff the produced XLSX against the
reference oracle for that servicer (baseline XLSX or live legacy run).

They are deliberately separate from
``tests/integration/comparison/`` — those tests exercise the *diff
orchestrator* in isolation; the suites here exercise the *engine
output* end-to-end and form the v9.1 acceptance gate.
"""
