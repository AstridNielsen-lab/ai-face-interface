#!/usr/bin/env python3
"""
Extrator de características faciais usando MediaPipe
Detecta olhos e boca na imagem rosto3d.png e salva como imagens separadas
"""

import cv2
import numpy as np
import mediapipe as mp
import os

def extract_eyes_mouth():
    """Extrai olhos e boca da imagem rosto3d.png"""
    
    # Caminhos
    IMAGE_PATH = 'assets/rosto3d.png'
    EYES_OUTPUT = 'assets/eyes.png'
    MOUTH_OUTPUT = 'assets/mouth.png'
    DATA_OUTPUT = 'assets/face_features.json'
    
    print(f"🔍 Processando imagem: {IMAGE_PATH}")
    
    # Verificar se a imagem existe
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Imagem não encontrada: {IMAGE_PATH}")
        return False
    
    # Carregar imagem
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print(f"❌ Erro ao carregar imagem: {IMAGE_PATH}")
        return False
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape
    
    # Inicializar MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Índices dos landmarks para olhos e boca (MediaPipe Face Mesh)
    LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    MOUTH_INDICES = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 
                     78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 95, 88, 178, 87, 14, 317, 402, 318, 324]
    
    try:
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            
            # Processar imagem
            results = face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                print("❌ Nenhuma face detectada")
                return False
            
            face_landmarks = results.multi_face_landmarks[0]
            
            # Converter landmarks para coordenadas de pixel
            landmarks = []
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmarks.append([x, y])
            
            landmarks = np.array(landmarks)
            
            # Extrair região dos olhos
            left_eye_points = landmarks[LEFT_EYE_INDICES]
            right_eye_points = landmarks[RIGHT_EYE_INDICES]
            
            # Combinar ambos os olhos
            all_eye_points = np.vstack([left_eye_points, right_eye_points])
            
            # Calcular bounding box dos olhos com margem
            eye_x_min = max(0, np.min(all_eye_points[:, 0]) - 20)
            eye_y_min = max(0, np.min(all_eye_points[:, 1]) - 15)
            eye_x_max = min(w, np.max(all_eye_points[:, 0]) + 20)
            eye_y_max = min(h, np.max(all_eye_points[:, 1]) + 15)
            
            # Recortar região dos olhos
            eyes_region = image[eye_y_min:eye_y_max, eye_x_min:eye_x_max]
            
            # Salvar imagem dos olhos
            cv2.imwrite(EYES_OUTPUT, eyes_region)
            print(f"✅ Olhos salvos em: {EYES_OUTPUT}")
            
            # Extrair região da boca
            mouth_points = landmarks[MOUTH_INDICES]
            
            # Calcular bounding box da boca com margem
            mouth_x_min = max(0, np.min(mouth_points[:, 0]) - 15)
            mouth_y_min = max(0, np.min(mouth_points[:, 1]) - 10)
            mouth_x_max = min(w, np.max(mouth_points[:, 0]) + 15)
            mouth_y_max = min(h, np.max(mouth_points[:, 1]) + 10)
            
            # Recortar região da boca
            mouth_region = image[mouth_y_min:mouth_y_max, mouth_x_min:mouth_x_max]
            
            # Salvar imagem da boca
            cv2.imwrite(MOUTH_OUTPUT, mouth_region)
            print(f"✅ Boca salva em: {MOUTH_OUTPUT}")
            
            # Salvar dados das características
            features_data = {
                "eyes": {
                    "region": {
                        "x": int(eye_x_min),
                        "y": int(eye_y_min),
                        "width": int(eye_x_max - eye_x_min),
                        "height": int(eye_y_max - eye_y_min)
                    },
                    "left_eye_center": [int(np.mean(left_eye_points[:, 0])), int(np.mean(left_eye_points[:, 1]))],
                    "right_eye_center": [int(np.mean(right_eye_points[:, 0])), int(np.mean(right_eye_points[:, 1]))]
                },
                "mouth": {
                    "region": {
                        "x": int(mouth_x_min),
                        "y": int(mouth_y_min),
                        "width": int(mouth_x_max - mouth_x_min),
                        "height": int(mouth_y_max - mouth_y_min)
                    },
                    "center": [int(np.mean(mouth_points[:, 0])), int(np.mean(mouth_points[:, 1]))]
                },
                "image_dimensions": {
                    "width": w,
                    "height": h
                }
            }
            
            # Salvar dados em JSON
            import json
            with open(DATA_OUTPUT, 'w') as f:
                json.dump(features_data, f, indent=2)
            print(f"✅ Dados das características salvos em: {DATA_OUTPUT}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Extrator de Características Faciais")
    print("=" * 50)
    
    success = extract_eyes_mouth()
    
    if success:
        print("\n🎉 Extração concluída com sucesso!")
        print("As imagens dos olhos e boca foram salvas na pasta assets/")
    else:
        print("\n❌ Falha na extração das características")
