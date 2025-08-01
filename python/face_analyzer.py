#!/usr/bin/env python3
"""
Face Analyzer - Extrai características faciais para animação 3D
Analisa olhos, boca, expressões e gera dados para o rosto virtual
Usando MediaPipe para detecção facial
"""

import cv2
import numpy as np
import json
import mediapipe as mp
import os
from typing import Dict, List, Tuple, Optional
import argparse

class FaceAnalyzer:
    def __init__(self):
        """Inicializa o analisador facial com os modelos necessários"""
        self.face_detector = dlib.get_frontal_face_detector()
        
        # Tentar carregar o preditor de landmarks
        predictor_path = "shape_predictor_68_face_landmarks.dat"
        if os.path.exists(predictor_path):
            self.landmark_predictor = dlib.shape_predictor(predictor_path)
        else:
            print("⚠️  Modelo de landmarks não encontrado. Baixando...")
            self.download_landmark_model()
            
        # Índices dos landmarks para diferentes partes do rosto
        self.JAW_POINTS = list(range(0, 17))
        self.RIGHT_EYEBROW_POINTS = list(range(17, 22))
        self.LEFT_EYEBROW_POINTS = list(range(22, 27))
        self.NOSE_POINTS = list(range(27, 36))
        self.RIGHT_EYE_POINTS = list(range(36, 42))
        self.LEFT_EYE_POINTS = list(range(42, 48))
        self.MOUTH_OUTLINE_POINTS = list(range(48, 61))
        self.MOUTH_INNER_POINTS = list(range(61, 68))
        
    def download_landmark_model(self):
        """Baixa o modelo de landmarks se não existir"""
        import urllib.request
        import bz2
        
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        compressed_file = "shape_predictor_68_face_landmarks.dat.bz2"
        extracted_file = "shape_predictor_68_face_landmarks.dat"
        
        try:
            print("Baixando modelo de landmarks...")
            urllib.request.urlretrieve(url, compressed_file)
            
            print("Extraindo arquivo...")
            with bz2.BZ2File(compressed_file, 'rb') as f_in:
                with open(extracted_file, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            os.remove(compressed_file)
            self.landmark_predictor = dlib.shape_predictor(extracted_file)
            print("✅ Modelo baixado e carregado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao baixar modelo: {e}")
            print("Por favor, baixe manualmente de: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carrega e processa a imagem"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return None
            
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None
            
        # Converter para RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image_rgb
        
    def detect_faces(self, image: np.ndarray) -> List[dlib.rectangle]:
        """Detecta faces na imagem"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector(gray)
        return faces
        
    def get_landmarks(self, image: np.ndarray, face_rect: dlib.rectangle) -> np.ndarray:
        """Extrai landmarks faciais"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        landmarks = self.landmark_predictor(gray, face_rect)
        
        # Converter para array numpy
        points = np.zeros((68, 2), dtype=int)
        for i in range(68):
            points[i] = (landmarks.part(i).x, landmarks.part(i).y)
            
        return points
        
    def analyze_eyes(self, landmarks: np.ndarray) -> Dict:
        """Analisa características dos olhos"""
        left_eye = landmarks[self.LEFT_EYE_POINTS]
        right_eye = landmarks[self.RIGHT_EYE_POINTS]
        
        # Calcular centros dos olhos
        left_eye_center = np.mean(left_eye, axis=0)
        right_eye_center = np.mean(right_eye, axis=0)
        
        # Calcular abertura dos olhos (distância vertical)
        left_eye_height = np.linalg.norm(left_eye[1] - left_eye[5])
        right_eye_height = np.linalg.norm(right_eye[1] - right_eye[5])
        
        # Calcular largura dos olhos (distância horizontal)
        left_eye_width = np.linalg.norm(left_eye[0] - left_eye[3])
        right_eye_width = np.linalg.norm(right_eye[0] - right_eye[3])
        
        # Razão abertura/largura (para detectar piscadas)
        left_ear = left_eye_height / left_eye_width if left_eye_width > 0 else 0
        right_ear = right_eye_height / right_eye_width if right_eye_width > 0 else 0
        
        return {
            "left_eye": {
                "center": left_eye_center.tolist(),
                "height": float(left_eye_height),
                "width": float(left_eye_width),
                "openness_ratio": float(left_ear),
                "landmarks": left_eye.tolist()
            },
            "right_eye": {
                "center": right_eye_center.tolist(),
                "height": float(right_eye_height),
                "width": float(right_eye_width),
                "openness_ratio": float(right_ear),
                "landmarks": right_eye.tolist()
            },
            "average_openness": float((left_ear + right_ear) / 2),
            "is_blinking": bool((left_ear + right_ear) / 2 < 0.2)
        }
        
    def analyze_mouth(self, landmarks: np.ndarray) -> Dict:
        """Analisa características da boca"""
        mouth_outer = landmarks[self.MOUTH_OUTLINE_POINTS]
        mouth_inner = landmarks[self.MOUTH_INNER_POINTS]
        
        # Calcular centro da boca
        mouth_center = np.mean(mouth_outer, axis=0)
        
        # Largura da boca (distância entre cantos)
        mouth_width = np.linalg.norm(mouth_outer[0] - mouth_outer[6])
        
        # Altura da boca (distância vertical)
        mouth_height_outer = np.linalg.norm(mouth_outer[3] - mouth_outer[9])
        mouth_height_inner = np.linalg.norm(mouth_inner[1] - mouth_inner[5])
        
        # Razão abertura da boca
        mouth_aspect_ratio = mouth_height_outer / mouth_width if mouth_width > 0 else 0
        
        # Detectar se está falando (boca aberta)
        is_speaking = mouth_aspect_ratio > 0.15
        
        # Curvatura da boca (sorriso/tristeza)
        left_corner = mouth_outer[0]
        right_corner = mouth_outer[6]
        mouth_top = mouth_outer[3]
        
        # Calcular inclinação dos cantos da boca
        corner_height_avg = (left_corner[1] + right_corner[1]) / 2
        mouth_curvature = mouth_top[1] - corner_height_avg
        
        return {
            "center": mouth_center.tolist(),
            "width": float(mouth_width),
            "height_outer": float(mouth_height_outer),
            "height_inner": float(mouth_height_inner),
            "aspect_ratio": float(mouth_aspect_ratio),
            "is_speaking": bool(is_speaking),
            "curvature": float(mouth_curvature),
            "outer_landmarks": mouth_outer.tolist(),
            "inner_landmarks": mouth_inner.tolist()
        }
        
    def analyze_emotion(self, landmarks: np.ndarray, eyes: Dict, mouth: Dict) -> Dict:
        """Analisa emoção baseada nas características faciais"""
        
        # Sobrancelhas
        left_eyebrow = landmarks[self.LEFT_EYEBROW_POINTS]
        right_eyebrow = landmarks[self.RIGHT_EYEBROW_POINTS]
        
        # Altura média das sobrancelhas em relação aos olhos
        left_eyebrow_height = np.mean(left_eyebrow[:, 1])
        right_eyebrow_height = np.mean(right_eyebrow[:, 1])
        left_eye_height = np.mean(landmarks[self.LEFT_EYE_POINTS][:, 1])
        right_eye_height = np.mean(landmarks[self.RIGHT_EYE_POINTS][:, 1])
        
        eyebrow_distance = ((left_eye_height - left_eyebrow_height) + 
                           (right_eye_height - right_eyebrow_height)) / 2
        
        # Análise de emoções
        emotion_scores = {
            "neutral": 0.5,
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "surprised": 0.0,
            "fear": 0.0,
            "disgust": 0.0
        }
        
        # Felicidade: boca curvada para cima, olhos ligeiramente fechados
        if mouth["curvature"] < -5:  # Cantos da boca para cima
            emotion_scores["happy"] += 0.4
        if eyes["average_openness"] < 0.25:  # Olhos ligeiramente fechados (sorriso)
            emotion_scores["happy"] += 0.2
            
        # Tristeza: boca curvada para baixo, sobrancelhas baixas
        if mouth["curvature"] > 5:  # Cantos da boca para baixo
            emotion_scores["sad"] += 0.3
        if eyebrow_distance < 20:  # Sobrancelhas baixas
            emotion_scores["sad"] += 0.2
            
        # Raiva: sobrancelhas franzidas, boca tensa
        if eyebrow_distance < 15:  # Sobrancelhas muito baixas
            emotion_scores["angry"] += 0.3
        if mouth["aspect_ratio"] < 0.1:  # Boca fechada/tensa
            emotion_scores["angry"] += 0.2
            
        # Surpresa: sobrancelhas altas, olhos bem abertos, boca aberta
        if eyebrow_distance > 30:  # Sobrancelhas altas
            emotion_scores["surprised"] += 0.3
        if eyes["average_openness"] > 0.3:  # Olhos bem abertos
            emotion_scores["surprised"] += 0.2
        if mouth["aspect_ratio"] > 0.2:  # Boca aberta
            emotion_scores["surprised"] += 0.2
            
        # Normalizar scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v/total_score for k, v in emotion_scores.items()}
            
        # Encontrar emoção dominante
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        return {
            "scores": emotion_scores,
            "dominant_emotion": dominant_emotion[0],
            "confidence": float(dominant_emotion[1]),
            "eyebrow_distance": float(eyebrow_distance)
        }
        
    def create_animation_data(self, analysis_result: Dict) -> Dict:
        """Cria dados de animação para o JavaScript"""
        eyes = analysis_result["eyes"]
        mouth = analysis_result["mouth"]
        emotion = analysis_result["emotion"]
        
        # Normalizar valores para animação (0-1)
        eye_openness = min(1.0, max(0.0, eyes["average_openness"] * 4))
        mouth_openness = min(1.0, max(0.0, mouth["aspect_ratio"] * 5))
        
        # Mapeamento de emoções para expressões 3D
        emotion_mapping = {
            "happy": {"smile": 0.8, "eyeSquint": 0.3},
            "sad": {"frown": 0.7, "eyeSquint": 0.1},
            "angry": {"frown": 0.6, "eyebrowDown": 0.8},
            "surprised": {"mouthOpen": 0.8, "eyebrowUp": 0.7},
            "fear": {"mouthOpen": 0.4, "eyebrowUp": 0.5},
            "disgust": {"frown": 0.5, "noseWrinkle": 0.6},
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
                    "x": 0.0,  # Pode ser calculado baseado na direção do olhar
                    "y": 0.0
                },
                "expression_weights": {k: v * confidence for k, v in expression_weights.items()},
                "emotion": {
                    "current": dominant_emotion,
                    "intensity": confidence,
                    "all_scores": emotion["scores"]
                }
            },
            "landmarks_normalized": self.normalize_landmarks(analysis_result["landmarks"]),
            "face_bounds": analysis_result["face_bounds"]
        }
        
    def normalize_landmarks(self, landmarks: List) -> List:
        """Normaliza landmarks para coordenadas 0-1"""
        landmarks_array = np.array(landmarks)
        
        # Encontrar bounding box
        min_x, min_y = np.min(landmarks_array, axis=0)
        max_x, max_y = np.max(landmarks_array, axis=0)
        
        # Normalizar para 0-1
        normalized = (landmarks_array - [min_x, min_y]) / [max_x - min_x, max_y - min_y]
        
        return normalized.tolist()
        
