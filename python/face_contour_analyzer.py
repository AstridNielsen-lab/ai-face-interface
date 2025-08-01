#!/usr/bin/env python3
"""
Face Contour Analyzer - Análise facial avançada com geração de máscara de contornos
Usa MediaPipe para detecção facial e OpenCV para processamento de imagem
Gera máscaras de contorno e análise de características faciais
"""

import cv2
import numpy as np
import json
import mediapipe as mp
import os
from typing import Dict, List, Tuple, Optional
import argparse
import time

class FaceContourAnalyzer:
    def __init__(self):
        """Inicializa o analisador com MediaPipe e OpenCV"""
        # Inicializar MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configurações de detecção
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("✅ FaceContourAnalyzer inicializado com sucesso!")
        
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carrega e valida a imagem"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return None
            
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None
            
        print(f"✅ Imagem carregada: {image_path} - Dimensões: {image.shape}")
        return image
        
    def detect_face_landmarks(self, image: np.ndarray) -> Optional[Dict]:
        """Detecta landmarks faciais usando MediaPipe"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detectar face mesh
        mesh_results = self.face_mesh.process(rgb_image)
        
        if not mesh_results.multi_face_landmarks:
            print("❌ Nenhuma face detectada na imagem")
            return None
            
        # Pegar a primeira face detectada
        face_landmarks = mesh_results.multi_face_landmarks[0]
        
        # Converter landmarks para coordenadas de pixel
        h, w = image.shape[:2]
        landmarks_px = []
        
        for landmark in face_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks_px.append([x, y])
            
        print(f"✅ Detectados {len(landmarks_px)} landmarks faciais")
        
        return {
            "landmarks": landmarks_px,
            "mesh_results": mesh_results,
            "image_dimensions": (w, h)
        }
        
    def generate_contour_mask(self, image: np.ndarray, landmarks: List[List[int]], method: str = "all") -> np.ndarray:
        """Gera máscara de contorno baseada nos landmarks"""
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        landmarks_array = np.array(landmarks, dtype=np.int32)
        
        if method == "convex_hull":
            # Usar convex hull para contorno externo
            hull = cv2.convexHull(landmarks_array)
            cv2.fillPoly(mask, [hull], 255)
            
        elif method == "face_outline":
            # Usar landmarks específicos para contorno facial
            face_outline_indices = [
                # Contorno da face (jawline)
                10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
            ]
            
            if len(landmarks) > max(face_outline_indices):
                face_points = [landmarks[i] for i in face_outline_indices]
                face_points = np.array(face_points, dtype=np.int32)
                cv2.fillPoly(mask, [face_points], 255)
            else:
                # Fallback para convex hull
                hull = cv2.convexHull(landmarks_array)
                cv2.fillPoly(mask, [hull], 255)
                
        else:  # method == "all"
            # Usar todos os landmarks
            hull = cv2.convexHull(landmarks_array)
            cv2.fillPoly(mask, [hull], 255)
            
        return mask
        
    def extract_facial_contours(self, image: np.ndarray, landmarks: List[List[int]]) -> Dict:
        """Extrai contornos de diferentes partes do rosto"""
        contours = {}
        
        # Definir índices dos landmarks para diferentes partes (MediaPipe Face Mesh)
        regions = {
            "left_eye": [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            "right_eye": [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            "mouth": [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95],
            "nose": [1, 2, 5, 4, 6, 168, 8, 9, 10, 151, 195, 197, 196, 3, 51, 48, 115, 131, 134, 102, 49, 220],
            "left_eyebrow": [46, 53, 52, 51, 48, 115, 131, 134, 102, 49, 220, 305, 293, 334, 296, 336],
            "right_eyebrow": [285, 295, 282, 283, 276, 353, 383, 300, 368, 369, 299, 333, 298, 301]
        }
        
        for region_name, indices in regions.items():
            try:
                if len(landmarks) > max(indices):
                    region_points = np.array([landmarks[i] for i in indices], dtype=np.int32)
                    contours[region_name] = region_points.tolist()
                else:
                    contours[region_name] = []
            except:
                contours[region_name] = []
                
        return contours
        
    def analyze_facial_features(self, landmarks: List[List[int]]) -> Dict:
        """Analisa características faciais baseadas nos landmarks"""
        if len(landmarks) < 468:  # MediaPipe Face Mesh tem 468 landmarks
            return {"error": "Landmarks insuficientes para análise"}
            
        features = {}
        
        try:
            # Análise dos olhos
            left_eye_landmarks = [33, 160, 158, 133, 153, 144]
            right_eye_landmarks = [362, 385, 387, 263, 373, 380]
            
            if all(i < len(landmarks) for i in left_eye_landmarks + right_eye_landmarks):
                left_eye_points = np.array([landmarks[i] for i in left_eye_landmarks])
                right_eye_points = np.array([landmarks[i] for i in right_eye_landmarks])
                
                # Calcular abertura dos olhos
                left_eye_height = np.linalg.norm(left_eye_points[1] - left_eye_points[5])
                left_eye_width = np.linalg.norm(left_eye_points[0] - left_eye_points[3])
                
                right_eye_height = np.linalg.norm(right_eye_points[1] - right_eye_points[5])
                right_eye_width = np.linalg.norm(right_eye_points[0] - right_eye_points[3])
                
                left_ear = left_eye_height / left_eye_width if left_eye_width > 0 else 0
                right_ear = right_eye_height / right_eye_width if right_eye_width > 0 else 0
                
                features["eyes"] = {
                    "left_openness": float(left_ear),
                    "right_openness": float(right_ear),
                    "average_openness": float((left_ear + right_ear) / 2),
                    "is_blinking": bool((left_ear + right_ear) / 2 < 0.2)
                }
            
            # Análise da boca
            mouth_landmarks = [61, 291, 39, 181, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
            
            if all(i < len(landmarks) for i in mouth_landmarks):
                mouth_points = np.array([landmarks[i] for i in mouth_landmarks])
                
                # Largura e altura da boca
                mouth_width = np.linalg.norm(mouth_points[0] - mouth_points[6])
                mouth_height = np.linalg.norm(mouth_points[3] - mouth_points[9])
                
                mouth_aspect_ratio = mouth_height / mouth_width if mouth_width > 0 else 0
                
                features["mouth"] = {
                    "width": float(mouth_width),
                    "height": float(mouth_height),
                    "aspect_ratio": float(mouth_aspect_ratio),
                    "is_open": bool(mouth_aspect_ratio > 0.1)
                }
                
        except Exception as e:
            features["error"] = f"Erro na análise: {str(e)}"
            
        return features
        
    def create_artistic_mask(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Cria uma máscara artística com efeitos visuais"""
        h, w = image.shape[:2]
        artistic_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Aplicar diferentes efeitos
        # 1. Contorno Canny
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        
        # Aplicar máscara aos contornos
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # 2. Criar máscara colorida
        artistic_mask[:, :, 0] = masked_edges  # Canal azul
        artistic_mask[:, :, 1] = mask  # Canal verde
        artistic_mask[:, :, 2] = masked_edges  # Canal vermelho
        
        # 3. Adicionar brilho
        glow = cv2.GaussianBlur(mask, (21, 21), 0)
        artistic_mask[:, :, 1] = cv2.add(artistic_mask[:, :, 1], glow // 2)
        
        return artistic_mask
        
    def process_image(self, image_path: str, output_dir: str = "output") -> Dict:
        """Processa a imagem completa: detecção, análise e geração de máscaras"""
        print(f"🎯 Iniciando processamento de: {image_path}")
        
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Carregar imagem
        image = self.load_image(image_path)
        if image is None:
            return {"error": "Falha ao carregar imagem"}
            
        # Detectar landmarks
        face_data = self.detect_face_landmarks(image)
        if face_data is None:
            return {"error": "Nenhuma face detectada"}
            
        landmarks = face_data["landmarks"]
        
        # Analisar características faciais
        features = self.analyze_facial_features(landmarks)
        
        # Extrair contornos por região
        contours = self.extract_facial_contours(image, landmarks)
        
        # Gerar diferentes tipos de máscara
        masks = {}
        
        # Máscara convex hull
        mask_hull = self.generate_contour_mask(image, landmarks, "convex_hull")
        masks["convex_hull"] = mask_hull
        
        # Máscara de contorno facial
        mask_outline = self.generate_contour_mask(image, landmarks, "face_outline")
        masks["face_outline"] = mask_outline
        
        # Máscara artística
        artistic_mask = self.create_artistic_mask(image, mask_hull)
        masks["artistic"] = artistic_mask
        
        # Salvar resultados
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Salvar máscaras
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_mask_hull.png"), mask_hull)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_mask_outline.png"), mask_outline)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_mask_artistic.png"), artistic_mask)
        
        # Criar imagem com landmarks
        debug_image = image.copy()
        for i, (x, y) in enumerate(landmarks):
            cv2.circle(debug_image, (x, y), 1, (0, 255, 0), -1)
            
        # Desenhar contornos das regiões
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        for i, (region, points) in enumerate(contours.items()):
            if points:
                points_array = np.array(points, dtype=np.int32)
                cv2.polylines(debug_image, [points_array], True, colors[i % len(colors)], 2)
                
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_debug.png"), debug_image)
        
        # Compilar resultado
        result = {
            "image_path": image_path,
            "output_directory": output_dir,
            "timestamp": time.time(),
            "face_detected": True,
            "landmarks_count": len(landmarks),
            "features": features,
            "contours": contours,
            "files_generated": [
                f"{base_name}_mask_hull.png",
                f"{base_name}_mask_outline.png",
                f"{base_name}_mask_artistic.png",
                f"{base_name}_debug.png"
            ]
        }
        
        # Salvar análise em JSON
        json_path = os.path.join(output_dir, f"{base_name}_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Processamento concluído! Arquivos salvos em: {output_dir}")
        return result

