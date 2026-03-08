from core.lucy_voice import LucyVoice
from core.lucy_memory import LucyMemory
from core.lucy_brain import LucyBrain
import threading
from datetime import datetime
import random
import sys

class Lucy:
    """
    Lucy - Assistente Virtual com Aprendizado por Padrões de Convivência
    Versão 1.0 - Correções de bugs
    """

    def __init__(self):
        print("🚀 Inicializando Lucy...")

        # Inicializar componentes
        self.memory = LucyMemory()
        self.brain = LucyBrain(self.memory)
        self.user_name = self.memory.data['user_facts'].get('nome', 'amigo')
        self.voice = LucyVoice(self.user_name)

        # Configurar saudações
        self._setup_greetings()

        # Contador de sessão
        self.session_interactions = 0

        print(f"✅ Lucy pronta! Usuário: {self.user_name}")
        print("💡 Dica: Ensine-me comandos com 'Quando eu disser X você deve Y'")

    def _setup_greetings(self):
        """Configura saudações baseadas no horário"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            period = "Bom dia"
        elif 12 <= hour < 18:
            period = "Boa tarde"
        else:
            period = "Boa noite"

        self.greetings = [
            f"{period}, {self.user_name}! Sou a Lucy. Como posso ajudar?",
            f"Oi! {period}! Lucy aqui, pronta para aprender!",
        ]

        if self.memory.data['interaction_count'] > 10:
            self.greetings.append(
                f"{period}, {self.user_name}! Já conversamos "
                f"{self.memory.data['interaction_count']} vezes!"
            )

        self.farewells = [
            f"Até logo, {self.user_name}! Vou guardar tudo que aprendi.",
            "Tchau! Até a próxima!",
            f"Até mais! Estarei aqui quando precisar.",
        ]

    def learn_in_background(self, user_input, lucy_response):
        """Processa aprendizado em thread separada"""
        try:
            # Detectar e registrar humor
            mood = self.brain.detect_mood(user_input)
            self.memory.personality['user_mood_history'].append({
                'timestamp': datetime.now().isoformat(),
                'mood': mood
            })

            # Registrar rotina
            hour = datetime.now().hour
            cmd_type = self.brain.classify_command(user_input)
            self.memory.data['routines'][str(hour)].append(cmd_type)

            # Adicionar ao histórico
            self.memory.add_to_history(user_input, lucy_response)

            # Atualizar contadores
            self.memory.data['interaction_count'] += 1
            self.session_interactions += 1

            # Atualizar nome se mudou
            new_name = self.memory.data['user_facts'].get('nome')
            if new_name and new_name != self.user_name:
                self.user_name = new_name
                self.voice.user_name = new_name

            # Salvar periodicamente
            if self.memory.data['interaction_count'] % 5 == 0 or cmd_type == 'ensino':
                self.memory.save_all()

        except Exception as e:
            print(f"⚠️ Erro no aprendizado: {e}")

    def run(self):
        """Loop principal de interação"""
        self.voice.speak(random.choice(self.greetings))

        while True:
            try:
                # Ouvir usuário
                user_input = self.voice.listen()
                if not user_input:
                    continue

                # Limpar input
                user_input = user_input.strip()

                # Verificar saída
                if any(kw in user_input.lower() for kw in ['sair', 'tchau', 'desligar']):
                    self.voice.speak(random.choice(self.farewells))
                    self.memory.save_all()
                    break

                # Processar pelo cérebro
                response = self.brain.think(user_input)

                # Falar resposta
                self.voice.speak(response)

                # Aprendizado em background
                threading.Thread(
                    target=self.learn_in_background,
                    args=(user_input, response),
                    daemon=True
                ).start()

            except KeyboardInterrupt:
                print("\n👋 Interrompido")
                self.voice.speak("Até logo!")
                self.memory.save_all()
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                self.voice.speak("Ops, algo deu errado. Pode tentar de novo?")

if __name__ == "__main__":
    try:
        lucy = Lucy()
        lucy.run()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)