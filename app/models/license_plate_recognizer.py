from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LicensePlateRecognizer:
    VERSION = "2.0.0"
    
    def __init__(self, yolo_model_path, debug_dir):
        self.yolo_model_path = yolo_model_path
        self.debug_dir = debug_dir
        self.last_debug_image = None
        self.last_raw_result = None
        try:
            # Load YOLO model
            self.model = YOLO(yolo_model_path)
            logger.info(f"YOLO model loaded successfully from {yolo_model_path}")
        except Exception as e:
            logger.error(f"Failed to initialize YOLO model: {str(e)}")
            raise
        
        try:
            # Explicitly disable GPU for PaddleOCR unless confirmed working
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ar', use_gpu=False, 
                               det_db_box_thresh=0.7, det_db_unclip_ratio=1.7)
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise

    def save_debug_image(self, image, texts):
        filename = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        debug_path = os.path.join(self.debug_dir, filename)
        os.makedirs(self.debug_dir, exist_ok=True)  # Ensure directory exists
        success = cv2.imwrite(debug_path, image)
        if not success:
            logger.error(f"Failed to save debug image to {debug_path}")
        logger.info(f"Debug image saved: {debug_path} with texts: {texts}")
        return f"/static/debug/{filename}"  # Return URL path
    
    def crop_plate(self, img):
        try:
            # Perform prediction on the image (img can be path or array)
            results = self.model.predict(source=img, conf=0.25)
            logger.info(f"YOLO prediction completed with {len(results)} results")

            # Open the image as PIL if img is a path, else convert from array
            if isinstance(img, str):
                image = Image.open(img)
            elif isinstance(img, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            else:
                raise ValueError("Unsupported image type for cropping")

            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    max_width = -1
                    selected_box = None

                    # Find the box with the maximum width
                    for box in result.boxes:
                        res = box.xyxy[0]  # Get coordinates
                        width = res[2].item() - res[0].item()  # x_max - x_min

                        if width > max_width:
                            max_width = width
                            selected_box = res

                    if selected_box is not None:
                        x_min, y_min, x_max, y_max = map(int, selected_box)
                        cropped_image = image.crop((x_min, y_min, x_max, y_max))
                        logger.info(f"Cropped plate: ({x_min}, {y_min}, {x_max}, {y_max})")
                        return cropped_image
                else:
                    logger.info("No bounding boxes detected by YOLO")
            return None
        except Exception as e:
            logger.exception(f"Error cropping plate: {str(e)}")
            raise

    def get_lower_box(self, results):
        if not results or not results[0]:
            return None, None, None
        if len(results[0]) == 1:
            bbox, (text, prob) = results[0][0]
            return text, prob, bbox
        # Multiple boxes: select the one with the highest bottom y-coordinate
        lower_box = max(results[0], key=lambda x: max([p[1] for p in x[0]]))  # Max y of bbox
        bbox, (text, prob) = lower_box
        return text, prob, bbox

    def detect_text(self, cropped_image):
        try:
            # Convert PIL Image to NumPy array
            image_array = np.array(cropped_image)
            
            # Convert to BGR if the image has 3 channels (RGB)
            image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) if len(image_array.shape) == 3 and image_array.shape[-1] == 3 else image_array
            logger.info(f"Processing image with shape: {image.shape}")

            # Split the image horizontally into two halves
            height, width = image.shape[:2]
            mid_point = width // 2
            left_half = image[:, :mid_point, :]  # Left half
            right_half = image[:, mid_point:, :]  # Right half

            # Perform OCR on each half and select the lower box
            detected_texts = []
            texts_only = []
            left_bbox = None
            right_bbox = None

            # OCR on left half
            try:
                left_results = self.ocr.ocr(left_half, cls=True)
                if left_results and left_results[0]:
                    left_text, left_prob, left_bbox = self.get_lower_box(left_results)
                    if left_text:
                        detected_texts.append((left_text, left_prob))
                        texts_only.append(left_text)
                        logger.info(f"Left half text: {left_text}, prob: {left_prob}")
            except RuntimeError as e:
                logger.exception(f"PaddleOCR failed on left half: {str(e)}")
                raise

            # OCR on right half
            try:
                right_results = self.ocr.ocr(right_half, cls=True)
                if right_results and right_results[0]:
                    right_text, right_prob, right_bbox = self.get_lower_box(right_results)
                    if right_text:
                        detected_texts.append((right_text, right_prob))
                        texts_only.append(right_text)
                        logger.info(f"Right half text: {right_text}, prob: {right_prob}")
            except RuntimeError as e:
                logger.exception(f"PaddleOCR failed on right half: {str(e)}")
                raise

            # Combine the halves back for visualization
            combined_image = np.hstack((left_half, right_half))

            # Draw bounding boxes on the combined image
            if left_bbox is not None:
                left_bbox = np.array(left_bbox).astype(int)
                cv2.polylines(combined_image, [left_bbox], isClosed=True, color=(0, 255, 0), thickness=1)
            if right_bbox is not None:
                right_bbox = np.array(right_bbox).astype(int)
                right_bbox[:, 0] += mid_point  # Shift x-coordinates
                cv2.polylines(combined_image, [right_bbox], isClosed=True, color=(0, 255, 0), thickness=1)

            debug_url = self.save_debug_image(combined_image, detected_texts)
            return [detected_texts, texts_only, debug_url]
        
        except Exception as e:
            logger.exception(f"Error in detect_text: {str(e)}")
            raise

    @staticmethod
    def clean_text(texts):
        tmp = []
        for t in texts:
            t = t.replace(' ', '')
            if not (1569 <= ord(t[0]) <= 1610):  # Check if first char is Arabic
                tmp.append(t[::-1])  # Reverse if not Arabic
            else:
                tmp.append(t)
        return tmp