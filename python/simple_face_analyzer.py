#!/usr/bin/env python3
"""
Simple Face Analyzer - Extrai características faciais para animação 3D
Usando MediaPipe para detecção facial
"""

import cv2
import numpy as np
import json
import mediapipe as mp
import os
import argparse
from typing import Dict, Optional

class SimpleFaceAnalyzer:
    def __init__(self):
        """Inicializa o analisador facial"""
        # MediaPipe components
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Face landmark indices
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.MOUTH_INDICES = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318]
        
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carrega a imagem"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return None
            
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None
            
        return image
        
    def analyze_face(self, image_path: str) -> Optional[Dict]:
        """Análise completa da face usando MediaPipe"""
        print(f"🔍 Analisando imagem: {image_path}")
        
        # Carregar imagem
        image = self.load_image(image_path)
        if image is None:
            return None
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]
        
        # Análise com MediaPipe - configurações mais permissivas
        with self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3) as face_mesh:
            
            results = face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                print("❌ Nenhuma face detectada na imagem")
                return None
                
            print("✅ Face detectada com sucesso!")
            
            # Extrair landmarks da primeira face
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = []
            
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks.append([x, y])
                
            # Analisar características
            eye_analysis = self.analyze_eyes(landmarks)
            mouth_analysis = self.analyze_mouth(landmarks)
            emotion_analysis = self.analyze_emotion(eye_analysis, mouth_analysis)
            
            # Resultado completo
            result = {
                "image_path": image_path,
                "face_bounds": {
                    "x": 0,
                    "y": 0,
                    "width": width,
                    "height": height
                },
                "landmarks": landmarks,
                "eyes": eye_analysis,
                "mouth": mouth_analysis,
                "emotion": emotion_analysis,
                "timestamp": __import__('time').time()
            }
            
            # Criar dados de animação
            animation_data = self.create_animation_data(result)
            result["animation"] = animation_data
            
            return result
            
    def analyze_eyes(self, landmarks) -> Dict:
        """Analisa características dos olhos"""
        left_eye_points = [landmarks[i] for i in self.LEFT_EYE_INDICES if i < len(landmarks)]
        right_eye_points = [landmarks[i] for i in self.RIGHT_EYE_INDICES if i < len(landmarks)]
        
        if not left_eye_points or not right_eye_points:
            return {
                "average_openness": 0.5,
                "is_blinking": False,
                "left_eye_center": [0, 0],
                "right_eye_center": [0, 0]
            }
        
        # Calcular centros dos olhos
        left_eye_center = np.mean(left_eye_points, axis=0)
        right_eye_center = np.mean(right_eye_points, axis=0)
        
        # Calcular abertura dos olhos (estimativa simples)
        left_eye_height = max([p[1] for p in left_eye_points]) - min([p[1] for p in left_eye_points])
        right_eye_height = max([p[1] for p in right_eye_points]) - min([p[1] for p in right_eye_points])
        left_eye_width = max([p[0] for p in left_eye_points]) - min([p[0] for p in left_eye_points])
        right_eye_width = max([p[0] for p in right_eye_points]) - min([p[0] for p in right_eye_points])
        
        # Razão de abertura dos olhos
        left_ratio = left_eye_height / left_eye_width if left_eye_width > 0 else 0
        right_ratio = right_eye_height / right_eye_width if right_eye_width > 0 else 0
        average_openness = (left_ratio + right_ratio) / 2
        
        return {
            "average_openness": float(average_openness),
            "is_blinking": bool(average_openness < 0.15),
            "left_eye_center": left_eye_center.tolist(),
            "right_eye_center": right_eye_center.tolist(),
            "left_eye_ratio": float(left_ratio),
            "right_eye_ratio": float(right_ratio)
        }
        
    def analyze_mouth(self, landmarks) -> Dict:
        """Analisa características da boca"""
        mouth_points = [landmarks[i] for i in self.MOUTH_INDICES if i < len(landmarks)]
        
        if not mouth_points:
            return {
                "aspect_ratio": 0.0,
                "is_speaking": False,
                "center": [0, 0],
                "curvature": 0.0
            }
        
        # Calcular centro da boca
        mouth_center = np.mean(mouth_points, axis=0)
        
        # Calcular dimensões da boca
        mouth_height = max([p[1] for p in mouth_points]) - min([p[1] for p in mouth_points])
        mouth_width = max([p[0] for p in mouth_points]) - min([p[0] for p in mouth_points])
        
        # Razão de abertura da boca
        aspect_ratio = mouth_height / mouth_width if mouth_width > 0 else 0
        
        # Detectar fala
        is_speaking = aspect_ratio > 0.1
        
        # Curvatura da boca (sorriso/tristeza) - estimativa simples
        if len(mouth_points) >= 3:
            top_y = min([p[1] for p in mouth_points])
            left_corner = min(mouth_points, key=lambda p: p[0])
            right_corner = max(mouth_points, key=lambda p: p[0])
            corners_avg_y = (left_corner[1] + right_corner[1]) / 2
            curvature = corners_avg_y - top_y  # Positivo = sorriso, negativo = tristeza
        else:
            curvature = 0.0
        
        return {
            "aspect_ratio": float(aspect_ratio),
            "is_speaking": bool(is_speaking),
            "center": mouth_center.tolist(),
            "curvature": float(curvature),
            "width": float(mouth_width),
            "height": float(mouth_height)
        }
        
    def analyze_emotion(self, eyes: Dict, mouth: Dict) -> Dict:
        """Analisa emoção baseada nas características faciais"""
        
        # Scores de emoções baseados em características simples
        emotion_scores = {
            "neutral": 0.4,
            "happy": 0.0,
            "sad": 0.0,
            "surprised": 0.0,
            "angry": 0.0
        }
        
        # Felicidade: sorriso (curvatura positiva da boca)
        if mouth["curvature"] > 5:
            emotion_scores["happy"] += 0.4
            
        # Tristeza: boca curvada para baixo
        if mouth["curvature"] < -3:
            emotion_scores["sad"] += 0.3
            
        # Surpresa: boca muito aberta
        if mouth["aspect_ratio"] > 0.15:
            emotion_scores["surprised"] += 0.3
            
        # Olhos fechados podem indicar felicidade (sorriso)
        if eyes["average_openness"] < 0.1:
            emotion_scores["happy"] += 0.2
            
        # Normalizar scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
        # Encontrar emoção dominante
        dominant = max(emotion_scores.items(), key=lambda x: x[1])
        
        return {
            "scores": emotion_scores,
            "dominant_emotion": dominant[0],
            "confidence": float(dominant[1])
        }
        
    def create_animation_data(self, analysis_result: Dict) -> Dict:
        """Cria dados de animação para o JavaScript"""
        eyes = analysis_result["eyes"]
        mouth = analysis_result["mouth"]
        emotion = analysis_result["emotion"]
        
        # Normalizar valores para animação (0-1)
        eye_openness = min(1.0, max(0.0, eyes["average_openness"] * 3))
        mouth_openness = min(1.0, max(0.0, mouth["aspect_ratio"] * 6))
        
        # Mapeamento de emoções para expressões 3D
        emotion_mapping = {
            "happy": {"smile": 0.8, "eyeSquint": 0.3},
            "sad": {"frown": 0.7, "eyeSquint": 0.1},
            "angry": {"frown": 0.6, "eyebrowDown": 0.8},
            "surprised": {"mouthOpen": 0.8, "eyebrowUp": 0.7, "eyeWide": 0.6},
            "neutral": {}
        }
        
        dominant_emotion = emotion["dominant_emotion"]
        confidence = emotion["confidence"]
        
        # Aplicar expressão baseada na emoção dominante
        expression_weights = emotion_mapping.get(dominant_emotion, {})
        
        return {
            "facial_animation": {
                "eye_openness": eye_openness,
                "mouth_openness": mouth_openness,
                "eye_position": {
                    "x": 0.0,
                    "y": 0.0
                },
                "expression_weights": {k: v * confidence for k, v in expression_weights.items()},
                "emotion": {
                    "current": dominant_emotion,
                    "intensity": confidence,
                    "all_scores": emotion["scores"]
                }
            }
        }
        
    def save_analysis(self, analysis_result: Dict, output_path: str = "face_analysis.json"):
        """Salva resultado da análise em arquivo JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"✅ Análise salva em: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            
    def create_debug_image(self, image_path: str, analysis_result: Dict, output_path: str = "face_debug.jpg"):
        """Cria imagem com landmarks e análises marcadas"""
        image = cv2.imread(image_path)
        if image is None:
            return
            
        landmarks = analysis_result["landmarks"]
        
        # Desenhar landmarks
        for i, (x, y) in enumerate(landmarks):
            cv2.circle(image, (int(x), int(y)), 1, (0, 255, 0), -1)
            
        # Destacar olhos
        for idx in self.LEFT_EYE_INDICES:
            if idx < len(landmarks):
                x, y = landmarks[idx]
                cv2.circle(image, (int(x), int(y)), 2, (255, 0, 0), -1)
                
        for idx in self.RIGHT_EYE_INDICES:
            if idx < len(landmarks):
                x, y = landmarks[idx]
                cv2.circle(image, (int(x), int(y)), 2, (255, 0, 0), -1)
                
        # Destacar boca
        for idx in self.MOUTH_INDICES:
            if idx < len(landmarks):
                x, y = landmarks[idx]
                cv2.circle(image, (int(x), int(y)), 2, (0, 0, 255), -1)
        
        # Adicionar informações
        eyes = analysis_result["eyes"]
        mouth = analysis_result["mouth"]
        emotion = analysis_result["emotion"]["dominant_emotion"]
        confidence = analysis_result["emotion"]["confidence"]
        
        cv2.putText(image, f"Emotion: {emotion} ({confidence:.2f})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, f"Eye Openness: {eyes['average_openness']:.2f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, f"Mouth Openness: {mouth['aspect_ratio']:.2f}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, f"Speaking: {'Yes' if mouth['is_speaking'] else 'No'}", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imwrite(output_path, image)
        print(f"✅ Imagem de debug salva em: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Analisador Facial Simples para Animação 3D")
    parser.add_argument("--image", "-i", default="face3d.png", help="Caminho para a imagem")
    parser.add_argument("--output", "-o", default="face_analysis.json", help="Arquivo de saída JSON")
    parser.add_argument("--debug", "-d", action="store_true", help="Criar imagem de debug")
    
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = SimpleFaceAnalyzer()
    
    # Analisar face
    result = analyzer.analyze_face(args.image)
    
    if result:
        # Salvar análise
        analyzer.save_analysis(result, args.output)
        
        # Criar imagem de debug se solicitado
        if args.debug:
            analyzer.create_debug_image(args.image, result, "face_debug.jpg")
        
        # Mostrar resumo
        print("\n📊 RESUMO DA ANÁLISE:")
        print(f"Emoção dominante: {result['emotion']['dominant_emotion']} ({result['emotion']['confidence']:.2f})")
        print(f"Abertura dos olhos: {result['eyes']['average_openness']:.2f}")
        print(f"Abertura da boca: {result['mouth']['aspect_ratio']:.2f}")
        print(f"Falando: {'Sim' if result['mouth']['is_speaking'] else 'Não'}")
        print(f"Piscando: {'Sim' if result['eyes']['is_blinking'] else 'Não'}")
        
        # Dados de animação
        print(f"\n🎭 DADOS DE ANIMAÇÃO:")
        anim = result['animation']['facial_animation']
        print(f"Abertura dos olhos (normalizada): {anim['eye_openness']:.2f}")
        print(f"Abertura da boca (normalizada): {anim['mouth_openness']:.2f}")
        print(f"Pesos de expressão: {anim['expression_weights']}")
        
    else:
        print("❌ Falha na análise da face")

if __name__ == "__main__":
    main()
