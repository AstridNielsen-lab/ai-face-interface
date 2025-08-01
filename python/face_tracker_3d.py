import cv2
import numpy as np
import mediapipe as mp
import math
import time

class FaceTracker3D:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configuração do Face Mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        )
        
        # Pontos importantes do rosto para a máscara
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        
        # Cores para diferentes partes
        self.colors = {
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'red': (0, 0, 255),
            'yellow': (0, 255, 255),
            'purple': (255, 0, 255),
            'cyan': (255, 255, 0)
        }
        
        self.animation_frame = 0
        
        # Ajustes manuais
        self.manual_adjustments = {
            'mouth_offset_y': 0,
            'mouth_offset_x': 0,
            'eye_offset_y': 0,
            'face_scale': 1.0
        }
        
        # Carregar ajustes salvos ao inicializar
        self.load_manual_adjustments()
        
        # Variáveis para controle do mouse
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.adjustment_mode = 'mouth'  # 'mouth', 'eyes', 'face'
        
    def mouse_callback(self, event, x, y, flags, param):
        """Callback para eventos do mouse"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_dragging = True
            self.last_mouse_pos = (x, y)
            print(f"Modo: {self.adjustment_mode} - Arraste para ajustar")
            
        elif event == cv2.EVENT_MOUSEMOVE and self.mouse_dragging:
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            
            if self.adjustment_mode == 'mouth':
                self.manual_adjustments['mouth_offset_x'] += dx // 2
                self.manual_adjustments['mouth_offset_y'] += dy // 2
                print(f"Boca X: {self.manual_adjustments['mouth_offset_x']}, Y: {self.manual_adjustments['mouth_offset_y']}")
            
            elif self.adjustment_mode == 'eyes':
                self.manual_adjustments['eye_offset_y'] += dy // 2
                print(f"Olhos Y: {self.manual_adjustments['eye_offset_y']}")
                
            self.last_mouse_pos = (x, y)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_dragging = False
            print("Ajuste concluído!")
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Botão direito alterna o modo de ajuste
            modes = ['mouth', 'eyes', 'face']
            current_index = modes.index(self.adjustment_mode)
            self.adjustment_mode = modes[(current_index + 1) % len(modes)]
            print(f"Modo alterado para: {self.adjustment_mode}")
        
    def save_manual_adjustments(self):
        """Salva os ajustes manuais em arquivo JSON"""
        import json
        try:
            with open('manual_adjustments.json', 'w') as f:
                json.dump(self.manual_adjustments, f, indent=2)
            print("Ajustes manuais salvos!")
        except Exception as e:
            print(f"Erro ao salvar ajustes: {e}")
    
    def load_manual_adjustments(self):
        """Carrega os ajustes manuais do arquivo JSON"""
        import json
        try:
            with open('manual_adjustments.json', 'r') as f:
                saved_adjustments = json.load(f)
                self.manual_adjustments.update(saved_adjustments)
            print(f"Ajustes manuais carregados: {self.manual_adjustments}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Nenhum ajuste manual encontrado, usando padrões.")
        
    def create_3d_mask_overlay(self, image, landmarks, frame_count):
        """Cria uma sobreposição de máscara 3D animada"""
        h, w = image.shape[:2]
        overlay = image.copy()
        
        # Criar máscara transparente
        mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Animação baseada no frame
        pulse = abs(math.sin(frame_count * 0.1)) * 0.5 + 0.5
        glow_intensity = int(pulse * 100)
        
        # Desenhar contorno do rosto com efeito 3D
        face_points = []
        for idx in self.FACE_OVAL:
            if idx < len(landmarks.landmark):
                x = int(landmarks.landmark[idx].x * w)
                y = int(landmarks.landmark[idx].y * h)
                face_points.append((x, y))
        
        if len(face_points) > 3:
            face_points = np.array(face_points, np.int32)
            
            # Criar efeito de profundidade
            for i in range(5, 0, -1):
                color_intensity = int(glow_intensity * (i / 5))
                color = (0, color_intensity, 0)  # Verde com intensidade variável
                cv2.polylines(mask, [face_points], True, color, thickness=i*2)
        
        # Desenhar olhos com animação
        self.draw_animated_eyes(mask, landmarks, w, h, frame_count)
        
        # Desenhar lábios com animação
        self.draw_animated_lips(mask, landmarks, w, h, frame_count)
        
        # Adicionar pontos faciais animados
        self.draw_animated_landmarks(mask, landmarks, w, h, frame_count)
        
        # Misturar com a imagem original
        alpha = 0.7
        result = cv2.addWeighted(overlay, 1-alpha, mask, alpha, 0)
        
        return result
    
    def draw_animated_eyes(self, mask, landmarks, w, h, frame_count):
        """Desenha olhos com animação"""
        blink_effect = abs(math.sin(frame_count * 0.05)) * 0.8 + 0.2
        
        for eye_indices in [self.LEFT_EYE, self.RIGHT_EYE]:
            eye_points = []
            for idx in eye_indices:
                if idx < len(landmarks.landmark):
                    x = int(landmarks.landmark[idx].x * w)
                    y = int(landmarks.landmark[idx].y * h)
                    eye_points.append((x, y))
            
            if len(eye_points) > 3:
                eye_points = np.array(eye_points, np.int32)
                color_intensity = int(blink_effect * 255)
                cv2.fillPoly(mask, [eye_points], (color_intensity, 0, color_intensity))
    
    def draw_animated_lips(self, mask, landmarks, w, h, frame_count):
        """Desenha lábios com animação e ajuste manual"""
        lip_pulse = abs(math.sin(frame_count * 0.08)) * 0.6 + 0.4
        
        lip_points = []
        for idx in self.LIPS:
            if idx < len(landmarks.landmark):
                x = int(landmarks.landmark[idx].x * w) + self.manual_adjustments['mouth_offset_x']
                y = int(landmarks.landmark[idx].y * h) + self.manual_adjustments['mouth_offset_y']
                lip_points.append((x, y))
        
        if len(lip_points) > 3:
            lip_points = np.array(lip_points, np.int32)
            color_intensity = int(lip_pulse * 200)
            cv2.fillPoly(mask, [lip_points], (0, 0, color_intensity))
    
    def draw_animated_landmarks(self, image, landmarks, w, h, frame_count):
        """Desenha pontos de referência animados"""
        wave_offset = math.sin(frame_count * 0.1) * 3
        
        # Pontos importantes para destacar
        important_points = [1, 2, 5, 6, 8, 9, 10, 151, 175, 199, 200, 236, 3, 51, 48, 115, 131, 134, 102, 49, 220, 305, 292, 333, 298, 301]
        
        for i, landmark in enumerate(landmarks.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h + wave_offset)
            
            if i in important_points:
                # Pontos importantes com animação especial
                radius = int(abs(math.sin(frame_count * 0.05 + i * 0.1)) * 5 + 2)
                intensity = int(abs(math.cos(frame_count * 0.1 + i * 0.2)) * 255)
                cv2.circle(image, (x, y), radius, (0, intensity, intensity), -1)
            else:
                # Pontos normais em verde
                cv2.circle(image, (x, y), 1, self.colors['green'], -1)
    
    def process_image(self, image_path):
        """Processa uma imagem estática com animação"""
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erro: Não foi possível carregar a imagem {image_path}")
            return
        
        print("Processando detecção facial...")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            print("Nenhum rosto detectado na imagem!")
            return
        
        print(f"Detectado {len(results.multi_face_landmarks)} rosto(s)!")
        
        # Criar janela redimensionável
        cv2.namedWindow('Face Tracking 3D - Pressione ESC para sair', cv2.WINDOW_NORMAL)
        
        # Configurar callback do mouse
        cv2.setMouseCallback('Face Tracking 3D - Pressione ESC para sair', self.mouse_callback)
        
        print("\n=== CONTROLES ===")
        print("MOUSE:")
        print("  - Botão esquerdo + arrastar: Ajustar posição")
        print("  - Botão direito: Alternar modo (boca/olhos/rosto)")
        print("TECLADO:")
        print("  - W/S: Boca para cima/baixo")
        print("  - A/D: Boca para esquerda/direita")
        print("  - R: Reset ajustes")
        print("  - 1: Salvar ajustes")
        print("  - 2: Carregar ajustes")
        print("  - ESC: Sair")
        print(f"\nModo atual: {self.adjustment_mode.upper()}")
        print("================\n")
        
        frame_count = 0
        start_time = time.time()
        
        # Loop de animação
        while True:
            current_image = image.copy()
            
            # Processar cada rosto detectado
            for face_landmarks in results.multi_face_landmarks:
                # Criar máscara 3D animada
                current_image = self.create_3d_mask_overlay(current_image, face_landmarks, frame_count)
                
                # Desenhar mesh facial básico
                self.mp_drawing.draw_landmarks(
                    current_image,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
            
            # Adicionar informações na tela
            fps = frame_count / (time.time() - start_time) if frame_count > 0 else 0
            cv2.putText(current_image, f'FPS: {fps:.1f}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(current_image, 'ESC=Sair | W/S=Boca Y | A/D=Boca X | R=Reset | 1=Salvar | 2=Carregar', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)
            cv2.putText(current_image, f'Frame: {frame_count}', (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(current_image, f'Modo: {self.adjustment_mode.upper()}', (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            cv2.putText(current_image, f'Boca Y: {self.manual_adjustments["mouth_offset_y"]}', (10, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.putText(current_image, f'Boca X: {self.manual_adjustments["mouth_offset_x"]}', (10, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # Exibir resultado
            cv2.imshow('Face Tracking 3D - Pressione ESC para sair', current_image)
            
            frame_count += 1
            
            # Controle de velocidade da animação
            key = cv2.waitKey(50) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('s'):  # Salvar frame atual
                filename = f'face_tracking_frame_{frame_count}.png'
                cv2.imwrite(filename, current_image)
                print(f"Frame salvo como {filename}")
            elif key == ord('w'):  # Boca para cima
                self.manual_adjustments['mouth_offset_y'] -= 2
                print(f"Boca Y: {self.manual_adjustments['mouth_offset_y']}")
            elif key == ord('s'):  # Boca para baixo
                self.manual_adjustments['mouth_offset_y'] += 2
                print(f"Boca Y: {self.manual_adjustments['mouth_offset_y']}")
            elif key == ord('a'):  # Boca para esquerda
                self.manual_adjustments['mouth_offset_x'] -= 2
                print(f"Boca X: {self.manual_adjustments['mouth_offset_x']}")
            elif key == ord('d'):  # Boca para direita
                self.manual_adjustments['mouth_offset_x'] += 2
                print(f"Boca X: {self.manual_adjustments['mouth_offset_x']}")
            elif key == ord('r'):  # Reset ajustes
                self.manual_adjustments['mouth_offset_y'] = 0
                self.manual_adjustments['mouth_offset_x'] = 0
                print("Ajustes resetados!")
            elif key == ord('1'):  # Salvar ajustes
                self.save_manual_adjustments()
            elif key == ord('2'):  # Carregar ajustes
                self.load_manual_adjustments()
        
        cv2.destroyAllWindows()
        print("Processamento concluído!")
    
    def process_webcam(self):
        """Processa feed da webcam em tempo real"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro: Não foi possível abrir a webcam")
            return
        
        print("Iniciando rastreamento facial via webcam...")
        print("Pressione ESC para sair")
        
        cv2.namedWindow('Face Tracking 3D - Webcam', cv2.WINDOW_NORMAL)
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Espelhar horizontalmente para melhor experiência
            frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Criar máscara 3D animada
                    frame = self.create_3d_mask_overlay(frame, face_landmarks, frame_count)
                    
                    # Desenhar mesh facial
                    self.mp_drawing.draw_landmarks(
                        frame,
                        face_landmarks,
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                    )
            
            # Adicionar informações na tela
            fps = frame_count / (time.time() - start_time) if frame_count > 0 else 0
            cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, 'Pressione ESC para sair', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Tracking 3D - Webcam', frame)
            
            frame_count += 1
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("Rastreamento via webcam encerrado!")

