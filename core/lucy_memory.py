import json
import os
import pickle
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Tentativa de importar bibliotecas de ML (opcionais para não travar o sistema)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
except ImportError:
    TfidfVectorizer = None
    MultinomialNB = None

# Importa as configurações do seu config.py
try:
    from config import MEMORY_CONFIG
except ImportError:
    # Fallback caso o config.py não seja encontrado
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MEMORY_CONFIG = {
        'memory_file': DATA_DIR / "lucy_memory.json",
        'patterns_file': DATA_DIR / "lucy_patterns.pkl",
        'personality_file': DATA_DIR / "lucy_personality.json",
        'history_file': DATA_DIR / "lucy_history.json",
    }

class LucyMemory:
    """Sistema de memória persistente da Lucy - Corrigido para caminhos absolutos"""

    def __init__(self):
        # 1. Carrega os caminhos do config.py
        self.memory_file = MEMORY_CONFIG['memory_file']
        self.patterns_file = MEMORY_CONFIG['patterns_file']
        self.personality_file = MEMORY_CONFIG['personality_file']
        self.history_file = MEMORY_CONFIG['history_file']
        self.context_stack = []  # Guarda os ultimos 5 diálogos (user, Lucy)

        # 2. Garante que a pasta 'data' existe antes de tentar carregar/salvar
        Path(self.memory_file).parent.mkdir(parents=True, exist_ok=True)

        # 3. Inicializa os dados
        self.data = self.load_memory()
        self.personality = self.load_personality()
        self.model_data = self.load_or_init_model()
        self.conversation_history = self.load_history()


    def add_context(self, user_input, lucy_response):
        """Adiciona uma interação à memória de curto prazo."""
        self.context_stack.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'lucy': lucy_response
        })
        # Manter apenas os últimos 5 diálogos
        if len(self.context_stack) > 5:
            self.context_stack.pop(0)

    def get_last_context(self):
        """Retorna a última coisa que foi dita."""
        return self.context_stack[-1] if self.context_stack else None

    def load_memory(self):
        """Carrega memória principal com suporte a caminhos Path e tratamento de erros"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Reconstruir defaultdict para as rotinas
                    if 'routines' in data:
                        routines = defaultdict(list)
                        routines.update(data['routines'])
                        data['routines'] = routines
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Erro ao carregar memória: {e}. Criando nova.")

        return {
            "user_facts": {"nome": "amigo"}, # Valor padrão inicial
            "preferences": {},
            "routines": defaultdict(list),
            "command_mappings": {},
            "interaction_count": 0,
            "first_meeting": datetime.now().isoformat(),
            "lucy_facts": {
                "name": "Lucy",
                "birth_date": datetime.now().isoformat(),
                "version": "1.1",
                "personality": "amigável, curiosa e atenta"
            }
        }

    def load_personality(self):
        """Carrega traços de personalidade da pasta data"""
        if os.path.exists(self.personality_file):
            try:
                with open(self.personality_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "humor_level": 0.5,
            "formality": 0.3,
            "curiosity": 0.8,
            "empathy": 0.7,
            "user_mood_history": [],
            "conversation_depth": 0
        }

    def load_or_init_model(self):
        """Carrega modelo de ML (.pkl) da pasta data"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, IOError):
                print("⚠️ Modelo corrompido. Inicializando novo.")

        # Inicialização segura caso sklearn não esteja instalado
        return {
            'vectorizer': TfidfVectorizer(max_features=100) if TfidfVectorizer else None,
            'classifier': MultinomialNB() if MultinomialNB else None,
            'patterns': defaultdict(list)
        }

    def load_history(self):
        """Carrega histórico de conversas da pasta data"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def add_to_history(self, user_msg, lucy_response):
        """Adiciona turno ao histórico"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'lucy': lucy_response
        })
        # Manter apenas as últimas 20 interações
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def save_all(self):
        """Salva todos os dados na pasta correta de forma atômica"""
        try:
            # 1. Salvar Memory (Converter defaultdict para dict normal para o JSON aceitar)
            mem_to_save = self.data.copy()
            if isinstance(mem_to_save.get('routines'), defaultdict):
                mem_to_save['routines'] = dict(mem_to_save['routines'])
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(mem_to_save, f, indent=2, ensure_ascii=False)

            # 2. Salvar Personality
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality, f, indent=2, ensure_ascii=False)

            # 3. Salvar History
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)

            # 4. Salvar Model (Pickle)
            with open(self.patterns_file, 'wb') as f:
                pickle.dump(self.model_data, f)

            print(f"💾 Memória salva com sucesso em: {Path(self.memory_file).parent}")

        except Exception as e:
            print(f"❌ Erro ao salvar dados na pasta data: {e}")