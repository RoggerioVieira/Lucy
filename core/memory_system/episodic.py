import json
import uuid
import logging
from datetime import datetime
from pathlib import Path

class EpisodicMemory:
    def __init__(self, storage_path="data/memory_system/episodic/"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self.logger = logging.getLogger("Lucy.Episodic")
        self.index = self._load_index()

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return []

    def _save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=4, ensure_ascii=False)

    def create_episode(self, event_type, agent, location, content, valence=0.5):
        episode_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        episode_data = {
            "id": episode_id, "timestamp": timestamp, "event_type": event_type,
            "agent": agent, "location": location, "content": content, "valence": valence
        }
        
        try:
            with open(self.storage_path / f"{episode_id}.json", 'w', encoding='utf-8') as f:
                json.dump(episode_data, f, indent=4, ensure_ascii=False)
            
            summary = f"User: {content.get('input','')} | Lucy: {content.get('output','')}" if isinstance(content, dict) else str(content)
            self.index.append({"id": episode_id, "timestamp": timestamp, "summary": summary[:50]})
            self._save_index()
            return episode_id
        except Exception as e:
            self.logger.error(f"Erro ao salvar episódio: {e}")
            return None
