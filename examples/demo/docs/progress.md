# Taskly progress (the one index)

**Start here.** Every doc is reached from a line below; `grep -n '^##'` the file, read one section.

## Areas

| File | Scope | Main code |
|---|---|---|
| [api](progress/api.md) | the Python server: routes, config keys, specification revision | `src/server/app.py`, `src/server/version.py` |
| [web](progress/web.md) | the web and mobile clients, and where they differ | `src/web/routes.js`, `src/mobile/routes.js` |

## Which section to open

- Routes, config keys, revision: [api](progress/api.md).
- Client screens and platform differences: [web](progress/web.md).

## Reference docs

Consistency and the release gate: `docs/spec/` (`specs.toml`, `config-keys.toml`, `platforms.toml`, `divergences.toml`, `known.toml`) · subagent runs: `docs/agents/ledger.txt`.
