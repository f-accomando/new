---
schema: 1
id: {ID}
state: FREE
task: handshake
waiting_on: 
progress: 0
wakeup: {yes|no}
ack: 
updated: {ISO 8601 with zone}
---
# {ID} - {name}

> **Only {ID} writes here** (the others read). The supervisor (SPV) reads this file and updates table 1b of `SYNC.md`.
> Update the block with `python tools/sync_hdr.py {ID} --state ... --task ... [--waiting-on] [--progress] [--eta]`, then commit and
> `git pull --rebase origin sync/{name} && git push origin HEAD:sync/{name}`. At every finished task.

## Profile
(10 lines at most: where it runs and its breaking points, **whether it wakes itself up (timer/scheduler: `--wakeup yes|no`)**, models and what for, subagents yes/no, strengths and limits, tools with version)

## Requirements
(only if `SYNC.md` section 2 lists them: for each one `YES`, `NO` or `PARTIAL {note}`)

## Tasks

## Deliveries
(one line per finished work order: `DELIVERED {WO-ID} @ {branch}@{commit} · verify: {command} → {result} · {ISO}`)

## Progress

## Problems

## Requests
