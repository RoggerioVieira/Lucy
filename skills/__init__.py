from .base_skill import BaseSkill
from .spotify_skill import SpotifySkill
from .weather_skill import WeatherSkill
from .reminder_skill import ReminderSkill

def get_all_skills(memory=None):
    return [
        SpotifySkill(memory),
        WeatherSkill(memory),
        ReminderSkill(memory)
    ]
