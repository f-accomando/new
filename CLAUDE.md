# <PROJECT> — Session Operating Notes

<One paragraph: what the project is, the stack, the main branch, the repository.>
Main branch: `<main-branch>`. Build: `<build-cmd>`. Tests: `<test-cmd>`.

> Template: replace every `<placeholder>`, delete the rows that do not apply, keep the structure.
> The whole workflow is explained in [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

---

## 1. Targeted Information Retrieval (zero token waste)

Read files in slices (grep, then `offset`/`limit`). All current state is tracked in
[`docs/progress.md`](docs/progress.md) (the single index) and in the area sheets `docs/progress/<area>.md`.

### Quick lookup commands
| Need | Command to run |
|---|---|
| **What is left to do in an area** | `grep -n -A 15 '^## Open work' docs/progress/<area>.md` |
| **Binding rules of an area** | `grep -n -A 20 '^## Rules' docs/progress/<area>.md` |
| **Find code in a big file** | `grep -n -m5 '<symbol>' <file>` then `Read` with `offset`/`limit` |
| **Plans and milestones** | `grep -n '^## Level' docs/ROADMAP.md` |
| **Undecided questions** | `docs/open-decisions.md` |

---

## 2. Rules of Engagement and Development

- **Branches**: open a branch only when the user asks for development (feature, fix, refactor). Questions, analysis and reads stay on the current branch.
  - Name: `claude/<descriptive-name>` (for example `claude/search-filters`): the name says what is being developed.
  - If the scope or the name is unclear, ask the user for the name before creating the branch or editing files.
  - Base: an up-to-date `<main-branch>`. If the session imposes a branch, use that one only.
- **Selective tests**: run only the tests the change touches (`<test-cmd> -k <name>`). The full suite runs in CI.
- **Secrets**: keys, tokens and passwords live outside the repository (environment or a secret store).
- **Licences**: the sources hold only original or permissively licensed code.
- **Writing rules**: state each rule as what to do ("do it this way"), not as a prohibition. When a rule is retired, delete it; do not replace it with its negation, because a "do not X" line keeps the old behaviour in view and reads as a new rule. Add an explicit prohibition only as an exception, when the agent keeps repeating something harmful despite the positive rule, and note the harm next to it.
- **Project-specific rules** go in the `## Rules (do not break)` section of the area sheet, never here.

---

## 3. Subagent Architecture and Smart Routing

### The principle: separate deciding from executing
Top-tier models are expensive on output tokens: they produce short decisions and plans. Cheap models write the code (many tokens).
The router picks the agent by how well the task is already specified, not by its apparent size.

### Roles (definitions in `.claude/agents/`)
| Agent | Model / effort | Does | Out of scope |
|---|---|---|---|
| **`planner`** | Opus medium (read-only) | Turns vague or large tasks into Work Orders with verifiable criteria | Write code |
| **`coder`** | Haiku high | Writes code from a precise, exhaustive Work Order | Design, resolving ambiguity |
| **`mechanic`** | Haiku low | Zero-risk, fully specified tasks (rename, format, templates, ticks in `docs/progress/`) | Logic decisions |
| **`light`** | Sonnet medium | Simple tasks with technical judgment, docs checked against the real code, 1-2 file fixes | Long and vague jobs |
| **`deep`** | Opus xhigh | One isolated, critical problem (bug with reproduction, one architectural decision) | Implement whole features |
| **`research`** | Haiku low (read-only) | Exploration across many files, compact summaries | Modify anything |
| **`ops`** | Haiku low (Bash only) | Shell commands that are already decided: git fetch/status, `<build-cmd>`, audits, sync heartbeat | Decide, fix, kill processes, merge |

### Readiness Gate
Before assigning a task to an executing model (`mechanic`, `coder`, `light`), answer five questions. The task is ready for a low-tier agent only if ALL answers are **YES**:
1. **Files/functions**: are the files and functions to touch named explicitly?
2. **Determinism**: is the change described so that two people would produce the same diff (no open design choice)?
3. **Verifiable criterion**: is there a deterministic command that checks it (test, build, lint, expected output)?
4. **Limited scope**: does it involve about 3 files or fewer?
5. **No blockers**: is it independent of decisions still pending?

> **Rule**: with even one NO, the task goes to **`planner`**, which makes it ready or splits it into atomic Work Orders. It does not go to `deep` either.

### Rules for `deep`
- Invoked only with necessity 4-5 (below). It accepts only a tight problem statement: symptom + exact reproduction + suspected area + attempts already made.
- A request without reproduction, or a generic one ("implement X"), goes back to `planner`.
- Output: root-cause diagnosis and a minimal fix; the implementation returns to `coder` or `light`.

### Necessity of the expensive model (1-5)
Every request for a model more expensive than the standard one declares **necessity N out of 5, the reason, and the estimated cost against the cheap model** (for example "about 5x"). There is exactly one reason, and it is written down:
- **Prior failure**: "necessity 4 out of 5: a previous model already failed (`FAILED x2`)".
- **High cost of error**: "necessity 4 out of 5: resolving or redoing an error is expensive".

| N | Meaning |
|---|---|
| 1 | The cheap model can do it; requested only for convenience |
| 2 | Almost certainly the cheap model can do it; the expensive one saves at most one round |
| 3 | Likely an error or two rounds with the cheap model: `planner` starts |
| 4 | The cheap model already failed, or the error is costly |
| 5 | Almost a necessity: the error is irreversible, or the alternative is giving up |

**Autonomy threshold = 4**: with N=1-3 the expensive model is not used; with N=4 or 5 the agent switches to it **without asking**, stating score and reason in chat. To change the threshold, edit this line. The score is an estimate; the ledger measures it.

**Ledger**: after each finished subagent, the main agent appends one row to `docs/agents/ledger.txt` (append only):
`date|agent|model|task|area|gate|necessity|outcome|tokens|tools|secs`. Run `python scripts/agent_audit.py` to tune the thresholds.

### Evidence-based escalation
Agents close with an explicit status:
- **`DONE`**: the verification command passes.
- **`BLOCKED: <reason>`**: ambiguous specification or missing decision; the task goes back to `planner`.
- **`FAILED x2`**: the check still fails after two attempts; the task moves up one level (coder to light, light to deep).

### Work Order format
Every order from `planner` has: objective (one sentence), files/functions to touch, the change with no open design choice, verification command and expected result, recommended agent. Skill: `work-order`.

---

## 4. Global Invariants

- <Invariant that holds across the whole project, for example a data format or a naming rule.>
- **Module-specific rules**: each area lists its non-negotiable rules in the final `## Rules (do not break)` section of `docs/progress/<area>.md`.

---

## 5. Task Closure and Continuous Maintenance

Before finishing any activity:
1. **Update the status**: remove or update the finished items in `## Open work` of `docs/progress/<area>.md`.
2. **Update the rules**: a new or changed constraint goes in `## Rules (do not break)` of that file.
3. **Integrity check**: `python scripts/docs_audit.py score` reports no broken links and no orphan files.
4. **Consistency**: after touching a format, an API, a config key or the behaviour of a single platform, run `python scripts/consistency.py check` and update `docs/spec/`. Everything must converge before the release gate (`consistency.py gate`).
5. **CI**: after touching `.github/workflows/` or a test timeout, run `python scripts/ci_audit.py`.
6. **Self-test**: after touching any script, run `python scripts/selftest.py`.

---

## 6. Multi-operator Sync and Handshake

Several agents (Claude local/cloud, Antigravity, others) can work in parallel with the protocol in [`SYNC.md`](SYNC.md) (template; rules and lessons in [`docs/progress/sync.md`](docs/progress/sync.md)).
Each project has a dedicated **sync branch** `sync/<name>`. `SYNC.md`, `sync/*` and `tools/sync_*.py` are used and pushed only there, never on `<main-branch>`, so sync sessions never touch each other; code lives on working branches cut from `<main-branch>`.

**"Do the handshake `<branch>`"** (from the user) = join the sync of that branch with no further explanation:
1. `git fetch origin`, check out `<branch>` in a separate worktree or clone (not on your working branch), `git pull --rebase`.
2. Read `SYNC.md` (roles section 1, contracts section 2, work orders section 3, rules 3b/3c) and `sync/operators.toml`; find the supervisor (SPV) and your ID (if none, propose one to SPV).
3. Create **only** `sync/<ID>.md` from `sync/_template.md`: the status block via `python tools/sync_hdr.py <ID> --state FREE --task handshake`, then `## Profile` (where you run, breaking points, models, subagents, tools with version) and `## Requirements` if section 2 lists them.
4. Commit, `git pull --rebase origin <branch> && git push origin HEAD:<branch>`, then wait for the assignment written by SPV. **Start no work before it.**

**Delivery**: one standard line in `## Deliveries` of your own file, `DELIVERED {WO-ID} @ {branch}@{commit} · verify: {command} → {result} · {ISO}`, then `FREE`. SPV answers `REVIEW: APPROVED` or `REVIEW: CHANGES REQUESTED` and integrates only after the first. `DONE` is the terminal state, not a delivery. A non-standard signal starts nothing.

**Inbox and check**: every new task or urgency arrives in `sync/inbox/<ID>.md` (max 5 lines, written by SPV). At each heartbeat read the `git diff` of your inbox, then run `python tools/sync_hdr.py <ID> --ack auto`. SPV runs `python tools/sync_check.py` to see who is alive and what is unread. Declare `--wakeup yes|no` in your profile. Log rows stay under 600 characters; a rule change is a `RULE` row confirmed with `ack`.

**Heartbeat cost**: a heartbeat is `fetch` + inbox + `--ack auto`. Run by the main agent it re-reads the whole conversation each time; a small subagent or `python tools/sync_watch.py --id <ID> --branch <sync-branch>` (no model, wakes the agent only on news) costs a fraction.

**Sign-off**: when SPV writes `SIGNOFF <ID>: reason`, the operator starts nothing new, delivers and pushes what exists, writes the closure in its own file, marks itself `DONE` with `sync_hdr.py` and stops the heartbeats. It returns only with a new handshake asked by SPV.

Fixed rules: one writer for each file (`SYNC.md` only SPV, `sync/<ID>.md` only `<ID>`); event-driven heartbeat with no timer (update your file and push at every finished task); `eta` is mandatory in `WORKING`/`WAITING`; more than 10 minutes past `eta` without an update = `IDLE` (no `eta`: 60 minutes; `FREE` and `DONE` are never `IDLE`); messages between operators are a block `from <ID> to <ID>: ...` in chat; tasks take 45 minutes or less; the main agent stays free; Log rows 600 characters or less; operator status in chat only on request.
