# api (Taskly server)

## How it is today

### Routes
- `src/server/app.py` registers `/tasks`, `/search`, `/export` with `@route(...)`; search it with `grep -n '@route' src/server/app.py`.

### Config keys
- Read through `cfg("<name>")`: `port`, `page_size`, `export_dir`. The registry is `docs/spec/config-keys.toml`.

### Specification revision
- `SPEC_REV` in `src/server/version.py` equals the last revision of `docs/spec/specs.toml`.

## Open work

- [ ] Add pagination to `/search` (new spec item and revision 3).

## Rules (do not break)

- A new route is added in the server, the web client and the mobile client in the same change, or recorded in `docs/spec/divergences.toml`.
- A new config key is registered in `docs/spec/config-keys.toml` in the same change.
