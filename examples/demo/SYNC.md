# Sync protocol (`SYNC.md`): worked example, project "search filters"

> A finished, trimmed example of the template in the repository root (`SYNC.md`): same sections, filled for a fictional project.
> The full rules are in the template; this copy keeps the parts that show how a real sync reads.

- **Project**: search filters · **Repo**: example/taskly · **Code base**: `main` · **Sync branch**: `sync/search-filters`
- **Started**: 2026-10-01 · **Supervisor (SPV)**: local Sonnet session · **User**: decides, does the final merges

## 1. Roles and files (one writer per file)

| Operator | ID | Runs where | Writes | Branch |
|---|---|---|---|---|
| Supervisor | `SPV` | local | `SYNC.md` + `sync/SPV.md` + `sync/inbox/*` + `sync/wo/*` | `sync/search-filters` |
| server filters | `ALPHA` | laptop | `sync/ALPHA.md` | `claude/search-filters` |
| mobile panel | `BETA` | cloud container | `sync/BETA.md` | `claude/mobile-filters` |
| user | `USER` | - | nothing | - |

## 2. Architecture and shared contracts

### Global goal
Search gets tag and date filters. ALPHA builds the server side, BETA the mobile panel; both converge in SPV's integration branch before `main`.

### Decisions taken
1. The filter syntax is `tag=<value>&from=<date>`; an empty value is an error (2026-10-01, see WO-1b).

### File split (the perimeter)
- `ALPHA`: `src/server/search.py`, `tests/test_search.py`.
- `BETA`: `src/mobile/*`, `tests/mobile_filters.test.js`.
- Shared: `src/web/routes.js` only if a Work Order names it, one line each.

## 3. Task board

| WO | Operator | State | File |
|---|---|---|---|
| WO-1, WO-1b | `ALPHA` | `DELIVERED` | `sync/wo/ALPHA.md` |
| WO-2 | `BETA` | `DELIVERED` | `sync/wo/BETA.md` |

## 5. Handover Log

| Timestamp | Operator | Branch / Commit | Action | Message |
|---|---|---|---|---|
| 2026-10-01T09:00+02:00 | SPV | `sync/search-filters` | `INIT` | Sync started: ALPHA (server filters) and BETA (mobile panel). Work orders in `sync/wo/`. Perimeters in section 2. |
| 2026-10-01T10:40+02:00 | ALPHA | `claude/search-filters`@a1b2c3d | `REVIEW: CHANGES REQUESTED` | WO-1: perimeter ok, 6 tests pass, but `parse_filters("tag=")` returns every task. Reviewer reproduced it with a new test (`-k filters_empty`, fails). Fix in WO-1b, in your inbox. Nothing outside `src/server/search.py` and its test. |
| 2026-10-01T11:20+02:00 | ALPHA | `claude/search-filters`@e4f5a6b | `REVIEW: APPROVED` | WO-1b: the new test fails on the old code (0/1) and passes with the fix (8 passed). Perimeter ok. Integrated in `integration/search-filters`. |
| 2026-10-01T11:35+02:00 | BETA | `claude/mobile-filters`@b7c8d9e | `REVIEW: APPROVED` | WO-2: 5/5 on node 20; the Python-side check was skipped by the container (3.10), rerun by the reviewer on 3.12: ok. Not verifiable without a phone: the touch targets. |
| 2026-10-01T12:00+02:00 | SPV | `sync/search-filters` | `SIGNOFF` | SIGNOFF ALPHA, BETA: project finished. Deliver and push what you have, write the closing line in your file, mark yourself DONE, stop the heartbeats. |
