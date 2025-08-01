/**
 * Face Analysis Module - Integração com Python para análise facial
 * Gerencia a análise de rostos e geração de máscaras de contorno
 */

class FaceAnalysisManager {
    constructor() {
        this.isProcessing = false;
        this.currentAnalysis = null;
        this.maskCanvas = null;
        this.debugMode = false;
        
        this.init();
    }
    
    init() {
        console.log('🎯 FaceAnalysisManager inicializado');
        
        // Inicializar canvas da máscara
        this.maskCanvas = document.getElementById('clonedMaskCanvas');
        this.maskContext = this.maskCanvas?.getContext('2d');
        
        // Bind event listeners
        this.bindEvents();
        
        // Carregar análise existente se disponível
        this.loadExistingAnalysis();
    }
    
    bindEvents() {
        // Botões de análise
        const analyzeBtn = document.getElementById('analyzeImageBtn');
        const detectBtn = document.getElementById('detectFeaturesBtn');
        const generateMaskBtn = document.getElementById('generateMaskBtn');
        const cloneMaskBtn = document.getElementById('cloneMaskBtn');
        const startAnalysisBtn = document.getElementById('startAnalysisBtn');
        const resetAnalysisBtn = document.getElementById('resetAnalysisBtn');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }
        
        if (detectBtn) {
            detectBtn.addEventListener('click', () => this.detectFeatures());
        }
        
        if (generateMaskBtn) {
            generateMaskBtn.addEventListener('click', () => this.generateMask());
        }
        
        if (cloneMaskBtn) {
            cloneMaskBtn.addEventListener('click', () => this.cloneMask());
        }
        
        if (startAnalysisBtn) {
            startAnalysisBtn.addEventListener('click', () => this.startCompleteAnalysis());
        }
        
