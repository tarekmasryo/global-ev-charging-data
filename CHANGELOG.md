# Changelog — EV Charging Stations Dataset

## v1.0.3 (2026-02-09)
- Fix scripts linting (import order + line length).
- Restore `validate_dataset.py` CLI entrypoint and success output.

## v1.0.2 (2026-02-09)
- Added `is_fast_dc` vs `power_kw` consistency check in validation.

## v1.0.1 (2026-02-08)
- Added citation metadata (`CITATION.cff`).
- Added data-only checksum verification (`scripts/make_checksums.py`, `checksums.sha256`).
- CI verifies data checksums.

## v1.0 (2025-09-01)
- Initial global snapshot  
- **242,417 stations** across **121 countries**  
- Added derived columns: `power_class`, `is_fast_dc`  
- Included companion files: country summary, world summary, EV models  
