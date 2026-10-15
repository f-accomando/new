# Multi-operator sync protocol (`SYNC.md`)

> Reusable template. For a new project: **create the sync branch** `sync/<name>` from `<main-branch>`, copy this file there, replace the `{placeholders}`, fill sections 2 and 3, and empty the Log (section 5).
> A project's sync lives only on that branch: several sync sessions (other agents, other projects) then run in parallel without touching each other. `<main-branch>` keeps only the templates (this file, `sync/_template.md`, `sync/inbox/README.md`, `sync/operators.toml`, `tools/sync_*.py`).
> Rules and lessons: [`docs/progress/sync.md`](docs/progress/sync.md). A complete worked example is in `examples/demo/SYNC.md`.

- **Project**: {name} · **Repo**: {owner/repo} · **Code base**: `<main-branch>` · **Sync branch**: `sync/{name}` · **Governance**: [`AGENTS.md`](AGENTS.md)
- **Started**: {date} · **Supervisor (SPV)**: {who} · **User**: decides, does the final merges

---

## 1. Roles and files (one writer per file)

| Operator | ID | Runs where | Writes | Branch |
|---|---|---|---|---|
| {supervisor} | `SPV` | {place} | `SYNC.md` + `sync/SPV.md` + `sync/inbox/*` + `sync/wo/*` | `sync/{name}` |
| {operator A} (from handshake) | `ALPHA` | to declare in the profile | `sync/ALPHA.md` | `claude/{topic-a}` |
| {operator B} (from handshake) | `BETA` | to declare in the profile | `sync/BETA.md` | `claude/{topic-b}` |
| user | `USER` | - | nothing (talks in the sessions) | - |

1. `SYNC.md` is written **only by SPV**: contracts, work orders, decisions, the status table (section 1b), notices to all.
2. Every other operator writes **only its own** `sync/<ID>.md`: state, task, progress, problems, requests. Everyone reads everything.
3. Operators are listed in [`sync/operators.toml`](sync/operators.toml) (written by SPV; a new operator is a new block).
4. **Sync files and Log rows are pushed only to the sync branch** (`git pull --rebase origin sync/{name}`, never a merge commit). **Code** stays on working branches cut from `<main-branch>` and reaches it only after SPV's review (section 3c) and with the user's consent. At the end SPV archives `SYNC.md` in `docs/archive/` on `<main-branch>` and the sync branch closes.
5. SPV writes rows from a **separate worktree** of the sync branch, so it never switches its working branch.
6. Requests between operators go through SPV; urgencies are written in the operator's own file and SPV routes them. When an operator is blocked and silent, the only channel is a message from the user in its session.

### States (the same names everywhere)

| State | Meaning |
|---|---|
| `WORKING {task}` | working on that task |
| `WAITING {who}` | blocked until the user, another operator or a service acts |
| `FREE` | agreed tasks finished and pushed, available for other work |
| `DONE` | terminal: session over, nothing left to claim |
| `IDLE` | `WORKING`/`WAITING` more than 10 min past `eta` without an update (no `eta`: more than 60 min): to be reported to the user. `FREE` and `DONE` are never `IDLE` |

### Status block (top of every `sync/<ID>.md`)

Written by [`tools/sync_hdr.py`](tools/sync_hdr.py), never by hand. Fields: `schema`, `id`, `state`, `task`, `waiting_on`, `progress`, `eta`, `wakeup`, `ack`, `updated`.

- Times are **ISO 8601 with a zone** (`2026-10-14T12:00+02:00`); readers compare in UTC.
- `eta`: mandatory in every `WORKING` and `WAITING`; it says when the operator will be reachable again. In a task it is "delivery ready in N min"; in the handshake or while waiting for a prompt it is "answer expected in N min" (minimum 3, at most 3 short checks, then a normal `eta`). When work runs long the operator moves it with a progress line before it expires.
- `ack`: time of the last `SYNC.md` row read (read receipt). `--ack auto` confirms the last row present after the fetch (delivery received), NOT that the agent understood it: an agent that acts on a row writes `read <row time>` in its own Log.
- The table in 1b is **generated** from the blocks: SPV writes no predicted states, only states read from files with the file's time. Hypotheses are labelled `HYPOTHESIS`.

