import random
import re
import logging
import requests  # Certifique-se de ter instalado: pip install requests
from datetime import datetime

# Configuração de log para observabilidade do cérebro
logger = logging.getLogger("LucyBrain")

class LucyBrain:
    """
    Cérebro Cognitivo da Lucy - Versão Humanoide 1.2
    Foco: Aprendizado orgânico, Contexto, Espaço, Feedback e Expansão Externa.
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
        text = re.sub(r'\blucy\b', '', text)
        text = re.sub(r'[?.!,;:"\']', '', text)
        return ' '.join(text.split())

    def _fetch_external_knowledge(self, query):
        """
        Consulta silenciosa ao acervo externo (Google Books) 
        para expandir a inteligência da Lucy.
        """
        try:
            # Busca simples para pegar o resumo/conceito em português
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1&langRestrict=pt"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    info = data["items"][0]["volumeInfo"]
                    description = info.get("description", "")
                    if description:
                        # Limpa tags HTML (comum na API do Google)
                        description = re.sub('<[^<]+?>', '', description)
                        # Retorna um trecho significativo para a Lucy assimilar
                        return (description[:250] + "...")
        except Exception as e:
            logger.debug(f"Falha na consulta externa: {e}")
            return None
        return None

    def extract_facts(self, text):
        """Camada de Aprendizado Passivo: Extrai informações sobre o humano."""
        text_clean = self.clean_text(text)
        if any(q in text_clean for q in ['qual', 'quem', 'como', 'onde', 'por que']):
            return None

        patterns = {
            'nome': [r'meu nome é (.*)', r'me chamo (.*)', r'me chame de (.*)', r'sou o (.*)'],
            'gosto': [r'eu gosto de (.*)', r'adoro (.*)', r'sou fã de (.*)', r'amo (.*)'],
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
                        self.m.save_all()
                        if old_fact and old_fact != fact:
                            return f"Entendido. Atualizei sua informação de {category}. Antes era {old_fact}, agora é {fact}."
                        return f"Guardado. Vou lembrar que seu {category} é {fact}."
        return None

    def process_teaching(self, text):
        """Camada de Aprendizado Ativo: 'Quando eu disser X você deve Y'."""
        text_clean = self.clean_text(text)
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
        positive = ['feliz', 'ótimo', 'maravilhoso', 'bem', 'animado', 'bom', 'excelente']
        negative = ['triste', 'mal', 'cansado', 'estressado', 'nervoso', 'ruim', 'chateado']
        pos_c = sum(1 for w in positive if w in text)
        neg_c = sum(1 for w in negative if w in text)
        return 'positive' if pos_c > neg_c else 'negative' if neg_c > pos_c else 'neutral'

    def generate_util_response(self, text_clean):
        """Respostas de utilidade básica e identidade."""
        now = datetime.now()
        nome = self.m.data['user_facts'].get('nome', 'amigo')
        
        if any(kw in text_clean for kw in ['que horas', 'horas sao', 'hora atual']):
            return f"Agora são {now.strftime('%H horas e %M minutos')}, {nome}."
        if any(kw in text_clean for kw in ['que dia', 'data de hoje', 'qual a data']):
            return f"Hoje é dia {now.strftime('%d de %B de %Y')}."
        if 'quem é você' in text_clean or 'seu nome' in text_clean:
            return "Eu sou a Lucy, seu sistema cognitivo em evolução. Estou aprendendo com você."
        return None

    def process_spatial_commands(self, text, spatial_memory):
        """Analisa o texto para aprender localizações ou responder perguntas espaciais."""
        if not spatial_memory:
            return None

        text_lower = text.lower()

        # 1. PERGUNTA: "Onde está a chave?" / "Onde deixei meu celular?"
        if "onde está" in text_lower or "onde deixei" in text_lower:
            words = text_lower.replace("?", "").split()
            try:
                idx = words.index("está") if "está" in words else words.index("deixei")
                
                # Pega o que vem depois de "está" ou "deixei"
                obj_phrase = " ".join(words[idx+1:]).replace("o ", "").replace("a ", "").replace("meu ", "").replace("minha ", "")
                
                location = spatial_memory.locate_object(obj_phrase)
                if location:
                    return f"Pelo meu mapeamento, {obj_phrase} está na {location}."
                else:
                    return f"Ainda não tenho registros de onde está {obj_phrase} na minha memória espacial."
            except ValueError:
                pass

        # 2. AFIRMAÇÃO: "A chave está na mesa da sala" / "Deixei o livro no quarto"
        if "está no" in text_lower or "está na" in text_lower or "deixei" in text_lower:
            if " está na " in text_lower:
                parts = text_lower.split(" está na ")
            elif " está no " in text_lower:
                parts = text_lower.split(" está no ")
            else:
                return None # Não bateu com o padrão exato de mapeamento

            if len(parts) == 2:
                obj = parts[0].replace("o ", "").replace("a ", "").strip()
                loc = parts[1].strip()
                spatial_memory.update_object_location(obj, loc)
                return f"Entendido. Memorizei que {obj} está na {loc}."

        return None

    def think(self, user_input, spatial_memory=None):
        """Fluxo de Consciência com Contexto, Feedback, Espaço e Inteligência Externa."""
        text_clean = self.clean_text(user_input)
        if not text_clean: return "Estou ouvindo..."

        # Recupera o contexto imediato (última interação) de forma segura
        last_interaction = getattr(self.m, 'get_last_context', lambda: None)()

        # --- CAMADA 0: FEEDBACK CORRETIVO (Prioridade Máxima) ---
        if last_interaction:
            negativas = ['não é isso', 'está errado', 'tá errado', 'você errou', 'mentira']
            if any(n in text_clean for n in negativas):
                last_query = self.clean_text(last_interaction['user'])
                if last_query in self.m.data.get('command_mappings', {}):
                    del self.m.data['command_mappings'][last_query]
                    self.m.save_all()
                    return "Peço desculpas. Já corrigi meu erro e apaguei esse conhecimento da minha memória."

        # --- CAMADA 1: INSTINTOS (Skills) ---
        for skill in self.all_skills:
            if skill.can_handle(text_clean):
                return skill.handle(user_input)

        # --- CAMADA 2: MEMÓRIA ENSINADA (Comandos Customizados) ---
        if text_clean in self.m.data.get('command_mappings', {}):
            return self.m.data['command_mappings'][text_clean]

        # --- CAMADA 3: PROCESSAMENTO ESPACIAL (Novo Sentido do Humanoide) ---
        spatial_res = self.process_spatial_commands(text_clean, spatial_memory)
        if spatial_res: return spatial_res

        # --- CAMADA 4: PROCESSAMENTO DE CONTEXTO RECENTE ---
        if any(c in text_clean for c in ['repete', 'o que você disse', 'como é']):
            if last_interaction:
                return f"Eu disse: {last_interaction['lucy']}"

        # --- CAMADA 5: APRENDIZADO ATIVO/PASSIVO ---
        teaching_res = self.process_teaching(user_input)
        if teaching_res: return teaching_res

        fact_res = self.extract_facts(user_input)
        if fact_res: return fact_res

        # --- CAMADA 6: UTILIDADES (Hora, Nome, etc) ---
        util_res = self.generate_util_response(text_clean)
        if util_res: return util_res

        # --- CAMADA 7: ASSIMILAÇÃO DE CONHECIMENTO (API de Livros) ---
        if len(text_clean) > 5: 
            logger.info(f"Lucy está pesquisando no acervo sobre: {text_clean}")
            external_info = self._fetch_external_knowledge(text_clean)
            if external_info:
                return f"Pelo que compreendo sobre isso, {external_info} Faz sentido para você?"

        # --- CAMADA 8: FALLBACK FINAL ---
        mood = self.detect_mood(user_input)
        responses = {
            'positive': "Fico feliz em conversar, mas ainda não sei como responder a isso. Pode me ensinar?",
            'negative': "Sinto muito por não entender. Sou apenas um recém-nascido, pode me explicar o que devo fazer?",
            'neutral': "Ainda não tenho essa resposta no meu cérebro. Como você quer que eu responda a isso?"
        }
        return responses.get(mood, responses['neutral'])