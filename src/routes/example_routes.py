from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import logging
import numpy as np
import cv2
from core.detection.video_capture import Biometric
from data.database import Database

app = FastAPI()
router = APIRouter()
database = Database()
biometric = Biometric(database.db)

clients = {}

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
            logging.info(frame)
            if frame is None or frame.size == 0:
                logging.error(f"Received empty frame from client {client_id}")
                continue

            logging.info(f"Received frame from client {client_id} with shape {frame.shape}")
            result = biometric.detect_face_in_video(frame, encodings, user_names)
            
            if client_id in clients:
                if websocket.client_state == websocket.client_state.CONNECTED:
                    logging.info(result)
                    await websocket.send_json(result)
                if result.get("match") or result.get("error") is not None:
                    break
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
