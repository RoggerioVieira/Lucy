"""
Skill de alarmes e lembretes
"""

from .base_skill import BaseSkill
import re
from datetime import datetime, timedelta
import threading
import time

class ReminderSkill(BaseSkill):
    """Alarmes e lembretes com horário"""
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.description = "Alarmes e lembretes"
        self.triggers = ['lembre', 'alarme', 'avise', 'timer', 'lembrar']
        self.reminders = []
        self._load_reminders()
        self._start_checker()
    
    def _load_reminders(self):
        if self.memory and 'reminders' in self.memory.data:
            self.reminders = self.memory.data['reminders']
    
    def _save_reminders(self):
        if self.memory:
            self.memory.data['reminders'] = self.reminders
            self.memory.save_all()
    
    def _start_checker(self):
        def check():
            while True:
                self._check_due()
                time.sleep(30)
        threading.Thread(target=check, daemon=True).start()
    
    def _check_due(self):
        now = datetime.now()
        for r in self.reminders:
            if not r.get('triggered'):
                rt = datetime.fromisoformat(r['datetime'])
                if now >= rt:
                    r['triggered'] = True
                    print(f"\n🔔 LEMBRETE: {r['message']}\n")
        self._save_reminders()
    
    def can_handle(self, text: str) -> bool:
        keywords = ['lembre', 'alarme', 'avise', 'timer', 'lembrar', 'me avise']
        return any(kw in text.lower() for kw in keywords)
    
    def handle(self, text: str, **kwargs) -> str:
        if 'listar' in text.lower():
            return self._list()
        if 'as ' in text.lower() or 'às' in text.lower():
            return self._create_time(text)
        if 'em ' in text.lower():
            return self._create_duration(text)
        return self._create_simple(text)
    
    def _create_time(self, text):
        match = re.search(r'(?:às|as)\s*(\d{1,2}):(\d{2})', text)
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            now = datetime.now()
            rt = now.replace(hour=h, minute=m, second=0)
            if rt < now: rt += timedelta(days=1)
            msg = self._extract_msg(text) or "Lembrete!"
            self.reminders.append({'message': msg, 'datetime': rt.isoformat(), 'triggered': False})
            self._save_reminders()
            return f"⏰ Lembrete às {h:02d}:{m:02d}: '{msg}'"
        return "❌ Formato de hora não reconhecido. Use: às 15:30"

    def _create_duration(self, text):
        match = re.search(r'(\d+)\s*(minutos?|min|horas?|h)', text.lower())
        if match:
            amt = int(match.group(1))
            unit = match.group(2)
            now = datetime.now()
            rt = now + (timedelta(minutes=amt) if 'min' in unit else timedelta(hours=amt))
            msg = self._extract_msg(text) or f"Lembrete após {amt} {unit}"
            self.reminders.append({'message': msg, 'datetime': rt.isoformat(), 'triggered': False})
            self._save_reminders()
            return f"⏰ Lembrete em {amt} {unit}: '{msg}'"
        return "❌ Use: 'em 5 minutos' ou 'em 1 hora'"

    def _create_simple(self, text):
        msg = self._extract_msg(text)
        if msg:
            self.reminders.append({'message': msg, 'datetime': datetime.now().isoformat(), 'triggered': False})
            self._save_reminders()
            return f"✅ Anotado: '{msg}'"
        return "❌ O que devo lembrar?"

    def _extract_msg(self, text):
        clean = text.lower()
        for w in ['lembre-me de', 'me lembre de', 'as ', 'às', 'em ', 'minutos', 'horas']:
            clean = clean.replace(w, '')
        clean = re.sub(r'\d{1,2}:\d{2}', '', clean)
        clean = re.sub(r'\d+\s*(min|h)', '', clean)
        return clean.strip() if clean.strip() else None

    def _list(self):
        active = [r for r in self.reminders if not r.get('triggered')]
        if not active: return "📭 Sem lembretes ativos"
        resp = "📋 Lembretes:\n"
        for i, r in enumerate(active[-5:], 1):
            t = datetime.fromisoformat(r['datetime']).strftime('%d/%m %H:%M')
            resp += f"{i}. [{t}] {r['message']}\n"
        return resp