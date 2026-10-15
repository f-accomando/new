# Inboxes - `sync/inbox/<ID>.md`

Written **only by SPV**, read **only by the recipient**: one task at a time, **5 lines at most**, with the work order, branch, verification command and the expected `eta`. Urgencies go here (not at the bottom of the Log of `SYNC.md`): the heartbeat checks the `git diff` of this file.

The operator, having read the inbox, writes `ack` with `python tools/sync_hdr.py <ID> --ack auto` and marks itself `WORKING`. After the delivery (`DELIVERED ...` in its own file) SPV empties the inbox or fills it with the next task. `python tools/sync_check.py` reports inboxes with more than 5 lines.

Example of a valid inbox:

```
WO-12 (search filters): branch claude/search-filters from main.
Files: src/server/search.py, tests/test_search.py only.
Verify: python -m pytest tests/test_search.py -k filters -> exit 0.
Deliver with a DELIVERED line; expected eta 40 min.
```
