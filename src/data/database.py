import logging
from minio import Minio
from arango import ArangoClient
from datetime import datetime
import io
import cv2
import numpy as np
import face_recognition

logging.basicConfig(level=logging.INFO)

class Database:

    def __init__(self) -> None:
        self.minio_client = Minio(
            "127.0.0.1:9000",
            access_key="IDgFdoGqKSpuZKXMebrZ",
            secret_key="Hm15AoFalP1LpiGvHZgw19PjwNMDO55ErcdmGpTI",
            secure=False
        )
        self.db = self.get_db()
        self.bucket_name = "shoptaki-images"
        self.create_bucket_if_not_exists(self.bucket_name)

    def get_db(self):
        client = ArangoClient()
        db = client.db('Shoptaki-recog', username='root', password='password')
        if not db.has_collection('images'):
            db.create_collection('images')
        return db

    def create_bucket_if_not_exists(self, bucket_name: str):
        if not self.minio_client.bucket_exists(bucket_name):
            self.minio_client.make_bucket(bucket_name)

    def save_image_to_minio_and_db(self, image: np.ndarray, user_name: str) -> dict:
        logging.info(image)
        
        if image is None or image.size == 0:
            logging.error("Captured image is empty or invalid")
            raise ValueError("Captured image is empty or invalid.")
        
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success:
            logging.error("Failed to encode image")
            raise ValueError("Failed to encode image.")
        
        image_bytes = io.BytesIO(encoded_image.tobytes())

        image_name = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        logging.info(f"Generated image name: {image_name}")

        self.minio_client.put_object(
            self.bucket_name,
            image_name,
            data=image_bytes,
            length=len(image_bytes.getvalue()),
            content_type='image/jpeg'
        )
        logging.info(f"Image saved to MinIO with name: {image_name}")
        face_encoding = face_recognition.face_encodings(image)[0]
        document = {
            "user_name": user_name,
            "image_name": image_name,
            "image_path": f"http://127.0.0.1:9000/{self.bucket_name}/{image_name}",
            "face_encoding": face_encoding.tolist()
        }

        self.db.collection('images').insert(document)
        logging.info(f"Document saved to ArangoDB: {document}")

        return document
