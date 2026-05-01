import json
import logging
from pathlib import Path

logger = logging.getLogger("Lucy.SpatialMemory")

class SpatialMemory:
    """Mapa mental do humanoide: Rastreia objetos e localizações físicas."""
    
    def __init__(self, file_path="data/memory_system/semantic/spatial_map.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.world_map = self._load_map()

    def _load_map(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar mapa espacial: {e}")
        
        # Estrutura inicial do mundo
        return {
            "locations": {}, # ex: {"cozinha": ["copo", "chave"]}
            "objects": {}    # ex: {"chave": "cozinha"}
        }

    def update_object_location(self, object_name, location_name):
        """Move ou adiciona um objeto a um local específico."""
        obj = object_name.lower().strip()
        loc = location_name.lower().strip()

        # Se o objeto já estava em outro lugar, removemos do local antigo
        old_loc = self.world_map["objects"].get(obj)
        if old_loc and old_loc in self.world_map["locations"]:
            if obj in self.world_map["locations"][old_loc]:
                self.world_map["locations"][old_loc].remove(obj)

        # Atualiza a nova localização do objeto
        self.world_map["objects"][obj] = loc

        # Garante que o local existe na lista de locais
        if loc not in self.world_map["locations"]:
            self.world_map["locations"][loc] = []
        
        if obj not in self.world_map["locations"][loc]:
            self.world_map["locations"][loc].append(obj)

        self.save()
        logger.info(f"📍 Espaço atualizado: '{obj}' agora está em '{loc}'.")

    def locate_object(self, object_name):
        """Busca onde um objeto está no mundo físico."""
        obj = object_name.lower().strip()
        return self.world_map["objects"].get(obj, None)

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.world_map, f, indent=4, ensure_ascii=False)

        