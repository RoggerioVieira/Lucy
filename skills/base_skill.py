from abc import ABC, abstractmethod

class BaseSkill(ABC):
    def __init__(self, lucy_memory=None):
        self.name = self.__class__.__name__.replace('Skill', '').lower()
        self.memory = lucy_memory
    
    @abstractmethod
    def can_handle(self, text: str) -> bool:
        pass
    
    @abstractmethod
    def handle(self, text: str, **kwargs) -> str:
        pass