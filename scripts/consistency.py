#!/usr/bin/env python3
"""
consistency.py - the same fact kept in step across files and platforms (docs/spec/CONSISTENCY.md).

  consistency.py [--root DIR] check     every rule below: exit 1 on drift that docs/spec/known.toml does not accept
  consistency.py [--root DIR] report    the same, with the accepted divergences listed (their reason) too
  consistency.py [--root DIR] gate      what still blocks the release gate (for example 1.0.0): everything must converge before it
  consistency.py [--root DIR] since PATTERN FILE   the first release tag that has PATTERN in FILE (for docs/spec/specs.toml)

The same fact lives in several files (the server in code, the clients in code, the docs): this compares them, so a change made
in one place and forgotten in the others is found when it is made, not months later. Plain Python 3.11+ (tomllib), no dependencies.

What it reads (all under <root>/docs/spec/):
  consistency.toml   which code files to compare ([spec], [config], [[match]] blocks)
  specs.toml         the revisions and items of the specification
  config-keys.toml   every config key the code reads
  platforms.toml     the platforms and the capabilities in which they really differ
  divergences.toml   every known difference between platforms, with cause and status
  known.toml         automatic findings that are accepted for now, with a reason
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tomllib

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
KINDS = ("capability", "history", "todo", "unknown", "text")
BLOCKING = ("history", "todo", "unknown")  # kinds that must be gone before the gate: only capability and text may stay
STATUSES = ("open", "suspended", "untested", "resolved")


def path(*p):
    return os.path.join(ROOT, *p)


def rd(rel):
    return open(path(rel), encoding="utf-8", errors="replace").read()


def toml(rel, default=None):
    full = path(rel)
    if not os.path.exists(full):
        if default is not None:
            return default
        raise SystemExit(f"consistency: missing {rel}")
    with open(full, "rb") as f:
        return tomllib.load(f)


class Finding:
    def __init__(self, rule, key, text):
        self.rule, self.key, self.text = rule, key, text

    def id(self):
        return f"{self.rule}:{self.key}"


def extract(spec):
    """the set of strings a {file, pattern} block finds (group 1 of each match, or the whole match)"""
    text = rd(spec["file"])
    return {m.group(1) if m.groups() else m.group(0) for m in re.finditer(spec["pattern"], text, re.M)}


# ------------------------------------------------------------------ the rules

def rule_match():
    """[[match]] blocks: one file is the truth, the copies (other code, docs) hold the same set"""
    out = []
    for blk in toml("docs/spec/consistency.toml", {}).get("match", []):
        name = blk["name"]
        try:
            truth = extract(blk["truth"])
        except OSError as exc:
            out.append(Finding("match", f"{name}:truth", f"{name}: cannot read {blk['truth']['file']} ({exc.strerror})"))
            continue
        if not truth:
            out.append(Finding("match", f"{name}:empty", f"{name}: the pattern finds nothing in {blk['truth']['file']}"))
        for cp in blk.get("copies", []):
            try:
                got = extract(cp)
            except OSError as exc:
                out.append(Finding("match", f"{name}:{cp['file']}", f"{name}: cannot read {cp['file']} ({exc.strerror})"))
                continue
            if got != truth:
                miss, extra = sorted(truth - got), sorted(got - truth)
                out.append(Finding("match", f"{name}:{cp['file']}",
                                   f"{name}: {cp['file']} differs from {blk['truth']['file']} (missing {miss}, extra {extra})"))
    return out


def rule_spec():
    """docs/spec/specs.toml: the code's revision is the registry's last, ids are unique, `where` files exist"""
    out = []
    reg = toml("docs/spec/specs.toml")
    last = max(r["rev"] for r in reg["revision"])
    cfg = toml("docs/spec/consistency.toml", {}).get("spec")
    if cfg:
        m = re.search(cfg["rev_pattern"], rd(cfg["rev_file"]))
        if not m or int(m.group(1)) != last:
            out.append(Finding("spec", "rev", f"revision in {cfg['rev_file']} is {m.group(1) if m else '?'}, docs/spec/specs.toml ends at revision {last}"))
    ids = set()
    for it in reg.get("item", []):
        if it["id"] in ids:
            out.append(Finding("spec", f"dup:{it['id']}", f"item {it['id']} is listed twice"))
        ids.add(it["id"])
        if it["since"] > last:
            out.append(Finding("spec", f"since:{it['id']}", f"item {it['id']} is since revision {it['since']}, the last is {last}"))
        for w in it["where"]:
            if not os.path.exists(path(w)):
                out.append(Finding("spec", f"where:{it['id']}", f"item {it['id']}: {w} does not exist"))
    return out


def rule_config():
    """docs/spec/config-keys.toml: every key the code reads is registered with the right scope; every registered key is read"""
    out = []
    cfg = toml("docs/spec/consistency.toml", {}).get("config")
    if not cfg:
        return out
    data = toml("docs/spec/config-keys.toml")
    plats = set(toml("docs/spec/platforms.toml").get("platform", {}))
    reg = {k["name"]: k for k in data.get("key", [])}
    patterns = [re.compile("^" + re.sub(r"<[^>]*>", r"\\w+", re.escape(p["name"]).replace("\\<", "<").replace("\\>", ">")) + "$")
                for p in data.get("pattern", [])]
    read_re = re.compile(cfg["read_pattern"])
    by_path = cfg.get("scope_by_path", [])
    seen, allsrc = {}, ""
    for g in cfg["globs"]:
        for full in glob.glob(path(g), recursive=True):
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            text = open(full, encoding="utf-8", errors="replace").read()
            allsrc += text
            area = next((b["scope"] for b in by_path if rel.startswith(b["prefix"])), "other")
            for k in read_re.findall(text):
                seen.setdefault(k, set()).add(area)
    for k in sorted(seen):
        if k not in reg and any(p.match(k) for p in patterns):
            continue
        if k not in reg:
            out.append(Finding("config", f"unregistered:{k}", f"the code reads `{k}` and docs/spec/config-keys.toml does not list it"))
        elif len(seen[k]) == 1 and next(iter(seen[k])) in plats and reg[k]["scope"] not in (next(iter(seen[k])), "tests"):
            out.append(Finding("config", f"scope:{k}", f"`{k}` is read only by {next(iter(seen[k]))} code and its scope is {reg[k]['scope']}"))
    for k, v in reg.items():
        if k not in seen:
            out.append(Finding("config", f"stale:{k}", f"`{k}` is in docs/spec/config-keys.toml and no code reads it"))
        for field in ("scope", "values", "default", "meaning"):
            if field not in v:
                out.append(Finding("config", f"field:{k}", f"`{k}` has no `{field}`"))
        if v.get("scope") not in ("all", "tests") and v.get("scope") not in plats:
            out.append(Finding("config", f"scopeid:{k}", f"`{k}` has scope '{v.get('scope')}', not 'all' or a platform of platforms.toml"))
    return out


def divergences():
    return toml("docs/spec/divergences.toml").get("divergence", [])


def rule_divergences():
    """docs/spec/divergences.toml: a capability difference names a listed capability; fields are valid; evidence files exist"""
    out = []
    caps = {c["id"] for c in toml("docs/spec/platforms.toml").get("capability", [])}
    for d in divergences():
        if d["cause"] == "capability" and d.get("capability") not in caps:
            out.append(Finding("divergence", f"capability:{d['id']}", f"{d['id']} is a capability difference with no capability of platforms.toml ({d.get('capability')})"))
        if d["cause"] not in KINDS or d["status"] not in STATUSES:
            out.append(Finding("divergence", f"fields:{d['id']}", f"{d['id']}: cause or status is not valid"))
        for ev in d.get("evidence", "").split(";"):
            p = ev.strip().split(":")[0]
            if p and not os.path.exists(path(p)):
                out.append(Finding("divergence", f"evidence:{d['id']}", f"{d['id']}: {p} does not exist"))
    return out


RULES = [rule_match, rule_spec, rule_config, rule_divergences]


# ------------------------------------------------------------------ the accepted divergences

def load_known():
    return {k["id"]: k for k in toml("docs/spec/known.toml", {}).get("accept", [])}


def run(verbose):
    known = load_known()
    bad, accepted, seen = [], [], set()
    for rule in RULES:
        for f in rule():
            seen.add(f.id())
            (accepted if f.id() in known else bad).append(f)
    stale = [k for k in known if k not in seen]
    for f in bad:
        print(f"DRIFT   {f.rule:12} {f.text}")
    if verbose:
        for f in accepted:
            k = known[f.id()]
            print(f"accepted {f.rule:11} {f.text}\n         because: {k['because']} ({k['kind']})")
    for k in stale:
        print(f"STALE   {k}: accepted in docs/spec/known.toml but it is not found any more: remove it")
    print(f"consistency: {len(bad)} drift, {len(accepted)} accepted, {len(stale)} stale")
    return 1 if bad or stale else 0


def gate():
    """what stops the release: accepted divergences that are not capability, open divergences, and spec items not implemented"""
    known = load_known()
    blockers = []
    for k, v in known.items():
        if v["kind"] not in KINDS:
            blockers.append(f"{k}: kind '{v['kind']}' is not one of {', '.join(KINDS)}")
        elif v["kind"] in BLOCKING:
            blockers.append(f"accepted drift {k} ({v['kind']}): {v['because']}")
    for d in divergences():
        if d["status"] in ("open", "suspended") and d["cause"] in BLOCKING:
            tag = " [suspended]" if d["status"] == "suspended" else ""
            blockers.append(f"{d['id']} ({d['cause']}, priority {d.get('priority', '-')}){tag}: {d['area']}: {d.get('action', '')}")
    for it in toml("docs/spec/specs.toml").get("item", []):
        if it["status"] != "implemented":
            blockers.append(f"spec item {it['id']} is {it['status']}: {it.get('note', '')}")
    for b in blockers:
        print("BLOCKS RELEASE  " + b)
    for d in divergences():
        if d["status"] == "untested":
            print(f"TO TRY ON THE REAL PLATFORM  {d['id']}: {d['area']}: {d.get('note', '')[:110]}")
    print(f"gate: {len(blockers)} blockers for the release")
    return 1 if blockers else 0


def since(pattern, rel):
    """the first release tag whose file has the pattern (git pickaxe)"""
    commit = subprocess.run(["git", "-C", ROOT, "log", "--format=%h", "--diff-filter=AM", "-S" + pattern, "--", rel],
                            capture_output=True, text=True).stdout.split()
    if not commit:
        print("not found in the history")
        return 1
    first = commit[-1]
    tags = subprocess.run(["git", "-C", ROOT, "tag", "--contains", first, "--sort=v:refname"], capture_output=True, text=True).stdout.split()
    print(f"{first} {tags[0] if tags else 'unreleased'}")
    return 0


def main(argv=None):
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="project folder (default: the folder above scripts/)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    sub.add_parser("gate")
    s = sub.add_parser("since")
    s.add_argument("pattern")
    s.add_argument("path")
    a = ap.parse_args(argv)
    if a.root:
        ROOT = os.path.abspath(a.root)
    if a.cmd == "since":
        return since(a.pattern, a.path)
    if a.cmd == "gate":
        return gate()
    return run(a.cmd == "report")


if __name__ == "__main__":
    sys.exit(main())
