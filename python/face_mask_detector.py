from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import os

class InteractiveFaceMask:
    def __init__(self, mask_image_path='rosto3dmask.jpg'):
        # Carregar cascatas do OpenCV
        self.face_cascade = cv.CascadeClassifier()
        self.eyes_cascade = cv.CascadeClassifier()
        self.smile_cascade = cv.CascadeClassifier()
        
        # Tentar carregar cascatas do OpenCV
        face_cascade_path = cv.data.haarcascades + 'haarcascade_frontalface_alt.xml'
        eyes_cascade_path = cv.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'
        smile_cascade_path = cv.data.haarcascades + 'haarcascade_smile.xml'
        
        if not self.face_cascade.load(face_cascade_path):
            print('--(!)Erro ao carregar cascade de face')
            exit(0)
        if not self.eyes_cascade.load(eyes_cascade_path):
            print('--(!)Erro ao carregar cascade de olhos')
            exit(0)
        if not self.smile_cascade.load(smile_cascade_path):
            print('--(!)Erro ao carregar cascade de sorriso')
            exit(0)
            
        # Carregar imagem da máscara
        self.mask_image = None
        if os.path.exists(mask_image_path):
            self.mask_image = cv.imread(mask_image_path, cv.IMREAD_UNCHANGED)
            print(f"Máscara carregada: {mask_image_path}")
        else:
            print(f"Aviso: Imagem da máscara não encontrada: {mask_image_path}")
            
        # Configurações
        self.show_detection_info = True
        self.apply_mask = True
        self.mask_opacity = 0.7
        
    def resize_mask_to_face(self, mask, face_width, face_height):
        """Redimensiona a máscara para se ajustar ao rosto detectado"""
        if mask is None:
            return None
            
        # Redimensionar máscara para o tamanho do rosto
        resized_mask = cv.resize(mask, (face_width, face_height))
        return resized_mask
        
    def apply_mask_to_face(self, frame, mask, x, y, w, h):
        """Aplica a máscara sobre o rosto detectado"""
        if mask is None:
            return frame
            
        # Redimensionar máscara para o tamanho do rosto
        face_mask = self.resize_mask_to_face(mask, w, h)
        if face_mask is None:
            return frame
            
        # Região do rosto no frame
        roi = frame[y:y+h, x:x+w]
        
        # Se a máscara tem canal alpha (transparência)
        if face_mask.shape[2] == 4:
            # Separar canais BGR e Alpha
            mask_bgr = face_mask[:, :, :3]
            mask_alpha = face_mask[:, :, 3] / 255.0
            
            # Aplicar máscara com transparência
            for c in range(3):
                roi[:, :, c] = roi[:, :, c] * (1 - mask_alpha * self.mask_opacity) + \
                              mask_bgr[:, :, c] * (mask_alpha * self.mask_opacity)
        else:
            # Aplicar máscara sem canal alpha
            roi_blended = cv.addWeighted(roi, 1 - self.mask_opacity, face_mask, self.mask_opacity, 0)
            frame[y:y+h, x:x+w] = roi_blended
            
        return frame
        
    def detect_and_display(self, frame):
        """Detecta faces, olhos e sorrisos no frame"""
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_gray = cv.equalizeHist(frame_gray)
        
        # Criar cópia do frame original para mostrar lado a lado
        original_frame = frame.copy()
        masked_frame = frame.copy()
        
        # Detectar faces
        faces = self.face_cascade.detectMultiScale(frame_gray, 1.1, 3, 0, (30, 30))
        
        for (x, y, w, h) in faces:
            # Centro do rosto
            center = (x + w//2, y + h//2)
            
            # Aplicar máscara no frame da direita
            if self.apply_mask and self.mask_image is not None:
                masked_frame = self.apply_mask_to_face(masked_frame, self.mask_image, x, y, w, h)
            
            # Desenhar detecções no frame original (esquerda)
            if self.show_detection_info:
                original_frame = cv.ellipse(original_frame, center, (w//2, h//2), 0, 0, 360, (255, 0, 255), 2)
                
                # Adicionar texto com info do rosto
                cv.putText(original_frame, f'Face {w}x{h}', (x, y-10), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            # ROI para detectar características faciais
            faceROI = frame_gray[y:y+h, x:x+w]
            roi_color_original = original_frame[y:y+h, x:x+w]
            
            # Detectar sorrisos
            smiles = self.smile_cascade.detectMultiScale(faceROI, 1.8, 20)
            for (sx, sy, sw, sh) in smiles:
                if self.show_detection_info:
                    cv.rectangle(roi_color_original, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)
                    cv.putText(original_frame, 'SORRINDO', (x + sx, y + sy - 10), 
                              cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Detectar olhos
            eyes = self.eyes_cascade.detectMultiScale(faceROI)
            for (x2, y2, w2, h2) in eyes:
                eye_center = (x + x2 + w2//2, y + y2 + h2//2)
                radius = int(round((w2 + h2) * 0.25))
                
                if self.show_detection_info:
                    original_frame = cv.circle(original_frame, eye_center, radius, (255, 255, 0), 2)
        
        # Criar visualização lado a lado
        combined_frame = self.create_side_by_side_view(original_frame, masked_frame, len(faces))
        
        return combined_frame
        
    def draw_info_panel(self, frame, num_faces):
        """Desenha painel de informações na tela"""
        h, w = frame.shape[:2]
        
        # Fundo do painel
        cv.rectangle(frame, (10, 10), (300, 120), (0, 0, 0), -1)
        cv.rectangle(frame, (10, 10), (300, 120), (255, 255, 255), 2)
        
        # Informações
        info_text = [
            f"Faces detectadas: {num_faces}",
            f"Mascara: {'ON' if self.apply_mask else 'OFF'} (M)",
            f"Info: {'ON' if self.show_detection_info else 'OFF'} (I)",
            f"Opacidade: {int(self.mask_opacity * 100)}% (+/-)"
        ]
        
        for i, text in enumerate(info_text):
            cv.putText(frame, text, (20, 35 + i * 20), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def create_side_by_side_view(self, original_frame, masked_frame, num_faces):
        """Cria uma visualização lado a lado dos frames original e mascarado"""
        h, w = original_frame.shape[:2]
        combined_frame = np.zeros((h, w * 2, 3), dtype=np.uint8)

        # Colocar frames lado a lado
        combined_frame[:, :w] = original_frame
        combined_frame[:, w:] = masked_frame

        # Adicionar labels para cada lado
        cv.putText(combined_frame, 'ORIGINAL - DETECÇÃO', (10, h - 30), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv.putText(combined_frame, 'MÁSCARA APLICADA', (w + 10, h - 30), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        
        # Desenhar linha divisória
        cv.line(combined_frame, (w, 0), (w, h), (255, 255, 255), 2)

        # Desenhar informações
        self.draw_info_panel(combined_frame, num_faces)

        return combined_frame
    def run_camera(self, camera_device=0):
        """Executa detecção em tempo real com câmera"""
        cap = cv.VideoCapture(camera_device)
        if not cap.isOpened():
            print('--(!)Erro ao abrir captura de vídeo')
            return
            
        print("=== CONTROLES ===")
        print("ESC: Sair")
        print("M: Toggle máscara ON/OFF")
        print("I: Toggle informações de detecção")
        print("+: Aumentar opacidade da máscara")
        print("-: Diminuir opacidade da máscara")
        print("S: Salvar frame atual")
        print("================")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if frame is None:
                print('--(!) Frame não capturado -- Encerrando!')
                break
                
            # Processar frame
            frame = self.detect_and_display(frame)
            
            # Mostrar frame
            cv.imshow('Máscara Facial Interativa', frame)
            
            # Controles de teclado
            key = cv.waitKey(10) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == ord('m') or key == ord('M'):
                self.apply_mask = not self.apply_mask
                print(f"Máscara: {'ON' if self.apply_mask else 'OFF'}")
            elif key == ord('i') or key == ord('I'):
                self.show_detection_info = not self.show_detection_info
                print(f"Info detecção: {'ON' if self.show_detection_info else 'OFF'}")
            elif key == ord('+') or key == ord('='):
                self.mask_opacity = min(1.0, self.mask_opacity + 0.1)
                print(f"Opacidade: {int(self.mask_opacity * 100)}%")
            elif key == ord('-'):
                self.mask_opacity = max(0.1, self.mask_opacity - 0.1)
                print(f"Opacidade: {int(self.mask_opacity * 100)}%")
            elif key == ord('s') or key == ord('S'):
                filename = f"face_tracking_frame_{frame_count}.png"
                cv.imwrite(filename, frame)
                print(f"Frame salvo: {filename}")
                
            frame_count += 1
                
        cap.release()
        cv.destroyAllWindows()
        
    def process_static_image(self, image_path):
        """Processa uma imagem estática"""
        if not os.path.exists(image_path):
            print(f"Imagem não encontrada: {image_path}")
            return
            
        frame = cv.imread(image_path)
        if frame is None:
            print(f"Erro ao carregar imagem: {image_path}")
            return
            
        # Processar imagem
        result = self.detect_and_display(frame)
        
        # Mostrar resultado
        cv.imshow('Detecção em Imagem Estática', result)
        
        print("Pressione qualquer tecla para fechar...")
        cv.waitKey(0)
        cv.destroyAllWindows()
        
        # Salvar resultado
        output_path = f"face_detected_{os.path.basename(image_path)}"
        cv.imwrite(output_path, result)
        print(f"Resultado salvo: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Detector de Máscara Facial Interativa')
    parser.add_argument('--mask', help='Caminho para imagem da máscara', default='rosto3dmask.jpg')
    parser.add_argument('--camera', help='Número da câmera', type=int, default=0)
    parser.add_argument('--image', help='Processar imagem estática em vez da câmera')
    
    args = parser.parse_args()
    
    # Criar detector
    detector = InteractiveFaceMask(args.mask)
    
    if args.image:
        # Processar imagem estática
        detector.process_static_image(args.image)
    else:
        # Executar com câmera
        detector.run_camera(args.camera)

if __name__ == '__main__':
    main()
