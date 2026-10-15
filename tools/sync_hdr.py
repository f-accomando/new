#!/usr/bin/env python3
"""Writes the status block at the top of sync/<ID>.md (--- ... ---) with `updated` taken from the clock (ISO 8601, time zone).

  python3 tools/sync_hdr.py ALPHA --state WORKING --task "WO-12 step 3" [--waiting-on user] [--progress 40] [--eta 2026-10-14T12:20+02:00]
  python3 tools/sync_hdr.py ALPHA --ack auto          # a heartbeat that also acknowledges the last Log row of SYNC.md
  python3 tools/sync_hdr.py ALPHA --wakeup no         # profile: this agent has no autonomous wake-up (yes | no)

state: DONE | WORKING | WAITING | IDLE | FREE;  waiting_on (only with WAITING): who must act (user, another operator, a service).
The text of the file is kept; only the block changes. A missing file is created with the section skeleton.
Options: --root DIR (project folder holding SYNC.md and sync/; default: the folder above tools/), also the env var SYNC_ROOT.
Then: git add sync/<ID>.md && git commit && git pull --rebase origin sync/<name> && git push origin HEAD:sync/<name>."""
import argparse
import datetime
import os
import re
import sys

ROOT = os.path.abspath(os.environ.get("SYNC_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATES = ("DONE", "WORKING", "WAITING", "IDLE", "FREE")
KEYS = ["schema", "id", "state", "task", "waiting_on", "progress", "eta", "wakeup", "ack", "updated"]
SKELETON = ("# {id}\n\n## Profile\n\n## Requirements\n\n## Tasks\n\n## Deliveries\n\n## Progress\n\n## Problems\n\n## Requests\n")


def parse(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}, text
    d = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        val = re.split(r"\s+#", v)[0].strip() if "#" in v else v.strip()
        d[k.strip()] = val
    return d, text[m.end():]


def last_row_time(root):
    """ISO time of the last Log row of SYNC.md: `| 2026-10-14 18:35 | ...` (the local zone when the row has none)"""
    path = os.path.join(root, "SYNC.md")
    last = ""
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"\|\s*(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d)(\S*)", line)
            if m:
                tz = m.group(3).strip()
                if not tz or not (tz.startswith("+") or tz.startswith("-") or tz == "Z"):
                    z = datetime.datetime.now().astimezone().strftime("%z")
                    tz = z[:3] + ":" + z[3:]
                last = "%sT%s%s" % (m.group(1), m.group(2), tz)
    return last


def main(argv=None):
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id")
    ap.add_argument("--state", choices=STATES)
    ap.add_argument("--task")
    ap.add_argument("--waiting-on", dest="waiting_on")
    ap.add_argument("--progress", type=int)
    ap.add_argument("--eta")
    ap.add_argument("--ack", help="ISO time of the last SYNC.md Log row read, or `auto` (the last row now in SYNC.md)")
    ap.add_argument("--wakeup", choices=("yes", "no"), help="does the agent wake itself up (timer, scheduler)?")
    ap.add_argument("--file")
    ap.add_argument("--root")
    a = ap.parse_args(argv)
    if a.root:
        ROOT = os.path.abspath(a.root)
    path = a.file or os.path.join(ROOT, "sync", a.id + ".md")
    text = open(path, encoding="utf-8", newline="").read() if os.path.exists(path) else SKELETON.format(id=a.id)
    nl = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    d, body = parse(text)
    d.update({"schema": "1", "id": a.id})
    if a.state:
        d["state"] = a.state
        if a.state != "WAITING":
            d["waiting_on"] = ""
    if a.task is not None:
        d["task"] = a.task
    if a.waiting_on is not None:
        d["waiting_on"] = a.waiting_on
    if a.progress is not None:
        d["progress"] = str(a.progress)
    if a.eta is not None:
        d["eta"] = a.eta
    if a.wakeup:
        d["wakeup"] = a.wakeup
    if a.ack:
        d["ack"] = last_row_time(ROOT) if a.ack == "auto" else a.ack
    if d.get("state") not in STATES:
        sys.exit("state? one of %s (use --state)" % "/".join(STATES))
    if d["state"] in ("WORKING", "WAITING") and not d.get("eta"):
        print("warning: %s without eta; the protocol requires one (--eta ISO)" % d["state"], file=sys.stderr)
    d["updated"] = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    head = "---\n" + "\n".join("%s: %s" % (k, d.get(k, "")) for k in KEYS if k in d or k == "waiting_on") + "\n---\n"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write((head + body).replace("\n", nl))
    print("%s: %s %s (updated %s)" % (path, d["state"], d.get("task", ""), d["updated"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
