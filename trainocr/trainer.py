import easyocr
import supervision as sv
import cv2
import numpy as np

# Image path
Image_path = '../inn_esp_2_1.jpg'
# Initialize EasyOCR reader (Russian language, CPU)
reader = easyocr.Reader(lang_list=['ru', 'en'],
                        model_storage_directory='model',
                        user_network_directory='user_network',
                        recog_network='iter_50000',
                        )

# Perform text detection on the image
result = reader.readtext(Image_path, allowlist='0123456789-.()№ АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяI')

# Load image using OpenCV
image = cv2.imread(Image_path)

# Prepare lists for bounding boxes, confidences, class IDs, and labels
xyxy, confidences, class_ids, label = [], [], [], []

# Extract data from OCR result
for detection in result:
    bbox, text, confidence = detection[0], detection[1], detection[2]

    # Convert bounding box format
    x_min = int(min([point[0] for point in bbox]))
    y_min = int(min([point[1] for point in bbox]))
    x_max = int(max([point[0] for point in bbox]))
    y_max = int(max([point[1] for point in bbox]))

    # Append data to lists
    xyxy.append([x_min, y_min, x_max, y_max])
    label.append(text)
    confidences.append(confidence)
    class_ids.append(0)

# Convert to NumPy arrays
detections = sv.Detections(
    xyxy=np.array(xyxy),
    confidence=np.array(confidences),
    class_id=np.array(class_ids)
)

# Annotate image with bounding boxes and labels
box_annotator = sv.BoxAnnotator()
annotated_image = box_annotator.annotate(scene=image, detections=detections)

# Use OpenCV to add Russian text labels
font = cv2.FONT_HERSHEY_COMPLEX
font_scale = 0.7
font_color = (0, 0, 0)  # Green color
font_thickness = 2

for i, (bbox, text) in enumerate(zip(xyxy, label)):
    x_min, y_min, x_max, y_max = bbox
    cv2.putText(annotated_image, text, (x_min, y_min - 10), font, font_scale, font_color, font_thickness)

# Display and save the annotated image
cv2.imshow('', annotated_image)
cv2.imwrite("../output.jpg", annotated_image)
