// gemini-api.js - Controlador de expressões faciais via API Gemini com animação de fala

class GeminiFaceController {
    constructor() {
        this.API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent";
        this.API_KEY = "AIzaSyAV6k7MxnZWDe_APYW2XO8PV2QfjrcTtqE";
        
        this.currentEmotion = "neutral";
        this.isProcessing = false;
        this.faceData = null;
        this.speechSynthesis = window.speechSynthesis;
        this.isSpeaking = false;
        
        // Carregar dados da análise facial
        this.loadFaceAnalysis();
        
        // Inicializar integração com animação de fala
        this.initSpeechAnimation();
    }
    
    initSpeechAnimation() {
        // Verificar se o SpeechDrivenAnimation está disponível
        if (window.speechDrivenAnimation) {
            console.log('🎵 Integração com animação de fala inicializada');
        }
    }
    
    async loadFaceAnalysis() {
        try {
            const response = await fetch('data/face_analysis.json');
            this.faceData = await response.json();
            console.log('✅ Dados faciais carregados:', this.faceData);
        } catch (error) {
            console.log('⚠️ Usando dados faciais padrão');
            this.faceData = this.getDefaultFaceData();
        }
    }
    
    getDefaultFaceData() {
        return {
            eyes: { average_openness: 0.5, is_blinking: false },
            mouth: { aspect_ratio: 0.3, is_speaking: false },
            emotion: { dominant_emotion: "neutral", confidence: 1.0 }
        };
    }
    
    async processUserInput(userMessage) {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.updateFaceIndicator('thinking');
        
        try {
            // Preparar prompt para Gemini analisar emoção da resposta
            const prompt = `
            Analise a mensagem do usuário e responda de forma natural.
            Também indique qual emoção o bot deve expressar no rosto.
            
            Mensagem: "${userMessage}"
            
            Responda no formato JSON:
            {
                "response": "sua resposta aqui",
                "emotion": "neutral|happy|sad|angry|surprised|thinking",
                "emotion_intensity": 0.1-1.0,
                "speaking_duration": 2000-5000
            }
            `;
            
            const response = await this.callGeminiAPI(prompt);
            const botData = JSON.parse(response);
            
            // Atualizar expressão facial
            this.updateFaceExpression(botData.emotion, botData.emotion_intensity);
            this.updateFaceIndicator('speaking');
            
            // Simular fala
            await this.simulateSpeaking(botData.speaking_duration);
            
            this.updateFaceIndicator('listening');
            return botData.response;
            
        } catch (error) {
            console.error('Erro ao processar entrada:', error);
            this.updateFaceExpression('neutral', 0.5);
            return "Desculpe, tive um problema para processar sua mensagem.";
        } finally {
            this.isProcessing = false;
        }
    }
    
