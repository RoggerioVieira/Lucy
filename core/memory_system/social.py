import json
from pathlib import Path
from datetime import datetime

class SocialCortex:
    def __init__(self, file_path="data/memory_system/social/people.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.profiles = self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {}

    def get_or_create_profile(self, name):
        name = name.strip().lower()
        if name not in self.profiles:
            self.profiles[name] = {"name": name, "trust_level": 0.5, "total_interactions": 0}
        return self.profiles[name]

    def update_interaction(self, name, impact=0.01):
        profile = self.get_or_create_profile(name)
        profile["total_interactions"] += 1
        profile["trust_level"] = max(0, min(1, profile["trust_level"] + impact))
        self.save()

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, indent=4, ensure_ascii=False)
