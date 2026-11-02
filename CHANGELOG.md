# Changelog

## [0.1.0-alpha.13] — 2026-11-01

### Security / Fixes

- Path-traversal guard, duplicate trip ids kept and reported instead of overwriting, header validation, per-day cap unaffected by duplicates.


### Added

- `travel.daily_limit_check`: per-employee, per-day spend against a daily cap, reporting every over-limit day with its overage. Read-only. Verified by `node --test test/*.test.mjs` (9/9).

## [Unreleased]

### Added

- `travel.reuse_check`: pre-ingest cross-trip reuse check that reports invoice IDs and card transaction IDs appearing under more than one trip (the classic double-claim pattern that the current id-keyed ingest would otherwise overwrite). Read-only. Verified by `node --test test/*.test.mjs` (7/7).

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
