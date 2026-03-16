"""
Skills Package - Exporta todas as skills disponíveis
"""

from .base_skill import BaseSkill
from .spotify_skill import SpotifySkill
from .weather_skill import WeatherSkill
from .reminder_skill import ReminderSkill
from .email_skill import EmailSkill
from .smart_home_skill import SmartHomeSkill

# Dicionário de skills disponíveis (usado pelo SkillManager)
AVAILABLE_SKILLS = {
    'spotify': SpotifySkill,
    'weather': WeatherSkill,
    'reminder': ReminderSkill,
    'email': EmailSkill,
    'smart_home': SmartHomeSkill,
}

__all__ = [
    'BaseSkill',
    'SpotifySkill',
    'WeatherSkill',
    'ReminderSkill',
    'EmailSkill',
    'SmartHomeSkill',
    'AVAILABLE_SKILLS',
    'SkillManager',
    'get_all_skills',
]

# Import circular-safe
try:
    from .skill_manager import SkillManager
except ImportError:
    SkillManager = None  # type: ignore


def get_all_skills(memory=None):
    """
    Retorna lista de todas as skills instanciadas.
    Retorna lista de objetos Skill (não tuplas).
    """
    if SkillManager is None:
        return []
    
    manager = SkillManager(memory)
    skills_list = []
    
    for name in AVAILABLE_SKILLS.keys():
        skill_instance = manager._get_skill_instance(name)
        if skill_instance:
            skills_list.append(skill_instance)
    
    return skills_list