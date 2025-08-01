# AI Face Interface Bot

Sistema de IA com rosto virtual animado que responde via API Gemini e manipula expressões faciais baseadas na análise de imagem.

## 📁 Estrutura do Projeto

```
ai-face-interface/
├── 📄 index.html              # Página principal da interface
├── 📄 server.js               # Servidor Node.js local
├── 📄 README.md              # Documentação do projeto
│
├── 📁 js/                    # Scripts JavaScript
│   ├── face3d.js            # Renderização 3D com Three.js
│   ├── gemini-api.js        # Integração com API Gemini
│   └── script.js            # Scripts principais da interface
│
├── 📁 css/                   # Estilos CSS
│   └── styles.css           # Estilos da interface
│
├── 📁 python/                # Scripts Python para análise facial
│   ├── face_analyzer.py     # Analisador facial completo
│   ├── face_tracker_3d.py   # Rastreamento 3D em tempo real
│   ├── extract_traces.py    # Extração de bordas/traços
│   ├── face_mask_detector.py # Detector de máscaras faciais
│   ├── simple_face_analyzer.py # Análise facial simplificada
│   └── generate_face_data.py # Gerador de dados para o bot
│
├── 📁 data/                  # Dados e configurações
│   ├── face_analysis.json   # Dados da análise facial
│   ├── ajuste_fino_config.json # Configurações de ajuste fino
│   └── manual_adjustments.json # Ajustes manuais
│
├── 📁 assets/                # Recursos visuais
│   ├── rosto3d.png          # Imagem base do rosto
│   ├── rosto3d_traces.png   # Traços extraídos
│   └── rosto3d_analyzed.png # Visualização da análise
│
└── 📁 docs/                  # Documentação
    └── requirements.txt     # Dependências Python
```

## 🚀 Como Usar

### 1. Iniciar o Servidor
```bash
node server.js
```

### 2. Acessar a Interface
Abra: `http://localhost:3000`

### 3. Gerar Dados Faciais (opcional)
```bash
python python/generate_face_data.py
```

## 🎯 Funcionalidades

- **🤖 Rosto Virtual 3D**: Renderizado com Three.js usando dados reais de análise facial
- **🧠 IA Conversacional**: Integração com Google Gemini API
- **😊 Expressões Dinâmicas**: O bot muda expressões baseado na conversa
- **📊 Análise Facial**: Extração de landmarks e características do rosto
- **🎭 Controles Manuais**: Botões para testar diferentes emoções
- **📈 Visualização em Tempo Real**: Canvas mostra máscara emocional

## 🔧 Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **3D**: Three.js para renderização
- **IA**: Google Gemini API
- **Backend**: Node.js (servidor local)
- **Análise**: Python + MediaPipe + OpenCV

## 📝 Configuração da API

No arquivo `js/gemini-api.js`, configure sua chave da API:
```javascript
this.API_KEY = "sua_chave_aqui";
```

## 🎨 Personalização

- **Emoções**: Modifique `getEmotionParameters()` em `gemini-api.js`
- **Cores**: Ajuste `emotionColors` para diferentes esquemas
- **3D**: Personalize geometria em `face3d.js`
- **Análise**: Configure parâmetros em `python/generate_face_data.py`

## 🔄 Fluxo de Funcionamento

1. **Análise**: Python extrai características da imagem `rosto3d.png`
2. **Dados**: Gera `face_analysis.json` com landmarks e parâmetros
3. **3D**: Three.js carrega dados e cria modelo 3D
4. **IA**: Gemini API processa mensagens e define emoções
5. **Animação**: Interface atualiza expressões em tempo real

## 🐛 Troubleshooting

- **Servidor não inicia**: Verifique se Node.js está instalado
- **3D não carrega**: Confirme que `data/face_analysis.json` existe
- **API falha**: Verifique chave do Gemini e conexão internet
- **Python errors**: Instale dependências: `pip install -r docs/requirements.txt`

---

**Desenvolvido com ❤️ usando tecnologias modernas de IA e computer vision**
