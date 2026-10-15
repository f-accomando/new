# The workflow in one page

A project workflow for AI-assisted development with Claude Code and Google Antigravity. It is neutral: replace `<PROJECT>`, `<area>`, `<build-cmd>`, `<test-cmd>` and the example content, keep the structure.
The long version, with a TL;DR and practical examples for every point, is the PDF [`scaffold-workflow-EN.pdf`](../scaffold-workflow-EN.pdf), built by `python scripts/build_workflow_pdf.py`.

## The idea

Separate **deciding** from **executing**: an expensive model writes short plans, a cheap model writes the code from a precise order. Everything an agent needs is reachable by a targeted search, every rule lives in one place, every claim is checked by a script.

## Map of the files

| Point | What it is | Where |
|---|---|---|
| Session notes for the agent | retrieval commands, rules of engagement, routing, gate, escalation, necessity, closure, sync | [`CLAUDE.md`](../CLAUDE.md), [`AGENTS.md`](../AGENTS.md), [`GEMINI.md`](../GEMINI.md) |
| Subagent roles | planner, coder, mechanic, light, deep, research, ops | `.claude/agents/*.md` |
| Skills | work orders, docs tidy-up loop, docs map | `.claude/skills/work-order`, `.claude/skills/docs-loop`, `.claude/skills/docs-map` |
| Docs system | one index, one sheet per area with `Open work` and `Rules (do not break)` | [`docs/progress.md`](progress.md), [`docs/progress/`](progress/core.md) |
| Roadmap | levels, with ID / Pri / Status / Goal / Requirement / Details / After | [`docs/ROADMAP.md`](ROADMAP.md) |
| Open questions | one section per area | [`docs/open-decisions.md`](open-decisions.md) |
| Readiness Gate | five questions before delegating | `CLAUDE.md` section 3, skill `work-order` |
| Ledger | one row per subagent run | `docs/agents/ledger.txt`, `scripts/agent_audit.py` |
| Consistency gate | spec registry, config keys, platforms, divergences | [`docs/spec/CONSISTENCY.md`](spec/CONSISTENCY.md), `scripts/consistency.py` |
| Docs audit | one number for the health of the docs | `scripts/docs_audit.py` |
| CI audit | timeouts, concurrency, ignored sync branches, test waits | `scripts/ci_audit.py`, `.ci-audit.toml` |
| Multi-operator sync | roles, states, inboxes, deliveries, reviews, sign-off | [`SYNC.md`](../SYNC.md), `sync/`, `tools/sync_*.py`, [`docs/progress/sync.md`](progress/sync.md) |
| Self-test | runs every script on the demo and breaks the demo on purpose | `scripts/selftest.py`, `examples/demo/` |

## Starting a project (short)

1. Copy the files above into the new repository; replace the placeholders in `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` and `.claude/agents/*.md`.
2. Write `docs/progress.md` and one `docs/progress/<area>.md` per area (with `Open work` and `Rules (do not break)`).
3. Fill `docs/spec/` and `docs/spec/consistency.toml` for the facts you keep in step across files.
4. Put `python scripts/selftest.py` (or your own checks) in CI and run `python scripts/ci_audit.py`.
5. Work: planner for vague tasks, the Readiness Gate for everything else, a ledger row per subagent run, the closure checklist at the end of each task.
6. For several operators: branch `sync/<name>`, copy `SYNC.md` and `sync/`, do the handshake.

## Checks you run

```bash
python scripts/selftest.py               # everything below on the demo, plus negative tests
python scripts/docs_audit.py score       # docs health
python scripts/consistency.py check      # drift between files and platforms
python scripts/consistency.py gate       # what blocks the release
python scripts/agent_audit.py            # ledger statistics
python scripts/ci_audit.py [--gh]        # CI rules
python tools/sync_check.py               # sync health (on the sync branch)
```

The scripts take `--root DIR` to audit another project folder (for example `examples/demo`).
