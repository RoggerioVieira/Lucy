from pathlib import Path
import os 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",)
USE_CLOUD_BRAIN = True # Mude para False para usar o cerebro local (menos poderoso, mas sem dependências externas)

# API de Conhecimento Externo
BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# Caminho absoluto para a pasta da Lucy
BASE_DIR = Path(r"C:\Users\Roger\OneDrive\Desktop\Lucy")
DATA_DIR = BASE_DIR / "data"

# Garante que a pasta existe (se não existir, ela cria)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configurações de memória apontando para o local fixo
MEMORY_CONFIG = {
    'memory_file': DATA_DIR / "lucy_memory.json",
    'personality_file': DATA_DIR / "lucy_personality.json",
    'patterns_file': DATA_DIR / "lucy_patterns.pkl",
    'history_file': DATA_DIR / "lucy_history.json",
    
}

# Mantém as tuas SKILLS
SKILLS_CONFIG = {
    'reminder': {'enabled': True},
    'spotify': {'enabled': False},
    'weather': {'enabled': False},
    'email': {'enabled': False},
    'smarthome': {'enabled': False}
}

LUCY_CONFIG = {
    'watcher_interval': 5,
    'slow_response_threshold': 1500,  # ms
    'max_reminders_history': 20,
    'timezone': 'America/Sao_Paulo',
    'snooze_minutes': 10,
    'save_interval': 5, # salva a cada 5 interações
}

