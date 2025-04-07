from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time
from datetime import datetime

class LicensePlateRecognizer:
    VERSION = "1.0.0"
    def __init__(self, model_path, debug_dir):
        self.model = YOLO(model_path)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ar', 
                            det_db_box_thresh=0.7, 
                            det_db_unclip_ratio=1.7)
        self.debug_dir = debug_dir
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)  # Create app/static/debug/ if it doesn’t exist
    
    def save_debug_image(self, image, texts):
        filename = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        debug_path = os.path.join(self.debug_dir, filename)
        cv2.imwrite(debug_path, image)
        return f"/static/debug/{filename}"  # Return URL path
    
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
        # Convert PIL Image to NumPy array first
        image_array = np.array(cropped_image)
        
        # Convert to BGR if the image has 3 channels (RGB)
        image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) if len(image_array.shape) == 3 and image_array.shape[-1] == 3 else image_array

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

        debug_url = self.save_debug_image(combined_image, detected_texts)
        return [detected_texts, texts_only, debug_url]
        
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