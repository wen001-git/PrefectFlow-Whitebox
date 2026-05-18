"""Data providers for the FastAPI layer.

This sub-package owns the *contract-only* fixture provider used by the
routers in :mod:`whitebox.api.routers`. The engine / storage backends
that will replace these providers land in later todos
(``e-engine-runner``, ``f-storage-adapter``); the public function
signatures here are deliberately the same ones a real backend would
expose, so swapping fixture → real is a single import change.
"""

from __future__ import annotations

from whitebox.api.data import fixtures

__all__ = ["fixtures"]
