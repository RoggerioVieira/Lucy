import time
from collections import deque

class WorkingMemory:
    def __init__(self, capacity=5):
        self.focus_buffer = deque(maxlen=capacity)
        self.last_active_entity = None

    def add_interaction(self, user_input, response):
        self.focus_buffer.append({
            "timestamp": time.time(),
            "user": user_input,
            "lucy": response
        })
        self._analyze_topic(user_input)

    def _analyze_topic(self, text):
        words = text.lower().split()
        potential_entities = [w for w in words if len(w) > 4]
        if potential_entities:
            self.last_active_entity = potential_entities[-1]

    def get_context_string(self):
        if not self.focus_buffer:
            return "Nenhum contexto anterior."
        ctx = [f"Usuário: {i['user']} -> Lucy: {i['lucy']}" for i in self.focus_buffer]
        return " | ".join(ctx)
