// face3d.js - Renderização 3D do rosto do bot usando análise facial

class FaceRenderer3D {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, 800 / 600, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        this.faceGeometry = null;
        this.faceMaterial = null;
        this.faceMesh = null;
        this.animationParams = {
            eyeOpenness: 0.5,
            mouthOpenness: 0.3,
            eyebrowPosition: 0.5,
            mouthCurvature: 0.5
        };
        
        this.init();
    }
    
    init() {
        // Configurar renderer
        this.renderer.setSize(800, 600);
        this.renderer.setClearColor(0x000000, 0.1);
        
        const container = document.getElementById('threejs-container-3d');
        if (container) {
            container.appendChild(this.renderer.domElement);
        }
        
        // Configurar luzes
        this.setupLighting();
        
        // Criar geometria do rosto baseada na análise
        this.createFaceFromAnalysis();
        
        // Posicionar câmera
        this.camera.position.set(0, 0, 5);
        this.camera.lookAt(0, 0, 0);
        
        // Iniciar animação
        this.animate();
        
        console.log('✅ Renderizador 3D inicializado');
    }
    
    setupLighting() {
        // Luz ambiente
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Luz direcional principal
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);
        
        // Luz de preenchimento
        const fillLight = new THREE.DirectionalLight(0x00ffff, 0.3);
        fillLight.position.set(-1, 0, 0.5);
        this.scene.add(fillLight);
    }
    
    async createFaceFromAnalysis() {
        try {
            // Tentar carregar dados da análise facial
            const response = await fetch('data/face_analysis.json');
            const faceData = await response.json();
            console.log('📊 Dados faciais para 3D:', faceData);
            
            this.createFaceGeometry(faceData);
        } catch (error) {
            console.log('⚠️ Usando geometria facial padrão');
            this.createDefaultFaceGeometry();
        }
    }
    
    createFaceGeometry(faceData) {
        // Criar geometria personalizada baseada nos dados da análise
        const geometry = new THREE.BufferGeometry();
        
        // Usar landmarks se disponíveis
        if (faceData && faceData.landmarks_normalized) {
            const vertices = this.landmarksToVertices(faceData.landmarks_normalized);
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        } else {
            this.createDefaultFaceGeometry();
            return;
        }
        
        // Material com shader personalizado para animações
        const material = new THREE.MeshPhongMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.8,
            wireframe: true
        });
        
        this.faceGeometry = geometry;
        this.faceMaterial = material;
        this.faceMesh = new THREE.Mesh(geometry, material);
        
        this.scene.add(this.faceMesh);
    }
    
    createDefaultFaceGeometry() {
        // Geometria padrão de rosto
        const geometry = new THREE.SphereGeometry(1, 32, 16);
        const material = new THREE.MeshPhongMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.7,
            wireframe: true
        });
        
        this.faceGeometry = geometry;
        this.faceMaterial = material;
        this.faceMesh = new THREE.Mesh(geometry, material);
        
        // Adicionar características básicas
        this.addBasicFaceFeatures();
        
        this.scene.add(this.faceMesh);
    }
    
    addBasicFaceFeatures() {
        // Olhos
        const eyeGeometry = new THREE.SphereGeometry(0.1, 8, 8);
        const eyeMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.3, 0.2, 0.8);
        this.faceMesh.add(leftEye);
        
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.3, 0.2, 0.8);
        this.faceMesh.add(rightEye);
        
        // Boca
        const mouthGeometry = new THREE.TorusGeometry(0.2, 0.05, 8, 16);
        const mouthMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
        
        const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
        mouth.position.set(0, -0.3, 0.8);
        mouth.rotation.x = Math.PI / 2;
        this.faceMesh.add(mouth);
        
        // Armazenar referências para animação
        this.leftEye = leftEye;
        this.rightEye = rightEye;
        this.mouth = mouth;
    }
    
    landmarksToVertices(landmarks) {
        const vertices = [];
        
        // Converter landmarks 2D normalizados para vértices 3D
        landmarks.forEach(point => {
            const x = (point[0] - 0.5) * 2; // Centralizar e escalar
            const y = -(point[1] - 0.5) * 2; // Inverter Y e centralizar
            const z = Math.random() * 0.2 - 0.1; // Profundidade aleatória
            
            vertices.push(x, y, z);
        });
        
        return vertices;
    }
    
    updateParameters(params) {
        this.animationParams = { ...this.animationParams, ...params };
        
        if (this.faceMesh) {
            this.applyFacialAnimation();
        }
    }
    
    applyFacialAnimation() {
        const params = this.animationParams;
        
        // Animar olhos
        if (this.leftEye && this.rightEye) {
            const eyeScale = params.eyeOpenness;
            this.leftEye.scale.y = eyeScale;
            this.rightEye.scale.y = eyeScale;
            
            // Piscar
            if (params.eyeOpenness < 0.2) {
                this.leftEye.material.emissive.setHex(0x004400);
                this.rightEye.material.emissive.setHex(0x004400);
            } else {
                this.leftEye.material.emissive.setHex(0x000000);
                this.rightEye.material.emissive.setHex(0x000000);
            }
        }
        
        // Animar boca
        if (this.mouth) {
            const mouthScale = 0.5 + params.mouthOpenness;
            this.mouth.scale.set(mouthScale, mouthScale, 1);
            
            // Curvatura da boca (sorriso/tristeza)
            const curvature = (params.mouthCurvature - 0.5) * 0.5;
            this.mouth.position.y = -0.3 + curvature;
            
            // Cor baseada na emoção
            if (params.mouthCurvature > 0.6) {
                this.mouth.material.color.setHex(0x00ff00); // Verde para feliz
            } else if (params.mouthCurvature < 0.4) {
                this.mouth.material.color.setHex(0x0066ff); // Azul para triste
            } else {
                this.mouth.material.color.setHex(0xff0000); // Vermelho neutro
            }
        }
        
        // Animar mesh principal
        if (this.faceMesh) {
            // Rotação sutil baseada na emoção
            const emotionRotation = (params.mouthCurvature - 0.5) * 0.1;
            this.faceMesh.rotation.z = emotionRotation;
            
            // Cor do material baseada na emoção
            const emotionIntensity = Math.abs(params.mouthCurvature - 0.5) * 2;
            this.faceMaterial.opacity = 0.7 + emotionIntensity * 0.3;
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Rotação automática sutil
        if (this.faceMesh) {
            this.faceMesh.rotation.y += 0.005;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    resize(width, height) {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
}

// Inicializar quando a página carregar
window.addEventListener('load', () => {
    window.faceAnimation = new FaceRenderer3D();
    console.log('🎭 Renderizador 3D do rosto inicializado');
});

// Ajustar tamanho da janela
window.addEventListener('resize', () => {
    if (window.faceAnimation) {
        window.faceAnimation.resize(800, 600);
    }
});
