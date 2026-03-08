"""
Skill de integração com Spotify
"""

from .base_skill import BaseSkill
import re

class SpotifySkill(BaseSkill):
    """Controla música no Spotify"""
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.description = "Controla música no Spotify"
        self.spotify = None
        self._init_spotify()
    
    def _init_spotify(self):
        # Simulação ou inicialização real com spotipy
        self.spotify = None 

    def can_handle(self, text: str) -> bool:
        keywords = ['tocar', 'musica', 'spotify', 'playlist', 'proxima', 'pausar', 'volume']
        return any(kw in text.lower() for kw in keywords)
    
    def handle(self, text: str, **kwargs) -> str:
        return "🎵 [Modo simulação] Spotify não configurado. Configure em config.py"