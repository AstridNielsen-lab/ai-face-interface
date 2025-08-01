import cv2
import dlib
import os
import json
from face_analyzer import FaceAnalyzer

# Caminhos
IMAGE_PATH = 'assets/rosto3d.png'
EYES_OUTPUT = 'assets/eyes.png'
MOUTH_OUTPUT = 'assets/mouth.png'

# Inicializar analisador de face
analyzer = FaceAnalyzer()

# Carregar imagem
def load_image(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

# Salvar características faciais

def save_facial_features():
    image = load_image(IMAGE_PATH)
    faces = analyzer.detect_faces(image)
    if not faces:
        print("Nenhuma face detectada.")
        return

    face_rect = faces[0]
    landmarks = analyzer.get_landmarks(image, face_rect)
    
    # Analisar olhos
    eyes = analyzer.analyze_eyes(landmarks)
    
    # Recortar olhos
    left_eye = landmarks[analyzer.LEFT_EYE_POINTS]
    right_eye = landmarks[analyzer.RIGHT_EYE_POINTS]
    (x_min, y_min) = left_eye.min(axis=0)
    (x_max, y_max) = right_eye.max(axis=0)
    eyes_img = image[y_min:y_max, x_min:x_max]
    cv2.imwrite(EYES_OUTPUT, cv2.cvtColor(eyes_img, cv2.COLOR_RGB2BGR))

    # Analisar boca
    mouth = analyzer.analyze_mouth(landmarks)

    # Recortar boca
    mouth_outer = landmarks[analyzer.MOUTH_OUTLINE_POINTS]
    (x_min, y_min) = mouth_outer.min(axis=0)
    (x_max, y_max) = mouth_outer.max(axis=0)
    mouth_img = image[y_min:y_max, x_min:x_max]
    cv2.imwrite(MOUTH_OUTPUT, cv2.cvtColor(mouth_img, cv2.COLOR_RGB2BGR))

    print(f"Olhos e boca salvos como {EYES_OUTPUT} e {MOUTH_OUTPUT}.")

if __name__ == "__main__":
    save_facial_features()
