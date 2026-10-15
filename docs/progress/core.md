# core (the example area sheet)

Copy this file for every area (`docs/progress/<area>.md`), then link it from `docs/progress.md`. Keep the three fixed sections. State, not chronicle: no dates, no "we did".

## How it is today

### Module A
- What it does in one line; where it lives (`src/module_a/`); the symbols worth searching (`parse_request`, `Router`).
- How to find things fast: `grep -n 'def parse_request' src/module_a/*.py`.

### Module B
- Same shape. One `###` for each module so a reader can open only the subsection they need.

## Open work

- [ ] Item one: the next thing to do in this area, with the file it touches and the check that proves it done.
- [ ] Item two: link its row in `docs/ROADMAP.md` by ID (for example R1).

## Rules (do not break)

- A rule here is a constraint that keeps the area working; it is stated as what to do ("keep X in Y").
- Add a rule when a constraint is introduced or changed; delete it when it stops being true.
