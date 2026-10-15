---
name: docs-map
description: Map of which file to open for each area and how to read large files without burning tokens. Use it before reading docs/progress*, docs/ROADMAP.md, a spec file or any file over about 15 KB, when you need to find where something lives, or when you must update progress after a change.
---

# Where to read and how to update (little, by sections)

A single index: `docs/progress.md` (areas, navigation, reference docs). Start there. To keep the docs lean after a change use the skill `docs-loop`.

Rule: never a large file in full. `grep -n` on the symbol or on `^##`, then `Read` with `offset`/`limit` on the span. A file already read in the session is not reread.

## Where things are

| Need | File |
|---|---|
| Index of areas | `docs/progress.md` |
| State of one area (how it works, open work, rules) | `docs/progress/<area>.md` |
| Plans by level (ID, priority, status, goal, requirement, details, after) | `docs/ROADMAP.md` |
| Questions nobody has decided yet | `docs/open-decisions.md` |
| What the product promises (revisions, config keys, platforms) | `docs/spec/*.toml` and `docs/spec/CONSISTENCY.md` |
| Known differences between platforms | `docs/spec/divergences.toml` |
| Subagent runs and outcomes | `docs/agents/ledger.txt` |
| Multi-operator sync (on its own branch) | `SYNC.md`, `sync/` |

## Progress sheets (current state, not chronicle)
Every area file has `## How it is today`, `## Open work`, `## Rules (do not break)`.

To update after a change:
1. `grep -n '^##' docs/progress/<area>.md`, read only the subsection of the module you touched.
2. Fix or remove the lines that became false; add only state (files, symbols), never dates or "we did". A closed item leaves `## Open work`.
3. A file over about 120 lines is split by theme (`<area>-<theme>.md`), linked from its parent and from `docs/progress.md`.
4. Roadmap item opened or closed: only its row in `docs/ROADMAP.md` and the milestone line in `docs/progress.md`.

Delegate to `mechanic` when the lines are already decided.

## Large code files (never in full)
Search with `grep -n '<symbol>' <file>` or list definitions with `grep -n '^def \|^class \|^function ' <file> | head -50`, then `Read` the span. Add the search command for a big file to the area sheet so the next reader skips the discovery.

## Wide searches
"Where is X / who uses Y" across several files: the `research` agent (it returns the conclusion, not the files).
