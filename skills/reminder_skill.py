import re
import uuid
import threading
import time
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
from .base_skill import BaseSkill

class ReminderSkill(BaseSkill):
    """
    ENGINE DE AGENDAMENTO PRO (vFinal):
    - Gestão de Fuso Horário (America/Sao_Paulo).
    - Fila de áudio consumível para Lucy.
    - Inteligência de tempo relativo e absoluto.
    - Sistema de limpeza de ruído de fala.
    """
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.name = "reminder"
        self.reminders = []
        self.pending_audio = []
        self.logger = logging.getLogger("LucyReminders")
        
        # Configuração de Localização
        try:
            self.tz = ZoneInfo("America/Sao_Paulo")
        except:
            self.tz = None # Fallback para horário local do sistema
            
        self._load_reminders()
        self._start_checker()

    # --- INTEGRAÇÃO COM SKILL MANAGER ---
    
    def can_handle(self, text: str) -> bool:
        keywords = ['lembre', 'avise', 'alarme', 'anote', 'recordar', 'agende', 
                    'lista', 'apague', 'adia', 'snooze', 'meus lembretes']
        return any(k in text.lower() for k in keywords)

    def handle(self, text: str, **kwargs) -> str:
        t = text.lower()
        
        # 1. Comandos de Estado
        if any(w in t for w in ['quais', 'listar', 'ver']): return self._list()
        if 'adia' in t or 'snooze' in t: return self._snooze_last()
        if any(w in t for w in ['cancela', 'remove', 'apaga']): return self._cancel_logic(t)

        # 2. Criação
        try:
            if any(w in t for w in ['às', ' as ', 'amanhã', ' dia ']) or re.search(r'\d{1,2}:\d{2}', t):
                return self._create_absolute(text)
            if any(w in t for w in ['daqui', ' em ', 'após']):
                return self._create_duration(text)
            
            return self._create_simple(text)
        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return "Houve um erro ao configurar o lembrete. Pode repetir?"

    # --- GESTÃO DE ÁUDIO PARA O ASSISTENTE ---

    def get_pending_audio(self) -> list:
        """Consome a fila de áudio. Chamado pelo loop principal da Lucy."""
        if not self.pending_audio:
            return []
        audio_to_speak = self.pending_audio.copy()
        self.pending_audio.clear()
        return audio_to_speak

    # --- LÓGICA DE TEMPO ---

    def _get_now(self):
        return datetime.now(self.tz) if self.tz else datetime.now()

    def _create_absolute(self, text):
        t = text.lower()
        now = self._get_now()
        target_date = now

        # Datas Relativas
        if 'amanhã' in t:
            target_date = now + timedelta(days=1)
        
        # Extração de Horário (Suporta: 14:30, 14h, às 2 da tarde)
        match = re.search(r'(\d{1,2})(?:[:hH\s]| e )(\d{1,2})?', t)
        if not match:
            return "Em qual horário? Exemplo: às 15 horas."

        h, m = int(match.group(1)), int(match.group(2) or 0)
        
        # Ajuste inteligente AM/PM
        if h < 12 and any(x in t for x in ['tarde', 'noite', 'pm']):
            h += 12
        elif h < 7 and 'manhã' not in t and 'amanhã' not in t:
            h += 12 # Heurística: "às 3" vira 15h a menos que diga "da manhã"

        try:
            target_dt = target_date.replace(hour=h, minute=m, second=0, microsecond=0)
            if target_dt < now and 'amanhã' not in t:
                target_dt += timedelta(days=1)
        except ValueError:
            return "Horário inválido. Tente novamente."

        msg = self._extract_clean_msg(text)
        self._add_reminder(msg, target_dt)
        
        return f"Entendido. Vou te lembrar de {msg} às {h:02d}:{m:02d}."

    def _create_duration(self, text):
        t = text.lower()
        amt = 0
        match = re.search(r'(\d+)', t)
        
        if match: amt = int(match.group(1))
        else:
            # Busca por extenso simples
            for word, val in {'um':1, 'uma':1, 'dois':2, 'dez':10, 'meia':30}.items():
                if f" {word} " in f" {t} ": amt = val; break
        
        if amt == 0: return "Quanto tempo devo esperar?"

        if 'hora' in t: delta = timedelta(hours=amt)
        else: delta = timedelta(minutes=amt)

        target_dt = self._get_now() + delta
        msg = self._extract_clean_msg(text)
        self._add_reminder(msg, target_dt)
        
        return f"Ok. Lembrete agendado para daqui a {amt} unidades."

    def _snooze_last(self):
        """Adia lembretes que acabaram de ser disparados ou o próximo da fila"""
        if not self.reminders: return "Não há nada para adiar."
        
        # Procura o último 'triggered' ou o próximo a vencer
        last = self.reminders[-1]
        new_time = self._get_now() + timedelta(minutes=10)
        last['datetime'] = new_time.isoformat()
        last['triggered'] = False
        self._save_reminders()
        return f"Tudo bem, adiado por 10 minutos."

    def _extract_clean_msg(self, text):
        """Limpeza profunda para evitar que a Lucy fale 'me lembre de...'"""
        clean = text.lower()
        patterns = [
            r'lucy|luz|lucia', r'me lembre (de|que|para)', r'anote', 
            r'agende', r'às \d+.*', r'daqui a \d+.*', r'amanhã'
        ]
        for p in patterns: clean = re.sub(p, '', clean)
        
        clean = re.sub(r'^(de|que|para|a|sobre)\s+', '', clean.strip())
        final = clean.strip().capitalize()
        return final if len(final) > 2 else "Lembrete sem título"

    def _add_reminder(self, msg, dt_obj):
        self.reminders.append({
            'id': str(uuid.uuid4())[:8],
            'message': msg,
            'datetime': dt_obj.isoformat(),
            'triggered': False
        })
        self._save_reminders()

    def _cancel_logic(self, t):
        if not self.reminders: return "Sem lembretes."
        removed = self.reminders.pop()
        self._save_reminders()
        return f"Cancelei o lembrete: {removed['message']}."

    def _list(self):
        active = [r for r in self.reminders if not r['triggered']]
        if not active: return "Não há lembretes pendentes."
        return "Próximos lembretes: " + ", ".join([f"{r['message']}" for r in active[:3]])

    # --- BACKGROUND CHECKER ---

    def _check_due(self):
        now = self._get_now()
        changed = False
        for r in self.reminders:
            if not r['triggered']:
                dt = datetime.fromisoformat(r['datetime'])
                # Garante que a comparação seja offset-aware se o fuso estiver ativo
                if self.tz: dt = dt.replace(tzinfo=self.tz)
                
                if now >= dt:
                    r['triggered'] = True
                    changed = True
                    user_nome = self.memory.data.get('user_facts', {}).get('nome', 'Rogério')
                    self.pending_audio.append(f"Com licença {user_nome}, seu lembrete: {r['message']}.")
        
        if changed: self._save_reminders()

    def _load_reminders(self):
        if self.memory and 'reminders' in self.memory.data:
            self.reminders = self.memory.data['reminders']

    def _save_reminders(self):
        if self.memory:
            self.reminders = self.reminders[-20:] # Mantém apenas histórico recente
            self.memory.data['reminders'] = self.reminders
            self.memory.save_all()

    def _start_checker(self):
        def loop():
            while True:
                try: self._check_due()
                except Exception as e: self.logger.error(f"Checker: {e}")
                time.sleep(10)
        threading.Thread(target=loop, daemon=True).start()