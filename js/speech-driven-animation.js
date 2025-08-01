/**
 * Speech-driven facial animation
 * Synchronizes facial expressions with the bot's speech
 */

class SpeechDrivenAnimation {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.bufferLength = null;
        this.maskCanvas = document.getElementById('clonedMaskCanvas');
        this.maskContext = this.maskCanvas?.getContext('2d');

        this.initAudio();
    }

    initAudio() {
        try {
            // Inicializar AudioContext
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            // Criar AnalyserNode
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;
            this.bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(this.bufferLength);

            // Conectar AnalyserNode a um destino
            this.analyser.connect(this.audioContext.destination);

            console.log('🎵 AudioContext inicializado.');
        } catch (error) {
            console.error('Erro ao inicializar AudioContext:', error);
        }
    }

    connectAudioSource(sourceNode) {
        sourceNode.connect(this.analyser);
        this.animateMask();
    }

    animateMask() {
        requestAnimationFrame(() => this.animateMask());

        this.analyser.getByteTimeDomainData(this.dataArray);

        const canvas = this.maskCanvas;
        const ctx = this.maskContext;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = '#00ffff';

        ctx.beginPath();

        const sliceWidth = (canvas.width * 1.0) / this.bufferLength;
        let x = 0;

        for (let i = 0; i < this.bufferLength; i++) {
            const v = this.dataArray[i] / 128.0;
            const y = (v * canvas.height) / 2;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();

        // Simulate facial expressions based on volume
        const volume = this.getAverageVolume(this.dataArray);
        this.updateExpression(volume);
    }

    getAverageVolume(array) {
        let sum = 0;
        for (let i = 0; i < array.length; i++) {
            sum += array[i];
        }
        return sum / array.length;
    }

    updateExpression(volume) {
        const faceModel = window.faceAnalysisManager?.currentAnalysis;

        if (!faceModel) return;

        faceModel.features.mouth.aspect_ratio = (volume / 255 * 1.5).toFixed(2);
        faceModel.features.eyes.average_openness = 1 - faceModel.features.mouth.aspect_ratio;

        // Update facial parameters UI (for demonstration purpose)
        window.faceAnalysisManager.updateFacialParameters();
    }

    startUsingBotAudio() {
        const audioElement = document.getElementById('botAudio');
        if (audioElement) {
            const sourceNode = this.audioContext.createMediaElementSource(audioElement);
            this.connectAudioSource(sourceNode);
        }
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.speechDrivenAnimation = new SpeechDrivenAnimation();
    
    // Exemplo de controle
    const startBtn = document.getElementById('startAnimationBtn');
    startBtn?.addEventListener('click', () => {
        window.speechDrivenAnimation.startUsingBotAudio();
    });

    // Placeholder para áudio
    const audioPlaceholder = document.createElement('audio');
    audioPlaceholder.id = 'botAudio';
    audioPlaceholder.src = './path/to/bot_speech.mp3';
    audioPlaceholder.style.display = 'none';
    audioPlaceholder.controls = true; // Somente para depuração
    document.body.appendChild(audioPlaceholder);
});

// Exportar para uso global
window.SpeechDrivenAnimation = SpeechDrivenAnimation;