def ajustar_fino():
    import json

    ajuste_fino = {
        "min_detection_confidence": float(input("Confiança mínima de detecção (0.0 a 1.0): ").strip()),
        "min_tracking_confidence": float(input("Confiança mínima de rastreamento (0.0 a 1.0): ").strip())
    }

    with open('ajuste_fino_config.json', 'w') as f:
        json.dump(ajuste_fino, f)

    print("Ajustes salvos em 'ajuste_fino_config.json'!")


def carregar_ajuste_fino():
    import json

    try:
        with open('ajuste_fino_config.json', 'r') as f:
            ajuste_fino = json.load(f)
            print("Carregado ajuste fino:", ajuste_fino)
            return ajuste_fino
    except (FileNotFoundError, json.JSONDecodeError):
        print("Nenhum ajuste fino encontrado ou arquivo malformado. Usando ajustes padrão.")
        return {}


def main():
    print("=== Face Tracker 3D ===")
    print("1. Processar imagem face3d.png")
    print("2. Usar webcam em tempo real")
    print("3. Fazer ajuste fino")
    
    choice = input("Escolha uma opção (1, 2 ou 3): ").strip()
    
    if choice == "3":
        ajustar_fino()
        return

    ajuste_fino = carregar_ajuste_fino()
    
    tracker = FaceTracker3D()
    
    if ajuste_fino:
        tracker.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=ajuste_fino.get('min_detection_confidence', 0.3),
            min_tracking_confidence=ajuste_fino.get('min_tracking_confidence', 0.3)
        )

    if choice == "1":
        tracker.process_image("face3d.png")
    elif choice == "2":
        tracker.process_webcam()
    else:
        print("Opção inválida! Processando imagem por padrão...")
        tracker.process_image("face3d.png")

if __name__ == "__main__":
    main()
