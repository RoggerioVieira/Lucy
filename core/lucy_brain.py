from datetime import datetime
import random
import re
import logging

# Configuração de log para observabilidade do cérebro
logger = logging.getLogger("LucyBrain")

class LucyBrain:
    """
    Cérebro Cognitivo da Lucy - Versão Humanoide 1.0
    Foco: Aprendizado orgânico, extração de fatos e execução de instintos (skills).
    """

    def __init__(self, memory_obj):
        self.m = memory_obj
        self.all_skills = []
        self._load_neural_skills()

    def _load_neural_skills(self):
        """Carrega os 'instintos' (skills) de forma resiliente."""
        try:
            from skills import get_all_skills
            self.all_skills = get_all_skills(self.m)
            logger.info(f"✅ Skills/Instintos carregados: {[s.name for s in self.all_skills]}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao carregar plugin de skills: {e}")
            # Modo de Emergência: Tenta carregar o Reminder diretamente
            try:
                from skills.reminder_skill import ReminderSkill
                self.all_skills.append(ReminderSkill(self.m))
                logger.warning("🛠️ Modo de Emergência: Apenas ReminderSkill ativo.")
            except:
                logger.critical("🚨 Falha total no sistema de skills.")

    def clean_text(self, text):
        """Normalização sensorial: Prepara o texto para o processamento neural."""
        if not text: return ""
        text = str(text).strip().lower()
        
        # Remove gatilhos de ativação (Lucy) e caracteres especiais que causam ruído
        text = re.sub(r'\blucy\b', '', text)
        text = re.sub(r'[?.!,;:"\']', '', text)
        
        return ' '.join(text.split())

    def extract_facts(self, text):
        """Camada de Aprendizado Passivo: Extrai informações sobre o humano."""
        text_clean = self.clean_text(text)
        
        # Filtro de segurança: Não extrai fatos de perguntas
        if any(q in text_clean for q in ['qual', 'quem', 'como', 'onde', 'por que']):
            return None

        patterns = {
            'nome': [r'meu nome é (.*)', r'me chamo (.*)', r'me chame de (.*)', r'sou o (.*)'],
            'gosto': [r'eu gosto de (.*)', r'adoro (.*)', r'sou fã de (.*)'],
            'trabalho': [r'trabalho com (.*)', r'sou (.*) profissional', r'minha profissão é (.*)']
        }

        for category, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, text_clean)
                if match:
                    fact = match.group(1).strip()
                    if 2 < len(fact) < 50:
                        old_fact = self.m.data['user_facts'].get(category)
                        self.m.data['user_facts'][category] = fact
                        self.m.save_all() # Persistência imediata no OneDrive
                        
                        if old_fact and old_fact != fact:
                            return f"Entendido. Atualizei sua informação de {category}. Antes era {old_fact}, agora é {fact}."
                        return f"Guardado. Vou lembrar que seu {category} é {fact}."
        return None

    def process_teaching(self, text):
        """Camada de Aprendizado Ativo: 'Quando eu disser X você deve Y'."""
        text_clean = self.clean_text(text)
        
        # Regex flexível para capturar o ensinamento
        pattern = r"quando eu (?:disser|falar)\s+(.+?)\s+(?:você deve|voce deve|voce|você)\s+(.+)"
        match = re.search(pattern, text_clean)
        
        if match:
            trigger = match.group(1).strip()
            action = match.group(2).strip()
            self.m.data['command_mappings'][trigger] = action
            self.m.save_all()
            return f"Sinapse criada. Sempre que disser '{trigger}', eu vou '{action}'."
        return None

    def detect_mood(self, text):
        """Analisa o estado emocional do input."""
        text = self.clean_text(text)
        positive = ['feliz', 'ótimo', 'maravilhoso', 'bem', 'animado', 'bom']
        negative = ['triste', 'mal', 'cansado', 'estressado', 'nervoso', 'ruim']
        
        pos_c = sum(1 for w in positive if w in text)
        neg_c = sum(1 for w in negative if w in text)

        return 'positive' if pos_c > neg_c else 'negative' if neg_c > pos_c else 'neutral'

    def generate_util_response(self, text_clean):
        """Respostas de utilidade básica (Relógio Interno)."""
        now = datetime.now()
        nome = self.m.data['user_facts'].get('nome', 'amigo')
        
        if any(kw in text_clean for kw in ['que horas', 'horas sao', 'hora atual']):
            return f"Agora são {now.strftime('%H horas e %M minutos')}, {nome}."
        
        if any(kw in text_clean for kw in ['que dia', 'data de hoje', 'qual a data']):
            return f"Hoje é dia {now.strftime('%d de %B de %Y')}."
            
        if 'quem é você' in text_clean or 'seu nome' in text_clean:
            return "Eu sou a Lucy, seu sistema cognitivo em evolução. Estou aprendendo com você."

        return None

    def think(self, user_input):
        """Fluxo de Consciência: Onde o input vira ação ou aprendizado."""
        text_clean = self.clean_text(user_input)
        if not text_clean: return "Estou ouvindo..."

        logger.info(f"🧠 Processando input: '{text_clean}'")

        # 1. INSTINTOS (Skills): Verificando se é uma ação física/complexa
        for skill in self.all_skills:
            if skill.can_handle(text_clean):
                logger.debug(f"Skill acionada: {skill.name}")
                return skill.handle(user_input)

        # 2. MEMÓRIA ENSINADA: Verificando comandos customizados
        if text_clean in self.m.data['command_mappings']:
            return self.m.data['command_mappings'][text_clean]

        # 3. APRENDIZADO ATIVO: O usuário está me ensinando algo agora?
        teaching_res = self.process_teaching(user_input)
        if teaching_res: return teaching_res

        # 4. APRENDIZADO PASSIVO: O usuário está me contando algo sobre ele?
        fact_res = self.extract_facts(user_input)
        if fact_res: return fact_res

        # 5. UTILIDADES E CONTEXTO: Hora, Data, Quem sou eu?
        util_res = self.generate_util_response(text_clean)
        if util_res: return util_res

        # 6. RESPOSTA SOBRE O USUÁRIO (Contextual)
        if any(q in text_clean for q in ['meu nome', 'como eu me chamo', 'quem sou eu']):
            nome = self.m.data['user_facts'].get('nome')
            return f"Você é {nome}." if nome else "Ainda não guardei seu nome. Como posso te chamar?"

        # 7. FALLBACK (Curiosidade do Recém-Nascido)
        mood = self.detect_mood(user_input)
        responses = {
            'positive': "Fico feliz, mas ainda não sei como responder a isso. Pode me ensinar?",
            'negative': "Sinto muito. Eu ainda não entendo o que isso significa. O que eu deveria fazer?",
            'neutral': "Ainda não tenho essa informação no meu cérebro. Como você quer que eu responda?"
        }
        return responses[mood]