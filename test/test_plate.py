from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time
def crop_Plate(yolo_model, img):
    model = YOLO(yolo_model)
    count = 0

    # Perform prediction on the image
    results = model.predict(source=img, conf=0.25)

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

def detect_text_with_paddleocr(cropped_image,debug_dir='/workspaces/GATE_KEEPER/backend/debug'):
    """
    This function splits the cropped image horizontally into two halves, performs OCR on each using PaddleOCR,
    and returns the detected text from the lower bounding box in each half if multiple boxes are found.
    Bounding boxes of the selected text are drawn after combining the halves.

    :param cropped_image: numpy array, cropped license plate image
    :return: list of tuples (detected_text, confidence) from lower boxes of both halves
    """
    # Initialize PaddleOCR for Arabic
    ocr = PaddleOCR(use_angle_cls=True, lang='ar', det_db_box_thresh=0.7, det_db_unclip_ratio=1.7)

    # Convert image to BGR if needed
    image = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR) if cropped_image.shape[-1] == 3 else cropped_image
    # print(f"Original image shape: {image.shape}")

    # Split the image horizontally into two halves
    height, width = image.shape[:2]
    mid_point = width // 2
    left_half = image[:, :mid_point, :]  # Left half
    right_half = image[:, mid_point:, :]  # Right half

    # Save halves for debugging
    # cv2.imwrite("debug_left_half.jpg", left_half)
    # cv2.imwrite("debug_right_half.jpg", right_half)
    # print(f"Left half shape: {left_half.shape}, Right half shape: {right_half.shape}")

    # Perform OCR on each half and select the lower box
    detected_texts = []
    texts_only = []
    left_bbox = None
    right_bbox = None

    # Helper function to get the lower box and its bounding box
    def get_lower_box(results):
        if not results or not results[0]:
            return None, None, None
        if len(results[0]) == 1:
            bbox, (text, prob) = results[0][0]
            return text, prob, bbox
        # Multiple boxes: select the one with the highest bottom y-coordinate
        lower_box = max(results[0], key=lambda x: max([p[1] for p in x[0]]))  # Max y of bbox
        bbox, (text, prob) = lower_box
        return text, prob, bbox

    # OCR on left half
    # print("Processing left half...")
    left_results = ocr.ocr(left_half, cls=True)
    if left_results and left_results[0]:
        # print(f"Left half detected {len(left_results[0])} boxes")
        for (bbox, (text, prob)) in left_results[0]:
            # text = text.replace(' ','')[::-1]
            # text.replace(' ','')
            # text = text[::-1]
            # print(f"Left half - Detected text: {text} with confidence {prob:.2f}, BBox: {bbox}")
            pass
        # Select the lower box
        left_text, left_prob, left_bbox = get_lower_box(left_results)
        if left_text:
            detected_texts.append((left_text, left_prob))
            texts_only.append(left_text)
            # print(f"Left half - Selected lower text: {left_text} with confidence {left_prob:.2f}")
    else:
        pass
        # print("No text detected in left half")

    # OCR on right half
    # print("Processing right half...")
    right_results = ocr.ocr(right_half, cls=True)
    if right_results and right_results[0]:
        # print(f"Right half detected {len(right_results[0])} boxes")
        for (bbox, (text, prob)) in right_results[0]:
            # text.replace(' ','')
            # text = text[::-1]
            # print(f"Right half - Detected text: {text} with confidence {prob:.2f}, BBox: {bbox}")
            pass
        # Select the lower box
        right_text, right_prob, right_bbox = get_lower_box(right_results)
        if right_text:
            detected_texts.append((right_text, right_prob))
            texts_only.append(right_text)
            # print(f"Right half - Selected lower text: {right_text} with confidence {right_prob:.2f}")
    else:
        # print("No text detected in right half")
        pass
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

    fname = f"{debug_dir}/plate_{str(int(time()*1000)%10000000)}.jpg"
    cv2.imwrite(fname,combined_image)
    return [detected_texts,texts_only,fname]

if __name__ == "__main__":
    debug_dir='./debug'
    os.makedirs(debug_dir, mode=0o755, exist_ok=True)    
    yolo_model = 'yolo11m_car_plate_trained.pt'
    final_test = crop_Plate(yolo_model,
                            "test.jpg")
    text = detect_text_with_paddleocr(np.array(final_test),debug_dir)
    # text = text[1]
    tmp = []
    for t in text[1]:
        t = t.replace(' ','')
        if not(ord(t[0]) >= 1569 and ord(t[0]) <= 1610):
            tmp.append(t[::-1])
        else:
            tmp.append(t)
    print(f"=========={tmp}==========")

    print(text)