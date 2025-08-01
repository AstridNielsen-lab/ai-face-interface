import cv2
import numpy as np
def extract_traces(image_path, output_path):
    # Carregar imagem
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Não foi possível carregar a imagem: {image_path}")
    
    # Aplicar detecção de bordas
    edges = cv2.Canny(image, 100, 200)
    
    # Salvar resultado
    cv2.imwrite(output_path, edges)
    
    print(f"Imagem processada e salva em: {output_path}")

if __name__ == "__main__":
    extract_traces('rosto3d.png', 'rosto3d_traces.png')
