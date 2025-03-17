from fastapi import FastAPI, File, UploadFile, Form
import torch
import numpy as np
import base64
import cv2
import pandas
from io import BytesIO
from PIL import Image
import uvicorn
from ultralytics import YOLO
import python_multipart

app = FastAPI()

model = YOLO("best.pt")

@app.post("/evaluate/")
async def evaluate(file: UploadFile = File(...), component_name: str = Form(...)):
    file_content = await file.read()
    image_data = base64.b64decode(file_content)
    image = Image.open(BytesIO(image_data))
    image_np = np.array(image)

    results = model(image_np)

    detections = [results[0].names[cls.item()] for cls in results[0].boxes.cls.int()]
    signature = 'signature' in detections
    stamp = 'stamp' in detections
    esp = 'esp' in detections

    return {
        "signature": signature,
        "stamp": stamp,
        "esp": esp
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)