    async callGeminiAPI(prompt) {
        const requestBody = {
            contents: [{
                parts: [{
                    text: prompt
                }]
            }]
        };
        
        const response = await fetch(`${this.API_URL}?key=${this.API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    }
    
    updateFaceExpression(emotion, intensity = 0.5) {
        this.currentEmotion = emotion;
        
        // Atualizar parâmetros faciais baseado na emoção
        const faceParams = this.getEmotionParameters(emotion, intensity);
        
        // Aplicar na interface
        this.applyFaceParameters(faceParams);
        
        // Atualizar display da emoção
        const emotionDisplay = document.getElementById('currentExpression');
        if (emotionDisplay) {
            emotionDisplay.textContent = emotion.toUpperCase();
        }
        
        console.log(`🎭 Emoção atualizada: ${emotion} (${intensity})`);
    }
    
    getEmotionParameters(emotion, intensity) {
        const baseParams = {
            eyeOpenness: this.faceData?.eyes?.average_openness || 0.5,
            mouthOpenness: this.faceData?.mouth?.aspect_ratio || 0.3,
            eyebrowPosition: 0.5,
            mouthCurvature: 0.5
        };
        
        switch(emotion) {
            case 'happy':
                return {
                    ...baseParams,
                    eyeOpenness: Math.max(0.3, baseParams.eyeOpenness - 0.2 * intensity),
                    mouthCurvature: 0.5 + (0.4 * intensity),
                    eyebrowPosition: 0.5 + (0.2 * intensity)
                };
                
            case 'sad':
                return {
                    ...baseParams,
                    eyeOpenness: Math.max(0.2, baseParams.eyeOpenness - 0.3 * intensity),
                    mouthCurvature: 0.5 - (0.3 * intensity),
                    eyebrowPosition: 0.5 - (0.3 * intensity)
                };
                
            case 'angry':
                return {
                    ...baseParams,
                    eyeOpenness: Math.min(0.8, baseParams.eyeOpenness + 0.2 * intensity),
                    mouthCurvature: 0.5 - (0.2 * intensity),
                    eyebrowPosition: 0.5 - (0.4 * intensity)
                };
                
            case 'surprised':
                return {
                    ...baseParams,
                    eyeOpenness: Math.min(1.0, baseParams.eyeOpenness + 0.4 * intensity),
                    mouthOpenness: Math.min(0.8, baseParams.mouthOpenness + 0.3 * intensity),
                    eyebrowPosition: 0.5 + (0.4 * intensity)
                };
                
            case 'thinking':
                return {
                    ...baseParams,
                    eyeOpenness: baseParams.eyeOpenness - 0.1,
                    eyebrowPosition: 0.5 + (0.1 * intensity)
                };
                
            default: // neutral
                return baseParams;
        }
    }
    
    applyFaceParameters(params) {
        // Atualizar parâmetros na interface
        document.getElementById('eyePosition')?.textContent = 
            `${params.eyeOpenness.toFixed(2)}, 0.0`;
        document.getElementById('mouthOpening')?.textContent = 
            `${(params.mouthOpenness * 100).toFixed(0)}%`;
        document.getElementById('emotionIntensity')?.textContent = 
            `${(params.mouthCurvature * 100).toFixed(0)}%`;
            
        // Aplicar na animação 3D (se disponível)
        if (window.faceAnimation) {
            window.faceAnimation.updateParameters(params);
        }
        
        // Atualizar canvas de máscara traçada
        this.updateTracedMask(params);
    }
    
    updateTracedMask(params) {
        const canvas = document.getElementById('tracedMaskCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Desenhar rosto baseado nos parâmetros
        this.drawFaceMask(ctx, params, canvas.width, canvas.height);
    }
    
    drawFaceMask(ctx, params, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Cores baseadas na emoção
        const emotionColors = {
            'happy': '#00ff00',
            'sad': '#0066ff', 
            'angry': '#ff3300',
            'surprised': '#ffff00',
            'thinking': '#ff6600',
            'neutral': '#00ffff'
        };
        
        ctx.strokeStyle = emotionColors[this.currentEmotion] || '#00ffff';
        ctx.lineWidth = 2;
        
        // Contorno do rosto
        ctx.beginPath();
        ctx.ellipse(centerX, centerY, 80, 100, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Olhos
        const eyeY = centerY - 20;
        const eyeOpenness = params.eyeOpenness;
        
        // Olho esquerdo
        ctx.beginPath();
        ctx.ellipse(centerX - 25, eyeY, 15, 8 * eyeOpenness, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Olho direito
        ctx.beginPath();
        ctx.ellipse(centerX + 25, eyeY, 15, 8 * eyeOpenness, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Boca
        const mouthY = centerY + 30;
        const mouthCurve = (params.mouthCurvature - 0.5) * 20;
        const mouthOpen = params.mouthOpenness * 15;
        
        ctx.beginPath();
        ctx.moveTo(centerX - 20, mouthY - mouthCurve);
        ctx.quadraticCurveTo(centerX, mouthY + mouthCurve + mouthOpen, centerX + 20, mouthY - mouthCurve);
        ctx.stroke();
        
        // Sobrancelhas
        const browY = centerY - 35 + (0.5 - params.eyebrowPosition) * 10;
        
        ctx.beginPath();
        ctx.moveTo(centerX - 35, browY);
        ctx.lineTo(centerX - 15, browY);
        ctx.moveTo(centerX + 15, browY);
        ctx.lineTo(centerX + 35, browY);
        ctx.stroke();
    }
    
    updateFaceIndicator(state) {
        // Atualizar indicadores visuais
        const indicators = ['listeningIndicator', 'thinkingIndicator', 'speakingIndicator'];
        
        indicators.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.remove('active');
            }
        });
        
        const activeIndicator = document.getElementById(state + 'Indicator');
        if (activeIndicator) {
            activeIndicator.classList.add('active');
        }
    }
    
    async simulateSpeaking(duration) {
        return new Promise(resolve => {
            let elapsed = 0;
            const interval = setInterval(() => {
                // Simular movimento da boca durante a fala
                const speakingIntensity = Math.sin(elapsed / 100) * 0.1 + 0.4;
                const currentParams = this.getEmotionParameters(this.currentEmotion, 0.5);
                currentParams.mouthOpenness = speakingIntensity;
                
                this.applyFaceParameters(currentParams);
                
                elapsed += 100;
                if (elapsed >= duration) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });
    }
}

// Instância global
window.geminiFaceController = new GeminiFaceController();

// gemini-api.js - Controlador de expressões faciais via API Gemini

class GeminiFaceController {
    constructor() {
        this.API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent";
        this.API_KEY = "AIzaSyAV6k7MxnZWDe_APYW2XO8PV2QfjrcTtqE";
        
        this.currentEmotion = "neutral";
        this.isProcessing = false;
        this.faceData = null;
        
        // Carregar dados da análise facial
        this.loadFaceAnalysis();
    }
    
    async loadFaceAnalysis() {
        try {
            const response = await fetch('face_analysis.json');
            this.faceData = await response.json();
            console.log('✅ Dados faciais carregados:', this.faceData);
        } catch (error) {
            console.log('⚠️ Usando dados faciais padrão');
            this.faceData = this.getDefaultFaceData();
        }
    }
    
    getDefaultFaceData() {
        return {
            eyes: { average_openness: 0.5, is_blinking: false },
            mouth: { aspect_ratio: 0.3, is_speaking: false },
            emotion: { dominant_emotion: "neutral", confidence: 1.0 }
        };
    }
    
    async processUserInput(userMessage) {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.updateFaceIndicator('thinking');
        
        try {
            // Preparar prompt para Gemini analisar emoção da resposta
            const prompt = `
            Analise a mensagem do usuário e responda de forma natural.
            Também indique qual emoção o bot deve expressar no rosto.
            
            Mensagem: "${userMessage}"
            
            Responda no formato JSON:
            {
                "response": "sua resposta aqui",
                "emotion": "neutral|happy|sad|angry|surprised|thinking",
                "emotion_intensity": 0.1-1.0,
                "speaking_duration": 2000-5000
            }
            `;
            
            const response = await this.callGeminiAPI(prompt);
            const botData = JSON.parse(response);
            
            // Atualizar expressão facial
            this.updateFaceExpression(botData.emotion, botData.emotion_intensity);
            this.updateFaceIndicator('speaking');
            
            // Simular fala
            await this.simulateSpeaking(botData.speaking_duration);
            
            this.updateFaceIndicator('listening');
            return botData.response;
            
        } catch (error) {
            console.error('Erro ao processar entrada:', error);
            this.updateFaceExpression('neutral', 0.5);
            return "Desculpe, tive um problema para processar sua mensagem.";
        } finally {
            this.isProcessing = false;
        }
    }
    
    async callGeminiAPI(prompt) {
        const requestBody = {
            contents: [{
                parts: [{
                    text: prompt
                }]
            }]
        };
        
        const response = await fetch(`${this.API_URL}?key=${this.API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    }
    
    updateFaceExpression(emotion, intensity = 0.5) {
        this.currentEmotion = emotion;
        
        // Atualizar parâmetros faciais baseado na emoção
        const faceParams = this.getEmotionParameters(emotion, intensity);
        
        // Aplicar na interface
        this.applyFaceParameters(faceParams);
        
        // Atualizar display da emoção
        const emotionDisplay = document.getElementById('currentExpression');
        if (emotionDisplay) {
            emotionDisplay.textContent = emotion.toUpperCase();
        }
        
        console.log(`🎭 Emoção atualizada: ${emotion} (${intensity})`);
    }
    
    getEmotionParameters(emotion, intensity) {
        const baseParams = {
            eyeOpenness: this.faceData?.eyes?.average_openness || 0.5,
            mouthOpenness: this.faceData?.mouth?.aspect_ratio || 0.3,
            eyebrowPosition: 0.5,
            mouthCurvature: 0.5
        };
        
        switch(emotion) {
            case 'happy':
                return {
                    ...baseParams,
                    eyeOpenness: Math.max(0.3, baseParams.eyeOpenness - 0.2 * intensity),
                    mouthCurvature: 0.5 + (0.4 * intensity),
                    eyebrowPosition: 0.5 + (0.2 * intensity)
                };
                
            case 'sad':
                return {
                    ...baseParams,
                    eyeOpenness: Math.max(0.2, baseParams.eyeOpenness - 0.3 * intensity),
                    mouthCurvature: 0.5 - (0.3 * intensity),
                    eyebrowPosition: 0.5 - (0.3 * intensity)
                };
                
            case 'angry':
                return {
                    ...baseParams,
                    eyeOpenness: Math.min(0.8, baseParams.eyeOpenness + 0.2 * intensity),
                    mouthCurvature: 0.5 - (0.2 * intensity),
                    eyebrowPosition: 0.5 - (0.4 * intensity)
                };
                
            case 'surprised':
                return {
                    ...baseParams,
                    eyeOpenness: Math.min(1.0, baseParams.eyeOpenness + 0.4 * intensity),
                    mouthOpenness: Math.min(0.8, baseParams.mouthOpenness + 0.3 * intensity),
                    eyebrowPosition: 0.5 + (0.4 * intensity)
                };
                
            case 'thinking':
                return {
                    ...baseParams,
                    eyeOpenness: baseParams.eyeOpenness - 0.1,
                    eyebrowPosition: 0.5 + (0.1 * intensity)
                };
                
            default: // neutral
                return baseParams;
        }
    }
    
    applyFaceParameters(params) {
        // Atualizar parâmetros na interface
        document.getElementById('eyePosition')?.textContent = 
            `${params.eyeOpenness.toFixed(2)}, 0.0`;
        document.getElementById('mouthOpening')?.textContent = 
            `${(params.mouthOpenness * 100).toFixed(0)}%`;
        document.getElementById('emotionIntensity')?.textContent = 
            `${(params.mouthCurvature * 100).toFixed(0)}%`;
            
        // Aplicar na animação 3D (se disponível)
        if (window.faceAnimation) {
            window.faceAnimation.updateParameters(params);
        }
        
        // Atualizar canvas de máscara traçada
        this.updateTracedMask(params);
    }
    
    updateTracedMask(params) {
        const canvas = document.getElementById('tracedMaskCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Desenhar rosto baseado nos parâmetros
        this.drawFaceMask(ctx, params, canvas.width, canvas.height);
    }
    
    drawFaceMask(ctx, params, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Cores baseadas na emoção
        const emotionColors = {
            'happy': '#00ff00',
            'sad': '#0066ff', 
            'angry': '#ff3300',
            'surprised': '#ffff00',
            'thinking': '#ff6600',
            'neutral': '#00ffff'
        };
        
        ctx.strokeStyle = emotionColors[this.currentEmotion] || '#00ffff';
        ctx.lineWidth = 2;
        
        // Contorno do rosto
        ctx.beginPath();
        ctx.ellipse(centerX, centerY, 80, 100, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Olhos
        const eyeY = centerY - 20;
        const eyeOpenness = params.eyeOpenness;
        
        // Olho esquerdo
        ctx.beginPath();
        ctx.ellipse(centerX - 25, eyeY, 15, 8 * eyeOpenness, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Olho direito
        ctx.beginPath();
        ctx.ellipse(centerX + 25, eyeY, 15, 8 * eyeOpenness, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Boca
        const mouthY = centerY + 30;
        const mouthCurve = (params.mouthCurvature - 0.5) * 20;
        const mouthOpen = params.mouthOpenness * 15;
        
        ctx.beginPath();
        ctx.moveTo(centerX - 20, mouthY - mouthCurve);
        ctx.quadraticCurveTo(centerX, mouthY + mouthCurve + mouthOpen, centerX + 20, mouthY - mouthCurve);
        ctx.stroke();
        
        // Sobrancelhas
        const browY = centerY - 35 + (0.5 - params.eyebrowPosition) * 10;
        
        ctx.beginPath();
        ctx.moveTo(centerX - 35, browY);
        ctx.lineTo(centerX - 15, browY);
        ctx.moveTo(centerX + 15, browY);
        ctx.lineTo(centerX + 35, browY);
        ctx.stroke();
    }
    
    updateFaceIndicator(state) {
        // Atualizar indicadores visuais
        const indicators = ['listeningIndicator', 'thinkingIndicator', 'speakingIndicator'];
        
        indicators.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.remove('active');
            }
        });
        
        const activeIndicator = document.getElementById(state + 'Indicator');
        if (activeIndicator) {
            activeIndicator.classList.add('active');
        }
    }
    
    async simulateSpeaking(duration) {
        return new Promise(resolve => {
            let elapsed = 0;
            const interval = setInterval(() => {
                // Simular movimento da boca durante a fala
                const speakingIntensity = Math.sin(elapsed / 100) * 0.1 + 0.4;
                const currentParams = this.getEmotionParameters(this.currentEmotion, 0.5);
                currentParams.mouthOpenness = speakingIntensity;
                
                this.applyFaceParameters(currentParams);
                
                elapsed += 100;
                if (elapsed >= duration) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });
    }
}

// Instância global
window.geminiFaceController = new GeminiFaceController();
