from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import logging
import numpy as np
import cv2
from core.detection.video_capture import Biometric
from data.database import Database
from fastapi import File, UploadFile, Form, HTTPException

app = FastAPI()
router = APIRouter()
database = Database()
biometric = Biometric(database.db)

clients = {}


@router.get("/")
async def hello():
    return {"Hello" : "World" }

@router.post("/capture")
async def capture_and_save_image(file: UploadFile = File(...), user_name: str = Form(...)):
    logging.info("Starting /capture endpoint")
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        logging.error(f"Failed to read image file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read image file.")

    if frame is None or frame.size == 0:
        raise HTTPException(status_code=500, detail="Uploaded image is empty or invalid.")

    try:
        document = database.save_image_to_minio_and_db(frame, user_name)
    except ValueError as e:
        logging.error(f"Error in save_image_to_minio_and_db: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    logging.info("Image captured and saved successfully")
    return {"message": "Image captured and saved successfully.", "document": document}

@router.websocket("/ws/detection")
async def websocket_detection(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)
    clients[client_id] = websocket
    encodings, user_names = biometric.fetch_encodings_from_db()

    try:
        while True:
            data = await websocket.receive_bytes()
            nparr = np.frombuffer(data, dtype="uint8")
            frame = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
            # frame = cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB)
            # logging.info(frame)
            if frame is None or frame.size == 0:
                logging.error(f"Received empty frame from client {client_id}")
                continue

            logging.info(f"Received frame from client {client_id} with shape {frame.shape}")
            result = biometric.detect_face_in_video(frame, encodings, user_names)
            
            if client_id in clients:
                if websocket.client_state == websocket.client_state.CONNECTED:
                    logging.info(result)
                    await websocket.send_json(result)
                # if result.get("error") is not None:
                #     break
            else:
                break

    except WebSocketDisconnect:
        logging.info(f"Client {client_id} disconnected")
    except Exception as e:
        logging.error(f"Error during WebSocket communication with client {client_id}: {e}")
    finally:
        if client_id in clients:
            clients.pop(client_id, None)
        if websocket.client_state == websocket.client_state.CONNECTED:
            await websocket.close()
