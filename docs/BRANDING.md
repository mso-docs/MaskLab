# MaskLab visual identity

Two mirrored mask halves represent paired behavioral conditions. Teal (#0B9D91) and violet (#7864DF) distinguish conditions; the central negative-space split keeps them visually separate. The descriptor is “Behavioral Research.”

Canonical assets in `frontend/public/brand/`:

- `masklab-logo.svg` / `.png`: dark wordmark for light backgrounds.
- `masklab-logo-dark.svg` / `.png`: light wordmark for dark backgrounds.
- `masklab-mark.svg` / `.png`: symbol alone for square icons.

All six assets have transparent backgrounds. Wordmark PNGs: 2080 × 560. Icon PNG: 1024 × 1024. SVGs include accessible title/description metadata. SVG text uses DejaVu Sans with Arial/sans-serif fallbacks; PNGs preserve the exact rendered typography. Keep proportions and clear space. Original artwork is covered by the repository MIT license; sponsor logos are not incorporated.

The frontend can reference `/brand/masklab-logo.svg` or the dark-background variant, with meaningful alt text. UI integration has not been performed as part of asset creation.

Implementation integration — 2026-10-28: the React sidebar now selects the matching SVG wordmark for light/dark appearance; the symbol is the favicon. FastAPI serves the bundled `/brand/` assets. Existing artwork remains unchanged.
