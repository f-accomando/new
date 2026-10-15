---
name: work-order
description: Generator and validator of Work Orders. Applies the Readiness Gate (5 questions) to decide whether a task can go to mechanic, coder or light, or must be made ready by planner first. Use it whenever you are about to delegate a task or write a Work Order.
---

# Work Orders and the Readiness Gate

Goal: maximum token efficiency, deterministic diffs, no decision taken by the executing agent.

## 1. The Readiness Gate (5 questions)
Answer before assigning a task to execution:

1. **Explicit files/functions**: are the paths and the exact symbols to touch named?
2. **Diff determinism**: would two programmers write the same diff (no open design choice)?
3. **Verifiable criterion**: is there a deterministic command (test, build, lint, assertion)?
4. **Contained scope**: about 3 files or fewer?
5. **No pending dependency**: does it avoid any decision still to be made?

Outcome:
- **5 out of 5 YES**: READY. Pick `mechanic` (pure mechanics), `coder` (code from the order) or `light` (needs a little judgment).
- **At least one NO**: NOT READY. Invoke `planner` to resolve the ambiguity and produce one or more Work Orders. Never send it straight to `deep`.

## 2. Template

```markdown
### WORK ORDER: [SHORT-ID]
- **Objective**: [one clear sentence]
- **Files/functions to touch**: [exact paths and symbols]
- **Required change**: [expected diff, parameters, logic; no ambiguity]
- **Verification command**: [for example `<test-cmd> -k search`]
- **Expected result**: [exit code 0 / specific output]
- **Assigned agent**: [mechanic | coder | light]
```

Size: a Work Order takes 45 minutes or less (target 15). Larger work is split into steps, one order each.

## 3. Closing protocol
The executing agent returns exactly one status:
- `DONE`: the verification command ran and passed; a brief diff summary follows.
- `BLOCKED: <reason>`: incomplete specification, mismatched signature or missing decision; back to `planner`.
- `FAILED x2`: two consecutive failed attempts; escalate one level (coder to light, light to deep).

## 4. Ledger
After each finished subagent run append one row to `docs/agents/ledger.txt`:
`date|agent|model|task|area|gate|necessity|outcome|tokens|tools|secs` (`-` for gate or necessity when not applicable).
`python scripts/agent_audit.py` turns the rows into the calibration report.
