🤖 Lucy - Assistente Virtual Modular v1.1
Assistente de voz em Python com aprendizado por padrões de convivência.
Arquitetura modular: Voice → Brain → Memory.
✨ Novidades da v1.1
🏗️ Arquitetura Modular: Código organizado em classes especializadas
💾 Persistência Robusta: Tratamento de erros e recuperação de dados
🧠 Pipeline de Processamento: Fluxo inteligente: Ensino → Fatos → Contexto → Resposta
😊 Análise de Humor Avançada: Detecta 5 estados emocionais (positivo, negativo, animado, cansado, neutro)
📜 Histórico de Conversas: Lucy lembra do contexto recente
📝 Modo Texto Fallback: Funciona mesmo sem microfone
🎯 Comandos Personalizados: Ensine Lucy novas ações facilmente
📁 Estrutura do Projeto
plain
Copy
lucy_project/
├── lucy_assistant.py    # Classe principal (orquestração)
├── lucy_voice.py        # I/O de áudio (fala e escuta)
├── lucy_brain.py        # Processamento de linguagem e lógica
├── lucy_memory.py       # Persistência de dados
├── test_lucy.py         # Script de testes
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
🚀 Instalação Rápida
bash
Copy
# 1. Clone ou baixe os arquivos
# 2. Crie ambiente virtual (recomendado)
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Teste a instalação
python test_lucy.py

# 5. Inicie a Lucy
python lucy_assistant.py
💬 Como Usar
Primeiro Contato
plain
Copy
Você: "Oi Lucy!"
Lucy: "Olá! Sou a Lucy. Como posso ajudar?"

Você: "Meu nome é Carlos e eu trabalho com design"
Lucy: "Entendi! Vou lembrar que seu nome é Carlos e trabalho é design"
Ensinar Novos Comandos
plain
Copy
Você: "Quando eu disser 'modo foco' você deve tocar música clássica"
Lucy: "✅ Aprendido! Quando você disser 'modo foco', vou: tocar música clássica"

[Depois...]

Você: "modo foco"
Lucy: "🎯 Comando personalizado: tocar música clássica"
Perguntar Sobre Você
plain
Copy
Você: "O que você sabe sobre mim?"
Lucy: "Sei várias coisas sobre você:
       • Seu nome: Carlos
       • Seu trabalho: design
       • Seu gosto: rock"
Detectar Humor
plain
Copy
Você: "Estou muito cansado hoje"
Lucy: "Parece que você precisa de um descanso. Que tal uma música relaxante?"
🧠 Como Lucy Aprende
1. Extração de Fatos
Detecta padrões como:
"meu nome é", "eu gosto de", "trabalho com", "tenho medo de"
2. Detecção de Rotinas
Registra quando você faz o quê:
JSON
Copy
"routines": {
  "8": ["musica", "clima"],    // 8h da manhã
  "14": ["busca", "lembrete"]  // 14h
}
3. Comandos Personalizados
Mapeia gatilhos → ações:
JSON
Copy
"command_mappings": {
  "hora do café": "contar piada",
  "cheguei em casa": "tocar playlist relax"
}
4. Análise de Humor
Detecta emoções e responde com empatia:
😊 Positivo: "Que ótimo ouvir isso!"
😢 Negativo: "Sinto muito que esteja assim..."
🎉 Animado: "Ebaa! Que notícia boa!"
😴 Cansado: "Parece que precisa de descanso..."
🛠️ Arquitetura
plain
Copy
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  LucyVoice  │────▶│  LucyBrain  │────▶│ LucyMemory  │
│  (Entrada)  │     │(Processamento)│    │ (Persistência)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   Pipeline  │
                    │ 1. Ensino?  │
                    │ 2. Comando? │
                    │ 3. Fatos?   │
                    │ 4. Contexto?│
                    │ 5. Gerar    │
                    └─────────────┘
📝 Comandos Disponíveis
Table
Comando	Exemplo	Descrição
Saudação	"Oi Lucy"	Responde com contexto temporal
Hora	"Que horas são?"	Informa hora atual
Data	"Que dia é hoje?"	Informa data completa
Piada	"Conte uma piada"	Conta piadas aleatórias
Lembrete	"Lembre-me de comprar pão"	Salva lembretes
Sobre mim	"O que você sabe sobre mim?"	Lista fatos memorizados
Ensinar	"Quando eu disser X você deve Y"	Cria comandos personalizados
Sair	"Tchau"	Encerra e salva dados
🔧 Personalização
Alterar Personalidade
Edite lucy_personality.json:
JSON
Copy
{
  "humor_level": 0.8,    // Mais engraçada
  "formality": 0.2,      // Mais casual
  "curiosity": 0.9,      // Faz mais perguntas
  "empathy": 0.8         // Mais empática
}
Adicionar Novos Padrões de Fatos
Edite lucy_brain.py, método extract_facts():
Python
Copy
patterns = {
    'novo_campo': ['padrão 1', 'padrão 2'],
    # ...
}
🐛 Troubleshooting
Erro: No module named 'speech_recognition'
bash
Copy
pip install SpeechRecognition
Erro: No module named 'pyaudio'
Windows:
bash
Copy
pip install pipwin
pipwin install pyaudio
Linux:
bash
Copy
sudo apt-get install portaudio19-dev
pip install pyaudio
Lucy não fala
O sistema cai automaticamente para modo texto. Verifique se há alto-falantes.
Erro de permissão nos arquivos
Lucy tenta criar arquivos no diretório atual. Certifique-se de ter permissão de escrita.
🚀 Roadmap
[ ] Integração com Spotify
[ ] Controle de dispositivos IoT
[ ] LLM local (Llama/Ollama) para conversas naturais
[ ] Reconhecimento de múltiplos usuários
[ ] Sincronização em nuvem
[ ] Interface web de configuração
📄 Licença
MIT License - Sinta-se livre para modificar e distribuir!
Criado com ❤️ e Python