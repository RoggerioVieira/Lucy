import sys
import random
import threading
import time
import logging
from datetime import datetime
from queue import Queue

# Importamos as tuas configurações
try:
    from config import BASE_DIR, DATA_DIR, MEMORY_CONFIG, SKILLS_CONFIG, LUCY_CONFIG
except ImportError:
    print("❌ Erro: config.py não encontrado ou com erros. Verifique o arquivo.")
    sys.exit(1)

# --- CONFIGURAÇÃO DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "lucy_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LucyCore")

class Lucy:
    """
    ASSISTENTE LUCY - VERSÃO DEFINITIVA
    Utiliza caminhos absolutos do config.py e sistema de mensageria assíncrona.
    """
    
    def __init__(self):
        self._start_time = time.time()
        self._is_speaking = False  # Previne colisão de áudio
        self.running = False
        self.conversation_count = 0
        self.msg_queue = Queue()   # Fila de lembretes e avisos
        
        logger.info(f"🚀 Iniciando Lucy em {BASE_DIR}")
        
        # 1. Sistema de Memória (Camada de Dados)
        try:
            from core.lucy_memory import LucyMemory
            # Passamos o dicionário de caminhos que você definiu
            self.memory = LucyMemory(config=MEMORY_CONFIG)
            self.user_name = self.memory.data.get("user_facts", {}).get("nome", "amigo")
        except Exception as e:
            logger.critical(f"Falha ao carregar persistência: {e}")
            sys.exit(1)

        # 2. Hardware e Inteligência
        from core.lucy_voice import LucyVoice
        from core.lucy_brain import LucyBrain
        self.voice = LucyVoice(self.user_name)
        self.brain = LucyBrain(self.memory)
        
        # 3. Gerenciamento de Skills (Modulável)
        self.skill_manager = None
        self.reminder_skill = None
        self._init_skills_system()

        self._init_templates()

    def _init_skills_system(self):
        """Inicializa skills baseado no seu SKILLS_CONFIG"""
        try:
            from skills.skill_manager import SkillManager
            self.skill_manager = SkillManager(self.memory)
            
            # Carrega referência direta apenas se habilitado no seu config
            if SKILLS_CONFIG['reminder']['enabled']:
                self.reminder_skill = self.skill_manager._get_skill_instance("reminder")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar SkillManager: {e}. Tentando fallback direto...")
            # Fallback de segurança para Reminder
            if SKILLS_CONFIG['reminder']['enabled']:
                try:
                    from skills.reminder_skill import ReminderSkill
                    self.reminder_skill = ReminderSkill(self.memory)
                except:
                    logger.error("❌ Falha total no sistema de lembretes.")

    def _init_templates(self):
        hour = datetime.now().hour
        period = "Bom dia" if 5 <= hour < 12 else "Boa tarde" if 12 <= hour < 18 else "Boa noite"
        self.greetings = [
            f"{period}, {self.user_name}! Estou pronta.",
            f"Oi {self.user_name}, Lucy online. Como posso ajudar?",
            f"Sistemas carregados em {LUCY_CONFIG['timezone']}. O que temos para hoje?"
        ]
        self.farewells = ["Encerrando por agora. Até logo!", "Lucy entrando em standby. Tchau!"]

    def speak(self, text):
        """Bloqueia a flag de fala para evitar interrupções de lembretes"""
        if not text: return
        self._is_speaking = True
        try:
            self.voice.speak(text)
        finally:
            self._is_speaking = False

    # --- WATCHER DE LEMBRETES ---

    def _start_reminder_watcher(self):
        """Thread que monitora a skill de lembretes"""
        if not self.reminder_skill: return

        def watcher_loop():
            logger.info("🔔 Monitor de lembretes ativo.")
            while self.running:
                try:
                    # Coleta o que a skill produziu e joga na fila
                    pending = self.reminder_skill.get_pending_audio()
                    for msg in pending:
                        self.msg_queue.put(msg)
                except Exception as e:
                    logger.debug(f"Watcher loop noise: {e}")
                time.sleep(LUCY_CONFIG['watcher_interval'])

        threading.Thread(target=watcher_loop, daemon=True).start()

    # --- LOOP PRINCIPAL ---

    def run(self):
        self.running = True
        self._start_reminder_watcher()
        self.speak(random.choice(self.greetings))

        try:
            while self.running:
                # A. PROCESSA FILA ASSÍNCRONA (Avisos/Lembretes)
                while not self.msg_queue.empty():
                    if not self._is_speaking:
                        msg = self.msg_queue.get()
                        logger.info(f"🔔 Disparando lembrete: {msg}")
                        self.speak(f"Com licença, {self.user_name}. {msg}")
                    else:
                        time.sleep(0.5)
                        break

                # B. ESCUTA USUÁRIO
                user_input = self.voice.listen()
                if not user_input: continue

                # C. COMANDOS DE SISTEMA
                if self._handle_system_commands(user_input): continue

                # D. EXECUÇÃO DO CÉREBRO
                start_time = time.time()
                self._execute_pipeline(user_input)
                
                # Check de performance baseado no seu threshold (1500ms)
                duration = (time.time() - start_time) * 1000
                if duration > LUCY_CONFIG['slow_response_threshold']:
                    logger.warning(f"🐢 Resposta lenta: {duration:.0f}ms")

        except KeyboardInterrupt:
            self._shutdown()

    def _execute_pipeline(self, user_input):
        response = None
        
        # 1. Skills
        if self.skill_manager:
            response, _ = self.skill_manager.find_and_execute(user_input)
        elif self.reminder_skill and self.reminder_skill.can_handle(user_input):
            response = self.reminder_skill.handle(user_input)

        # 2. Brain
        if not response:
            response = self.brain.think(user_input)

        self.speak(response or "Não consegui processar isso, pode repetir?")
        self.conversation_count += 1
        
        # Autosave baseado no seu config.py
        if self.conversation_count % LUCY_CONFIG['save_interval'] == 0:
            self._background_save()

    def _handle_system_commands(self, text):
        t = text.lower()
        if any(w in t for w in ['sair', 'tchau', 'desligar']):
            self._shutdown()
            return True
        if 'status' in t:
            active_reminders = len([r for r in self.reminder_skill.reminders if not r.get('triggered')]) if self.reminder_skill else 0
            self.speak(f"Estou operando normalmente. Temos {active_reminders} lembretes pendentes.")
            return True
        return False

    def _background_save(self):
        logger.info("💾 Executando autosave em background...")
        threading.Thread(target=self.memory.save_all, daemon=True).start()

    def _shutdown(self):
        logger.info("🛑 Desligando Lucy...")
        self.running = False
        self.speak(random.choice(self.farewells))
        self.memory.save_all()
        self.voice.stop()
        sys.exit(0)

if __name__ == "__main__":
    Lucy().run()