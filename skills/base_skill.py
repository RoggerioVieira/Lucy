"""
Classe base para todas as skills
"""

from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """Classe base abstrata para skills"""
    
    def __init__(self, lucy_memory=None):
        self.name = self.__class__.__name__.replace('Skill', '').lower()
        self.description = "Skill base"
        self.triggers = []
        self.enabled = True
        self.memory = lucy_memory
    
    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Verifica se pode processar o texto"""
        pass
    
    @abstractmethod
    def handle(self, text: str, **kwargs) -> str:
        """Processa o comando"""
        pass
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def get_help(self) -> str:
        return f"Skill {self.name}: {self.description}"