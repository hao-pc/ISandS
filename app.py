from fastapi import FastAPI, File, UploadFile, Form
import torch
import numpy as np
import base64
import cv2
import pandas
from io import BytesIO
from PIL import Image
import uvicorn
from starlette.responses import JSONResponse
from ultralytics import YOLO
import pytesseract
from pdf2image import convert_from_path
import python_multipart

app = FastAPI()

model = YOLO("best.pt")

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
tessdata_dir_config = r'C:/Program Files/Tesseract-OCR/tessdata'

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image, lang='rus', config=tessdata_dir_config).lower().replace('\n', ' ').replace('  ', ' ').strip()
    return text

@app.post("/evaluate/")
async def evaluate(file: UploadFile = File(...), component_name: str = Form(...)):
    file_content = await file.read()
    image_data = base64.b64decode(file_content)
    image = Image.open(BytesIO(image_data))

    if file.filename.endswith('.pdf'):
        images = convert_from_path(pdf_path=BytesIO(image_data), poppler_path='C:/poppler-24.08.0/Library/bin')
        text = ""
        for img in images:
            text += pytesseract.image_to_string(image, lang='rus', config=tessdata_dir_config)
    else:
        text = pytesseract.image_to_string(image, lang='rus', config=tessdata_dir_config)

    image_np = np.array(image)

    results = model(image_np)

    detections = [results[0].names[cls.item()] for cls in results[0].boxes.cls.int()]
    signature = 'signature' in detections
    stamp = 'stamp' in detections
    esp = 'esp' in detections

    print(component_name)
    print(text)

    contains_component = component_name.lower() in text

    print(contains_component)

    return JSONResponse({
        "label": contains_component,
        "signature": signature,
        "stamp": stamp,
        "esp": esp
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)