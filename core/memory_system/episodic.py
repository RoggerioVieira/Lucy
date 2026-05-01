import json
import uuid
from datetime import datetime
from pathlib import Path
import logging

class EpisodicMemory:
    """O 'Hipocampo' da Lucy: Registra experiências como episódios únicos."""
    
    def __init__(self, storage_path="data/memory_system/episodic/"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("Lucy.EpisodicMemory")

    def create_episode(self, event_type, agent, location, content, valence=0.5):
        """
        Gera um novo episódio de memória.
        valence: 0.0 (muito negativo) a 1.0 (muito positivo)
        """
        episode_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        episode_data = {
            "id": episode_id,
            "timestamp": timestamp,
            "event_type": event_type, # ex: 'dialogue', 'observation', 'task'
            "agent": agent,           # Quem interagiu
            "location": location,     # Onde ocorreu (contexto)
            "content": content,       # O dado bruto
            "emotional_valence": valence,
            "linked_memories": []     # IDs de outras memórias relacionadas
        }

        file_path = self.storage_path / f"{episode_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(episode_data, f, indent=4, ensure_ascii=False)
            return episode_id
        except Exception as e:
            self.logger.error(f"Erro ao gravar episódio crítico: {e}")
            return None