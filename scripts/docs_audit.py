#!/usr/bin/env python3
"""Audit of the tracking docs, for the docs-loop skill.

  docs_audit.py score [--json]   one number (lower is better) and what makes it up
  docs_audit.py repeats [DAYS]   prompts and commands repeated across sessions (skill candidates)
  docs_audit.py log SCORE keep|discard "what changed"   append to .claude/docs-loop/results.tsv
  docs_audit.py best             last kept score

Options (before the command): --root DIR   audit another project folder (default: the folder above scripts/).

Score = tokens always loaded (CLAUDE.md + docs/progress.md) + mean tokens of the area file
reached from the index + penalties (orphans, broken links, oversize files, duplicated lines).
Tokens are bytes / 4. Nothing here writes to the docs. Exit 0 when there is no penalty, 1 otherwise."""
import glob
import json
import os
import re
import sys
import time
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
INDEX = "docs/progress.md"
LIMIT_LINES = 120
P_ORPHAN, P_BROKEN, P_BIG, P_DUP, P_NOINDEX = 500, 300, 200, 50, 2000


def loop_file():
    return os.path.join(ROOT, ".claude", "docs-loop", "results.tsv")


def rd(rel):
    try:
        return open(os.path.join(ROOT, rel), encoding="utf8", errors="replace").read()
    except OSError:
        return ""


def tok(rel):
    try:
        return os.path.getsize(os.path.join(ROOT, rel)) / 4
    except OSError:
        return 0


def tracked():
    out = ["CLAUDE.md", INDEX]
    out += sorted(os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "docs", "progress", "*.md")))
    return out


def md_links(rel):
    base = os.path.dirname(rel)
    for m in re.finditer(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", rd(rel)):
        yield os.path.normpath(os.path.join(base, m.group(1))).replace("\\", "/")


def named_paths(rel):
    """backticked paths such as `scripts/tool.py` whose first folder exists in the project"""
    for m in re.finditer(r"`([\w.-]+/[\w./-]+\.\w+)`", rd(rel)):
        p = m.group(1)
        first = p.split("/")[0]
        if "*" in p or "<" in p or p.startswith(".") or not os.path.isdir(os.path.join(ROOT, first)):
            continue
        yield p


def cmd_score(as_json):
    files = tracked()
    always = tok("CLAUDE.md") + tok(INDEX)
    linked = sorted(set(md_links(INDEX)))
    area = [x for x in linked if x.startswith("docs/progress/")]
    mean_area = sum(tok(a) for a in area) / max(1, len(area))
    pen = []
    for f in files[2:]:
        if f not in linked:
            pen.append((P_ORPHAN, f"orphan: {f} is not linked from the index"))
    for f in files:
        for link in md_links(f):
            if not os.path.exists(os.path.join(ROOT, link)):
                pen.append((P_BROKEN, f"broken link in {f}: {link}"))
        for p in named_paths(f):
            if not os.path.exists(os.path.join(ROOT, p)):
                pen.append((P_BROKEN, f"missing file named in {f}: {p}"))
    for f in files[2:]:
        n = rd(f).count("\n")
        if n > LIMIT_LINES:
            pen.append((P_BIG, f"{f} has {n} lines (limit ~{LIMIT_LINES}): split by topic"))
    seen = defaultdict(set)
    for f in files:
        for line in rd(f).splitlines():
            t = line.strip()
            if len(t) >= 60 and not t.startswith(("|", "#")):
                seen[t].add(f)
    for t, fs in seen.items():
        if len(fs) > 1:
            pen.append((P_DUP, f"duplicated in {', '.join(sorted(fs))}: {t[:50]}..."))
    if "docs/progress.md" not in rd("CLAUDE.md"):
        pen.append((P_NOINDEX, "CLAUDE.md does not point to the single index docs/progress.md"))
    score = always + mean_area + sum(p for p, _ in pen)
    res = {
        "score": round(score), "always_loaded": round(always), "mean_area": round(mean_area),
        "penalty": sum(p for p, _ in pen), "penalties": [m for _, m in pen],
        "files": {f: round(tok(f)) for f in files},
    }
    if as_json:
        print(json.dumps(res, indent=1))
    else:
        print(f"score {res['score']}  (always loaded {res['always_loaded']} + mean area {res['mean_area']} + penalties {res['penalty']})")
        for f, t in sorted(res["files"].items(), key=lambda x: -x[1])[:6]:
            print(f"  {t:6d} tok  {f}")
        for m in res["penalties"][:15]:
            print("  !", m)
    return 1 if pen else 0


def norm(s):
    s = s.lower()
    s = re.sub(r"[a-z]:[\\/][^\s]*|/[\w./-]+", "<path>", s)
    s = re.sub(r"\d+", "N", s)
    return re.sub(r"\s+", " ", s).strip()


def cmd_repeats(days):
    d = os.path.join(HOME, ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", ROOT))
    cutoff = time.time() - days * 86400
    prompts, cmds = defaultdict(set), defaultdict(set)
    for f in glob.glob(os.path.join(d, "*.jsonl")):
        if os.path.getmtime(f) < cutoff:
            continue
        sid = os.path.basename(f)
        for line in open(f, encoding="utf8", errors="replace"):
            if '"type":"user"' in line or '"name":"Bash"' in line:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                c = (r.get("message") or {}).get("content")
                if r.get("type") == "user" and isinstance(c, str) and not c.startswith("<") and not r.get("isSidechain"):
                    key = " ".join(norm(c).split()[:7])
                    if len(key) > 12:
                        prompts[key].add(sid)
                elif isinstance(c, list):
                    for b in c:
                        if b.get("type") == "tool_use" and b.get("name") == "Bash":
                            key = " ".join(norm((b.get("input") or {}).get("command", "")).split()[:4])
                            if len(key) > 8:
                                cmds[key].add(sid)
    skills = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md"))}
    print(f"existing skills: {', '.join(sorted(skills)) or 'none'}")
    print("repeated prompts (3 or more sessions):")
    for k, s in sorted(prompts.items(), key=lambda x: -len(x[1])):
        if len(s) >= 3:
            print(f"  {len(s):3d}  {k}")
    print("repeated commands (3 or more sessions):")
    for k, s in sorted(cmds.items(), key=lambda x: -len(x[1]))[:15]:
        if len(s) >= 3:
            print(f"  {len(s):3d}  {k}")
    return 0


def cmd_log(a):
    path = loop_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf8") as f:
        if new:
            f.write("time\tscore\tstatus\tchange\n")
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')}\t{a[0]}\t{a[1]}\t{a[2] if len(a) > 2 else ''}\n")
    return 0


def cmd_best():
    try:
        rows = [x.split("\t") for x in open(loop_file(), encoding="utf8").read().splitlines()[1:]]
    except OSError:
        print("none")
        return 0
    kept = [r for r in rows if len(r) > 2 and r[2] == "keep"]
    print(kept[-1][1] if kept else "none")
    return 0


def main(argv):
    global ROOT
    argv = list(argv)
    if "--root" in argv:
        i = argv.index("--root")
        ROOT = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    c = argv[0] if argv else ""
    a = argv[1:]
    if c == "score":
        return cmd_score("--json" in a)
    if c == "repeats":
        return cmd_repeats(int(a[0]) if a else 30)
    if c == "log" and len(a) >= 2:
        return cmd_log(a)
    if c == "best":
        return cmd_best()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
