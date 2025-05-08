# 🚘 License Plate Detection Filter

**License Plate Detection Filter** is a modular [OpenFilter](https://github.com/PlainsightAI/openfilter)-based component that detects license plates in video frames using a custom-trained [Faster R-CNN](https://pytorch.org/vision/stable/models/generated/torchvision.models.detection.fasterrcnn_resnet50_fpn.html) model.

It supports per-frame bounding box predictions, polygon ROI forwarding, and configurable JSON logging — making it easy to plug into OpenFilter pipelines and downstream processing systems.

[![PyPI version](https://img.shields.io/pypi/v/filter-license-plate-detection.svg?style=flat-square)](https://pypi.org/project/filter-license-plate-detection/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/PlainsightAI/filter-license-plate-detection/blob/main/LICENSE)
![Build Status](https://github.com/PlainsightAI/filter-license-plate-detection/actions/workflows/ci.yaml/badge.svg)

---

## ✨ Features

- 🚘 Detects license plates in RGB video frames using Faster R-CNN
- 🔍 Configurable confidence threshold and debug logging
- 📤 Forwards detection ROIs as polygons to other filters
- 🧾 Optional logging of per-frame detections to JSON
- 🧩 Fully compatible with [OpenFilter](https://github.com/PlainsightAI/openfilter) pipelines

---

## 📦 Installation

Install from PyPI:

```bash
pip install filter-license-plate-detection
````

Or install from source:

```bash
# Clone the repo
git clone https://github.com/PlainsightAI/filter-license-plate-detection.git
cd filter-license-plate-detection

# (Optional but recommended) create a virtual environemnt:
python -m venv venv && source venv/bin/activate

# Install the filter and download the model
make install
```

---

## 🚀 Quick Start (CLI)

Run the License Plate Detection Filter as part of a pipeline:

```bash
openfilter run \
  - VideoIn --sources file://example_video.mp4!loop \
  - filter_license_plate_detection.filter.FilterLicensePlateDetection \
      --model_path ./model.pth \
      --forward_detection_rois true \
      --write_detections_to_json true \
      --output_json_path ./detections.json \
  - Webvis
```

Or simply:

```bash
make run
```

Then open [http://localhost:8000](http://localhost:8000) to view results.

---

## 🧰 Using from PyPI

After installation:

```bash
pip install filter-license-plate-detection
```

You can run the filter directly:

### Standalone usage

```python
from filter_license_plate_detection.filter import FilterLicensePlateDetection

if __name__ == "__main__":
    FilterLicensePlateDetection.run()
```

### In an OpenFilter pipeline

```python
from openfilter.filter_runtime.filter import Filter
from openfilter.filter_runtime.filters.video_in import VideoIn
from openfilter.filter_runtime.filters.webvis import Webvis
from filter_license_plate_detection.filter import FilterLicensePlateDetection

if __name__ == "__main__":
    Filter.run_multi([
        (VideoIn, dict(sources='file://example.mp4!loop')),
        (FilterLicensePlateDetection, dict(
            model_path="./model.pth",
            confidence_threshold=0.75,
            forward_detection_rois=True
        )),
        (Webvis, {}),
    ])
```

---

## 🧪 Testing

Run unit tests:

```bash
make test
```

Or a specific test:

```bash
pytest -v tests/test_filter_license_plate_detection.py
```

Tests include:

* Model inference
* Confidence filtering
* Polygon forwarding
* JSON logging
* Frame skipping logic

---

## ⚙️ Configuration

| Config Key                 | Description                                     | Type    | Default                               |
| -------------------------- | ----------------------------------------------- | ------- | ------------------------------------- |
| `model_path`               | Path to the model `.pth` file                   | `str`   | `./model.pth`                         |
| `confidence_threshold`     | Minimum confidence to keep detections           | `float` | `0.7`                                 |
| `debug`                    | Enable debug logging                            | `bool`  | `False`                               |
| `write_detections_to_json` | Write detection results to a JSON file          | `bool`  | `False`                               |
| `output_json_path`         | Path to the output JSON log file                | `str`   | `./output/license_plate_results.json` |
| `forward_detection_rois`   | Forward detected bounding boxes as polygon ROIs | `bool`  | `False`                               |
| `roi_output_label`         | Metadata key under which to store ROIs          | `str`   | `license_plate_roi`                   |

All fields can also be configured via environment variables using the prefix `FILTER_` (e.g., `FILTER_MODEL_PATH`).

---

## 📤 Detection Output Format

Each frame’s detection output is stored in:

```python
frame.data['license_plate_detection']
```

Example output:

```json
{
  "frame_id": "frame_001",
  "plates": [
    {
      "label": "license_plate",
      "score": 0.92,
      "box": [320, 180, 460, 240]
    }
  ]
}
```

If `forward_detection_rois` is enabled, the filter also adds polygon metadata:

```python
frame.data["meta"]["license_plate_roi"] = [
  [(320, 180), (460, 180), (460, 240), (320, 240)]
]
```

---

## 📄 License

Licensed under the [Apache 2.0 License](https://github.com/PlainsightAI/filter-license-plate-detection/blob/main/LICENSE).

---

## 🙌 Acknowledgements

Thanks for using and improving the License Plate Detection Filter!
To report bugs or suggest improvements, [open a GitHub issue](https://github.com/PlainsightAI/filter-license-plate-detection/issues/new/choose).