        if (resetAnalysisBtn) {
            resetAnalysisBtn.addEventListener('click', () => this.resetAnalysis());
        }
    }
    
    async loadExistingAnalysis() {
        try {
            // Tentar carregar análise existente
            const response = await fetch('assets/rosto3d_analysis.json');
            if (response.ok) {
                this.currentAnalysis = await response.json();
                this.updateUI();
                console.log('✅ Análise existente carregada', this.currentAnalysis);
            }
        } catch (error) {
            console.log('ℹ️ Nenhuma análise existente encontrada');
        }
    }
    
    async analyzeImage() {
        if (this.isProcessing) return;
        
        this.setProcessing(true);
        this.updateStatus('Analisando imagem...');
        
        try {
            // Simular análise usando Python backend
            // Em uma implementação real, isso faria uma chamada para um servidor Python
            const result = await this.simulateAnalysis();
            
            this.currentAnalysis = result;
            this.updateUI();
            this.updateStatus('Análise concluída!');
            
        } catch (error) {
            console.error('Erro na análise:', error);
            this.updateStatus('Erro na análise');
        } finally {
            this.setProcessing(false);
        }
    }
    
    async detectFeatures() {
        if (!this.currentAnalysis) {
            await this.analyzeImage();
        }
        
        if (this.currentAnalysis?.features) {
            this.highlightFeatures();
            this.updateStatus('Características detectadas!');
        }
    }
    
    async generateMask() {
        if (!this.currentAnalysis) {
            await this.analyzeImage();
        }
        
        this.setProcessing(true);
        this.updateStatus('Gerando máscara...');
        
        try {
            await this.createMaskVisualization();
            this.updateStatus('Máscara gerada!');
        } catch (error) {
            console.error('Erro ao gerar máscara:', error);
            this.updateStatus('Erro ao gerar máscara');
        } finally {
            this.setProcessing(false);
        }
    }
    
    async cloneMask() {
        if (!this.currentAnalysis) {
            await this.generateMask();
        }
        
        this.setProcessing(true);
        this.updateStatus('Clonando características...');
        
        try {
            await this.applyMaskCloning();
            this.updateStatus('Características clonadas!');
        } catch (error) {
            console.error('Erro ao clonar máscara:', error);
            this.updateStatus('Erro ao clonar máscara');
        } finally {
            this.setProcessing(false);
        }
    }
    
    async startCompleteAnalysis() {
        this.setProcessing(true);
        this.updateStatus('Iniciando análise completa...');
        
        try {
            // Sequência completa de análise
            await this.analyzeImage();
            await this.detectFeatures();
            await this.generateMask();
            await this.cloneMask();
            
            this.updateStatus('Análise completa finalizada!');
            
            // Atualizar gerador de código
            this.generateCode();
            
        } catch (error) {
            console.error('Erro na análise completa:', error);
            this.updateStatus('Erro na análise completa');
        } finally {
            this.setProcessing(false);
        }
    }
    
    resetAnalysis() {
        this.currentAnalysis = null;
        this.clearMaskCanvas();
        this.updateUI();
        this.updateStatus('Análise resetada');
    }
    
    async simulateAnalysis() {
        // Simula uma análise baseada nos dados reais que obtivemos
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    image_path: "assets/rosto3d.png",
                    face_detected: true,
                    landmarks_count: 478,
                    features: {
                        eyes: {
                            left_openness: 0.258,
                            right_openness: 0.265,
                            average_openness: 0.261,
                            is_blinking: false
                        },
                        mouth: {
                            width: 86.33,
                            height: 90.61,
                            aspect_ratio: 1.050,
                            is_open: true
                        }
                    },
                    contours: {
                        left_eye: [[204, 267], [208, 270], [214, 273], [267, 272]],
                        right_eye: [[354, 272], [357, 273], [364, 274], [416, 267]],
                        mouth: [[248, 432], [291, 458], [366, 439], [263, 432]],
                        nose: [[307, 362], [307, 374], [308, 328], [309, 240]]
                    },
                    timestamp: Date.now()
                });
            }, 2000);
        });
    }
    
    async createMaskVisualization() {
        if (!this.maskCanvas || !this.currentAnalysis) return;
        
        const ctx = this.maskContext;
        const canvas = this.maskCanvas;
        
        // Limpar canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Configurar estilo
        ctx.strokeStyle = '#00ffff';
        ctx.fillStyle = 'rgba(0, 255, 255, 0.1)';
        ctx.lineWidth = 2;
        
        // Desenhar contornos das características
        const contours = this.currentAnalysis.contours;
        const scale = Math.min(canvas.width / 617, canvas.height / 616); // Escalar para o canvas
        
        Object.entries(contours).forEach(([feature, points]) => {
            if (points && points.length > 0) {
                ctx.beginPath();
                
                // Converter coordenadas e desenhar
                points.forEach((point, index) => {
                    const x = point[0] * scale;
                    const y = point[1] * scale;
                    
                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                
                ctx.closePath();
                ctx.stroke();
                ctx.fill();
            }
        });
        
        // Adicionar efeito de brilho
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#00ffff';
        ctx.stroke();
    }
    
    async applyMaskCloning() {
        if (!this.currentAnalysis) return;
        
        // Simular aplicação de clonagem
        const maskInfo = document.getElementById('maskInfo');
        if (maskInfo) {
            maskInfo.textContent = `Máscara clonada - ${this.currentAnalysis.landmarks_count} pontos mapeados`;
        }
        
        // Adicionar efeito visual de processamento
        this.addProcessingEffect();
    }
    
    highlightFeatures() {
        // Destacar características na interface
        const imageContainer = document.querySelector('.image-container');
        if (imageContainer) {
            imageContainer.classList.add('feature-detected');
            
            setTimeout(() => {
                imageContainer.classList.remove('feature-detected');
            }, 2000);
        }
    }
    
    addProcessingEffect() {
        const processingIndicator = document.getElementById('processingIndicator');
        if (processingIndicator) {
            processingIndicator.style.display = 'flex';
            
            setTimeout(() => {
                processingIndicator.style.display = 'none';
            }, 3000);
        }
    }
    
    updateUI() {
        // Atualizar informações da imagem
        const imageInfo = document.getElementById('imageInfo');
        if (imageInfo && this.currentAnalysis) {
            imageInfo.textContent = `Modelo: Rosto 3D | Status: Analisado | Landmarks: ${this.currentAnalysis.landmarks_count}`;
        }
        
        // Atualizar informações da máscara
        const maskInfo = document.getElementById('maskInfo');
        if (maskInfo && this.currentAnalysis) {
            const features = this.currentAnalysis.features;
            let info = 'Máscara gerada - ';
            
            if (features.eyes) {
                info += `Olhos: ${(features.eyes.average_openness * 100).toFixed(1)}% abertos, `;
            }
            
            if (features.mouth) {
                info += `Boca: ${features.mouth.is_open ? 'Aberta' : 'Fechada'}`;
            }
            
            maskInfo.textContent = info;
        }
        
        // Atualizar parâmetros faciais no painel lateral
        this.updateFacialParameters();
    }
    
    updateFacialParameters() {
        if (!this.currentAnalysis?.features) return;
        
        const features = this.currentAnalysis.features;
        
        // Atualizar abertura dos olhos
        const eyePosition = document.getElementById('eyePosition');
        if (eyePosition && features.eyes) {
            eyePosition.textContent = `${features.eyes.left_openness.toFixed(3)}, ${features.eyes.right_openness.toFixed(3)}`;
        }
        
        // Atualizar abertura da boca
        const mouthOpening = document.getElementById('mouthOpening');
        if (mouthOpening && features.mouth) {
            mouthOpening.textContent = `${(features.mouth.aspect_ratio * 100).toFixed(1)}%`;
        }
        
        // Atualizar intensidade emocional baseada na análise
        const emotionIntensity = document.getElementById('emotionIntensity');
        if (emotionIntensity) {
            const intensity = features.mouth?.is_open ? 75 : 50;
            emotionIntensity.textContent = `${intensity}%`;
        }
    }
    
    generateCode() {
        const codeOutput = document.getElementById('generatedCode');
        if (codeOutput && this.currentAnalysis) {
            const code = this.createAnimationCode();
            codeOutput.textContent = code;
        }
    }
    
    createAnimationCode() {
        if (!this.currentAnalysis?.features) return '// Nenhuma análise disponível';
        
        const features = this.currentAnalysis.features;
        
        return `// Código de animação facial gerado automaticamente
// Baseado na análise de ${this.currentAnalysis.landmarks_count} landmarks

const facialAnimation = {
    // Características dos olhos
    eyes: {
        leftOpenness: ${features.eyes?.left_openness.toFixed(3) || 0.5},
        rightOpenness: ${features.eyes?.right_openness.toFixed(3) || 0.5},
        averageOpenness: ${features.eyes?.average_openness.toFixed(3) || 0.5},
        isBlinking: ${features.eyes?.is_blinking || false}
    },
    
    // Características da boca
    mouth: {
        width: ${features.mouth?.width.toFixed(2) || 0},
        height: ${features.mouth?.height.toFixed(2) || 0},
        aspectRatio: ${features.mouth?.aspect_ratio.toFixed(3) || 0},
        isOpen: ${features.mouth?.is_open || false}
    },
    
    // Função para aplicar animação
    applyAnimation: function(faceModel) {
        // Aplicar abertura dos olhos
        faceModel.morphTargetInfluences[0] = this.eyes.averageOpenness;
        
        // Aplicar abertura da boca
        faceModel.morphTargetInfluences[1] = this.mouth.aspectRatio;
        
        // Aplicar expressão baseada no estado
        if (this.mouth.isOpen) {
            faceModel.morphTargetInfluences[2] = 0.7; // Expressão de fala
        }
    }
};

// Usar a animação
// facialAnimation.applyAnimation(yourFaceModel);`;
    }
    
    setProcessing(processing) {
        this.isProcessing = processing;
        
        // Desabilitar/habilitar botões
        const buttons = document.querySelectorAll('.image-btn, .mask-btn, .global-btn');
        buttons.forEach(btn => {
            btn.disabled = processing;
            if (processing) {
                btn.classList.add('processing');
            } else {
                btn.classList.remove('processing');
            }
        });
    }
    
    updateStatus(message) {
        console.log(`🔍 ${message}`);
        
        // Atualizar logs do sistema
        this.addLogEntry('ANÁLISE', message);
    }
    
    addLogEntry(type, message) {
        const conversationLog = document.getElementById('conversationLog');
        if (conversationLog) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry system';
            logEntry.innerHTML = `
                <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                <span class="type">[${type}]</span>
                <span class="message">${message}</span>
            `;
            
            conversationLog.appendChild(logEntry);
            conversationLog.scrollTop = conversationLog.scrollHeight;
        }
    }
    
    clearMaskCanvas() {
        if (this.maskContext) {
            this.maskContext.clearRect(0, 0, this.maskCanvas.width, this.maskCanvas.height);
        }
    }
    
    // Método para exportar análise
    exportAnalysis() {
        if (this.currentAnalysis) {
            const dataStr = JSON.stringify(this.currentAnalysis, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = 'face_analysis_export.json';
            link.click();
        }
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.faceAnalysisManager = new FaceAnalysisManager();
});

// Exportar para uso global
window.FaceAnalysisManager = FaceAnalysisManager;
