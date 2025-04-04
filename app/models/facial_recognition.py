import torch
import numpy as np
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import pickle
import base64
import re
from PIL import Image

class FacialRecognition:
    VERSION = "1.0.0"
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(image_size=160, margin=10, keep_all=False, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def process_image_data(self, image_data):
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = re.sub('^data:image/.+;base64,', '', image_data)
            image_data = base64.b64decode(image_data)
        
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def generate_embedding(self, image_data):
        img = self.process_image_data(image_data)
        if img is None:
            raise ValueError("Invalid image data")

        face = self.mtcnn(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if face is None:
            raise ValueError("No face detected")

        face = face.unsqueeze(0).to(self.device)
        embedding = self.resnet(face).detach().cpu().numpy().flatten()
        return embedding

    def compare_embeddings(self, embedding1, embedding2):
        return np.linalg.norm(embedding1 - embedding2)