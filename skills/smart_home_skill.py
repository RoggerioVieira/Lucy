"""
Skill para controle de casa inteligente
"""

from .base_skill import BaseSkill
import re

class SmartHomeSkill(BaseSkill):
    """Controla dispositivos domésticos"""
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.description = "Controle de casa inteligente"
        self.triggers = ['luz', 'lampada', 'ar condicionado', 'cortina', 'porta', 'modo ']
    
    def can_handle(self, text: str) -> bool:
        keywords = ['luz', 'lampada', 'ar condicionado', 'cortina', 'porta', 
                   'trancar', 'ligar', 'desligar', 'modo cinema', 'modo festa']
        return any(kw in text.lower() for kw in keywords)
    
    def handle(self, text: str, **kwargs) -> str:
        text_lower = text.lower()
        if 'luz' in text_lower or 'lampada' in text_lower:
            return self._handle_light(text)
        if 'ar condicionado' in text_lower or 'temperatura' in text_lower:
            return self._handle_ac(text)
        if 'cortina' in text_lower:
            return self._handle_curtain(text)
        if 'modo' in text_lower:
            return self._handle_scene(text)
        return "❌ Dispositivo não reconhecido"
    
    def _handle_light(self, text):
        if 'ligar' in text.lower() or 'acender' in text.lower(): return "💡 Luz ligada!"
        elif 'desligar' in text.lower() or 'apagar' in text.lower(): return "🌑 Luz desligada!"
        return "💡 Comando de luz não reconhecido"
    
    def _handle_ac(self, text):
        match = re.search(r'(\d+)\s*(?:graus?|°)', text)
        if match:
            temp = match.group(1)
            return f"❄️ Ar condicionado ajustado para {temp}°C"
        return "❄️ Ar condicionado comandado!"
    
    def _handle_curtain(self, text):
        return "🪟 Cortina acionada!"

    def _handle_scene(self, text):
        scenes = {'cinema': '💡 Modo cinema ativado', 'festa': '🎉 Modo festa ativado'}
        for scene, msg in scenes.items():
            if scene in text.lower(): return msg
        return "🎬 Cena não encontrada"