---
name: docs-loop
description: Tidies CLAUDE.md, docs/progress.md and docs/progress/*.md with a measure-driven loop (one change, one measurement, keep or discard) to get a single index, lean docs, fewer rereads and skills from repeated workflows. Use it after editing those files, at the end of a milestone, or when the user asks to optimise the docs or the tokens.
---

# docs-loop: lean docs, a single index, fewer rereads

Measure: `python scripts/docs_audit.py score` (lower is better). It adds the always-loaded tokens (`CLAUDE.md` + `docs/progress.md`), the mean tokens of an area file, and penalties for orphans, broken links, files over about 120 lines, duplicated lines, and a `CLAUDE.md` that does not point to the index.

## 1. Baseline
```bash
python scripts/docs_audit.py score
python scripts/docs_audit.py repeats 30   # prompts and commands repeated in 3 or more sessions
python scripts/docs_audit.py best         # last kept score
```

## 2. Loop (at most 8 rounds, no confirmation between rounds)
One round = one hypothesis, chosen in this order:
1. An audit penalty: orphan (link it from the index), broken link (fix it), file over 120 lines (split by theme `<area>-<theme>.md` and add the line to the index), duplicate (keep one copy and point to it).
2. `CLAUDE.md` is the largest always-loaded file: what applies to one area moves to the `## Rules (do not break)` section of its `docs/progress/<area>.md`, leaving one line in `CLAUDE.md`.
3. A frequently reread file: split it or index it; for large code, add a search command to the area sheet (never line numbers).
4. A line of `docs/progress.md` that does not help to find a file.

For each round:
1. Copy the touched files to `.claude/docs-loop/backup/`.
2. Edit; reread the diff: information is **moved, not lost**.
3. `python scripts/docs_audit.py score`.
4. Score dropped and nothing lost: `python scripts/docs_audit.py log <score> keep "<what>"`. Otherwise restore the backup and `log <score> discard "<what>"`.

Stop after 8 rounds, after 2 discards in a row, or when no hypothesis is left.

## 3. Repeated workflows become skills
From `repeats`: a prompt or command sequence that returns in 3 or more sessions and that no skill covers. Write `.claude/skills/<name>/SKILL.md` (under about 60 lines, the description names the trigger). At most 2 new skills per run.

## 4. Rules
- One index: `docs/progress.md`; `CLAUDE.md` points there and lists no other doc.
- Search with `grep -n`, then read a slice. State, not chronicle; short lines; each topic in one file.
- Commit only when the user asks.

## 5. Closing
Report: score before and after, rounds kept and discarded (`.claude/docs-loop/results.tsv`), skills created or proposed.
