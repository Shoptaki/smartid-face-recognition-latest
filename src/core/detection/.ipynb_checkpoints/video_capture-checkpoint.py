import dlib
import cv2

model_path = 'shape_predictor_68_face_landmarks.dat'


try:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)
except RuntimeError as e:
    print(f"Error loading the model file: {e}")
    print("Ensure that 'shape_predictor_68_face_landmarks.dat' is correctly downloaded and accessible.")
    exit()

def extract_face_vector(frame):
    print(f"Original frame type: {type(frame)}, shape: {frame.shape}")

    if frame.ndim == 2: 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    else:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    print(f"Converted frame type: {type(rgb_frame)}, shape: {rgb_frame.shape}")

    try:
        faces = detector(rgb_frame)
    except Exception as e:
        print(f"Error detecting faces: {e}")
        return []

    face_vectors = []
    for face in faces:
        shape = predictor(rgb_frame, face)
        face_vectors.append(shape)
    return face_vectors

def show_live_video():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            face_vectors = extract_face_vector(frame)
            if face_vectors:
                print("Face Vectors:", face_vectors)

            cv2.imshow('Live Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

show_live_video()
