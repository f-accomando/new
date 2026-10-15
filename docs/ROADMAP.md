# Roadmap

Plans by **level**. A level is a set of items that can start once the previous level is done; inside a level, items are independent unless the `After` column says otherwise.
Finished items leave this file (the history is in git); day-to-day detail lives in `docs/progress/<area>.md`.

Columns:

| Column | Meaning |
|---|---|
| **ID** | stable identifier (`R1`, `R2`...), used by commits, work orders and `docs/progress/` |
| **Pri** | 1 = do first ... 5 = nice to have |
| **Status** | `open`, `active`, `blocked`, `suspended` |
| **Goal** | one sentence: what is true when it is done |
| **Requirement** | the checkable "done when": a command, a test, a number |
| **Details** | where the working notes are (an area sheet, a design doc) |
| **After** | IDs that must finish first (`-` if none) |

Size convention (optional, add to Goal): **S** = days, **M** = 1-2 weeks, **L** = more than 2 weeks.

---

## Level 1: foundations

| ID | Pri | Status | Goal | Requirement | Details | After |
|---|---|---|---|---|---|---|
| R1 | 1 | active | The example area builds and passes its checks (S) | `<build-cmd>` and `<test-cmd>` exit 0 on a clean clone | [core](progress/core.md) | - |
| R2 | 2 | open | Every config key the code reads is registered (S) | `python scripts/consistency.py check` prints 0 drift | [CONSISTENCY](spec/CONSISTENCY.md) | R1 |

## Level 2: the first release

| ID | Pri | Status | Goal | Requirement | Details | After |
|---|---|---|---|---|---|---|
| R3 | 1 | open | The release gate is empty (M) | `python scripts/consistency.py gate` prints 0 blockers | [CONSISTENCY](spec/CONSISTENCY.md) | R2 |
| R4 | 3 | open | CI finishes in under 10 minutes (S) | `python scripts/ci_audit.py --gh` shows a mean under 10 min | `.github/workflows/ci.yml` | R1 |

## Level 3: later

| ID | Pri | Status | Goal | Requirement | Details | After |
|---|---|---|---|---|---|---|
| R5 | 4 | suspended | An idea waiting for a decision (M) | recorded in [open-decisions](open-decisions.md) | [open-decisions](open-decisions.md) | R3 |

---

## Decisions in force

- {Decision, date, one line of reason.} Remove it when it stops being true.

## Ideas (not scheduled)

- Ideas are appended here as `R<n>` lines and promoted into a level when someone takes them.
