# <PROJECT> progress (the one index)

**Start here.** This is the only file `CLAUDE.md` sends you to: every other doc is reached from a line below.
Find the line, `grep -n '^##'` the file it names, read one section.

Working notes on the **current** state of <PROJECT>, for whoever changes the code: how each area is built today, what is open,
and the rules that keep it working. One topic lives in one file; the others link to it.

Not here: history (git log), measurements, plans ([`docs/ROADMAP.md`](ROADMAP.md)), working rules (`CLAUDE.md`).

## Areas

| File | Scope | Main code |
|---|---|---|
| [core](progress/core.md) | the example area: replace it with your own, one file per area | `src/` |
| [sync](progress/sync.md) | multi-agent sync: rules, lessons, cost of heartbeats | `SYNC.md`, `sync/`, `tools/` |

## Which section to open

Open the file of the area and `grep -n '^##'` it; read only the section you need. Every area file ends with *Open work* and *Rules (do not break)*.

- The example area: [core](progress/core.md).
- Several operators on one repository (`SYNC.md`, `sync/`): [sync](progress/sync.md).

## Reference docs (not progress)

How the whole workflow fits together: [`docs/WORKFLOW.md`](WORKFLOW.md) · plans by level: [`docs/ROADMAP.md`](ROADMAP.md) · consistency and the release gate:
[`docs/spec/CONSISTENCY.md`](spec/CONSISTENCY.md) · open decisions: [`docs/open-decisions.md`](open-decisions.md) · subagent runs: `docs/agents/ledger.txt`.

## Active milestones by area

- R1 (the example item of the roadmap): [core](progress/core.md)
