#!/usr/bin/env python3
"""Audit of the CI workflow against the rules that keep it cheap and predictable.

  ci_audit.py [--root DIR] [--workflow PATH] [--gh]

Checks (exit 1 if any fails; stdlib only, the workflow is read as text):
  1. every job of the workflow has `timeout-minutes`, and the workflow has a `concurrency` block;
  2. `on.push` ignores the sync branches (`branches-ignore` lists `sync/**`), so a heartbeat push starts no run;
  3. test waits: in the test files named by `test_globs`, `expect("text", timeout=T)` is flagged when T is lower than the known
     wait for that text (table `[waits]` in <root>/.ci-audit.toml);
  4. every command in `required_run` appears in a `run:` step of the workflow;
  5. with --gh: `gh run list` gives the mean duration and the success share of the last runs (skipped with a warning when gh is missing).

Config (optional) <root>/.ci-audit.toml:
  workflow = ".github/workflows/ci.yml"
  test_globs = ["tests/**/*.py"]
  required_run = ["python scripts/selftest.py"]
  [waits]
  "index rebuild" = 19
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECT = re.compile(r"""expect\(\s*["'](.+?)["'].*?timeout\s*=\s*(\d+(?:\.\d+)?)""")


def load_cfg(root):
    p = os.path.join(root, ".ci-audit.toml")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return tomllib.load(f)
    return {}


def split_jobs(text):
    """{job name: its text} for the children of the top-level `jobs:` key (2-space indentation)"""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if re.match(r"jobs:\s*$", l))
    except StopIteration:
        return {}
    jobs, name, buf = {}, None, []
    for l in lines[start + 1:]:
        if l and not l.startswith((" ", "#")):
            break
        m = re.match(r"  ([\w-]+):\s*$", l)
        if m:
            if name:
                jobs[name] = "\n".join(buf)
            name, buf = m.group(1), []
        elif name:
            buf.append(l)
    if name:
        jobs[name] = "\n".join(buf)
    return jobs


def push_ignores_sync(text):
    m = re.search(r"^on:\s*\n(.*?)(?=^\S)", text + "\nend:", re.S | re.M)
    block = m.group(1) if m else ""
    p = re.search(r"^  push:\s*\n(.*?)(?=^  \S|\Z)", block, re.S | re.M)
    if not p:
        return False
    return bool(re.search(r"branches-ignore:.*?sync/\*\*", p.group(1), re.S))


def audit(root, workflow, cfg):
    problems = []
    wf = os.path.join(root, workflow)
    if not os.path.exists(wf):
        return [f"workflow {workflow} not found"]
    text = open(wf, encoding="utf-8").read()
    jobs = split_jobs(text)
    if not jobs:
        problems.append("no jobs found in the workflow")
    for name, body in jobs.items():
        if not re.search(r"^\s+timeout-minutes:\s*\d+", body, re.M):
            problems.append(f"job '{name}' has no timeout-minutes")
    if not re.search(r"^concurrency:", text, re.M):
        problems.append("the workflow has no concurrency block (superseded runs keep burning minutes)")
    if not push_ignores_sync(text):
        problems.append("on.push does not ignore sync/** (a heartbeat push would start a run)")
    waits = cfg.get("waits", {})
    for g in cfg.get("test_globs", []):
        for full in glob.glob(os.path.join(root, g), recursive=True):
            rel = os.path.relpath(full, root).replace("\\", "/")
            for n, line in enumerate(open(full, encoding="utf-8", errors="replace"), 1):
                m = EXPECT.search(line)
                if not m:
                    continue
                label, t = m.group(1), float(m.group(2))
                for known, secs in waits.items():
                    if known in label and t < secs:
                        problems.append(f"{rel}:{n} waits {t:g} s for '{label}', the known wait is {secs} s")
    runs = "\n".join(re.findall(r"^\s*-?\s*run:\s*(.+)$", text, re.M))
    for cmd in cfg.get("required_run", []):
        if cmd not in runs and cmd not in text:
            problems.append(f"no `run:` step executes `{cmd}`")
    return problems


def gh_stats(root, workflow):
    if not shutil.which("gh"):
        print("gh not found: skipping the run statistics")
        return
    r = subprocess.run(["gh", "run", "list", "-w", os.path.basename(workflow), "-L", "20", "--json", "conclusion,createdAt,updatedAt"],
                       cwd=root, capture_output=True, text=True)
    if r.returncode:
        print("gh run list failed: " + r.stderr.strip()[:120])
        return
    import datetime
    runs = json.loads(r.stdout or "[]")
    secs = []
    for x in runs:
        a = datetime.datetime.fromisoformat(x["createdAt"].replace("Z", "+00:00"))
        b = datetime.datetime.fromisoformat(x["updatedAt"].replace("Z", "+00:00"))
        secs.append((b - a).total_seconds())
    ok = sum(1 for x in runs if x["conclusion"] == "success")
    if runs:
        print(f"last {len(runs)} runs: mean {sum(secs) / len(secs) / 60:.1f} min, success {100 * ok / len(runs):.0f}%")
    else:
        print("no runs yet")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--workflow")
    ap.add_argument("--gh", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    cfg = load_cfg(root)
    workflow = a.workflow or cfg.get("workflow", ".github/workflows/ci.yml")
    problems = audit(root, workflow, cfg)
    for p in problems:
        print("  !", p)
    print(f"ci_audit: {len(problems)} problem(s) in {workflow}")
    if a.gh:
        gh_stats(root, workflow)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
