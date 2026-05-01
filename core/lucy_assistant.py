import sys
import random
import threading
import time
import logging
from datetime import datetime
from queue import Queue

# Importações do Sistema Cognitivo
from core.memory_system.episodic import EpisodicMemory
from core.memory_system.social import SocialCortex
from core.memory_system.working_memory import WorkingMemory  
from core.memory_system.spatial import SpatialMemory  
from core.memory_system.consolidation import SleepCycle      

# Importação das configurações
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
        logging.FileHandler(DATA_DIR / "lucy_system.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LucyCore")

class Lucy:
    """
    ASSISTENTE LUCY - VERSÃO HUMANOIDE (Com suporte Híbrido Nuvem/Local)
    Gere voz, inteligência e memória biológica de forma assíncrona.
    """
    
    def __init__(self):
        # 1. Camada de Memória Cognitiva Completa
        self.episodic_memory = EpisodicMemory()
        self.social_cortex = SocialCortex()
        self.working_memory = WorkingMemory(capacity=5)  # RAM do humanoide
        self.spatial_memory = SpatialMemory()            # Mapa físico 3D
        
        # 2. Estado do Sistema
        self._start_time = time.time()
        self._is_speaking = False  
        self.running = False
        self.conversation_count = 0
        self.msg_queue = Queue()   # Fila para notificações e lembretes
        
        logger.info(f"🚀 Inicializando sistemas cognitivos em {BASE_DIR}")
        
        # 3. Persistência de Dados (Memória de Fatos)
        try:
            from core.lucy_memory import LucyMemory
            self.memory = LucyMemory()
            self.user_name = self.memory.data.get("user_facts", {}).get("nome", "amigo")
        except Exception as e:
            logger.critical(f"Falha ao carregar persistência de dados: {e}")
            sys.exit(1)

        # 4. Interface Sensorial e Processamento
        from core.lucy_voice import LucyVoice
        self.voice = LucyVoice(self.user_name)
        
        # --- O INTERRUPTOR DE CÉREBROS (NUVEM vs LOCAL) ---
        try:
            from config import USE_CLOUD_BRAIN, GEMINI_API_KEY
            if USE_CLOUD_BRAIN:
                from core.lucy_brain_cloud import LucyBrainCloud
                self.brain = LucyBrainCloud(self.memory, api_key=GEMINI_API_KEY)
                logger.info("☁️ Conectado ao Cérebro de Nuvem (Gemini).")
            else:
                from core.lucy_brain import LucyBrain
                self.brain = LucyBrain(self.memory)
                logger.info("🧠 Usando Cérebro Local Clássico (Regex).")
        except ImportError:
            # Caso dê algum erro ou as variáveis não existam no config.py, volta para o antigo
            from core.lucy_brain import LucyBrain
            self.brain = LucyBrain(self.memory)
            logger.warning("⚠️ Usando Cérebro Local (Fallback Automático).")
        # ---------------------------------------------------
        
        # 5. Módulo de Competências (Skills)
        self.skill_manager = None
        self.reminder_skill = None
        self._init_skills_system()

        self._init_templates()

    def _init_skills_system(self):
        """Carrega o gestor de competências e o sistema de lembretes"""
        try:
            from skills.skill_manager import SkillManager
            self.skill_manager = SkillManager(self.memory)
            
            if SKILLS_CONFIG['reminder']['enabled']:
                self.reminder_skill = self.skill_manager._get_skill_instance("reminder")
        except Exception as e:
            logger.warning(f"⚠️ Aviso: SkillManager indisponível ({e}). Usando modo reduzido.")

    def _init_templates(self):
        """Saudações baseadas no tempo e contexto"""
        hour = datetime.now().hour
        period = "Bom dia" if 5 <= hour < 12 else "Boa tarde" if 12 <= hour < 18 else "Boa noite"
        self.greetings = [
            f"{period}, {self.user_name}! Sistemas cognitivos ativos.",
            f"Oi {self.user_name}, Lucy online. Como posso ajudar o meu humano hoje?",
            f"Ambiente verificado em {LUCY_CONFIG['timezone']}. Estou pronta para interagir."
        ]
        self.farewells = ["A hibernar sistemas. Até logo!", "Lucy em standby. Tchau!"]

    def speak(self, text):
        """Executa a fala garantindo que não há sobreposição com notificações"""
        if not text: return
        self._is_speaking = True
        try:
            self.voice.speak(text)
        finally:
            self._is_speaking = False

    def _start_reminder_watcher(self):
        """Monitoriza eventos em tempo real (Lembretes/Alertas)"""
        if not self.reminder_skill: return

        def watcher_loop():
            logger.info("🔔 Monitor sensorial de tempo ativo.")
            while self.running:
                try:
                    pending = self.reminder_skill.get_pending_audio()
                    for msg in pending:
                        self.msg_queue.put(msg)
                except Exception as e:
                    logger.debug(f"Erro no watcher: {e}")
                time.sleep(LUCY_CONFIG['watcher_interval'])

        threading.Thread(target=watcher_loop, daemon=True).start()

    def run(self):
        """Inicia o loop vital da Lucy"""
        self.running = True
        self._start_reminder_watcher()
        self.speak(random.choice(self.greetings))

        try:
            while self.running:
                # 1. Atender notificações prioritárias (Fila de Mensagens)
                while not self.msg_queue.empty():
                    if not self._is_speaking:
                        msg = self.msg_queue.get()
                        logger.info(f"🔔 Evento disparado: {msg}")
                        self.speak(f"Com licença, {self.user_name}. {msg}")
                    else:
                        break # Aguarda a fala atual terminar

                # 2. Perceção (Escuta o ambiente)
                user_input = self.voice.listen()
                if not user_input: continue

                # 3. Comandos Críticos de Sistema
                if self._handle_system_commands(user_input): continue

                # 4. Processamento e Ação
                start_time = time.time()
                self._execute_pipeline(user_input)
                
                # Monitorização de Latência Cognitiva
                duration = (time.time() - start_time) * 1000
                if duration > LUCY_CONFIG['slow_response_threshold']:
                    logger.warning(f"🐢 Latência cognitiva alta: {duration:.0f}ms")

        except KeyboardInterrupt:
            self._shutdown()

    def _execute_pipeline(self, user_input):
        """Decide se usa uma Skill ou o Cérebro geral"""
        response = None
        
        # Prioridade 1: Competências específicas (As skills locais continuam funcionando!)
        if self.skill_manager:
            response, _ = self.skill_manager.find_and_execute(user_input)

        # Prioridade 2: Processamento Neural (Brain)
        if not response:
            try:
                # Tenta usar o Cérebro de Nuvem passando TODOS os contextos
                response = self.brain.think(
                    user_input, 
                    spatial_memory=self.spatial_memory,
                    working_memory=self.working_memory,
                    social_cortex=self.social_cortex
                )
            except TypeError:
                # Trava de segurança: Se estivermos usando o Cérebro Local Clássico,
                # ele aceita menos parâmetros, então chamamos do jeito antigo.
                response = self.brain.think(user_input, spatial_memory=self.spatial_memory)

        final_response = response or "A minha rede neural não gerou uma resposta. Pode reformular?"
        
        # --- ATUALIZAÇÃO SENSORIAL E DE CURTO PRAZO ---
        self.working_memory.add_interaction(user_input, final_response)
        
        self.speak(final_response)
        
        # --- REGISTO DE MEMÓRIA EPISÓDICA (Longo Prazo) ---
        self.episodic_memory.create_episode(
            event_type="dialogue",
            agent=self.user_name,
            location="environment_alpha", # Localização base
            content={"input": user_input, "output": final_response},
            valence=0.5 
        )
        self.social_cortex.update_interaction(self.user_name)
        
        self.conversation_count += 1
        if self.conversation_count % LUCY_CONFIG['save_interval'] == 0:
            self._background_save()

    def _handle_system_commands(self, text):
        t = text.lower()
        if any(w in t for w in ['sair', 'tchau', 'desligar']):
            self._shutdown()
            return True
            
        if 'status' in t:
            self.speak("Sistemas operacionais. Memória episódica, espacial e córtex social ativos.")
            return True
            
        # --- Comando de Sono (Consolidação) ---
        if any(w in t for w in ['vá dormir', 'vai dormir', 'hibernar']):
            self.speak("Entrando em ciclo de sono profundo para consolidar memórias. Boa noite!")
            
            # Inicia o ciclo de sono bloqueando a thread principal rapidamente
            sleep_cycle = SleepCycle(self.episodic_memory, self.social_cortex, self.memory)
            apagadas = sleep_cycle.go_to_sleep()
            
            self.speak(f"Acordei. Limpei {apagadas} memórias inúteis da minha mente.")
            return True
            
        return False

    def _background_save(self):
        """Consolidação de memória em background"""
        logger.info("💾 Consolidando memórias...")
        threading.Thread(target=self.memory.save_all, daemon=True).start()
        # Salva o mapa mental em background
        threading.Thread(target=self.spatial_memory.save, daemon=True).start()

    def _shutdown(self):
        logger.info("🛑 Hibernando sistemas...")
        self.running = False
        self.speak(random.choice(self.farewells))
        
        # --- Consolidação final antes de desligar ---
        logger.info("💤 Executando ciclo de sono antes de desligar a energia...")
        sleep_cycle = SleepCycle(self.episodic_memory, self.social_cortex, self.memory)
        sleep_cycle.go_to_sleep()
        
        # Salva todos os estados cognitivos
        self.memory.save_all()
        self.social_cortex.save() 
        self.spatial_memory.save()
        
        self.voice.stop()
        sys.exit(0)

if __name__ == "__main__":
    try:
        Lucy().run()
    except Exception as e:
        logger.error(f"Kernel Panic: {e}")