class UltraRealisticAndroidAI {
    constructor() {
        this.API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent";
        this.API_KEY = "AIzaSyAV6k7MxnZWDe_APYW2XO8PV2QfjrcTtqE";
        
        // Elementos DOM
        this.container = document.getElementById('threejs-container');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.conversationLog = document.getElementById('conversationLog');
        this.audioSpectrum = document.getElementById('audioSpectrum');
        this.loadingScreen = document.getElementById('loadingScreen');
        this.progressBar = document.getElementById('progressBar');
        this.loadingStatus = document.getElementById('loadingStatus');
        
        // Status indicators
        this.listeningIndicator = document.getElementById('listeningIndicator');
        this.thinkingIndicator = document.getElementById('thinkingIndicator');
        this.speakingIndicator = document.getElementById('speakingIndicator');
        
        // Parameter displays
        this.currentExpressionEl = document.getElementById('currentExpression');
        this.eyePositionEl = document.getElementById('eyePosition');
        this.mouthOpeningEl = document.getElementById('mouthOpening');
        this.emotionIntensityEl = document.getElementById('emotionIntensity');
        
        // Estados
        this.isListening = false;
        this.isThinking = false;
        this.isSpeaking = false;
        this.currentEmotion = 'neutral';
        this.emotionValue = 0.5;
        
        // Three.js components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.androidHead = null;
        this.leftEye = null;
        this.rightEye = null;
        this.mouth = null;
        this.faceMesh = null;
        this.lights = [];
        this.particles = [];
        
        // Animation properties
        this.animationId = null;
        this.eyeTargetX = 0;
        this.eyeTargetY = 0;
        this.eyeCurrentX = 0;
        this.eyeCurrentY = 0;
        this.blinkTimer = 0;
        this.mouthAnimation = 0;
        this.speechIntensity = 0;
        this.breathingPhase = 0;
        this.currentExpression = 'idle';
        
        // APIs do navegador
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        
        this.initializeLoadingSequence();
        this.initializeVoiceRecognition();
        this.setupEventListeners();
        this.startAnimation();
        this.greetUser();
    }
    
    initializeCanvas() {
        // Configurar canvas
        this.ctx.imageSmoothingEnabled = true;
        this.ctx.imageSmoothingQuality = 'high';
        
        // Inicializar partículas
        this.initializeParticles();
        
        // Estado inicial
        this.currentExpression = 'idle';
        this.displayBootSequence();
    }
    
