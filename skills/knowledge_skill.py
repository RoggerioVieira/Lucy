# skills/knowledge_skill.py
import requests
from skills.base_skill import BaseSkill

class KnowledgeSkill(BaseSkill):
    def __init__(self, memory):
        super().__init__(memory)
        self.name = "KnowledgeBase"

    def can_handle(self, text):
        # Esta skill não é ativada por comandos diretos, 
        # ela é uma ferramenta de consulta para o Brain.
        return False 

    def get_concept(self, query):
        """Busca um conceito na Google Books API para alimentar o cérebro."""
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    # Retorna apenas a descrição para a Lucy 'aprender' o conceito
                    return data["items"][0]["volumeInfo"].get("description", "")
        except Exception:
            return None
        return None