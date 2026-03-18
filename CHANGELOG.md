# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows Semantic Versioning.

## [0.5.0] - 2026-03-18

### Added
- New built-in motion library under `martin.fx` with animation and transition helpers such as `FadeIn`, `SlideIn`, `ScaleIn`, `BlurIn`, `RotateIn`, `Float`, `Pulse`, `Spin`, and `Transition`.
- Compatibility alias package `martin_fx` so motion helpers can also be imported outside the main namespace if desired.
- Automatic injection of MARTIN FX keyframes into `App`, so effects work out of the box after `pip install martin-framework`.

### Changed
- Documentation now shows the packaged install name `martin-framework`.

## [0.4.0] - 2026-03-17

### Added
- Utility widgets to load external and inline assets from Python: `Script`, `Stylesheet`, `StyleTag`.
- Snapshot and behavior test suite under `tests/`.
- Universal HTML attributes support across widgets (`attrs`, `role`, `tabindex`, `aria_*`, `data_*`).
- Default accessibility labels (`aria-label`) for interactive widgets where meaningful.
- CI workflow for automatic tests on push and pull request.

### Changed
- `Modal` accessibility behavior improved with dialog semantics, focus management, and `Esc` close behavior.
- Navigation widgets (`NavBar`, `Tabs`) improved with better ARIA semantics and keyboard support.
- API/static server internals hardened for safer HTML/attribute rendering and path handling.
- `Request` parser improved with `query_multi`, and safer JSON/form parsing defaults.

### Fixed
- Escaping edge cases in URL wrapping and HTML attribute rendering.
- Static file serving path traversal and URL decoding safety gaps.
- Regex escaping warning in `calendar.py`.

### Compatibility
- No intentional breaking changes in public Python APIs.

### Upgrade Notes
- Existing applications should continue to run without code changes.
- If you use custom HTML attributes, prefer the new universal kwargs (`role`, `tabindex`, `aria_*`, `data_*`, or `attrs={...}`) for consistency.
- CI now runs tests automatically on push and pull request via GitHub Actions.

## [0.3.0] - 2026-03-09

### Added
- Initial pre-alpha release of MARTIN framework primitives and CLI.
