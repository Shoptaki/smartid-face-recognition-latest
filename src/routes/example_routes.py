from fastapi import APIRouter, FastAPI, HTTPException, Form
import cv2
import logging
from core.detection.video_capture import Biometric
from data.database import Database
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()
database = Database()
biometric = Biometric(database.db)

@router.get("/")
def read_example():
    return "You've landed on FastAPI"

# For capturing and saving
@router.post("/capture")
def capture_and_save_image(user_name: str = Form(...)):
    logging.info("Starting /capture endpoint")
    
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    if not cap.isOpened():
        logging.error("Unable to access the webcam")
        raise HTTPException(status_code=500, detail="Unable to access the webcam.")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to capture image.")

    if frame is None or frame.size == 0:
        raise HTTPException(status_code=500, detail="Captured image is empty or invalid.")

    try:
        document = database.save_image_to_minio_and_db(frame, user_name)
    except ValueError as e:
        logging.error(f"Error in save_image_to_minio_and_db: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    logging.info("Image captured and saved successfully")
    return {"message": "Image captured and saved successfully.", "document": document}

@router.get("/detection")
def face_recognition_endpoint():
    encodings, user_names = biometric.fetch_encodings_from_db()
    return biometric.detect_face_in_video(encodings, user_names)

@router.get("/example/")
def read_example():
    return {"message": "This is an example route"}
