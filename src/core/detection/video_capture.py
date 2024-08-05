import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import logging
from fastapi.responses import JSONResponse

class Biometric:

    def __init__(self, db):
        self.db = db

    def fetch_encodings_from_db(self):
        cursor = self.db.collection('images').all()
        encodings = []
        user_names = []

        for document in cursor:
            logging.info(document)
            face_encoding = document['face_encoding']
            user_name = document['user_name']
            encodings.append(face_encoding)
            user_names.append(user_name)

        return encodings, user_names

    def detect_face_in_video(self, encodings, user_names):
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return JSONResponse(content={"error": "Unable to access the webcam."}, status_code=500)

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.2) as face_detection:
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        return JSONResponse(content={"error": "Failed to capture image."}, status_code=500)

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(frame_rgb)

                    if results.detections:
                        for detection in results.detections:
                            h, w, _ = frame_rgb.shape
                            try:
                                top = int(detection.location_data.relative_bounding_box.ymin * h)
                                right = int((detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width) * w)
                                bottom = int((detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height) * h)
                                left = int(detection.location_data.relative_bounding_box.xmin * w)
                                face_roi = frame_rgb[top:bottom, left:right]

                                face_roi_bgr = cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR)
                                face_locations = face_recognition.face_locations(face_roi_bgr)
                                face_encodings = face_recognition.face_encodings(face_roi_bgr, face_locations)

                                if face_encodings:
                                    face_encoding = face_encodings[0]
                                    matches = face_recognition.compare_faces(encodings, face_encoding)
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    if True in matches:
                                        match_index = matches.index(True)
                                        return JSONResponse(content={"match": True, "user_name": user_names[match_index]}, status_code=200)
                                    else:
                                        return JSONResponse(content={"match": False}, status_code=200)
                            except AttributeError:
                                continue
            except KeyboardInterrupt:
                cap.release()
                cv2.destroyAllWindows()
                return JSONResponse(content={"error": "Keyboard interrupt."}, status_code=500)