### 1b. State and waits

Source of truth: `python tools/sync_check.py` (state read from the files, with time). Operators not yet through the handshake are listed here with the date.

---

## 1c. Work cycle

1. **Architecture**: SPV receives the requirements from the user and fills sections 2 and 3.
2. **Push the specs**: SPV publishes `SYNC.md` on the sync branch.
3. **Parallel development**: each operator works on its own branch, cut from an up-to-date `<main-branch>`.
4. **Merge** into `<main-branch>` only with the user's consent.

Integration rules:
- A file has one area owner; whoever needs a change in someone else's file asks SPV.
- Unavoidable shared files (for example a build file): one line each, named in the Work Order.
- The contracts of section 2 change only with a Log row and `BLOCKED` on the work orders that depend on them.

---

## 2. Architecture and shared contracts

### Global goal
{Two or three sentences: what the independent developments are, who does what, where everything converges.}

### Development requirements (optional, see 3c)
- {toolchain, runtime versions, emulators, accounts, models, subagents}. Each operator answers YES/NO/PARTIAL in its own file, `## Requirements`.

### Decisions taken (they change only with a Log row)
1. {decision, date, pointer to the work order that explains it}

### File split (the perimeter)
- `ALPHA`: {the files and folders it may touch}, on `claude/{topic-a}`.
- `BETA`: {the files and folders it may touch}, on `claude/{topic-b}`.
- Shared: {file}: only if named in a Work Order.

---

## 3. Task board

One block per work order, in the format of [`CLAUDE.md`](CLAUDE.md) section 3 with the Readiness Gate (skill `work-order`). Tasks take **45 minutes or less** (target 15): bigger ones are split into steps, one work order per step. Steps that do not depend on a decision are authorised **in sequence** with a single final review.

Full work orders live in `sync/wo/<ID>.md` (written by SPV, one block per step).

| WO | Operator | State | File |
|---|---|---|---|
| {WO-1, WO-2} | `ALPHA` | `PENDING` (waits for the handshake) | [`sync/wo/ALPHA.md`](sync/wo/ALPHA.md) |

---

## 3b. Times, timers and closure

**Estimates**: an LLM agent needs about 0.3-0.5 times the "human" estimate, except where it waits for an execution (build, emulation). Recalibrate the table with observed times at each milestone.

| WO | Estimate | Observed |
|---|---|---|
| (filled at delivery) | - | - |

**Heartbeat**:
0. **At start** (from the handshake): **short beats of 3-5 minutes** (read `SYNC.md` and `sync/`, update your file) **until you have taken the first work order**: you read the `ASSIGNED` row, wrote `ack` and marked yourself `WORKING`; then the normal rhythm. **SPV** keeps the short beats until every new operator confirmed. Safety cap: after 6 short beats without an assignment, move to 15 minutes and SPV tells the user.
1. **Event-driven heartbeat, no timer** (all operators): update your file and push **at every finished task**. A long task is split by the operator, each step announced with a progress line. A problem or a request for the intervention of SPV or the user is a pushed row (`WAITING`, `waiting_on`) **plus one short sentence in chat to the user**. Chat alone does not count: SPV reads the repository. Operators that wake themselves can use `sync_watch.py`, which costs no tokens.
2. SPV checks against `eta`: more than 10 min past it without an update is `IDLE`; without `eta`, after 60 min. SPV runs `sync_check.py` only when woken (a user message or a session notification), without polling.
2b. **Messages between operators**: whoever needs an immediate prompt for another operator (SPV included) writes in chat one self-contained block starting `from <ID> to <ID>: ...`; the user copies it where needed. The sender also leaves a row with time and subject in the recipient's inbox (for SPV) or in its own file, so the handover is verifiable.
3. The main agent stays reachable (to communicate, interrupt, resize): long work goes to subagents, or to steps with a check in between.

