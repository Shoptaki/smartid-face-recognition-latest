import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import logging
from fastapi.responses import JSONResponse
import time


class Biometric:

    def __init__(self, db):
        self.db = db

    def fetch_encodings_from_db(self):
        cursor = self.db.collection('images').all()
        encodings = []
        user_names = []

        for document in cursor:
            face_encoding = document['face_encoding']
            user_name = document['user_name']
            encodings.append(face_encoding)
            user_names.append(user_name)

        return encodings, user_names

    def detect_face_in_video(self, frame, encodings, user_names):
        mp_face_detection = mp.solutions.face_detection
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logging.info(f"Converted frame to RGB.{frame_rgb}")

        try:
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.3) as face_detection:
                results = face_detection.process(frame_rgb)
                logging.info(f"Detection results: {results}")

                if results.detections:
                    logging.info(f"Detected {len(results.detections)} face(s).")
                    for detection in results.detections:
                        h, w, _ = frame.shape
                        top = int(detection.location_data.relative_bounding_box.ymin * h)
                        right = int((detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width) * w)
                        bottom = int((detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height) * h)
                        left = int(detection.location_data.relative_bounding_box.xmin * w)

                        logging.info(f"ROI Coordinates: top={top}, right={right}, bottom={bottom}, left={left}")
                        
                        if top >= bottom or left >= right:
                            logging.error("Invalid ROI coordinates.")
                            continue

                        face_roi = frame_rgb[top:bottom, left:right]
                        logging.info(f"Face ROI shape: {face_roi.shape}")

                        face_roi_bgr = cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR)
                        logging.info(f"this is face roi bgr {face_roi_bgr}")
                        face_locations = face_recognition.face_locations(face_roi_bgr,model='cnn')
                        face_encodings = face_recognition.face_encodings(face_roi_bgr, face_locations)

                        logging.info(f"Detected face locations: {face_locations}")
                        logging.info(f"Face encodings: {face_encodings}")

                        if face_encodings:
                            face_encoding = face_encodings[0]
                            matches = face_recognition.compare_faces(encodings, face_encoding)
                            distances = face_recognition.face_distance(encodings, face_encoding)

                            logging.info(f"Matches: {matches}")
                            logging.info(f"Distances: {distances}")

                            if True in matches:
                                match_index = matches.index(True)
                                return {"match": True, "user_name": user_names[match_index]}
                            else:
                                return {"match": False}
                        else:
                            logging.info("No face encodings found in the frame.")
                            return {"match": False}
                else:
                    logging.info("No detections found in the frame.")
                    return {"match": False}
        except Exception as e:
            logging.error(f"Error during face detection: {e}")
            return {"error": str(e)}



    # def detect_face_in_frame(self, frame, encodings, user_names):
    #     mp_face_detection = mp.solutions.face_detection

    #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.2) as face_detection:
    #         results = face_detection.process(frame_rgb)

    #         if results.detections:
    #             for detection in results.detections:
    #                 h, w, _ = frame_rgb.shape
    #                 top = int(detection.location_data.relative_bounding_box.ymin * h)
    #                 right = int((detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width) * w)
    #                 bottom = int((detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height) * h)
    #                 left = int(detection.location_data.relative_bounding_box.xmin * w)
    #                 face_roi = frame_rgb[top:bottom, left:right]

    #                 face_roi_bgr = cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR)
    #                 face_locations = face_recognition.face_locations(face_roi_bgr)
    #                 face_encodings = face_recognition.face_encodings(face_roi_bgr, face_locations)

    #                 if face_encodings:
    #                     face_encoding = face_encodings[0]
    #                     matches = face_recognition.compare_faces(encodings, face_encoding)
    #                     if True in matches:
    #                         match_index = matches.index(True)
    #                         return {"match": True, "user_name": user_names[match_index]}
    #                     else:
    #                         return {"match": False}
    #         return {"error": "No face detected"}