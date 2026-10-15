# <PROJECT> — Session Operating Notes (Google Antigravity / Gemini)

<One paragraph: what the project is, the stack, the main branch.> Build: `<build-cmd>`. Tests: `<test-cmd>`.
Same workflow as [`CLAUDE.md`](CLAUDE.md); this file holds only what differs for Antigravity. Full description: [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

---

## 1. Targeted Information Retrieval

Read files in slices. All current state is tracked in [`docs/progress.md`](docs/progress.md) and in `docs/progress/<area>.md`.

| Need | Command to run |
|---|---|
| **What is left to do in an area** | `grep -n -A 15 '^## Open work' docs/progress/<area>.md` |
| **Binding rules of an area** | `grep -n -A 20 '^## Rules' docs/progress/<area>.md` |
| **Find code in a big file** | `grep -n -m5 '<symbol>' <file>` then read the span |

---

## 2. Rules of Engagement

- **Branch**: before editing files for a new feature, propose a short branch name (`feat/<name>`) and ask the user. Base: an up-to-date `<main-branch>`.
- **Selective tests**: run only the tests the change touches (`<test-cmd> -k <name>`).
- **Secrets** live outside the repository. **Licences**: original or permissively licensed code only.
- **Writing rules**: state each rule as what to do; retire a rule by deleting it, never by writing its negation.

---

## 3. Subagent Architecture and Model Mapping

When Antigravity invokes subagents (`invoke_subagent`), map the roles as follows:

| Role | Antigravity model | Toolset | Does | Does NOT do |
|---|---|---|---|---|
| **`planner`** | `"pro"` | Read-only | Turns vague tasks into Work Orders with verifiable criteria | Write code |
| **`coder`** | `"flash"` | Full | Writes code from a precise Work Order | Design or open choices |
| **`mechanic`** | `"flash_lite"` | Full (atomic) | Zero-risk tasks: rename, format, templates, progress ticks | Logic decisions |
| **`light`** | `"flash"` | Full | Simple judgment tasks, verified docs, 1-2 file fixes | Long and vague jobs |
| **`deep`** | `"pro"` | Full | One isolated critical problem with certain reproduction | Implement whole features |
| **`research`** | native `research` subagent | Read-only | Code reconnaissance and symbol search | Touch files |
| **`ops`** | `"flash_lite"` | Bash only | Already-decided shell commands | Decide or fix |

### Readiness Gate
Assign a task to execution only if all five answers are YES: (1) files and functions named; (2) two people would write the same diff; (3) a deterministic verification command exists; (4) about 3 files or fewer; (5) no pending decision. Otherwise it goes to `planner` (`pro`), never directly to `deep`.

### Escalation and necessity
`DONE` (verification passes), `BLOCKED: <reason>` (back to `planner`), `FAILED x2` (up one level). The expensive model (`deep`) needs a declared necessity of 4 or 5 out of 5 with the reason; the scale and the autonomy threshold are in `CLAUDE.md` section 3. Log every finished run in `docs/agents/ledger.txt`.

---

## 4. Global Invariants

- <Invariant that holds across the whole project.>
- Module rules: `## Rules (do not break)` of `docs/progress/<area>.md`.

---

## 5. Task Closure

1. Update `## Open work` of the area sheet. 2. Record new constraints in `## Rules (do not break)`. 3. `python scripts/docs_audit.py score` shows no broken link or orphan. 4. After touching a format, API or config key: `python scripts/consistency.py check`. 5. After touching CI: `python scripts/ci_audit.py`.

---

## 6. Multi-operator Sync

Join a sync with "do the handshake `<branch>`": the steps, the delivery line (`DELIVERED ...`), the inbox rule and the sign-off are described in `CLAUDE.md` section 6 and in `SYNC.md`. Start no work before SPV writes your assignment.
