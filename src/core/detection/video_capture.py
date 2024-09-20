import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import logging
from fastapi.responses import JSONResponse
import time
from tensorflow.keras.models import load_model

class Biometric:
    def __init__(self, db):
        self.db = db
        # Load the liveness detection model
        self.liveness_model = load_model('/Users/gappiboi/Desktop/EPICS/shoptaki-smartid/src/core/detection/model.h5')

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
        
        try:
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
                results = face_detection.process(frame_rgb)
                logging.info(f"Detection results: {results}")

                h, w, _ = frame.shape
                logging.info(f"Frame dimensions: height={h}, width={w}")

                if results.detections:
                    logging.info(f"Detected {len(results.detections)} face(s).")
                    for detection in results.detections:
                        # Normalize ROI coordinates
                        top = int(detection.location_data.relative_bounding_box.ymin * h)
                        right = int((detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width) * w)
                        bottom = int((detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height) * h)
                        left = int(detection.location_data.relative_bounding_box.xmin * w)

                        logging.info(f"Normalized ROI Coordinates: top={top}, right={right}, bottom={bottom}, left={left}")

                        # Adjust the ROI size for close distances
                        roi_width = right - left
                        roi_height = bottom - top
                        # If the face is too close, the ROI might be too small, so increase it
                        if roi_width < 100 or roi_height < 100:
                            margin = 50  # Adjust the margin as needed
                            top = max(0, top - margin)
                            left = max(0, left - margin)
                            bottom = min(h, bottom + margin)
                            right = min(w, right + margin)

                        face_roi = frame_rgb[top:bottom, left:right]
                        face_roi_bgr = cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR)

                        # Resize the face ROI for the liveness model
                        face_for_liveness = cv2.resize(face_roi_bgr, (150, 150))
                        face_for_liveness = face_for_liveness.astype('float32') / 255.0
                        face_for_liveness = np.expand_dims(face_for_liveness, axis=0)

                        # Predict liveness
                        liveness_prediction = self.liveness_model.predict(face_for_liveness)
                        liveness_score = liveness_prediction[0][0]

                        logging.info(f"Liveness score: {liveness_score}")

                        if liveness_score < 0.95:
                            return {"match": False, "liveness": False, "reason": "Spoof detected"}

                        # Proceed with facial recognition
                        face_locations = face_recognition.face_locations(face_roi_bgr, model='cnn')
                        face_encodings = face_recognition.face_encodings(face_roi_bgr, face_locations)

                        if face_encodings:
                            face_encoding = face_encodings[0]
                            matches = face_recognition.compare_faces(encodings, face_encoding)
                            distances = face_recognition.face_distance(encodings, face_encoding)
                            if True in matches:
                                match_index = matches.index(True)
                                return {"match": True, "user_name": user_names[match_index], "liveness": True}
                            else:
                                return {"match": False, "liveness": True}
                        else:
                            logging.info("No face encodings found in the frame.")
                            return {"match": False, "liveness": True}
                else:
                    logging.info("No detections found in the frame.")
                    return {"match": False, "liveness": False}
        except Exception as e:
            return {"error": str(e)}

