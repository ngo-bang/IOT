from deepface import DeepFace
import cv2
def encode_face(image):
    resp_obj = DeepFace.represent(image, model_name='ArcFace', detector_backend="retinaface")
    embedding_vector = resp_obj[0]['embedding']
    return embedding_vector

