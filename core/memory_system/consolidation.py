import logging
from pathlib import Path

logger = logging.getLogger("Lucy.SleepCycle")

class SleepCycle:
    def __init__(self, episodic_mem, social_cortex, base_memory):
        self.episodic = episodic_mem
        self.social = social_cortex

    def go_to_sleep(self):
        logger.info("💤 Iniciando ciclo de sono (Fase REM)...")
        pruned_count = self._pruning_forgetting()
        logger.info(f"🌅 Acordando! Memórias inúteis apagadas: {pruned_count}")
        return pruned_count

    def _pruning_forgetting(self):
        pruned = 0
        valid_episodes = []
        for ep in self.episodic.index:
            summary = ep.get("summary", "").lower()
            if any(word in summary for word in ["não entendi", "estou ouvindo", "sistemas processando"]):
                ep_file = self.episodic.storage_path / f"{ep['id']}.json"
                if ep_file.exists():
                    try:
                        ep_file.unlink()
                        pruned += 1
                    except: pass
            else:
                valid_episodes.append(ep)
        
        self.episodic.index = valid_episodes
        self.episodic._save_index()
        return pruned
