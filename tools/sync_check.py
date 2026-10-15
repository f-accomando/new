#!/usr/bin/env python3
"""Objective check of the sync (SYNC.md section 3c): who is alive, who has read what, what breaks the protocol.

  python3 tools/sync_check.py [--strict] [--root DIR]

For every active operator of sync/operators.toml it reads the status block of sync/<ID>.md and prints:
  age of `updated`, `eta`, `ack` (the last Log row of SYNC.md it declares read), the Log rows addressed to it after that `ack`
  (unread), the size of its inbox sync/inbox/<ID>.md, and the problems:
  - no or broken status block; state not in DONE/WORKING/WAITING/IDLE/FREE;
  - IDLE by rule: WORKING/WAITING more than 10 min past its `eta` without an update, or 60 min without `eta` (never FREE/DONE);
  - unread: a row addressed to the operator is older than 30 min and newer than its `ack`;
  - a line of `## Deliveries` that is not `DELIVERED {WO-ID} @ {branch}@{commit} · verify: ... → ... · {ISO}`;
  - the inbox has more than 5 non-empty lines;
  - Log rows longer than 600 characters (ALL rows of the Log, not only the last ones).
A Log row is addressed to an operator when its message column names the ID, or the word ALL.
The state to tell the user is the one printed here (file, with its time), never a guess. Exit 1 with --strict if there is any problem.
Options: --root DIR (project folder holding SYNC.md and sync/; default: the folder above tools/), also the env var SYNC_ROOT."""
import datetime
import os
import re
import sys
import tomllib

