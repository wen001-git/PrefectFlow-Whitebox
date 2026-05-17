# Test report — `stage1-pending-registry`

**Date**: 2026-05-17
**Stage / todo**: Stage 1 — `stage1-pending-registry`
**Plan version**: v9.1
**Scope of this report**: verify that the v9.1 placeholder infrastructure
(servicers registry + 6 pending-servicer stubs) is in place, that the
non-MRC chapters have been archived under `docs/_archived/pre-mrc-pivot/`
without breaking the doc test matrix, and that the full repository-level
test suite is green.

## What was delivered

| Artifact | Path | Purpose |
|---|---|---|
| Servicers registry (zh) | `docs/_status/servicers-registry.zh.md` | Canonical per-servicer status matrix |
| Servicers registry (en) | `docs/_status/servicers-registry.en.md` | English mirror |
| Arvest stub | `docs/arvest/_pending.{zh,en}.md` | Placeholder reserving nav slot |
| CC5 stub | `docs/cc5/_pending.{zh,en}.md` | ditto |
| Selene stub | `docs/selene/_pending.{zh,en}.md` | ditto |
| SLS stub | `docs/sls/_pending.{zh,en}.md` | ditto |
| Scattered stub | `docs/scattered/_pending.{zh,en}.md` | ditto |
| Cross-servicer dataflow stub | `docs/dataflow/_pending.{zh,en}.md` | ditto |
| Archived v8 chapters | `docs/_archived/pre-mrc-pivot/{toc,overall-flow,carrington,shellpoint}.{zh,en}.md` | 4 polished chapters moved out of nav |
| Nav update | `mkdocs.yml` | Adds "Project status" + "Pending servicers" sections; drops the archived chapters |
| Doc-check update | `tools/stage_doc_checks.py` | New 7-pair set + 4 archived pairs; recursive `rglob`; ROOT fallback for whitebox-local citations; basename-cache prune for speed |

## Test matrix

| # | Check | Command | Result |
|---|---|---|---|
| T1 | Heading-skeleton alignment (zh↔en) for all 11 pairs | `python tools\stage_doc_checks.py` | ✅ 11/11 ALIGN OK |
| T2 | Source-citation existence (`*.py:LINE` resolves and in-range) | (same script) | ✅ 292 PASS / 0 missing / 0 out-of-range |
| T3 | pytest unit tests | `.venv\Scripts\pytest.exe -q` | ✅ 7 passed in ~4 s |
| T4 | MkDocs strict build | `.venv\Scripts\mkdocs.exe build --strict` | ✅ Built in ~15 s, no warnings/errors |

INFO-level `mkdocs-i18n` messages about `*.zh.md` files not appearing in
nav are pre-existing baseline behavior (the plugin emits these for every
language-suffixed file when nav lists only the base name). Strict build
still passes because they are INFO, not WARNING.

## Notes / follow-ups

- The 4 archived chapters remain under doc check coverage (heading
  alignment + citation existence) so they can't bit-rot silently while
  archived. They are no longer in the mkdocs nav, so site visitors don't
  see them by default; the files are still browseable directly.
- `tools/stage_doc_checks.py` citation scan now caches a basename→paths
  map of all `*.py` files under the read-only `PrefectFlow` repo,
  pruning `.git/.venv/__pycache__/...`. Previous version was O(citations
  × repo size) and was taking minutes; new version completes in seconds.
- Next: `stage1-mrc-toc` per plan v9.1 § "Stage 1 todos (MRC-first)".
