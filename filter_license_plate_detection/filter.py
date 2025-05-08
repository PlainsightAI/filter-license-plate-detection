import os
import json
import logging
import torch
import numpy as np
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms as T
from openfilter.filter_runtime.filter import FilterConfig, Filter, Frame
import cv2
from dotenv import load_dotenv

load_dotenv()

__all__ = ['FilterLicensePlateDetectionConfig', 'FilterLicensePlateDetection']

logger = logging.getLogger(__name__)
SKIP_PLATE_DETECTION_FLAG = 'skip_plate_detection'


class FilterLicensePlateDetectionConfig(FilterConfig):
    model_path: str = './model.pth'
    debug: bool = False
    output_json_path: str = './output/license_plate_results.json'
    write_detections_to_json: bool = False
    forward_detection_rois: bool = False
    roi_output_label: str = "license_plate_roi"
    confidence_threshold: float = 0.7


class FilterLicensePlateDetection(Filter):
    """Detects license plates using a custom Faster R-CNN model. Optionally forwards polygons."""

    @classmethod
    def normalize_config(cls, config: FilterLicensePlateDetectionConfig):
        config = FilterLicensePlateDetectionConfig(super().normalize_config(config))

        env_mapping = {
            "model_path": str,
            "debug": bool,
            "output_json_path": str,
            "write_detections_to_json": bool,
            "forward_detection_rois": bool,
            "roi_output_label": str,
            "confidence_threshold": float,
        }

        for key, expected_type in env_mapping.items():
            env_key = f"FILTER_{key.upper()}"
            env_val = os.getenv(env_key)
            if env_val is not None:
                if expected_type is bool:
                    setattr(config, key, env_val.strip().lower() == "true")
                elif expected_type is float:
                    setattr(config, key, float(env_val.strip()))
                else:
                    setattr(config, key, env_val.strip())

        logger.debug(f"Normalized config: {config}")
        return config

    def _label_is_plate(self, label: str) -> bool:
        return "plate" in label.lower()

    def load_model(self, model_path: str):
        num_classes = 2  # 1 class (license_plate) + background
        model = fasterrcnn_resnet50_fpn(weights=None)
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        return model

    def setup(self, config: FilterLicensePlateDetectionConfig):
        logger.info("Setting up FilterLicensePlateDetection...")

        self.debug = config.debug
        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        self.confidence_threshold = config.confidence_threshold
        self.write_json = config.write_detections_to_json
        self.forward_detection_rois = config.forward_detection_rois
        self.roi_output_label = config.roi_output_label

        self.output_json_path = config.output_json_path
        if self.write_json:
            os.makedirs(os.path.dirname(self.output_json_path), exist_ok=True)
            self.output_file = open(self.output_json_path, 'a', encoding='utf-8')
            logger.info(f"Will write detection logs to: {self.output_json_path}")
        else:
            self.output_file = None
            logger.info("JSON output logging is disabled.")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.load_model(config.model_path)
        logger.debug("Model loaded.")

        self.transform = self.get_transform(train=False)

    def get_transform(self, train, target_size=(640, 480)):
        transforms = []
        transforms.append(T.Lambda(lambda x: torch.from_numpy(np.array(x).astype(np.float32) / 255.0).permute(2, 0, 1)))
        if train:
            transforms.append(T.RandomHorizontalFlip(0.5))
        return T.Compose(transforms)

    def shutdown(self):
        if self.output_file:
            self.output_file.close()
            logger.info("Closed output file for license plate detection.")
        logger.info("FilterLicensePlateDetection shutdown complete.")

    def process(self, frames: dict[str, Frame]):
        for stream_id, frame in frames.items():
            frame_meta = frame.data.get('meta', {})
            if frame_meta.get(SKIP_PLATE_DETECTION_FLAG, False):
                continue

            frame_id = frame_meta.get('id', 'unknown')
            image = frame.rw_bgr.image
            orig_width, orig_height = image.shape[1], image.shape[0]

            frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(frame_rgb)
            image_tensor = self.transform(image_pil).to(self.device)
            _, trans_height, trans_width = image_tensor.shape

            with torch.no_grad():
                prediction = self.model([image_tensor])[0]

            boxes = prediction['boxes'].cpu()
            scores = prediction['scores'].cpu()

            keep = scores > self.confidence_threshold
            boxes = boxes[keep]
            scores = scores[keep]

            if len(boxes) > 0:
                scale_x = orig_width / trans_width
                scale_y = orig_height / trans_height
                boxes[:, [0, 2]] *= scale_x
                boxes[:, [1, 3]] *= scale_y

            logger.debug(f"[Frame {frame_id}] Model output: {prediction}")
            logger.debug(f"[Frame {frame_id}] Boxes: {boxes}")

            plates = []
            for box, score in zip(boxes, scores):
                x1, y1, x2, y2 = map(int, box)
                plates.append({
                    'label': 'license_plate',
                    'score': float(score),
                    'box': [x1, y1, x2, y2]
                })

            output_record = {
                'frame_id': frame_id,
                'plates': plates,
            }

            if self.write_json and self.output_file:
                self.output_file.write(json.dumps(output_record, ensure_ascii=False) + '\n')
                self.output_file.flush()

            frame.data.setdefault('meta', {})['license_plate_detection'] = plates
            logger.debug(f"[Frame {frame_id}] Detection summary: {output_record}")

            logger.debug(f"forward_detection_rois: {self.forward_detection_rois}")
            if self.forward_detection_rois and plates:
                polygons = []
                for plate in plates:
                    x1, y1, x2, y2 = plate['box']
                    polygon = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                    polygons.append(polygon)

                frame.data['meta'][self.roi_output_label] = polygons
                logger.info(f"[Frame {frame_id}] Forwarded {len(polygons)} polygon(s) under label '{self.roi_output_label}'")

        return frames


if __name__ == '__main__':
    FilterLicensePlateDetection.run()