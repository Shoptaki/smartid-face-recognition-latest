import cv2
import mediapipe as mp
import face_recognition
from fastapi.responses import JSONResponse

def load_static_image_encoding(image_path):
    static_img = face_recognition.load_image_file(image_path)
    return face_recognition.face_encodings(static_img)[0]

def detect_face_in_video(static_image_encoding):
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
                                results = face_recognition.compare_faces([static_image_encoding], face_encoding)
                                cap.release()
                                cv2.destroyAllWindows()
                                if results[0]:
                                    return JSONResponse(content={"match": True}, status_code=200)
                                else:
                                    return JSONResponse(content={"match": False}, status_code=200)
                        except AttributeError:
                            continue
        except KeyboardInterrupt:
            cap.release()
            cv2.destroyAllWindows()
            return JSONResponse(content={"error": "Keyboard interrupt."}, status_code=500)


static_image_encoding = load_static_image_encoding("photo.jpeg")            
detect_face_in_video(static_image_encoding)