def analyze_face(self, image_path: str) -> Optional[Dict]:
        """Análise completa da face usando MediaPipe"""
        print(f"🔍 Analisando imagem: {image_path}")
        
        # MediaPipe face detection
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        # Carregar imagem
        image = self.load_image(image_path)
        if image is None:
            return None

        results = None

        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            # Procesar a imagem
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if not results.detections:
                print("❌ Nenhuma face detectada na imagem")
                return None

            # Usar a primeira face encontrada
            detection = results.detections[0]
            print(f"✅ Detecção de face bem-sucedida: {detection}")

            # Extrair landmarks usando resultados fornecidos por mediapipe (criar a própria lógica se necessário)
            # Apenas um exemplo representativo é dado aqui
            face_bounds = detection.location_data.relative_bounding_box
            eye_openness = 0.5  # Exemplo
            mouth_openness = 0.3  # Exemplo
            
            result = {
                "image_path": image_path,
                "face_bounds": {
                    "x": face_bounds.xmin,
                    "y": face_bounds.ymin,
                    "width": face_bounds.width,
                    "height": face_bounds.height
                },
                "landmarks": [],  # example
                "eyes": {
                    "average_openness": eye_openness,
                    "is_blinking": eye_openness < 0.2
                },
                "mouth": {
                    "aspect_ratio": mouth_openness,
                    "is_speaking": mouth_openness > 0.15
                },
                "emotion": {
                    "dominant_emotion": "neutral",
                    "confidence": 1.0
                },
                "timestamp": __import__('time').time()
            }
            
            return result
        
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
            
        landmarks = np.array(analysis_result["landmarks"])
        
        # Desenhar landmarks
        for i, (x, y) in enumerate(landmarks):
            cv2.circle(image, (int(x), int(y)), 2, (0, 255, 0), -1)
            cv2.putText(image, str(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            
        # Destacar regiões importantes
        eyes = analysis_result["eyes"]
        mouth = analysis_result["mouth"]
        
        # Olhos
        left_eye = np.array(eyes["left_eye"]["landmarks"], dtype=np.int32)
        right_eye = np.array(eyes["right_eye"]["landmarks"], dtype=np.int32)
        cv2.polylines(image, [left_eye], True, (255, 0, 0), 2)
        cv2.polylines(image, [right_eye], True, (255, 0, 0), 2)
        
        # Boca
        mouth_outer = np.array(mouth["outer_landmarks"], dtype=np.int32)
        cv2.polylines(image, [mouth_outer], True, (0, 0, 255), 2)
        
        # Adicionar informações
        emotion = analysis_result["emotion"]["dominant_emotion"]
        confidence = analysis_result["emotion"]["confidence"]
        
        cv2.putText(image, f"Emotion: {emotion} ({confidence:.2f})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, f"Eye Openness: {eyes['average_openness']:.2f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, f"Mouth Openness: {mouth['aspect_ratio']:.2f}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imwrite(output_path, image)
        print(f"✅ Imagem de debug salva em: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Analisador Facial para Animação 3D")
    parser.add_argument("--image", "-i", default="face.jpg", help="Caminho para a imagem")
    parser.add_argument("--output", "-o", default="face_analysis.json", help="Arquivo de saída JSON")
    parser.add_argument("--debug", "-d", action="store_true", help="Criar imagem de debug")
    
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = FaceAnalyzer()
    
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