**Closure**:
1. Agreed tasks finished: `FREE`.
2. From `FREE` without jobs: checks after 15, 30 and 45 minutes (read `SYNC.md` and `sync/`). Then whoever is **not SPV** marks itself `DONE`.
3. Before marking `DONE`: clean working tree and everything pushed; with unsaved work or a long process running, do not close, and write it in your file.
4. SPV: when everyone is `DONE` and the tasks complete, last update of `SYNC.md`, ends the sync, marks itself `DONE` and writes the session report.
5. **Blocked and silent operator**: `sync_check` reports it `IDLE`, or it has a row or inbox item unacknowledged for more than 30 minutes while not `WAITING user`. SPV tells the user in chat with the ID and the expected row: the only channel is a user message in the operator's session.

**Tasks and free agents**:
- **Split heavy tasks**: no task may block an agent indefinitely. An estimate above 45 minutes is split into steps of 45 minutes or less, one row per step; SPV formalises them as work orders.
- **The main agent stays free**. Subagents do the work; the operator supervises its own subagents for its tasks: starts them, checks the result with the verification command, answers to SPV for it. Without subagents the operator works in steps with a check in between.
- **Problems**: report at once in your own file (what, where, what was already tried) and look for solutions. For a problematic task, try **alternatives with short parallel tests** (different subagents, 20-50 s each) and keep the best.
- **Repetitive tasks**: the third time the same operation appears it becomes a **skill** (or a script) and is noted in the Log.

**Lightness**:
- Log rows **600 characters or less**: decision, commit, check. Procedures belong in the work order or in `docs/design/`.
- A **hypothesis** is not sent as an instruction: verify it first, or label it `HYPOTHESIS`.
- Declare environment limits early (missing toolchains, containers that stop after inactivity, flaky network) in the profile and in the status block.
- While waiting for a long execution, audit the work and look for problems.
- Stand-in artifacts are declared as such; when the real files arrive, recalibrate and recheck whatever used them.

## 3c. Handshake, profile and requirements

**Handshake** = the procedure by which an operator joins the sync and becomes available. "Do the handshake" means, in order:
1. **Align** to the **sync branch** (the name the user gives after "do the handshake", for example `sync/{name}`): `git fetch origin`, check out (better in a separate worktree or clone) and `git pull --rebase`. Code development stays on `<main-branch>` or the branch the work order names.
2. **Read `SYNC.md`** (roles, contracts section 2, work orders section 3, rules) and your own `sync/` folder.
3. **Produce your own file** `sync/<ID>.md` with the status block (`tools/sync_hdr.py`) and `## Profile`.
4. **Become available**: with the file filled, mark `FREE` (or `WORKING` if a task is already yours). Until then SPV assigns no work.

**Review of a delivery** (SPV, before `REVIEW: APPROVED`): SPV does not trust the operator's report and has the delivery reviewed by an **independent** subagent (not the operator's), working in a temporary worktree of the delivered commit without touching the operator's. Checklist, in order:
1. **Perimeter**: `git diff <base>...<commit> --stat` against the files the work order names; a file outside the perimeter is flagged (acceptable only when consistent with a written decision).
2. **Commands**: rerun the verification command of every work order and report the real result. A failure is **pre-existing** (the same error on a clean base branch, tested side by side) or **introduced**; only the second blocks.
3. **Code**: read the diff for logic defects, security issues (external input, paths, overflow) and missing test cases.
4. **Result per work order**: `APPROVABLE` or `CHANGES` with reason and `file:line`; what cannot be verified without the real platform is declared.
SPV writes in the Log one row `REVIEW: APPROVED | CHANGES REQUESTED` (600 characters or less) and, if needed, a correction work order in the operator's inbox. Integration happens only on `APPROVED`, in SPV's integration branch; the merge into `<main-branch>` only with the user's consent.

**Operators without a direct channel** (other tools or sessions SPV can neither start nor message): SPV prepares for the user **one self-contained prompt** to paste in their session, and writes it in chat. It holds: ID, sync branch, the handshake sentence, the paths of the inbox (`sync/inbox/<ID>.md`) and of the work order (`sync/wo/<ID>.md`), the working branch, the file perimeter, the rule "after the handshake read the inbox and start without waiting", where to deliver (`DELIVERED`), the `--wakeup` to declare and "if you get blocked, say so in your file and stop". Before giving the prompt SPV has already pushed inbox, work order and the block in `operators.toml`. For operators SPV starts itself, the prompt is the brief of the session it starts, with the same content.

