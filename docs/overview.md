---
title: License Plate Detection Filter
sidebar_label: Overview
sidebar_position: 1
---

The **License Plate Detection Filter** identifies license plates in video frames using a custom [Faster R-CNN](https://pytorch.org/vision/stable/models/generated/torchvision.models.detection.fasterrcnn_resnet50_fpn.html) model. It can log detections to disk, propagate bounding boxes as ROI polygons, and integrates seamlessly with [OpenFilter](https://github.com/PlainsightAI/openfilter) pipelines.

This document is automatically published to production documentation on every production release.

---

## ✨ Key Features

- **CNN-based license plate detection** using PyTorch Faster R-CNN
- **Customizable confidence threshold** for filtering predictions
- **Optional JSON logging** of detections for post-processing and audit
- **ROI forwarding support** for integration with downstream filters (e.g., OCR or Crop)
- **Metadata-aware frame skipping** via `meta.skip_plate_detection`
- **Environment-variable-based configuration** for runtime overrides
- **Optimized for GPU or CPU inference** based on availability

---

## 🚀 Usage Modes

### 1. Standard Detection Mode

Given a frame, the filter performs detection and returns bounding boxes for license plates. The output is stored in:

```python
frame.data['license_plate_detection']
````

Each detection includes:

```json
{
  "label": "license_plate",
  "score": 0.91,
  "box": [x1, y1, x2, y2]
}
```

### 2. Polygon ROI Forwarding

If enabled via `forward_detection_rois`, the filter adds a `meta` entry:

```python
frame.data["meta"]["license_plate_roi"] = [
  [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
]
```

These can be consumed by other filters (e.g., Crop Filter, OCR Filter) downstream.

### 3. Skip Logic via Metadata

If `frame.data['meta']['skip_plate_detection'] = True`, the filter skips processing that frame.

---

## ⚙️ Configuration Options

| Field                      | Type    | Description                                                  |
| -------------------------- | ------- | ------------------------------------------------------------ |
| `model_path`               | `str`   | Path to the `.pth` file containing the trained model         |
| `confidence_threshold`     | `float` | Minimum score required to keep a detection (default: `0.7`)  |
| `debug`                    | `bool`  | Enables verbose debug logs                                   |
| `write_detections_to_json` | `bool`  | Whether to write per-frame results to a file                 |
| `output_json_path`         | `str`   | File path for detection logs (e.g., `./output/results.json`) |
| `forward_detection_rois`   | `bool`  | If `true`, forwards bounding boxes as polygon ROIs           |
| `roi_output_label`         | `str`   | Label under which forwarded ROIs are stored in `frame.meta`  |

All fields are configurable via code or environment variables prefixed with `FILTER_`.
Example: `FILTER_MODEL_PATH=./model.pth`

---

## 🧪 Example Configurations

### Basic detection

```python
FilterLicensePlateDetectionConfig(
  model_path="./model.pth",
  confidence_threshold=0.8,
  debug=False
)
```

### With JSON output and polygon forwarding

```python
FilterLicensePlateDetectionConfig(
  model_path="./model.pth",
  write_detections_to_json=True,
  output_json_path="./output/detections.json",
  forward_detection_rois=True,
  roi_output_label="license_plate_roi"
)
```

---

## 🧠 Output Behavior

* `frame.data['license_plate_detection']` includes detection results
* If `write_detections_to_json = True`, a JSONL log is appended with per-frame entries
* If `forward_detection_rois = True`, polygons are added under `frame.data['meta'][roi_output_label]`
* Frames marked with `meta.skip_plate_detection = True` are skipped silently

---

## 🧩 Integration

Use the filter directly:

```python
from filter_license_plate_detection.filter import FilterLicensePlateDetection
FilterLicensePlateDetection.run()
```

Or as part of a multi-stage pipeline:

```python
Filter.run_multi([
    (VideoIn, {...}),
    (FilterLicensePlateDetection, {...}),
    (Webvis, {...})
])
```

---

## 🧼 Notes

* The model is loaded onto GPU if available, otherwise CPU
* Model must have exactly 2 classes: background and license plate
* Polygon ROI forwarding uses `[x1, y1, x2, y1, x2, y2, x1, y2]` ordering
* Output JSON file is opened in append mode and flushed per frame

---

For contribution and development guidelines, see the [CONTRIBUTING guide](https://github.com/PlainsightAI/filter-license-plate-detection/blob/main/CONTRIBUTING.md).