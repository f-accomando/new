---
schema: 1
id: ALPHA
state: DONE
task: project closed
waiting_on: 
wakeup: no
ack: 2026-10-01T12:00+02:00
updated: 2026-10-01T12:10+02:00
---
# ALPHA - operator for the server filters

## Profile
- Runs on a laptop (Linux), Claude Code CLI; breaks if the laptop sleeps for more than 30 minutes.
- Models: Sonnet for the work, Haiku subagent for heartbeats and tests. Subagents: yes (`coder`, `ops`).
- Strengths: Python, API design. Limits: no phone, no browser.
- Tools: python 3.12, pytest 8.2, git 2.45.

## Requirements
- python 3.11 or newer: YES
- pytest: YES
- a phone to try the mobile client: NO

## Tasks
- WO-1 filter parser, WO-1b empty-value fix (both on `claude/search-filters`).

## Deliveries
DELIVERED WO-1 @ claude/search-filters@a1b2c3d · verify: python -m pytest tests/test_search.py -k filters → 6 passed · 2026-10-01T10:30+02:00
DELIVERED WO-1b @ claude/search-filters@e4f5a6b · verify: python -m pytest tests/test_search.py -k filters → 8 passed · 2026-10-01T11:10+02:00

## Progress
- read 2026-10-01T10:40+02:00: CHANGES REQUESTED on WO-1, empty `tag=` returns every task; fixing as WO-1b.

## Problems
- none open

## Requests
- none
