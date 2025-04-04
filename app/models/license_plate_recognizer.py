from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time

class LicensePlateRecognizer:
    VERSION = "1.0.0"
    def __init__(self, model_path, debug_dir):
        self.model = YOLO(model_path)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ar', 
                            det_db_box_thresh=0.7, 
                            det_db_unclip_ratio=1.7)
        self.debug_dir = debug_dir

    def crop_plate(self, img):
        # Perform prediction on the image
        results = self.model.predict(source=img, conf=0.25)

        # Open the image
        image = Image.open(img)

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                max_width = -1
                selected_box = None

                # Iterate through all detected boxes to find the one with the maximum width
                for box in result.boxes:
                    res = box.xyxy[0]  # Get the coordinates of the bounding box
                    width = res[2].item() - res[0].item()  # Calculate width (x_max - x_min)

                    if width > max_width:
                        max_width = width
                        selected_box = res  # Store the coordinates of the selected box

                if selected_box is not None:
                    x_min = selected_box[0].item()
                    y_min = selected_box[1].item()
                    x_max = selected_box[2].item()
                    y_max = selected_box[3].item()

                    # Crop the image using the bounding box coordinates
                    cropped_image = image.crop((x_min, y_min, x_max, y_max))
                    return cropped_image
            else:
                print("No bounding boxes detected.")
        return None

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
        # Convert image to BGR if needed
        image = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR) if cropped_image.shape[-1] == 3 else cropped_image

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
        left_results = self.ocr.ocr(left_half, cls=True)
        if left_results and left_results[0]:
            left_text, left_prob, left_bbox = self.get_lower_box(left_results)
            if left_text:
                detected_texts.append((left_text, left_prob))
                texts_only.append(left_text)

        # OCR on right half
        right_results = self.ocr.ocr(right_half, cls=True)
        if right_results and right_results[0]:
            right_text, right_prob, right_bbox = self.get_lower_box(right_results)
            if right_text:
                detected_texts.append((right_text, right_prob))
                texts_only.append(right_text)

        # Combine the halves back for visualization
        combined_image = np.hstack((left_half, right_half))

        # Draw bounding boxes on the combined image
        if left_bbox is not None:
            left_bbox = np.array(left_bbox).astype(int)
            cv2.polylines(combined_image, [left_bbox], isClosed=True, color=(0, 255, 0), thickness=1)
        if right_bbox is not None:
            right_bbox = np.array(right_bbox).astype(int)
            right_bbox[:, 0] += mid_point  # Shift x-coordinates to match combined image
            cv2.polylines(combined_image, [right_bbox], isClosed=True, color=(0, 255, 0), thickness=1)

        fname = f"{self.debug_dir}/plate_{str(int(time()*1000)%10000000)}.jpg"
        cv2.imwrite(fname, combined_image)
        return [detected_texts, texts_only, fname]

    @staticmethod
    def clean_text(texts):
        tmp = []
        for t in texts:
            t = t.replace(' ','')
            if not(ord(t[0]) >= 1569 and ord(t[0]) <= 1610):
                tmp.append(t[::-1])
            else:
                tmp.append(t)
        return tmp