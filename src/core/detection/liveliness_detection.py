import cv2
import numpy as np
from skimage.feature import local_binary_pattern
import dlib
from absl import logging

# Configure logging
logging.set_verbosity(logging.ERROR)

class LivenessDetection:
    def __init__(self):
        self.prev_frame = None
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # Load your dlib shape predictor model

    # Motion Detection
    def detect_motion(self, frame):
        if self.prev_frame is None:
            self.prev_frame = frame
            return False

        diff = cv2.absdiff(self.prev_frame, frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        non_zero_count = cv2.countNonZero(thresh)

        self.prev_frame = frame

        return non_zero_count > 1000  # Arbitrary threshold for motion

    # Texture Analysis
    def analyze_texture(self, face_image):
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, 26), range=(0, 25))
        return hist  # Further analysis

    # Blink Detection
    def is_blinking(self, eye_landmarks):
        ear = self.calculate_ear(eye_landmarks)
        return ear < 0.2  # Adjust threshold as necessary

    def calculate_ear(self, eye_landmarks):
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (A + B) / (2.0 * C)

    # Challenge-Response Test
    def show_prompt(self, frame, prompt_text):
        cv2.putText(frame, prompt_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Main Method for Video Processing
    def detect_liveness(self, encodings, user_names):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Unable to access the webcam.")
            return "Unable to access the webcam."

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to capture image.")
                continue

            # Check liveness by motion detection
            if not self.detect_motion(frame):
                continue

            # Show a prompt to the user (e.g., "Please look left")
            self.show_prompt(frame, "Please look left")

            # Convert frame to RGB for face detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.detector(frame_rgb)

            for face in faces:
                landmarks = self.predictor(frame_rgb, face)
                landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])

                # Process face texture
                face_roi = frame[face.top():face.bottom(), face.left():face.right()]
                texture_hist = self.analyze_texture(face_roi)
                
                # Check for blinking
                # Note: You need to extract eye landmarks and pass them to is_blinking method
                
                # For demonstration, let's assume a function `detect_eye_landmarks` exists
                # eye_landmarks = detect_eye_landmarks(frame, landmarks)
                # if self.is_blinking(eye_landmarks):
                #     logging.info("Blink detected.")

            cv2.imshow("Liveness Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return "Liveness detection completed."