ROOT = os.path.abspath(os.environ.get("SYNC_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATES = ("DONE", "WORKING", "WAITING", "IDLE", "FREE")
IDLE_MIN, LATE_MIN, UNREAD_MIN, ROW_MAX, INBOX_MAX = 60, 10, 30, 600, 5
DELIVERED = re.compile(r"^[-*]?\s*DELIVERED\s+\S+\s+@\s+\S+@\S+\s+[·\-]\s+verify:\s+.+(?:→|->).+[·\-]\s+\d{4}-\d\d-\d\dT\d\d:\d\d")


def toml_ops():
    """[(id, active)] from sync/operators.toml; humans are never checked"""
    path = os.path.join(ROOT, "sync", "operators.toml")
    with open(path, "rb") as f:
        ops = tomllib.load(f).get("operator", [])
    return [(o["id"], o.get("active", True) and o.get("kind") != "human") for o in ops]


def header(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None
    d = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        val = re.split(r"\s+#", v)[0].strip() if "#" in v else v.strip()
        d[k.strip()] = val
    return d


def iso(s):
    try:
        t = datetime.datetime.fromisoformat(s)
        return t if t.tzinfo else t.astimezone()
    except (ValueError, TypeError):
        return None


def rows(path):
    """[(datetime, full line)] of the Log rows `| 2026-10-14 18:35 | ...`"""
    out = []
    if not os.path.exists(path):
        return out
    local = datetime.datetime.now().astimezone().tzinfo
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d)(\S*)\s*\|", line)
        if m:
            t = iso(m.group(1) + "T" + m.group(2) + (m.group(3) or ""))
            if t:
                out.append((t if t.tzinfo else t.replace(tzinfo=local), line.rstrip("\r\n")))
    return out


def line(*cols):
    return "%-6s %-8s %5s %-17s %-17s %6s %5s  %s" % cols


def main(argv=None):
    global ROOT
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--root" in argv:
        i = argv.index("--root")
        ROOT = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    now = datetime.datetime.now().astimezone()
    log = rows(os.path.join(ROOT, "SYNC.md"))
    problems = []
    print("sync check at %s (Log rows: %d, last %s)" % (now.strftime("%H:%M"), len(log), log[-1][0].strftime("%H:%M") if log else "-"))
    print(line("ID", "state", "age", "eta", "ack", "unread", "inbox", "notes"))
    for oid, active in toml_ops():
        if not active:
            continue
        path = os.path.join(ROOT, "sync", oid + ".md")
        notes = []
        if not os.path.exists(path):
            print(line(oid, "-", "-", "-", "-", "-", "-", "no file"))
            problems.append("%s: no sync/%s.md (handshake not done)" % (oid, oid))
            continue
        text = open(path, encoding="utf-8").read()
        h = header(text)
        if not h:
            print(line(oid, "-", "-", "-", "-", "-", "-", "no status"))
            problems.append("%s: no status block (write it with tools/sync_hdr.py)" % oid)
            continue
        state = h.get("state", "")
        if state not in STATES:
            problems.append("%s: state '%s' is not one of %s" % (oid, state, "/".join(STATES)))
        upd, eta, ack = iso(h.get("updated", "")), iso(h.get("eta", "")), iso(h.get("ack", ""))
        age = int((now - upd).total_seconds() // 60) if upd else None
        if age is None:
            problems.append("%s: `updated` missing or not ISO 8601 with zone" % oid)
        elif state in ("WORKING", "WAITING") and not eta and oid != "SPV" and age > IDLE_MIN:
            problems.append("%s: IDLE by rule (no update for %d min, no eta); tell the user" % (oid, age))
            notes.append("IDLE")
        elif state in ("WORKING", "WAITING") and eta and oid != "SPV" and int((now - eta).total_seconds() // 60) > LATE_MIN and upd <= eta:
            problems.append("%s: IDLE by rule (no update for %d min, eta %s); tell the user" % (oid, age, h.get("eta")))
            notes.append("IDLE")
        elif state in ("WORKING", "WAITING") and not eta and oid != "SPV":
            notes.append("no eta")
        seen = ack or upd  # without `ack` an operator is taken to have read up to its last update
        addressed = []
        for t, ln in log:
            if seen and t <= seen:
                continue
            cols = ln.split("|")
            author = cols[2] if len(cols) > 2 else ""
            if re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(oid), author):
                continue
            body = "|".join(cols[4:]) if len(cols) > 4 else ln
            if re.search(r"(?<![A-Za-z])%s(?![A-Za-z])|(?<![A-Za-z])ALL(?![A-Za-z])" % re.escape(oid), body):
                addressed.append(t)
        stale = [t for t in addressed if (now - t).total_seconds() > UNREAD_MIN * 60]
        if stale and oid != "SPV" and state != "DONE":
            problems.append("%s: %d row(s) addressed to it not acknowledged (oldest %s, ack %s)" % (oid, len(stale), min(stale).strftime("%H:%M"), h.get("ack") or "none"))
        if not h.get("ack") and oid != "SPV":
            notes.append("no ack")
        if h.get("wakeup") not in ("yes", "no"):
            notes.append("wakeup?")
        m = re.search(r"^## Deliveries\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        for ln in (m.group(1).splitlines() if m else []):
            if ln.strip() and not ln.strip().startswith("(") and not DELIVERED.match(ln.strip()):
                problems.append("%s: not a standard delivery line: %s" % (oid, ln.strip()[:70]))
        inbox = os.path.join(ROOT, "sync", "inbox", oid + ".md")
        n_in = sum(1 for x in open(inbox, encoding="utf-8") if x.strip()) if os.path.exists(inbox) else 0
        if n_in > INBOX_MAX:
            problems.append("%s: inbox has %d lines (max %d)" % (oid, n_in, INBOX_MAX))
        print(line(oid, state, "%sm" % age if age is not None else "?", h.get("eta", "")[:16] or "-", h.get("ack", "")[:16] or "-", len(addressed), n_in or "-", " ".join(notes)))
    for t, ln in log:
        if len(ln) > ROW_MAX:
            problems.append("Log row of %s is %d chars (max %d): %s..." % (t.strftime("%H:%M"), len(ln), ROW_MAX, ln[28:70]))
    print()
    for p in problems:
        print("  ! " + p)
    print("%d problem(s)" % len(problems))
    return 1 if (problems and "--strict" in argv) else 0


if __name__ == "__main__":
    sys.exit(main())
