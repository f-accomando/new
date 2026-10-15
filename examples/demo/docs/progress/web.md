# web (Taskly clients)

## How it is today

### Web client
- `src/web/routes.js` lists the screens; it mirrors the server routes.

### Mobile client
- `src/mobile/routes.js` has no `/export` screen (the phone has no file system access: capability `no-fs-access`).
- `src/mobile/settings.js` reads `haptics`, a mobile-only key.

## Open work

- [ ] Search filters exist on the web client only (divergence D01).

## Rules (do not break)

- Screens are added to both clients together; a screen one platform cannot have is a capability in `docs/spec/platforms.toml`.
