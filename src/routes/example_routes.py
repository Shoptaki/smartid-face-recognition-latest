from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
# from core.detection.test import load_static_image_encoding, detect_face_in_video

router = APIRouter()

@router.get("/")
def read_example():
    return "You've landed on FastAPI"

@router.get("/detection")
# def face_recognition_endpoint():
#     static_image_encoding = load_static_image_encoding("photo.jpeg")
#     return detect_face_in_video(static_image_encoding)

@router.get("/example/")
def read_example():
    return {"message": "This is an example route"}