# Changelog
DriveID filter release notes


## [Unreleased]

### Changed

- Build the image on `openfilter-base` (weekly apt-upgraded python-slim) instead of a stale `python:X.Y.Z-slim` pin, clearing the OS-package CVEs the pin carried.
- Bump the openfilter dependency to 1.2.2

## v0.1.14 - 2026-08-04

### Changed

- Update the `openfilter[all]` dependency to `>=1.2.1,<2.0.0`.
- Grant `id-token: write` in the release workflow to enable keyless (cosign) SBOM attestation in the shared reusable.
- Restore the build-commit facet: rename `GITHUB_SHA` → `VERSION_SHA` after the source `COPY` so openfilter reports `version_sha`.
- Update dev-tooling floors and switch the dev pins to ranges (`setuptools>=83.0.0`, `wheel>=0.46.2`, `pytest>=9.0.3`, `pytest-cov>=6.0.0`).

## v0.1.13 - 2026-07-30

### Changed

- Update the openfilter dependency to `>=1.2.0,<2.0.0` (openfilter 1.2.0 moves to OpenCV 5).

## v0.1.12 - 2026-04-27

### Added
- Add Dockerfile and .dockerignore for Docker Hub publishing

## v0.1.11 - 2026-04-24

### Changed
- Fix release workflow secret names: `PYPI_API_TOKEN` → `PLAINSIGHT_PYPI_TOKEN`, `DOCKERHUB_TOKEN` → `DOCKERHUB_ACCESS_TOKEN` (org-level secret names). Without this the PyPI / Docker Hub tokens resolved to empty and no package has been published since the migration.
- Update the openfilter dependency to `>=0.1.30`, and align the CI workflow with the shared release gate (source-paths).
- Remove redundant ci.yaml (shared workflow handles PR testing).
- Add push + pull_request triggers to create-release.yaml.


## v0.1.9 - 2026-04-17

### Changed
- Add CI/CD workflows: create-release.yaml, ci.yaml, security-scan.yaml
- Update openfilter to >=0.1.27
- Add Makefile IMAGE for Docker Hub


## v0.1.8 - 2025-09-27

### Changed
- Updated documentation

## v0.1.7 - 2025-08-06

### Modified
- Updated dependencies

## v0.1.6 - 2025-08-06

### Modified
- Support for model context file name
- Updated dependencies

## v0.1.5 - 2025-07-30

### Added
- Support for model info-context

## v0.1.4 - 2025-07-15

### Changed
- Updated dependencies

## v0.1.3 - 2025-05-22

### Changed
- Updated dependencies

## v0.1.2 - 2025-05-22

### Added
- Initial release of the DriveID filter using a custom-trained Faster R-CNN model.
- Supports detection of license plates in image frames with the following features:
  - Loads a Torch model from a configurable `model_path`
  - Detects plates and returns bounding boxes with confidence scores
- Frame-level control:
  - Skips processing for frames with metadata flag `skip_plate_detection: true`
- Confidence threshold:
  - Discards detections below a configurable `confidence_threshold` (default: 0.7)
- Output formatting:
  - Writes detection results to a configurable `output_json_path` (if `write_detections_to_json` is enabled)
  - Each record includes:
    - `frame_id`
    - List of detected `plates` with bounding box and confidence score
- Forwarding support:
  - Optionally forwards polygon ROIs to downstream consumers via `frame.data['meta'][roi_output_label]`
  - Enabled using `forward_detection_rois`
  - Configurable label name via `roi_output_label`
- Debug mode:
  - Enables verbose logging when `debug` is true
- Device auto-detection:
  - Automatically uses CUDA if available; otherwise falls back to CPU
- Environment variable configuration:
  - All config fields can be overridden via `FILTER_*` env vars (e.g., `FILTER_MODEL_PATH`, `FILTER_DEBUG`)
- Includes PIL and OpenCV-based preprocessing with TorchVision transforms

### Changed
- Scaled predicted bounding boxes from model coordinates to original frame dimensions using width/height ratio
- Improved transform pipeline for input normalization
- Adjusted logging to show frame-wise outputs and polygon forwarding activity

### Fixed
- Fixed potential mismatch between input frame resolution and model preprocessing dimensions
- Ensured bounding box coordinates are properly rounded and cast to integers
- Resolved potential file writing issues by safely creating output directories for JSON logging

### Internal
- Refactored model loading into a separate method with dynamic class predictor injection
- Consolidated TorchVision transform logic into a reusable `get_transform()` method
- Enhanced logging throughout `setup`, `process`, and `shutdown` phases

### Experimental
- Polygon ROI forwarding via rectangular box conversion for downstream processing
