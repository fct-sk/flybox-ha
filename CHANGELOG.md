# Changelog

## 0.1.3

### Added

- Mobile Data binary sensor.
- Roaming binary sensor.
- Band Steering binary sensor.
- Roaming Upload sensor.
- Roaming Download sensor calculated as total roaming data minus roaming upload.

### Fixed

- Send an empty JSON payload when requesting connected hosts, fixing router response `retcode: 109` on the MeiG SRT858M.