    initializeParticles() {
        this.particles = [];
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * this.canvasWidth,
                y: Math.random() * this.canvasHeight,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: `hsl(${180 + Math.random() * 60}, 100%, 70%)`
            });
        }
    }
    
    displayBootSequence() {
        const bootMessages = [
            "INICIALIZANDO SISTEMA...",
            "CARREGANDO MODELOS NEURAIS...",
            "CONECTANDO À REDE...",
            "CALIBRANDO SENSORES...",
            "SISTEMA PRONTO!"
        ];
        
        let messageIndex = 0;
        const bootInterval = setInterval(() => {
            this.clearCanvas();
            this.drawBootMessage(bootMessages[messageIndex]);
            messageIndex++;
            
            if (messageIndex >= bootMessages.length) {
                clearInterval(bootInterval);
                this.currentExpression = 'idle';
            }
        }, 800);
    }
    
    drawBootMessage(message) {
        this.ctx.fillStyle = '#00ffff';
        this.ctx.font = 'bold 14px Orbitron';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(message, this.canvasWidth / 2, this.canvasHeight / 2);
        
        // Barra de progresso
        const progress = (Date.now() % 1000) / 1000;
        this.drawProgressBar(progress);
    }
    
    drawProgressBar(progress) {
        const barWidth = 200;
        const barHeight = 4;
        const x = (this.canvasWidth - barWidth) / 2;
        const y = this.canvasHeight / 2 + 30;
        
        // Background
        this.ctx.fillStyle = 'rgba(0, 255, 255, 0.2)';
        this.ctx.fillRect(x, y, barWidth, barHeight);
        
        // Progress
        this.ctx.fillStyle = '#00ffff';
        this.ctx.fillRect(x, y, barWidth * progress, barHeight);
    }
    
    startAnimation() {
        const animate = () => {
            this.updateCanvas();
            this.animationId = requestAnimationFrame(animate);
        };
        animate();
    }
    
    updateCanvas() {
        this.clearCanvas();
        
        // Desenhar baseado no estado atual
        switch (this.currentExpression) {
            case 'idle':
                this.drawIdleState();
                break;
            case 'listening':
                this.drawListeningState();
                break;
            case 'thinking':
                this.drawThinkingState();
                break;
            case 'speaking':
                this.drawSpeakingState();
                break;
            case 'happy':
                this.drawHappyState();
                break;
            case 'surprised':
                this.drawSurprisedState();
                break;
        }
        
        this.updateParticles();
        this.drawParticles();
    }
    
    clearCanvas() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight);
    }
    
    drawIdleState() {
        // Padrão de circuito neural idle
        const time = Date.now() * 0.001;
        
        // Rede neural de fundo
        this.drawNeuralNetwork(time);
        
        // Logo central
        this.drawCentralLogo();
        
        // Status text
        this.ctx.fillStyle = 'rgba(0, 255, 255, 0.8)';
        this.ctx.font = '12px Orbitron';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('AGUARDANDO...', this.canvasWidth / 2, this.canvasHeight - 30);
    }
    
    drawListeningState() {
        // Visualização de ondas de áudio
        const time = Date.now() * 0.01;
        
        // Círculos concêntricos pulsantes
        for (let i = 0; i < 5; i++) {
            const radius = 50 + i * 30 + Math.sin(time + i) * 10;
            const opacity = 0.8 - i * 0.15;
            
            this.ctx.strokeStyle = `rgba(0, 255, 0, ${opacity})`;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.canvasWidth / 2, this.canvasHeight / 2, radius, 0, Math.PI * 2);
            this.ctx.stroke();
        }
        
        // Emoji de microfone
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('🎤', this.canvasWidth / 2, this.canvasHeight / 2 + 15);
    }
    
    drawThinkingState() {
        // Padrão de pensamento complexo
        const time = Date.now() * 0.002;
        
        // Espiral de pensamento
        for (let i = 0; i < 100; i++) {
            const angle = i * 0.2 + time;
            const radius = i * 2;
            const x = this.canvasWidth / 2 + Math.cos(angle) * radius;
            const y = this.canvasHeight / 2 + Math.sin(angle) * radius;
            
            const opacity = 1 - (i / 100);
            this.ctx.fillStyle = `rgba(255, 170, 0, ${opacity})`;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Emoji de cérebro
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('🧠', this.canvasWidth / 2, this.canvasHeight / 2 + 15);
    }
    
    drawSpeakingState() {
        // Visualização de fala com ondas
        const time = Date.now() * 0.005;
        
        // Ondas de áudio emanando
        for (let i = 0; i < 8; i++) {
            const waveHeight = Math.sin(time + i * 0.5) * 20;
            const x = 50 + i * 40;
            
            this.ctx.strokeStyle = '#ff3366';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.moveTo(x, this.canvasHeight / 2 - waveHeight);
            this.ctx.lineTo(x, this.canvasHeight / 2 + waveHeight);
            this.ctx.stroke();
        }
        
        // Emoji de alto-falante
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('🔊', this.canvasWidth / 2, this.canvasHeight / 2 + 15);
    }
    
    drawHappyState() {
        // Explosão de partículas felizes
        const time = Date.now() * 0.003;
        
        // Círculos de alegria
        for (let i = 0; i < 20; i++) {
            const angle = (i / 20) * Math.PI * 2 + time;
            const radius = 80 + Math.sin(time * 2 + i) * 20;
            const x = this.canvasWidth / 2 + Math.cos(angle) * radius;
            const y = this.canvasHeight / 2 + Math.sin(angle) * radius;
            
            this.ctx.fillStyle = `hsl(${60 + i * 10}, 100%, 70%)`;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 5, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Emoji sorridente
        this.ctx.font = '64px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('😊', this.canvasWidth / 2, this.canvasHeight / 2 + 20);
    }
    
    drawSurprisedState() {
        // Explosão de surpresa
        const time = Date.now() * 0.008;
        
        // Raios de surpresa
        for (let i = 0; i < 12; i++) {
            const angle = (i / 12) * Math.PI * 2;
            const length = 100 + Math.sin(time + i) * 30;
            const x1 = this.canvasWidth / 2;
            const y1 = this.canvasHeight / 2;
            const x2 = x1 + Math.cos(angle) * length;
            const y2 = y1 + Math.sin(angle) * length;
            
            this.ctx.strokeStyle = '#ffff00';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
        }
        
        // Emoji surpreso
        this.ctx.font = '64px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('😲', this.canvasWidth / 2, this.canvasHeight / 2 + 20);
    }
    
    drawNeuralNetwork(time) {
        // Desenhar rede neural de fundo
        const nodes = 15;
        const positions = [];
        
        // Gerar posições dos nós
        for (let i = 0; i < nodes; i++) {
            positions.push({
                x: Math.random() * this.canvasWidth,
                y: Math.random() * this.canvasHeight
            });
        }
        
        // Desenhar conexões
        this.ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        for (let i = 0; i < positions.length; i++) {
            for (let j = i + 1; j < positions.length; j++) {
                const dist = Math.sqrt(
                    Math.pow(positions[i].x - positions[j].x, 2) +
                    Math.pow(positions[i].y - positions[j].y, 2)
                );
                
                if (dist < 150) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(positions[i].x, positions[i].y);
                    this.ctx.lineTo(positions[j].x, positions[j].y);
                    this.ctx.stroke();
                }
            }
        }
        
        // Desenhar nós
        positions.forEach((pos, i) => {
            const pulse = Math.sin(time + i) * 0.3 + 0.7;
            this.ctx.fillStyle = `rgba(0, 255, 255, ${pulse})`;
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, 3, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    drawCentralLogo() {
        // Logo central da IA
        const centerX = this.canvasWidth / 2;
        const centerY = this.canvasHeight / 2;
        
        // Círculo externo
        this.ctx.strokeStyle = '#00ffff';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 60, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Texto AI
        this.ctx.fillStyle = '#00ffff';
        this.ctx.font = 'bold 24px Orbitron';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('AI', centerX, centerY + 8);
    }
    
    updateParticles() {
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvasWidth;
            if (particle.x > this.canvasWidth) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvasHeight;
            if (particle.y > this.canvasHeight) particle.y = 0;
        });
    }
    
    drawParticles() {
        this.particles.forEach(particle => {
            this.ctx.fillStyle = particle.color.replace('70%', particle.opacity * 70 + '%');
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    // Comando para a IA desenhar coisas específicas
    drawAICommand(command) {
        this.clearCanvas();
        
        switch (command.toLowerCase()) {
            case 'coração':
                this.drawHeart();
                break;
            case 'estrela':
                this.drawStar();
                break;
            case 'gráfico':
                this.drawChart();
                break;
            default:
                this.drawCustomEmoji(command);
        }
    }
    
    drawHeart() {
        const centerX = this.canvasWidth / 2;
        const centerY = this.canvasHeight / 2;
        
        this.ctx.fillStyle = '#ff0066';
        this.ctx.font = '100px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('❤️', centerX, centerY + 30);
    }
    
    drawStar() {
        const centerX = this.canvasWidth / 2;
        const centerY = this.canvasHeight / 2;
        
        this.ctx.fillStyle = '#ffff00';
        this.ctx.font = '100px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('⭐', centerX, centerY + 30);
    }
    
    drawChart() {
        // Gráfico de barras simples
        const values = [20, 45, 80, 35, 60, 90, 25];
        const barWidth = 40;
        const maxHeight = 150;
        const startX = 50;
        
        values.forEach((value, i) => {
            const height = (value / 100) * maxHeight;
            const x = startX + i * (barWidth + 10);
            const y = this.canvasHeight - 100 - height;
            
            this.ctx.fillStyle = `hsl(${180 + i * 30}, 100%, 60%)`;
            this.ctx.fillRect(x, y, barWidth, height);
            
            // Labels
            this.ctx.fillStyle = '#00ffff';
            this.ctx.font = '12px Orbitron';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(value, x + barWidth / 2, y - 10);
        });
    }
    
    drawCustomEmoji(emoji) {
        const centerX = this.canvasWidth / 2;
        const centerY = this.canvasHeight / 2;
        
        this.ctx.font = '100px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(emoji, centerX, centerY + 30);
    }
    
    initializeVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'pt-BR';
            
            this.recognition.onstart = () => {
                this.setListening(true);
                console.log('Reconhecimento de voz iniciado');
            };
            
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (finalTranscript.trim()) {
                    this.processUserInput(finalTranscript.trim());
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Erro no reconhecimento de voz:', event.error);
                this.setListening(false);
            };
            
            this.recognition.onend = () => {
                this.setListening(false);
                console.log('Reconhecimento de voz finalizado');
            };
        } else {
            console.error('Reconhecimento de voz não suportado neste navegador');
            alert('Seu navegador não suporta reconhecimento de voz. Use Chrome, Edge ou Firefox.');
        }
    }
    
    setupEventListeners() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startListening());
        }
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopListening());
        }
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => this.resetSystem());
        }
        
        // Controles de expressão
        const expressionButtons = document.querySelectorAll('.expr-btn');
        expressionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const emotion = btn.getAttribute('data-emotion');
                this.setEmotion(emotion);
            });
        });
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
        }
    }
    
    setListening(listening) {
        this.isListening = listening;
        this.updateFaceExpression();
        this.updateIndicators();
    }
    
    setThinking(thinking) {
        this.isThinking = thinking;
        this.updateFaceExpression();
        this.updateIndicators();
    }
    
    setSpeaking(speaking) {
        this.isSpeaking = speaking;
        this.updateFaceExpression();
        this.updateIndicators();
    }
    
    updateFaceExpression() {
        // Atualizar expressão do canvas
        if (this.isListening) {
            this.currentExpression = 'listening';
        } else if (this.isThinking) {
            this.currentExpression = 'thinking';
        } else if (this.isSpeaking) {
            this.currentExpression = 'speaking';
        } else {
            this.currentExpression = 'idle';
        }
    }
    
    updateIndicators() {
        // Atualizar indicadores de status
        this.listeningIndicator.classList.toggle('active', this.isListening);
        this.thinkingIndicator.classList.toggle('active', this.isThinking);
        this.speakingIndicator.classList.toggle('active', this.isSpeaking);
        
        // Atualizar visualizador de áudio
        if (this.audioSpectrum) {
            this.audioSpectrum.classList.toggle('active', this.isListening);
        }
    }
    
    async processUserInput(userText) {
        this.addMessage(userText, 'user');
        this.setListening(false);
        this.setThinking(true);
        
        try {
            const response = await this.callGeminiAPI(userText);
            this.setThinking(false);
            
            if (response) {
                this.addMessage(response, 'ai');
                await this.speakResponse(response);
                
                // Expressar emoção baseada na resposta
                this.expressEmotion(response);
            }
        } catch (error) {
            console.error('Erro ao processar entrada do usuário:', error);
            this.setThinking(false);
            const errorMessage = 'Desculpe, ocorreu um erro ao processar sua mensagem.';
            this.addMessage(errorMessage, 'ai');
            await this.speakResponse(errorMessage);
        }
        
        // Reiniciar escuta após um pequeno delay
        setTimeout(() => {
            if (!this.isListening && this.startBtn.disabled) {
                this.startListening();
            }
        }, 1000);
    }
    
    async callGeminiAPI(userText) {
        const requestBody = {
            contents: [{
                parts: [{
                    text: `Você é uma IA amigável e expressiva em uma interface robótica. Responda de forma natural e empática. Usuário disse: "${userText}"`
                }]
            }]
        };
        
        try {
            const response = await fetch(`${this.API_URL}?key=${this.API_KEY}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                throw new Error(`Erro na API: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.candidates && data.candidates[0] && data.candidates[0].content) {
                return data.candidates[0].content.parts[0].text;
            } else {
                throw new Error('Resposta inválida da API');
            }
        } catch (error) {
            console.error('Erro na chamada da API:', error);
            throw error;
        }
    }
    
    async speakResponse(text) {
        return new Promise((resolve) => {
            this.setSpeaking(true);
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'pt-BR';
            utterance.rate = 0.9;
            utterance.pitch = 1.1;
            
            // Escolher uma voz feminina se disponível
            const voices = this.synthesis.getVoices();
            const portugueseVoice = voices.find(voice => 
                voice.lang.includes('pt') && voice.name.toLowerCase().includes('fem')
            ) || voices.find(voice => voice.lang.includes('pt'));
            
            if (portugueseVoice) {
                utterance.voice = portugueseVoice;
            }
            
            // Simular variações de intensidade durante a fala
            this.startSpeechVibrations();
            
            utterance.onend = () => {
                this.setSpeaking(false);
                this.stopSpeechVibrations();
                resolve();
            };
            
            utterance.onerror = () => {
                this.setSpeaking(false);
                this.stopSpeechVibrations();
                resolve();
            };
            
            this.synthesis.speak(utterance);
        });
    }
    
    startSpeechVibrations() {
        this.vibrationInterval = setInterval(() => {
            const intensity = 0.3 + Math.random() * 0.7; // Intensidade entre 0.3 e 1.0
            this.mouth.style.setProperty('--vibration-intensity', intensity);
            
            // Variar a velocidade das animações baseado na intensidade
            const vibrationSpeed = 0.05 + (intensity * 0.1); // Entre 0.05s e 0.15s
            this.mouth.style.animationDuration = `${vibrationSpeed}s, 0.3s`;
        }, 50); // Atualizar a cada 50ms para efeito mais fluido
    }
    
    stopSpeechVibrations() {
        if (this.vibrationInterval) {
            clearInterval(this.vibrationInterval);
            this.vibrationInterval = null;
        }
        // Resetar propriedades
        this.mouth.style.removeProperty('--vibration-intensity');
        this.mouth.style.removeProperty('animation-duration');
    }
    
    expressEmotion(text) {
        // Análise simples de sentimento para escolher expressão
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes('feliz') || lowerText.includes('alegre') || 
            lowerText.includes('ótimo') || lowerText.includes('excelente')) {
            this.aiFace.classList.add('happy');
            setTimeout(() => this.aiFace.classList.remove('happy'), 3000);
        } else if (lowerText.includes('surpresa') || lowerText.includes('incrível') || 
                   lowerText.includes('uau')) {
            this.aiFace.classList.add('surprised');
            setTimeout(() => this.aiFace.classList.remove('surprised'), 3000);
        }
    }
    
    addMessage(text, sender) {
        if (!this.conversationLog) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('log-entry', sender);
        
        const timestamp = new Date().toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        const typeLabel = sender === 'ai' ? '[IA]' : '[USUÁRIO]';
        
        messageDiv.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="type">${typeLabel}</span>
            <span class="message">${text}</span>
        `;
        
        this.conversationLog.appendChild(messageDiv);
        this.conversationLog.scrollTop = this.conversationLog.scrollHeight;
    }
    
    initializeLoadingSequence() {
        if (!this.loadingScreen) return;
        
        let progress = 0;
        const steps = [
            'Carregando modelos 3D...',
            'Inicializando rede neural...',
            'Configurando reconhecimento de voz...',
            'Conectando com APIs...',
            'Finalizando configuração...'
        ];
        
        let stepIndex = 0;
        
        const loadingInterval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 100) progress = 100;
            
            if (this.progressBar) {
                this.progressBar.style.width = progress + '%';
            }
            
            if (this.loadingStatus && stepIndex < steps.length) {
                this.loadingStatus.textContent = steps[stepIndex];
                stepIndex++;
            }
            
            if (progress >= 100) {
                clearInterval(loadingInterval);
                setTimeout(() => {
                    if (this.loadingScreen) {
                        this.loadingScreen.style.opacity = '0';
                        setTimeout(() => {
                            this.loadingScreen.style.display = 'none';
                        }, 500);
                    }
                }, 1000);
            }
        }, 400);
    }
    
    async greetUser() {
        setTimeout(async () => {
            const greeting = "Olá! Sou sua assistente IA interativa. Estou aqui para conversar com você!";
            this.addMessage(greeting, 'ai');
            await this.speakResponse(greeting);
            this.setEmotion('happy');
        }, 2000);
    }
    
    setEmotion(emotion) {
        this.currentEmotion = emotion;
        this.currentExpression = emotion;
        
        // Atualizar display de parâmetros
        if (this.currentExpressionEl) {
            this.currentExpressionEl.textContent = emotion.toUpperCase();
        }
        
        // Resetar para idle após alguns segundos
        setTimeout(() => {
            if (this.currentExpression === emotion && !this.isListening && !this.isThinking && !this.isSpeaking) {
                this.currentExpression = 'idle';
                if (this.currentExpressionEl) {
                    this.currentExpressionEl.textContent = 'NEUTRO';
                }
            }
        }, 3000);
    }
    
    resetSystem() {
        // Parar reconhecimento de voz se estiver ativo
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        
        // Parar síntese de voz se estiver ativa
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
        
        // Resetar estados
        this.isListening = false;
        this.isThinking = false;
        this.isSpeaking = false;
        this.currentExpression = 'idle';
        
        // Resetar botões
        if (this.startBtn) this.startBtn.disabled = false;
        if (this.stopBtn) this.stopBtn.disabled = true;
        
        // Limpar log
        if (this.conversationLog) {
            this.conversationLog.innerHTML = `
                <div class="log-entry system">
                    <span class="timestamp">[${new Date().toLocaleTimeString('pt-BR', { 
                        hour: '2-digit', 
                        minute: '2-digit',
                        second: '2-digit'
                    })}]</span>
                    <span class="type">[SISTEMA]</span>
                    <span class="message">Sistema reiniciado com sucesso</span>
                </div>
            `;
        }
        
        // Atualizar indicadores
        this.updateIndicators();
        
        console.log('Sistema reiniciado');
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar sequência do splash screen
    initializeSplashScreen();
});

// Função para gerenciar o splash screen
function initializeSplashScreen() {
    const splashScreen = document.getElementById('splashScreen');
    const mainInterface = document.getElementById('mainInterface');
    const enterSystemBtn = document.getElementById('enterSystemBtn');
    const progressBar = document.getElementById('splashProgressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    const loadingText = document.getElementById('splashLoadingText');
    const systemChecks = document.getElementById('systemChecks');
    const systemStatusEl = document.querySelector('.tech-specs .spec-value');
    
    let progress = 0;
    let currentStep = 0;
    
    const loadingSteps = [
        { text: 'INICIALIZANDO SISTEMAS...', duration: 800 },
        { text: 'CARREGANDO REDE NEURAL...', duration: 1000 },
        { text: 'CONFIGURANDO VOZ...', duration: 700 },
        { text: 'CONECTANDO API...', duration: 900 },
        { text: 'FINALIZANDO...', duration: 600 }
    ];
    
    const checkItems = [
        { selector: '[data-check="neural"]', delay: 1000 },
        { selector: '[data-check="voice"]', delay: 1800 },
        { selector: '[data-check="synthesis"]', delay: 2500 },
        { selector: '[data-check="api"]', delay: 3200 },
        { selector: '[data-check="models"]', delay: 3800 }
    ];
    
    // Função para atualizar progresso
    function updateProgress() {
        const targetProgress = ((currentStep + 1) / loadingSteps.length) * 100;
        
        const progressInterval = setInterval(() => {
            progress += 2;
            if (progress >= targetProgress) {
                progress = targetProgress;
                clearInterval(progressInterval);
                
                if (currentStep < loadingSteps.length - 1) {
                    currentStep++;
                    setTimeout(() => {
                        if (loadingText) loadingText.textContent = loadingSteps[currentStep].text;
                        updateProgress();
                    }, 200);
                } else {
                    // Carregamento completo
                    setTimeout(showEnterButton, 500);
                }
            }
            
            if (progressBar) progressBar.style.width = progress + '%';
            if (progressPercentage) progressPercentage.textContent = Math.round(progress) + '%';
        }, 30);
    }
    
    // Função para mostrar checks do sistema
    function activateSystemChecks() {
        checkItems.forEach((item, index) => {
            setTimeout(() => {
                const element = systemChecks.querySelector(item.selector);
                if (element) {
                    element.style.color = '#00ff88';
                    element.innerHTML = element.innerHTML.replace('🧠', '✅').replace('🎤', '✅').replace('🔊', '✅').replace('🌐', '✅').replace('🤖', '✅');
                }
            }, item.delay);
        });
    }
    
    // Função para mostrar botão de entrada
    function showEnterButton() {
        if (systemStatusEl) systemStatusEl.textContent = 'PRONTO';
        if (loadingText) loadingText.textContent = 'SISTEMA PRONTO!';
        
        setTimeout(() => {
            if (enterSystemBtn) {
                enterSystemBtn.style.display = 'flex';
                enterSystemBtn.style.opacity = '0';
                setTimeout(() => {
                    enterSystemBtn.style.transition = 'opacity 0.5s ease';
                    enterSystemBtn.style.opacity = '1';
                }, 100);
            }
        }, 500);
    }
    
    // Event listener para o botão de entrada
    if (enterSystemBtn) {
        enterSystemBtn.addEventListener('click', () => {
            // Fade out splash screen
            splashScreen.style.transition = 'opacity 0.8s ease';
            splashScreen.style.opacity = '0';
            
            setTimeout(() => {
                splashScreen.style.display = 'none';
                mainInterface.style.display = 'flex';
                mainInterface.style.opacity = '0';
                
                setTimeout(() => {
                    mainInterface.style.transition = 'opacity 0.8s ease';
                    mainInterface.style.opacity = '1';
                    
                    // Inicializar a IA após mostrar interface
                    setTimeout(() => {
                        window.aiInterface = new UltraRealisticAndroidAI();
                    }, 500);
                }, 100);
            }, 800);
        });
    }
    
    // Iniciar sequência de carregamento
    setTimeout(() => {
        updateProgress();
        activateSystemChecks();
    }, 1000);
}