def main():
    parser = argparse.ArgumentParser(description="Analisador Facial com Geração de Contornos")
    parser.add_argument("--image", "-i", default="assets/rosto3d.png", help="Caminho para a imagem")
    parser.add_argument("--output", "-o", default="output", help="Diretório de saída")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = FaceContourAnalyzer()
    
    # Processar imagem
    result = analyzer.process_image(args.image, args.output)
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
        return
        
    # Mostrar resumo
    print("\n📊 RESUMO DO PROCESSAMENTO:")
    print(f"• Landmarks detectados: {result['landmarks_count']}")
    print(f"• Características analisadas: {len(result['features'])}")
    print(f"• Regiões de contorno: {len(result['contours'])}")
    print(f"• Arquivos gerados: {len(result['files_generated'])}")
    
    if args.verbose:
        print("\n🔍 DETALHES DAS CARACTERÍSTICAS:")
        features = result.get('features', {})
        
        if 'eyes' in features:
            eyes = features['eyes']
            print(f"  👁️ Olhos:")
            print(f"    - Abertura média: {eyes.get('average_openness', 0):.3f}")
            print(f"    - Piscando: {'Sim' if eyes.get('is_blinking', False) else 'Não'}")
        
        if 'mouth' in features:
            mouth = features['mouth']
            print(f"  👄 Boca:")
            print(f"    - Proporção: {mouth.get('aspect_ratio', 0):.3f}")
            print(f"    - Aberta: {'Sim' if mouth.get('is_open', False) else 'Não'}")
    
    print(f"\n📁 Arquivos salvos em: {result['output_directory']}")
    for file in result['files_generated']:
        print(f"  • {file}")

if __name__ == "__main__":
    main()
