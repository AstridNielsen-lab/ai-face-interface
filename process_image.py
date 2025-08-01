import os
from python.face_analyzer import FaceAnalyzer
from python.extract_traces import extract_traces

IMAGE_PATH = 'assets/rosto3d.png'
ANALYZED_IMAGE_PATH = 'assets/rosto3d_analyzed.png'
TRACED_IMAGE_PATH = 'assets/rosto3d_traces.png'

# Instancia o FaceAnalyzer
face_analyzer = FaceAnalyzer()

# Análise facial
result = face_analyzer.analyze_face(IMAGE_PATH)
if result:
    face_analyzer.save_analysis(result)
    face_analyzer.create_debug_image(IMAGE_PATH, result, ANALYZED_IMAGE_PATH)

# Gerar máscara de traços
extract_traces(IMAGE_PATH, TRACED_IMAGE_PATH)

print("Processamento completo: Imagem analisada e traços extraídos.")