**Profile** (10 lines at most): **where it runs** and its breaking points, **models** and what for, **subagents** (yes/no, which), **strengths and limits**, **tools**. SPV derives `place`, `models`, `subagents`, `strengths`, `weak_points` in `sync/operators.toml` from it.

**Development requirements**: if the project needs them, SPV lists in section 2 the **specific requirements** (toolchain, hardware, emulators, access, models, subagents). Each operator confirms in its own file, `## Requirements`, `YES`, `NO` or `PARTIAL {note}` for each. SPV assigns work orders only to operators that meet them and, if nobody does, tells the user.

**Deliveries (one format)**: when an operator finishes a work order it writes in its own file, section `## Deliveries`, ONE line: `DELIVERED {WO-ID} @ {branch}@{commit} · verify: {command} → {result} · {ISO}`, then marks itself `FREE` (or moves to the next work order). `DONE` is NOT a delivery: it is the terminal state of the session. After reading the line SPV answers in the Log with `REVIEW: APPROVED` or `CHANGES REQUESTED`; only after `APPROVED` is the work integrable. A signal other than `DELIVERED` (free text, `DONE {task}`) starts nothing: SPV asks for it again in the standard format.

**Sign-off**: SPV can **release** an operator from the sync at any time with a Log row `SIGNOFF {ID}: {reason}`. Reasons: no suitable work left, the **requirements** (section 2) are not met, the operator is replaced or too slow or unstable, or the project is over. The operator, after reading the row: 1) starts no new work; 2) closes or delivers what is in progress (commit and push; a long process is declared in its file and SPV decides whether to wait); 3) writes a closing line in its file and marks itself `DONE` with `sync_hdr.py`; 4) stops the heartbeats. SPV marks the operator `DONE` in 1b and in `sync/operators.toml` (`active = false`, `signoff = "{reason}"`); the operator returns only with a new handshake asked by SPV. A sign-off is not a fault: it does not erase commits, and delivered work stays valid and goes to review like the rest. If the operator does not answer within 60 minutes, SPV marks it `IDLE` and tells the user.

**Inboxes, checks and wake-up** (the rules that prevent missed handovers):
- **Inboxes**: every new task and every urgency SPV writes to `sync/inbox/<ID>.md` (5 lines at most, one task; see `sync/inbox/README.md`). The heartbeat checks the `git diff` of the operator's own inbox, not the whole Log. Read receipt: `python tools/sync_hdr.py <ID> --ack auto`.
- **Objective check**: `python tools/sync_check.py` (age, `eta`, `ack`, unread rows, deliveries out of format, inboxes over 5 lines, Log rows over 600 characters). SPV runs it at every check: the state reported to the user is the one it prints, with its time.
- **Log rows 600 characters or less**; the rest goes into the work order or the inbox.
- **Heartbeat cost**: `python tools/sync_watch.py --id <ID> --branch sync/{name}` does the beat with no model and wakes the agent only when its inbox changes; see `docs/progress/sync.md` ("Cost of the heartbeats").
- **Rule changes**: a `RULE` row with ack required; it applies to an operator only after its `ack`.
- **Profile field** `wakeup yes|no` (`--wakeup`): does the agent wake itself up (timer, scheduler)? With `no`, SPV assigns jobs with an explicit `eta` and says when to call it back; the user wakes it with the start phrase (`docs/progress/sync.md`).

---

## 4. Notices to the user

- A Log row that needs a user action (manual sync, merge, key, device) starts with `USER:` and says what is needed.
- The state of every operator (format of 1b) is reported to the user **only on request** (or when someone is `IDLE` or a decision is needed): the truth is the table in 1b.

## 5. Handover Log

Only SPV adds rows. Columns: ISO time with zone · operator · branch/commit · action (`READY`, `REVIEW: APPROVED | CHANGES REQUESTED`, `ASSIGNED`, `RULE`, `SIGNOFF`, `DECISION`, `STOP`, `QUESTION`) · message (600 characters or less).

| Timestamp | Operator | Branch / Commit | Action | Message |
|---|---|---|---|---|
