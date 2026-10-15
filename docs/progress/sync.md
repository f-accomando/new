# sync (multi-operator coordination)

The protocol itself is `SYNC.md` (template on the main branch; the live copy lives on the project's `sync/<name>` branch).
This sheet holds the rules and the lessons that shaped it. Tools: `tools/sync_hdr.py`, `tools/sync_check.py`, `tools/sync_watch.py`.

## How it is today

- One **sync branch** per project, `sync/<name>`, cut from the main branch. `SYNC.md`, `sync/*` and `tools/sync_*.py` are pushed only there; the main branch keeps the templates.
- SPV (supervisor) writes `SYNC.md`, work orders (`sync/wo/<ID>.md`) and inboxes (`sync/inbox/<ID>.md`). Every other operator writes only `sync/<ID>.md`.
- State lives in a block at the top of each operator file, written by `sync_hdr.py` with ISO 8601 times and a zone.
- `sync_check.py` prints who is alive, who has not acknowledged what, malformed deliveries, long inboxes and long Log rows.
- Review of every delivery by an independent subagent in a temporary worktree (`SYNC.md` section 3c).

### Cost of the heartbeats
A heartbeat is `git fetch`, a look at the inbox and `sync_hdr.py <ID> --ack auto`. What costs is who runs it (orders of magnitude):

| Who runs the beat | Cost of one beat | Note |
|---|---|---|
| The main agent (a timer that re-sends a prompt) | rereads the whole conversation: hundreds of thousands of cached tokens | the most expensive; breaks if the session has no timer |
| A small subagent (cheap model, empty context) | about 5-15 thousand tokens | tens of times cheaper |
| A script, no model: `sync_watch.py` | 0 tokens | wakes the model only when its inbox or an addressed row changes |

### Lessons that became rules
1. A message is seen only when its reader polls: use inboxes, `ack`, and `sync_watch.py`; a stop order that nobody read costs the whole run it should have stopped.
2. Silence is ambiguous: `eta` is mandatory in `WORKING` and `WAITING`; silence before `eta` is not `IDLE`.
3. Two sources of truth drift: the status table is generated from the operator files; SPV reports only what a file says, with its time.
4. Times without a zone mislead: ISO 8601 with a zone everywhere, written by the tool, not by hand.
5. Steps that wait for the supervisor: authorise independent steps in sequence with one review at the end.
6. Stand-in files cause rework: use real files, or a probe against a real one, before scripting on top.
7. Long rows are skimmed: 600 characters at most; procedures live in the work order.
8. The writer needs a separate worktree for the sync branch, or pushes collide with the working branch.
9. A hypothesis sent as an instruction costs the reader a check: label it `HYPOTHESIS`.
10. A short probe (20-50 s) before every long run finds the errors that would show at its end.

## Open work

- [ ] Fill `sync/operators.toml` and section 2 of `SYNC.md` when a new project starts a sync.

## Rules (do not break)

- One writer per file: `SYNC.md` only SPV; `sync/<ID>.md` only `<ID>`.
- Sync files are pushed only to `sync/<name>`, with `git pull --rebase`, never a merge commit.
- Code reaches the main branch only after `REVIEW: APPROVED` and with the user's consent.
- Deliveries use one line: `DELIVERED {WO-ID} @ {branch}@{commit} · verify: {command} → {result} · {ISO}`.
- Inboxes hold 5 lines at most; Log rows 600 characters at most; tasks take 45 minutes or less.
- A rule change is a `RULE` row, valid for an operator only after its `ack`.
