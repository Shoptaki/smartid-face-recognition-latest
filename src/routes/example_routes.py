from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
from src.core.detection.fdlite import FaceDetection, FaceDetectionModel

router = APIRouter()
model = FaceDetection(model_type=FaceDetectionModel.FRONT_CAMERA)

@router.get("/")
def read_example():
    return "You've landed on FastAPI"

@router.get("/detection")
async def detect_faces(file: UploadFile = File(...)):
    try:
        # Read image file
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Run face detection
        detections = model(image)

        # Prepare response
        response = [
            {
                "bbox": {
                    "xmin": float(detection.bbox[0]),
                    "ymin": float(detection.bbox[1]),
                    "xmax": float(detection.bbox[2]),
                    "ymax": float(detection.bbox[3])
                },
                "score": float(detection.score)
            }
            for detection in detections
        ]

        return JSONResponse(content={"detections": response})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/example/")
def read_example():
    return {"message": "This is an example route"}