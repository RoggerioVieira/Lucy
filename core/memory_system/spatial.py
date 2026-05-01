import json
import logging
from pathlib import Path

logger = logging.getLogger("Lucy.SpatialMemory")

class SpatialMemory:
    def __init__(self, file_path="data/memory_system/semantic/spatial_map.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.world_map = self._load_map()

    def _load_map(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"locations": {}, "objects": {}}

    def update_object_location(self, object_name, location_name):
        obj = object_name.lower().strip()
        loc = location_name.lower().strip()

        old_loc = self.world_map["objects"].get(obj)
        if old_loc and old_loc in self.world_map["locations"]:
            if obj in self.world_map["locations"][old_loc]:
                self.world_map["locations"][old_loc].remove(obj)

        self.world_map["objects"][obj] = loc
        if loc not in self.world_map["locations"]:
            self.world_map["locations"][loc] = []
        if obj not in self.world_map["locations"][loc]:
            self.world_map["locations"][loc].append(obj)
        self.save()

    def locate_object(self, object_name):
        return self.world_map["objects"].get(object_name.lower().strip())

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.world_map, f, indent=4, ensure_ascii=False)
