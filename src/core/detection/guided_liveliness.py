import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import logging
from fastapi.responses import JSONResponse

class GuidedLivenessDetection:

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.required_steps = ["look_left", "look_right", "blink"]
        self.current_step = 0

    def detect_movement(self, frame):
        with self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Check for the current required movement
                if self.required_steps[self.current_step] == "look_left":
                    if self.is_head_turned(face_landmarks, direction="left"):
                        logging.info("User performed: look_left")
                        self.current_step += 1

                elif self.required_steps[self.current_step] == "look_right":
                    if self.is_head_turned(face_landmarks, direction="right"):
                        logging.info("User performed: look_right")
                        self.current_step += 1

                elif self.required_steps[self.current_step] == "blink":
                    if self.is_blinking(face_landmarks):
                        logging.info("User performed: blink")
                        self.current_step += 1

                if self.current_step >= len(self.required_steps):
                    logging.info("Liveness confirmed after all required steps were performed.")
                    return True  # Liveness confirmed

        return False  # Liveness not confirmed yet

    def is_head_turned(self, landmarks, direction):
        nose_tip = landmarks.landmark[1]
        nose_position = nose_tip.x

        if direction == "left" and nose_position < 0.4:  
            return True
        if direction == "right" and nose_position > 0.6:  
            return True

        return False

    def is_blinking(self, landmarks):
        left_eye_indices = [33, 160, 158, 133, 153, 144]
        right_eye_indices = [362, 385, 387, 263, 373, 380]

        left_ear = self.calculate_ear(landmarks, left_eye_indices)
        right_ear = self.calculate_ear(landmarks, right_eye_indices)
        ear = (left_ear + right_ear) / 2.0

        return ear < 0.2  

    def calculate_ear(self, landmarks, indices):
        eye_points = np.array([(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in indices])
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear

