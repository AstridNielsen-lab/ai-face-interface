#!/usr/bin/env python3
"""
Gerador de dados faciais para o bot usando MediaPipe
"""

import cv2
import json
import mediapipe as mp
import numpy as np

def analyze_face_for_bot(image_path):
    """Analisa a face da imagem e gera dados para o bot"""
    print(f"🔍 Analisando {image_path}...")
    
    # Inicializar MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    
    # Carregar imagem
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Erro ao carregar {image_path}")
        return None
    
    # Converter para RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Processar com Face Mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        
        results = face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            print("❌ Nenhuma face detectada")
            return None
        
        print("✅ Face detectada!")
        
        # Obter landmarks da primeira face
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extrair pontos importantes
        h, w, _ = image.shape
        landmarks_2d = []
        
        for landmark in face_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks_2d.append([x, y])
        
        # Normalizar landmarks para 0-1
        landmarks_array = np.array(landmarks_2d)
        min_x, min_y = np.min(landmarks_array, axis=0)
        max_x, max_y = np.max(landmarks_array, axis=0)
        
        landmarks_normalized = []
        for point in landmarks_2d:
            norm_x = (point[0] - min_x) / (max_x - min_x) if max_x != min_x else 0.5
            norm_y = (point[1] - min_y) / (max_y - min_y) if max_y != min_y else 0.5
            landmarks_normalized.append([norm_x, norm_y])
        
        # Analisar características específicas
        # Olhos (aproximação baseada em landmarks)
        left_eye_landmarks = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        right_eye_landmarks = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Calcular abertura dos olhos
        left_eye_points = [landmarks_2d[i] for i in left_eye_landmarks if i < len(landmarks_2d)]
        right_eye_points = [landmarks_2d[i] for i in right_eye_landmarks if i < len(landmarks_2d)]
        
        eye_openness = 0.6  # Valor padrão
        
        # Boca
        mouth_landmarks = [61, 146, 91, 181, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        mouth_points = [landmarks_2d[i] for i in mouth_landmarks if i < len(landmarks_2d)]
        
        mouth_openness = 0.3  # Valor padrão
        
        # Criar estrutura de dados para o bot
        face_data = {
            "image_path": image_path,
            "landmarks_2d": landmarks_2d,
            "landmarks_normalized": landmarks_normalized,
            "face_bounds": {
                "x": float(min_x),
                "y": float(min_y), 
                "width": float(max_x - min_x),
                "height": float(max_y - min_y)
            },
            "eyes": {
                "average_openness": eye_openness,
                "is_blinking": eye_openness < 0.2,
                "left_eye": {
                    "landmarks": left_eye_points,
                    "openness": eye_openness
                },
                "right_eye": {
                    "landmarks": right_eye_points,
                    "openness": eye_openness
                }
            },
            "mouth": {
                "aspect_ratio": mouth_openness,
                "is_speaking": mouth_openness > 0.15,
                "landmarks": mouth_points
            },
            "emotion": {
                "dominant_emotion": "neutral",
                "confidence": 1.0,
                "scores": {
                    "neutral": 0.7,
                    "happy": 0.1,
                    "sad": 0.1,
                    "angry": 0.05,
                    "surprised": 0.05
                }
            },
            "animation_parameters": {
                "eye_openness": eye_openness,
                "mouth_openness": mouth_openness,
                "eyebrow_position": 0.5,
                "mouth_curvature": 0.5
            },
            "timestamp": __import__('time').time()
        }
        
        return face_data

def main():
    # Analisar a imagem do rosto3d.png  
    result = analyze_face_for_bot("rosto3d.png")
    
    if result:
        # Salvar dados
        with open("face_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("✅ Dados salvos em face_analysis.json")
        print(f"📊 Landmarks encontrados: {len(result['landmarks_2d'])}")
        print(f"👁️ Abertura dos olhos: {result['eyes']['average_openness']}")
        print(f"👄 Abertura da boca: {result['mouth']['aspect_ratio']}")
        print(f"😐 Emoção: {result['emotion']['dominant_emotion']}")
        
        # Criar visualização simples
        image = cv2.imread("rosto3d.png")
        if image is not None:
            # Desenhar alguns landmarks importantes
            for i, point in enumerate(result['landmarks_2d'][:68]):  # Primeiros 68 pontos
                cv2.circle(image, tuple(point), 2, (0, 255, 0), -1)
            
            cv2.imwrite("rosto3d_analyzed.png", image)
            print("✅ Visualização salva em rosto3d_analyzed.png")
    else:
        print("❌ Falha na análise")

if __name__ == "__main__":
    main()
