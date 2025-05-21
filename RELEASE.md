# Changelog
License Plate Detection filter release notes

## [Unreleased]

## v0.1.3 - 2025-05-22

### Changed
- Updated dependencies

## v0.1.2 - 2025-05-22

### Added
- Initial release of the license plate detection filter using a custom-trained Faster R-CNN model.
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
