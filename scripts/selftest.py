#!/usr/bin/env python3
"""Self-test of the workflow scripts: runs every script on the demo project (examples/demo) and on this repository's own templates.

  python scripts/selftest.py [-v]

Two kinds of check:
  * positive: the script must exit with the expected code on a healthy project (for example 0);
  * negative: a temporary copy of the demo is broken on purpose (a missing timeout, a broken link, a drift, a bad ledger row, a bad
    delivery line, a late operator) and the script must notice (exit 1).
Exit 0 only when every check passes. Plain Python 3.11+, no dependencies, nothing outside the temporary folder is modified."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "examples", "demo")
PY = sys.executable
results = []
VERBOSE = "-v" in sys.argv


def run(args, expect, name, cwd=ROOT):
    r = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = r.returncode == expect
    results.append((ok, name, r.returncode, expect))
    if not ok or VERBOSE:
        print(("PASS " if ok else "FAIL ") + name + f" (exit {r.returncode}, expected {expect})")
        if not ok:
            print("   " + (r.stdout + r.stderr).strip().replace("\n", "\n   ")[:1500])
    return r


def sub(path, old, new):
    text = open(path, encoding="utf-8").read()
    if old not in text:
        raise SystemExit(f"selftest setup error: '{old}' not found in {path}")
    open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new, 1))


def fresh(tmp, label):
    dst = os.path.join(tmp, label)
    shutil.copytree(DEMO, dst)
    return dst


def main():
    s = lambda n: os.path.join(ROOT, "scripts", n)  # noqa: E731
    t = lambda n: os.path.join(ROOT, "tools", n)  # noqa: E731

    # every script compiles
    for f in sorted(os.listdir(os.path.join(ROOT, "scripts"))) + ["../tools/" + x for x in sorted(os.listdir(os.path.join(ROOT, "tools")))]:
        if f.endswith(".py"):
            full = os.path.normpath(os.path.join(ROOT, "scripts", f))
            try:
                compile(open(full, encoding="utf-8").read(), full, "exec")
                ok = True
            except SyntaxError as exc:
                print(f"FAIL compiles {os.path.basename(f)}: {exc}")
                ok = False
            results.append((ok, f"compiles {os.path.basename(f)}", 0 if ok else 1, 0))

    # positive: the demo
    run([s("docs_audit.py"), "--root", DEMO, "score"], 0, "docs_audit demo")
    run([s("consistency.py"), "--root", DEMO, "check"], 0, "consistency check demo")
    run([s("consistency.py"), "--root", DEMO, "report"], 0, "consistency report demo")
    run([s("consistency.py"), "--root", DEMO, "gate"], 1, "consistency gate demo (blockers by design)")
    run([s("agent_audit.py"), "--root", DEMO], 0, "agent_audit demo")
    run([s("ci_audit.py"), "--root", DEMO], 0, "ci_audit demo")
    run([t("sync_check.py"), "--strict", "--root", DEMO], 0, "sync_check demo")
    # positive: the repository's own templates
    run([s("docs_audit.py"), "score"], 0, "docs_audit templates")
    run([s("consistency.py"), "check"], 0, "consistency check templates")
    run([s("consistency.py"), "gate"], 0, "consistency gate templates")
    run([s("agent_audit.py")], 0, "agent_audit templates")
    run([s("ci_audit.py")], 0, "ci_audit templates")
    run([t("sync_watch.py"), "--help"], 0, "sync_watch --help")

    with tempfile.TemporaryDirectory() as tmp:
        # negative: ci_audit
        d = fresh(tmp, "ci")
        sub(os.path.join(d, ".github/workflows/ci.yml"), "    timeout-minutes: 30\n", "")
        run([s("ci_audit.py"), "--root", d], 1, "ci_audit notices a missing timeout")
        d = fresh(tmp, "ci2")
        sub(os.path.join(d, ".github/workflows/ci.yml"), "    branches-ignore: [reports, 'sync/**']\n", "")
        run([s("ci_audit.py"), "--root", d], 1, "ci_audit notices push not ignoring sync/**")
        d = fresh(tmp, "ci3")
        sub(os.path.join(d, "tests/e2e.py"), "timeout=30", "timeout=5")
        run([s("ci_audit.py"), "--root", d], 1, "ci_audit notices a too-short test wait")
        # negative: docs_audit
        d = fresh(tmp, "docs")
        with open(os.path.join(d, "docs/progress.md"), "a", encoding="utf-8") as f:
            f.write("\nSee [missing](progress/nowhere.md).\n")
        run([s("docs_audit.py"), "--root", d, "score"], 1, "docs_audit notices a broken link")
        d = fresh(tmp, "docs2")
        open(os.path.join(d, "docs/progress/orphan.md"), "w").write("# orphan\n\n## Open work\n\n## Rules (do not break)\n")
        run([s("docs_audit.py"), "--root", d, "score"], 1, "docs_audit notices an orphan file")
        # negative: consistency
        d = fresh(tmp, "cons")
        sub(os.path.join(d, "src/server/version.py"), "SPEC_REV = 2", "SPEC_REV = 3")
        run([s("consistency.py"), "--root", d, "check"], 1, "consistency notices a revision mismatch")
        d = fresh(tmp, "cons2")
        with open(os.path.join(d, "src/server/app.py"), "a", encoding="utf-8") as f:
            f.write('\n\n@route("/admin")\ndef admin():\n    return {}\n')
        run([s("consistency.py"), "--root", d, "check"], 1, "consistency notices a route missing in the clients")
        d = fresh(tmp, "cons3")
        with open(os.path.join(d, "src/server/app.py"), "a", encoding="utf-8") as f:
            f.write('\n\ndef theme():\n    return cfg("theme")\n')
        r = run([s("consistency.py"), "--root", d, "check"], 1, "consistency notices an unregistered config key")
        results.append(("`theme`" in r.stdout, "  ...and names the key", 0, 0))
        d = fresh(tmp, "cons4")
        sub(os.path.join(d, "docs/spec/known.toml"), "match:routes:src/mobile/routes.js", "match:routes:src/mobile/nothing.js")
        run([s("consistency.py"), "--root", d, "check"], 1, "consistency notices a stale accepted entry")
        # negative: agent_audit
        d = fresh(tmp, "agent")
        with open(os.path.join(d, "docs/agents/ledger.txt"), "a", encoding="utf-8") as f:
            f.write("2026-03-09|coder|haiku|a task|api|9|-|DONE|1|1|1\n")
        run([s("agent_audit.py"), "--root", d], 1, "agent_audit notices a bad ledger row")
        # sync: header tool, then checks on a temporary copy
        d = fresh(tmp, "sync")
        run([t("sync_hdr.py"), "ALPHA", "--root", d, "--state", "WORKING", "--task", "WO-9", "--wakeup", "yes"], 0, "sync_hdr writes a block (no eta: warning only)")
        run([t("sync_hdr.py"), "ALPHA", "--root", d, "--ack", "auto"], 0, "sync_hdr --ack auto")
        hdr = open(os.path.join(d, "sync", "ALPHA.md"), encoding="utf-8").read()
        results.append((bool(re.search(r"^ack: 2026-10-01T12:00", hdr, re.M)), "sync_hdr --ack auto reads the last Log row", 0, 0))
        sub(os.path.join(d, "sync", "ALPHA.md"), "updated:", "x_old:")
        run([t("sync_check.py"), "--strict", "--root", d], 1, "sync_check notices a broken status block")
        d = fresh(tmp, "sync2")
        sub(os.path.join(d, "sync/ALPHA.md"), "DELIVERED WO-1 @", "DONE WO-1 @")
        run([t("sync_check.py"), "--strict", "--root", d], 1, "sync_check notices a non-standard delivery line")
        d = fresh(tmp, "sync3")
        with open(os.path.join(d, "sync/inbox/ALPHA.md"), "a", encoding="utf-8") as f:
            f.write("extra 1\nextra 2\n")
        run([t("sync_check.py"), "--strict", "--root", d], 1, "sync_check notices an inbox over 5 lines")
        d = fresh(tmp, "sync4")
        run([t("sync_hdr.py"), "BETA", "--root", d, "--state", "WORKING", "--task", "WO-9", "--eta", "2020-01-01T00:00+00:00"], 0, "sync_hdr sets an old eta")
        # a WORKING operator whose eta is long past and that did not update since: IDLE by rule
        text = open(os.path.join(d, "sync/BETA.md"), encoding="utf-8").read()
        text = re.sub(r"updated: .*", "updated: 2019-12-31T23:00+00:00", text)
        open(os.path.join(d, "sync/BETA.md"), "w", encoding="utf-8", newline="").write(text)
        run([t("sync_check.py"), "--strict", "--root", d], 1, "sync_check notices an IDLE operator")

    bad = [r for r in results if not r[0]]
    print(f"selftest: {len(results) - len(bad)}/{len(results)} checks passed")
    for _, name, got, want in bad:
        print(f"  FAILED: {name} (exit {got}, expected {want})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
