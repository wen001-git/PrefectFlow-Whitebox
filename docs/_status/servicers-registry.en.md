# Project status · Servicers Registry (en)

> **Purpose**: the single source of truth for PrefectFlow-Whitebox
> reverse-engineering progress. Any servicer status change (⏳ → 🚧 → ✅) must
> update this file, the matching row in `plan.md`, the corresponding SQL todo
> status, and (after Stage 2) the validator registry tool output — all in the
> same commit.
>
> **Intended audience**: the current session agent, the next session's agent,
> and the user. Anyone asking "what have we analyzed?" / "what is still
> pending?" should look here first.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — created. v9.1 placeholder-everywhere rule activated. |

---

## Legend

| Marker | Meaning |
|---|---|
| ✅ | Done |
| 🚧 | In progress |
| ⏳ | Placeholder reserved, pending analysis (status `pending-deferred`) |
| ⛔ | Not started |
| 🔒 | Frozen, no longer applicable |

---

## Servicer status matrix

> Source of truth: this table. The same-named table in `plan.md` must match.

| Servicer | Sheets | Stage 1 doc | Stage 2 system | Last analyzed | Owner of next step | Open gaps / assumptions |
|---|---|---|---|---|---|---|
| **MRC** | 5 | 🚧 in progress (v9.1 active) | ⏳ pending Stage 1 review | 2026-05-15 (frozen pilot scope.md) | this session | full re-analysis underway |
| **Carrington** | 6 | ✅ chapter done (2026-05-17, archived under `_archived/pre-mrc-pivot/`) | ⛔ not started | 2026-05-17 | future session | may need refresh once MRC system shapes the template |
| **Shellpoint** | 5 | ✅ chapter done (2026-05-17, archived) | ⛔ not started | 2026-05-17 | future session | same as Carrington |
| **Arvest** | 4 (assumed) | ⏳ placeholder only | ⛔ not started | never | future session | sheet count assumed 4 — verify against `arvest_validation.py`; SQL templates unverified |
| **CC5** | 2 | ⏳ placeholder only | ⛔ not started | never | future session | smallest servicer; preferred future warm-up |
| **Selene** | 5 (assumed) | ⏳ placeholder only | ⛔ not started | never | future session | sheet count assumed 5 — verify |
| **SLS** | 5 (assumed) | ⏳ placeholder only | ⛔ not started | never | future session | **known issue: 2026-04 empty-data bug** must be documented when analyzed |
| **Scattered** (cross-servicer validators, ~8) | n/a | ⏳ placeholder only | ⛔ not started | never | future session | inventory of the 8 validators not yet enumerated |
| **Cross-servicer dataflow / lineage** | n/a | ⏳ placeholder only | ⛔ not started | never | future session | requires per-servicer docs to complete first |

---

## Placeholder index

For each `⏳ pending` servicer, the following placeholders must already exist:

| Servicer | Stage 1 stub | Stage 2 ingestion stub | Stage 2 handler stub | Lineage branch |
|---|---|---|---|---|
| Arvest    | [`docs/arvest/_pending.en.md`](../arvest/_pending.en.md)       | created in Stage 2 | created in Stage 2 | created in Stage 2 (dashed) |
| CC5       | [`docs/cc5/_pending.en.md`](../cc5/_pending.en.md)             | created in Stage 2 | created in Stage 2 | created in Stage 2 (dashed) |
| Selene    | [`docs/selene/_pending.en.md`](../selene/_pending.en.md)       | created in Stage 2 | created in Stage 2 | created in Stage 2 (dashed) |
| SLS       | [`docs/sls/_pending.en.md`](../sls/_pending.en.md)             | created in Stage 2 | created in Stage 2 | created in Stage 2 (dashed) |
| Scattered | [`docs/scattered/_pending.en.md`](../scattered/_pending.en.md) | created in Stage 2 | created in Stage 2 | created in Stage 2 (dashed) |
| Dataflow  | [`docs/dataflow/_pending.en.md`](../dataflow/_pending.en.md)   | created in Stage 2 | n/a | created in Stage 2 (dashed) |

---

## Maintenance rule

Any servicer state change (chapter delivery, todo update, newly discovered
gap) must update — in the **same commit** — all of:

1. This file (zh + en)
2. The servicer status matrix in `plan.md`
3. The corresponding SQL todo status
4. (Post-Stage-2) The validator registry tool output

See AGENTS.md § 6.8.
