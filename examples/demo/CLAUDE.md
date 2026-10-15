# Taskly (demo project) - Session Operating Notes

Taskly is a fictional task-list web app used to exercise the scaffold: a Python server (`src/server/`), a web client (`src/web/`) and a mobile client (`src/mobile/`). Main branch `main`.

## 1. Targeted information retrieval
State is tracked in [`docs/progress.md`](docs/progress.md) (the single index) and `docs/progress/<area>.md`.
- Open work of an area: `grep -n -A 15 '^## Open work' docs/progress/<area>.md`
- Rules of an area: `grep -n -A 20 '^## Rules' docs/progress/<area>.md`

## 2. Rules of engagement
- Branches `claude/<descriptive-name>` from an up-to-date `main`, only when development is requested.
- Selective tests: only the tests the change touches.
- Rules are written as what to do; project rules live in the area sheets.

## 3. Subagent routing
Roles in `.claude/agents/` of the scaffold: planner, coder, mechanic, light, deep, research, ops. A task goes to a low-tier agent only if it passes the 5-question Readiness Gate; otherwise to `planner`. `deep` needs a declared necessity of 4 or 5. Every finished run is logged in `docs/agents/ledger.txt`.

## 5. Task closure
1. Update `## Open work`. 2. Update `## Rules (do not break)`. 3. `python scripts/docs_audit.py score`. 4. `python scripts/consistency.py check` after touching routes, config keys or a platform. 5. `python scripts/ci_audit.py` after touching the workflow.
