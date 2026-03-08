import json
import os
import pickle
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class LucyMemory:
    """Sistema de memória persistente da Lucy"""

    def __init__(self):
        self.memory_file = "lucy_memory.json"
        self.patterns_file = "lucy_patterns.pkl"
        self.personality_file = "lucy_personality.json"
        self.history_file = "lucy_history.json"

        self.data = self.load_memory()
        self.personality = self.load_personality()
        self.model_data = self.load_or_init_model()
        self.conversation_history = self.load_history()

    def load_memory(self):
        """Carrega memória principal com tratamento de erros"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Reconstruir defaultdict
                    if 'routines' in data:
                        routines = defaultdict(list)
                        routines.update(data['routines'])
                        data['routines'] = routines
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Erro ao carregar memória: {e}. Criando nova.")

        return {
            "user_facts": {},
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
        """Carrega traços de personalidade"""
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
        """Carrega modelo de ML ou inicializa novo"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, IOError):
                print("⚠️ Modelo corrompido. Inicializando novo.")

        return {
            'vectorizer': TfidfVectorizer(max_features=100),
            'classifier': MultinomialNB(),
            'patterns': defaultdict(list)
        }

    def load_history(self):
        """Carrega histórico de conversas"""
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
        # Manter apenas últimas 20 interações
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def get_context(self, last_n=3):
        """Retorna contexto recente da conversa"""
        return self.conversation_history[-last_n:] if self.conversation_history else []

    def save_all(self):
        """Salva todos os dados de forma atômica"""
        try:
            # Salvar Memory
            mem_to_save = self.data.copy()
            mem_to_save['routines'] = dict(self.data['routines'])
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(mem_to_save, f, indent=2, ensure_ascii=False)

            # Salvar Personality
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality, f, indent=2, ensure_ascii=False)

            # Salvar History
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)

            # Salvar Model
            with open(self.patterns_file, 'wb') as f:
                pickle.dump(self.model_data, f)

        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")