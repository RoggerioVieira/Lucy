"""
Skill de previsão do tempo
"""

from .base_skill import BaseSkill
import requests

class WeatherSkill(BaseSkill):
    """Consulta clima e previsão do tempo"""
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.description = "Previsão do tempo e clima"
        self.api_key = None
        self._load_config()
    
    def _load_config(self):
        if self.memory and 'preferences' in self.memory.data:
            self.api_key = self.memory.data['preferences'].get('weather_api_key')
    
    def can_handle(self, text: str) -> bool:
        keywords = ['clima', 'tempo', 'temperatura', 'previsao', 'vai chover']
        return any(kw in text.lower() for kw in keywords)
    
    def handle(self, text: str, **kwargs) -> str:
        if not self.api_key:
            return "🌤️ [Modo simulação] Weather API key não configurada."
        return "🌤️ Consulta ao tempo realizada (simulação)."