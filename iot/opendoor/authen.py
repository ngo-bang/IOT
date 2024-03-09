from .encode import encode_face
import numpy as np
THRESHOLD = 0.6
def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def authe_image(img,emb2):
    emb1 = encode_face(img)
    if findCosineDistance(emb1,emb2)<THRESHOLD:
        return True
    return False
