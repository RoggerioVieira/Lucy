import speech_recognition as sr
import pyttsx3
import sys

class LucyVoice:
    """Sistema de I/O de voz da Lucy com fallbacks"""

    def __init__(self, user_name="amigo"):
        self.user_name = user_name
        self.text_only_mode = False

        # Inicializar TTS
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 165)
            self._setup_voice()
        except Exception as e:
            print(f"⚠️ Erro ao inicializar voz: {e}. Modo texto ativado.")
            self.text_only_mode = True
            self.engine = None

        # Inicializar reconhecimento
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # Testar microfone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
        except Exception as e:
            print(f"⚠️ Erro ao acessar microfone: {e}")
            self.recognizer = None

    def _setup_voice(self):
        """Configura voz feminina se disponível"""
        if not self.engine:
            return

        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                voice_name = voice.name.lower()
                if any(term in voice_name for term in ['female', 'mulher', 'feminina', 'maria', 'ana']):
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"⚠️ Não foi possível configurar voz feminina: {e}")

    def speak(self, text):
        """Fala o texto ou imprime se modo texto"""
        print(f"🤖 Lucy: {text}")

        if not self.text_only_mode and self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ Erro ao falar: {e}")

    def listen(self):
        """Escuta o usuário ou retorna input de texto se microfone falhar"""
        # Se não há reconhecimento de voz, usar modo texto
        if not self.recognizer:
            return self._text_input()

        with self.microphone as source:
            print("🎤 Lucy está ouvindo... (ou digite se preferir)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                # Tentar ouvir por 5 segundos
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"👤 {self.user_name}: {text}")
                return text.lower()

            except sr.WaitTimeoutError:
                print("⏱️ Tempo esgotado. Usando modo texto.")
                return self._text_input()
            except sr.UnknownValueError:
                print("❓ Não entendi. Pode repetir? (ou digite)")
                return self._text_input()
            except sr.RequestError as e:
                print(f"⚠️ Erro de conexão: {e}. Usando modo texto.")
                return self._text_input()

    def _text_input(self):
        """Fallback para entrada de texto"""
        try:
            text = input(f"👤 {self.user_name} (digite): ").strip()
            return text.lower() if text else None
        except (EOFError, KeyboardInterrupt):
            return None

    def ask_confirmation(self, question):
        """Pergunta e retorna True/False"""
        self.speak(question)
        response = self.listen()
        if response:
            return any(word in response for word in ['sim', 'yes', 'claro', 'pode', 'ok', 'certo'])
        return False