# Changelog

## [0.2.0] — 2026-11-13

### Breaking

- **Tool names no longer contain a dot.** The seven tools are now `travel_ingest`, `travel_match`, `travel_export`, `travel_policy_check`, `travel_duplicate_check`, `travel_reuse_check` and `travel_daily_limit_check`. Providers validate `tools[].name` against `^[a-zA-Z0-9_-]+$`; the old dotted names invalidated the whole `tools` array, so the plugin registered but every request carrying its tools was rejected with `Invalid 'tools[N].name'`. Minor bump because tool names are part of the 0.1.0 compatibility promise — update prompts, saved calls and permission rules that still use the old dotted names.
- `test/tool-name-wire.test.mjs` pins the wire pattern so a new tool cannot reintroduce a dot or drop the `travel_` namespace.
- Earlier changelog entries use the new spelling, so a repository-wide search no longer finds dotted tool names.

### Changed

- Documentation: five-language READMEs, the flow diagrams under `docs/assets/`, `samples/quickstart/run.mjs`, the acceptance script and the README-asset generator all use the underscore names; `travel_*` replaces the old `travel.*` namespace notation.

## [0.1.0] — 2026-11-03

### Stable

- First non-alpha release: tool names and the CLI surface are covered by a
  compatibility promise (breaking changes require a minor bump).
- Ships a quickstart sample, a one-line prompt, a permission block and real captures.

## [0.1.0] — 2026-11-01

### Packaging

- Package Standard v1: shipped `samples/quickstart/` (synthetic trip/invoice/card CSV + real-output gold `expected/result.json` + runner), `dsh.demo` metadata, README-zh eight blocks (including the demo prompt and permission lines), `docs/assets/quickstart.png` rendered from a real run, and a `PS1-QS01` acceptance row. `npm pack --dry-run` contains `samples/quickstart/*`; `node --test test/*.test.mjs` 25/25.
- The three most common errors now read `<what happened>（E_XXX）｜下一步：<action>`; `TROUBLESHOOTING.md` lists the three cases with symptom/cause/action.

### Security / Fixes

- Path-traversal guard, duplicate trip ids kept and reported instead of overwriting, header validation, per-day cap unaffected by duplicates.


### Added

- `travel_daily_limit_check`: per-employee, per-day spend against a daily cap, reporting every over-limit day with its overage. Read-only. Verified by `node --test test/*.test.mjs` (9/9).

## [Unreleased]

### Added

- `travel_reuse_check`: pre-ingest cross-trip reuse check that reports invoice IDs and card transaction IDs appearing under more than one trip (the classic double-claim pattern that the current id-keyed ingest would otherwise overwrite). Read-only. Verified by `node --test test/*.test.mjs` (7/7).

## [0.1.0-alpha.9] — 2026-11-01

### Changed

- Documentation: five-language fixture/acceptance links now resolve on npm; added specific related-checker/tool links.
- Marketplace metadata: taxonomy category, archetype, domains and status; docs page now shows the same.
- Added a real terminal hero (and GIF for the active docs set) plus `TROUBLESHOOTING.md`.

All notable changes to `dsh-travel-recon` are documented here. The format follows Keep a Changelog; this project uses alpha versions.

## [0.1.0-alpha.8] — 2026-11-01

### Added

- Five-language READMEs: English, 简体中文, Español, Português, हिन्दी.
- Local workflow SVG at `docs/assets/dsh-travel-recon-flow.svg`.
- Family cross-links (domain index, checker family, `dsh-kit`), compatibility, permissions, and related-work sections.
- Standard repository files: `SECURITY.md`, `PRIVACY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `icon.svg`.

### Changed

- README aligned with the PerryLink DSH checker/plugin family style; package remains public/synthetic, alpha, not GA.

## [Earlier]

Earlier alpha builds are available from npm and GitHub Releases; this file starts at the family-standard documentation wave.
