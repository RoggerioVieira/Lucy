from datetime import datetime
import random
from collections import Counter
import re

class LucyBrain:
    """Cérebro da Lucy - processamento de linguagem e lógica"""

    def __init__(self, memory_obj):
        self.m = memory_obj

    def clean_text(self, text):
        """Limpa texto: remove aspas, espaços, normaliza"""
        if not text:
            return ""
        text = str(text).strip()
        text = text.replace('"', '').replace("'", "")
        text = ' '.join(text.split())
        return text.lower().strip()

    def extract_facts(self, text):
        """Extrai fatos pessoais com validação rigorosa"""
        original_text = text
        text = self.clean_text(text)

        if '?' in original_text:
            return None

        question_starts = ['qual', 'quem', 'onde', 'quando', 'como', 'por que', 
                          'quanto', 'o que', 'quem sou', 'quem e voce']
        text_start = text[:20]
        if any(q in text_start for q in question_starts):
            return None

        patterns = {
            'nome': [
                'meu nome é', 'me chamo', 'pode me chamar de', 
                'sou o', 'sou a', 'meu apelido é', 'me chame de',
                'chame-me de', 'pode me chamar'
            ],
            'gosto': ['eu gosto de', 'adoro', 'sou fã de', 'amo', 'prefiro'],
            'nao_gosto': ['não gosto de', 'odeio', 'evito', 'não suporto'],
            'trabalho': [
                'trabalho com', 'trabalho como', 'minha profissão é', 
                'meu trabalho é', 'sou programador', 'sou engenheiro',
                'sou médico', 'sou professor', 'sou designer',
                'sou ', 'trabalho na area de', 'atuocomo'
            ],
            'rotina': ['sempre faço', 'costumo', 'minha rotina é', 'toda vez que'],
            'familia': ['meu pai', 'minha mãe', 'tenho um cachorro', 'tenho um gato', 'meu filho'],
            'hobbies': ['meu hobby é', 'gosto de fazer', 'nas horas vagas', 'me divirto com'],
            'comida': ['minha comida favorita é', 'adoro comer', 'gosto de comer'],
        }

        found_facts = []
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text:
                    start = text.find(keyword) + len(keyword)
                    rest = text[start:]

                    end_pos = len(rest)
                    for delim in ['.', ',', '!', '?', ';']:
                        if delim in rest:
                            end_pos = min(end_pos, rest.find(delim))

                    fact = rest[:end_pos].strip()

                    if not fact or len(fact) < 2 or len(fact) > 50:
                        continue
                    if fact in ['eu', 'voce', 'lucy', 'vc', 'tu', 'ele', 'ela', '']:
                        continue
                    if '?' in fact:
                        continue
                    small_words = ['o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em', 'no', 'na']
                    if fact in small_words:
                        continue

                    old_fact = self.m.data['user_facts'].get(category)
                    self.m.data['user_facts'][category] = fact
                    found_facts.append((category, fact, old_fact))
                    break

        if found_facts:
            cat, fact, old = found_facts[0]
            if old and old != fact:
                return f"Ah! Então agora seu {cat} é {fact}? Antes era {old}. Anotado!"
            return f"Entendi! Vou lembrar que seu {cat} é: {fact}"

        return None

    def detect_mood(self, text):
        """Detecta humor"""
        text = self.clean_text(text)

        positive = ['feliz', 'ótimo', 'maravilhoso', 'excelente', 'bem', 'animado', 'alegre', 'contente']
        negative = ['triste', 'mal', 'cansado', 'estressado', 'nervoso', 'deprimido', 'frustrado']
        excited = ['super', 'incrível', 'fantástico', 'uau', 'empolgado', 'animadíssimo']
        tired = ['exausto', 'morto', 'sem energia', 'só quero dormir', 'muito cansado']

        pos_c = sum(1 for w in positive if w in text)
        neg_c = sum(1 for w in negative if w in text)
        exc_c = sum(1 for w in excited if w in text)
        tir_c = sum(1 for w in tired if w in text)

        if exc_c > 0: return 'excited'
        if tir_c > 0: return 'tired'
        if pos_c > neg_c: return 'positive'
        if neg_c > pos_c: return 'negative'
        return 'neutral'

    def get_mood_response(self, mood):
        """Retorna apenas resposta de humor"""
        responses = {
            'positive': ["Que ótimo ouvir isso! 😊", "Adoro quando você está bem!", "Essa energia é contagiante!"],
            'negative': ["Sinto muito que esteja assim. 💙", "Parece que foi um dia difícil.", "Estou aqui para você."],
            'excited': ["Ebaa! 🎉", "Que notícia boa!", "Estou toda arrepiada!"],
            'tired': ["Parece que precisa de descanso... 😴", "Que tal uma pausa?"],
            'neutral': []
        }
        return random.choice(responses.get(mood, [])) if responses.get(mood) else ""

    def classify_command(self, text):
        """Classifica comando"""
        text = self.clean_text(text)

        categories = {
            'busca': ['pesquise', 'o que é', 'quem foi', 'como faz', 'onde fica'],
            'tempo': ['clima', 'temperatura', 'previsão', 'vai chover', 'como esta o tempo'],
            'lembrete': ['lembre', 'anote', 'adicione', 'lista', 'nao esqueca'],
            'musica': ['tocar', 'musica', 'playlist', 'som'],
            'sistema': ['abrir', 'fechar', 'executar', 'programa'],
            'pessoal': ['meu nome', 'quem sou eu', 'sobre mim', 'qual meu nome'],
            'lucy': ['quem é você', 'seu nome', 'voce é', 'lucy', 'quem e lucy'],
            'hora': ['que horas', 'hora atual', 'me diga as horas', 'horas sao'],
            'data': ['que dia é hoje', 'data de hoje', 'qual a data'],
            'piada': ['piada', 'conte algo engracado', 'me faca rir'],
            'ensino': ['quando eu disser', 'aprenda', 'quando eu falar', 'quando eu disser'],
        }

        for cat, kws in categories.items():
            if any(kw in text for kw in kws):
                return cat
        return 'outro'

    def check_contextual_memory(self, text):
        """Verifica memória para respostas contextuais"""
        text_clean = self.clean_text(text)

        name_queries = [
            'meu nome', 'qual meu nome', 'como eu me chamo', 
            'quem sou eu', 'qual é o meu nome', 'me chamo'
        ]
        if any(q in text_clean for q in name_queries):
            if 'nome' in self.m.data['user_facts']:
                nome = self.m.data['user_facts']['nome']
                return f"Seu nome é {nome}!"
            return "Ainda não sei seu nome. Como você se chama?"

        if any(q in text_clean for q in ['o que voce sabe', 'o que você sabe', 'o que sabe sobre mim']):
            facts = self.m.data['user_facts']
            if facts:
                response = "Sei isso sobre você:"
                for key, value in list(facts.items())[:5]:
                    response += f"• {key}: {value}"
                return response.strip()
            return "Ainda estou te conhecendo! Me conta algo sobre você?"

        hour = datetime.now().hour
        if str(hour) in self.m.data['routines']:
            frequent = Counter(self.m.data['routines'][str(hour)]).most_common(1)
            if frequent and frequent[0][1] >= 2:
                cmd, count = frequent[0]
                greetings = ['bom dia', 'boa tarde', 'boa noite', 'oi', 'ola', 'e ai']
                if any(g in text_clean for g in greetings):
                    return f"{text.capitalize()}! Costumo te ver pedindo {cmd} neste horário. Posso ajudar?"

        return None

    def process_teaching(self, text):
        """Processa ensino com regex melhorado e limpeza"""
        text_clean = self.clean_text(text)

        patterns = [
            r'quando eu disser\s+(.+?)\s+voce deve\s+(.+)',
            r'quando eu falar\s+(.+?)\s+voce\s+(.+)',
            r'quando eu disser\s+(.+?)\s+vc deve\s+(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                trigger = self.clean_text(match.group(1))
                action = self.clean_text(match.group(2))

                trigger = trigger.replace('aspas', '').replace('quotes', '').strip()

                if trigger and action and len(trigger) > 1:
                    keys_to_remove = []
                    for existing_trigger in list(self.m.data['command_mappings'].keys()):
                        existing_clean = self.clean_text(existing_trigger)
                        if trigger in existing_clean or existing_clean in trigger:
                            keys_to_remove.append(existing_trigger)

                    for key in keys_to_remove:
                        del self.m.data['command_mappings'][key]

                    self.m.data['command_mappings'][trigger] = action
                    return f"✅ Aprendido! Quando você disser '{trigger}', vou: {action}"

        return None

    def check_learned_command(self, text):
        """Verifica comandos aprendidos - PRIORIDADE PARA MATCH EXATO"""
        text_clean = self.clean_text(text)

        for trigger, action in self.m.data['command_mappings'].items():
            trigger_clean = self.clean_text(trigger)

            if trigger_clean == text_clean:
                return f"🎯 {action}"

            if trigger_clean in text_clean and len(text_clean) < len(trigger_clean) + 10:
                words_after = text_clean.replace(trigger_clean, '').strip()
                if not words_after or words_after in ['por favor', 'agora', 'ja', 'logo']:
                    return f"🎯 {action}"

        return None

    def generate_response(self, user_input, command_type):
        """Gera resposta baseada no comando"""
        now = datetime.now()
        nome = self.m.data['user_facts'].get('nome', 'amigo')

        responses = {
            'hora': f"Agora são {now.strftime('%H:%M')}, {nome}.",
            'data': f"Hoje é {now.strftime('%d de %B de %Y')}.",
            'piada': random.choice([
                "Por que o computador foi ao médico? Porque estava com vírus! 🦠",
                "O que o zero disse para o oito? Que cinto bonito! 👗",
                "Por que o livro de matemática ficou triste? Tinha muitos problemas. 📚",
            ]),
            # RESPOSTA ALTERADA - sem data de criação e contador
            'lucy': random.choice([
                "Sou a Lucy! Sua assistente pessoal. Estou sempre aprendendo com você! 🤖",
                "Meu nome é Lucy! Adoro conversar com você e aprender coisas novas!",
                "Sou Lucy! Uma assistente que fica mais inteligente a cada conversa!",
                "Prazer! Sou a Lucy. Estou aqui para ajudar e aprender com você!"
            ]),
            'busca': "Posso pesquisar isso! (Integração web em breve)",
            'tempo': "Deixe-me verificar... (API de clima em desenvolvimento)",
            'lembrete': "Anotado! 📌",
            'musica': "🎵 Tocando música... (Spotify integration coming soon)",
            'sistema': "Executando comando...",
            'ensino': "Use: 'Quando eu disser X você deve Y'",
            'outro': None
        }

        return responses.get(command_type)

    def think(self, user_input):
        """Pipeline de processamento - retorna na primeira resposta válida"""
        response = self.process_teaching(user_input)
        if response:
            return response

        response = self.check_learned_command(user_input)
        if response:
            return response

        response = self.extract_facts(user_input)
        if response:
            return response

        response = self.check_contextual_memory(user_input)
        if response:
            return response

        cmd_type = self.classify_command(user_input)
        response = self.generate_response(user_input, cmd_type)

        if response:
            if cmd_type not in ['hora', 'data', 'lucy']:
                mood = self.detect_mood(user_input)
                mood_resp = self.get_mood_response(mood)
                if mood_resp and mood != 'neutral':
                    return f"{mood_resp} {response}"
            return response

        mood = self.detect_mood(user_input)
        mood_resp = self.get_mood_response(mood)
        if mood_resp:
            return mood_resp

        return "Não entendi completamente, mas estou aprendendo! Pode me ensinar?"