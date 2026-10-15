# Consistency between platforms, formats and versions

One product, several platforms or clients built at different times (say a web client and a mobile client): menus, settings, keys and
formats drift apart, and nothing notices. This page is the rule that stops it, and the list of how to track what is still apart.
**Everything must converge before the release gate** (for example version 1.0.0).

## The principle

> The platforms behave **the same**, and the formats mean the same on all of them, **unless a capability really differs** (a touch screen and
> no keyboard, no offline storage, a different rendering engine...). A difference that comes from a listed capability is accepted;
> every other difference is a defect.

A defect is written in `docs/spec/divergences.toml` the day it is found and **blocks the gate** until it is resolved.

## Three numbers, three meanings

| Number | What it says | Where | Changes when |
|---|---|---|---|
| **Product version** | which build a user has | git tag or `git describe` | every release |
| **Specification revision** | what a client or a plugin may rely on: formats, API, config keys, platform behaviour | a constant in code (named in `docs/spec/consistency.toml`) and `docs/spec/specs.toml` | something a client can depend on is added |
| **Container version** | the layout of a stored file or message | the file format header | only when an old reader must refuse the file: a break |

## The files

| File | What it holds |
|---|---|
| `docs/spec/consistency.toml` | which code files `consistency.py` compares: `[spec]` (the revision constant), `[config]` (how keys are read), `[[match]]` blocks (one truth file and its copies) |
| `docs/spec/specs.toml` | the revisions and the items of the specification, each with its revision, status (`implemented`, `partial`, `planned`), files and platforms |
| `docs/spec/config-keys.toml` | every configuration key the code reads: scope, accepted values, default, meaning |
| `docs/spec/platforms.toml` | the platforms and the **capabilities** in which they really differ |
| `docs/spec/divergences.toml` | every known difference, with its cause (`capability`, `history`, `todo`, `unknown`) and status (`open`, `suspended`, `untested`, `resolved`) |
| `docs/spec/known.toml` | findings of the automatic rules that are accepted for now, with a reason and a kind |
| `scripts/consistency.py` | the rules: `check`, `report`, `gate`, `since` |

## What the script checks

`python scripts/consistency.py check` fails (exit 1) on:
- **match**: for each `[[match]]` block, the set of values found in the truth file (for example the route names of the server) equals the set in each copy (the clients, the docs);
- **spec**: the revision constant in code is the registry's last revision; item ids are unique; `since` is not in the future; every `where` file exists;
- **config**: every key the code reads is in `config-keys.toml` with the right scope, every registered key is still read, every entry has `scope`, `values`, `default`, `meaning`;
- **divergence**: a capability difference names a capability of `platforms.toml`; cause and status are valid; evidence files exist;
- **stale**: an entry of `known.toml` that no rule finds any more.

`report` adds the accepted findings with their reason. **`gate` lists what still blocks the release**: open or suspended divergences of cause `history`, `todo` or `unknown`, accepted findings of those kinds, and spec items that are not `implemented`.
`since PATTERN FILE` finds the first release tag containing a pattern, to fill `since` in `specs.toml`.

## Rules for a change

1. **Shared code first.** Logic that both platforms need lives in shared code. A feature added to one platform's own code is added to the other **in the same change**, or written in `divergences.toml` as `history` or `todo`.
2. **Platform code only for a capability.** When code differs, name the capability (`platforms.toml`) in a comment and in `divergences.toml` (`cause = "capability"`).
3. **A new API function or route** goes in the docs; **a new config key** in `config-keys.toml`; **a format change** in every writer and reader together. `consistency.py check` fails otherwise.
4. **If a client can depend on it**, add an `[[item]]` to `specs.toml` with a new revision (and raise the constant in code).
5. **Both platforms in the test**: the shared test suite runs against each platform's entry point.

## The gate

`python scripts/consistency.py gate` must print **0 blockers**: no open divergence of cause `history`, `todo` or `unknown` (only `capability` may stay), no spec item that is not `implemented`, no accepted finding except capability and text noise.
After the gate: a container version stays readable by every later release of the same major version; a new revision only **adds**; removing or changing a promise is a major version.

## Divergence statuses

| Status | Meaning | Blocks the gate |
|---|---|---|
| `open` | known, not fixed | yes (unless cause is `capability`) |
| `suspended` | on hold by the owner, decision pending | yes |
| `untested` | fixed in the code, not tried on the real platform; `consistency.py gate` prints it as "to try" | no |
| `resolved` | fixed and tried; the note says how | no |

## Decisions needed

List here the questions that decide whether a divergence is a defect or a capability. Remove each line when decided.
