# Pull Request

## Summary
<!-- one-paragraph description of what & why -->

## Scope
- [ ] This PR touches files under `whitebox/{engine,sheets,renderer,validators,transform,ingestion,registry}` (subject to the PR evidence rule below)
- [ ] This PR is documentation / tooling only (evidence rule does not apply)

---

## PR evidence rule (per `docs/stage2/11.0-architecture` § 6)

**Required for any PR that touches the modules listed above.**

### Command used
```bash
python tools/compare_validation.py auto \
  --remit-date <YYYY-MM-DD> \
  --servicer MRC \
  --output-dir runs/<run-id>
```

### `verdict.json` (paste contents)
```json
{
  "verdict": "...",
  "summary": "..."
}
```

### Outcome
- [ ] **PASS** — no diffs; safe to merge
- [ ] **MINOR_DIFFS** — diffs explained below + ADR reference in `decisions.md`
- [ ] **MAJOR_DIFFS** — **DO NOT MERGE**. Fix required before review.
- [ ] **ERROR** — orchestrator failed; fix tooling first.

### Justification (only if MINOR_DIFFS)
<!-- explain each diff + link to ADR -->

---

## Checklist
- [ ] Tests added or updated
- [ ] `decisions.md` updated if scope/architecture changed
- [ ] `plan.md` updated if scope/architecture changed
- [ ] No `openpyxl` version change (or: ADR linked)
- [ ] No new heavy FE dep added without ADR (per plan.md § 10.2 restraint)
