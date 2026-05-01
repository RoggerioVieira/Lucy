import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("Lucy.SleepCycle")

class SleepCycle:
    """
    Simula o ciclo de 'Sono' do humanoide.
    Roda offline para otimizar, limpar e consolidar o cérebro.
    """
    
    def __init__(self, episodic_mem, social_cortex, base_memory):
        self.episodic = episodic_mem
        self.social = social_cortex
        self.base_memory = base_memory

    def go_to_sleep(self):
        """Inicia o processo de consolidação e limpeza."""
        logger.info("💤 Iniciando ciclo de sono (Fase REM artificial)...")
        
        pruned_count = self._pruning_forgetting()
        self._consolidate_social_bonds()
        
        logger.info(f"🌅 Acordando! Ciclo concluído. Memórias inúteis apagadas: {pruned_count}")
        return pruned_count

    def _pruning_forgetting(self):
        """
        O 'Esquecimento Saudável'. Remove episódios inúteis (ex: erros de STT, 
        conversas sem conteúdo) para liberar espaço no 'hipocampo'.
        """
        pruned = 0
        valid_episodes = []
        
        for ep in self.episodic.index:
            summary = ep.get("summary", "").lower()
            
            # Regras de esquecimento (lixo cognitivo)
            is_trash = any(word in summary for word in [
                "não entendi", "estou ouvindo", "sistemas processando", "erro"
            ])
            
            if is_trash:
                # Remove o arquivo JSON físico do episódio
                ep_file = self.episodic.data_dir / f"{ep['id']}.json"
                if ep_file.exists():
                    try:
                        ep_file.unlink()
                        pruned += 1
                    except Exception as e:
                        logger.error(f"Erro ao apagar memória {ep['id']}: {e}")
            else:
                # Se for uma memória boa, mantém no novo índice
                valid_episodes.append(ep)
                
        # Atualiza o índice apenas com as memórias que sobreviveram à noite
        self.episodic.index = valid_episodes
        self.episodic._save_index()
        return pruned

    def _consolidate_social_bonds(self):
        """Transforma interações recentes em confiança a longo prazo."""
        for name, profile in self.social.profiles.items():
            interactions = profile.get("total_interactions", 0)
            
            # Se interagiu bastante, ganha um bônus de confiança durante o sono
            if interactions > 5 and profile["trust_level"] < 0.9:
                profile["trust_level"] += 0.05
                profile["trust_level"] = round(profile["trust_level"], 2)
                
        self.social.save()
        logger.info("👥 Vínculos sociais consolidados.")