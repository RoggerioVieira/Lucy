"""
LucyVoice com Retry, Timeout, VAD e Fallback para Texto
"""

import speech_recognition as sr
import pyttsx3
import time
import threading
from functools import wraps


def retry_on_failure(max_attempts=3, delay=0.5, exceptions=(Exception,)):
    """
    Decorator para retry com exponential backoff
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = delay * (2 ** attempt)
                        print(f"⚠️  Retry {attempt + 1}/{max_attempts} em {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                    continue
            # Todas tentativas falharam
            raise last_exception
        return wrapper
    return decorator


class LucyVoice:
    def __init__(self, user_name="amigo"):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 165)
        self._setup_voice()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.user_name = user_name
        
        # Modos de operação
        self.fallback_mode = False      # True = usar texto ao invés de voz
        self.tts_enabled = True
        self.stt_enabled = True
        
        # Estatísticas
        self.stt_failures = 0
        self.tts_failures = 0
        self.max_stt_failures = 3     # Após 3 falhas, ativa fallback
        
        # Timeout configurável
        self.listen_timeout = 5
        self.phrase_time_limit = 5
        
        # Thread de monitoramento
        self._stop_listening = threading.Event()
        
    def _setup_voice(self):
        """Configura voz feminina se disponível"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if any(term in voice.name.lower() for term in ['female', 'mulher', 'feminina', 'maria', 'ana']):
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text, priority=False):
        """
        TTS com fallback para print e controle de falhas
        """
        print(f"🤖 Lucy: {text}")
        
        if not self.tts_enabled or self.fallback_mode:
            return
        
        try:
            # Limitar tamanho do texto para evitar bloqueios
            if len(text) > 500:
                text = text[:497] + "..."
            
            self.engine.say(text)
            self.engine.runAndWait()
            self.tts_failures = 0  # Reset em sucesso
            
        except Exception as e:
            self.tts_failures += 1
            print(f"[TTS Error #{self.tts_failures}]: {e}")
            
            if self.tts_failures >= 2:
                print("🔇 TTS desabilitado - usando apenas texto")
                self.tts_enabled = False
    
    @retry_on_failure(max_attempts=3, delay=0.5, 
                      exceptions=(sr.WaitTimeoutError, sr.UnknownValueError))
    def _listen_with_retry(self):
        """
        STT com retry automático e VAD simples
        """
        with self.microphone as source:
            print("🎤 Lucy está ouvindo...")
            
            # Ajuste adaptativo de ruído (mais rápido)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            
            try:
                # Escuta com timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                # Reconhecimento com confiança implícita
                text = self.recognizer.recognize_google(
                    audio, 
                    language='pt-BR',
                    show_all=False
                )
                
                print(f"👤 {self.user_name}: {text}")
                self.stt_failures = 0  # Reset em sucesso
                return text.lower().strip()
                
            except sr.WaitTimeoutError:
                # Timeout é esperado, não conta como falha crítica
                raise  # Será capturado pelo retry
            
            except sr.UnknownValueError:
                # Não entendeu - tenta novamente
                print("🤷 Não entendi o áudio...")
                raise  # Será capturado pelo retry
            
            except sr.RequestError as e:
                # Erro de conexão - ativa fallback imediato
                print(f"🌐 Erro de conexão: {e}")
                self.stt_failures += 1
                if self.stt_failures >= self.max_stt_failures:
                    self._activate_fallback()
                raise
    
    def listen(self):
        """
        Método principal de escuta com fallback automático
        """
        if not self.stt_enabled or self.fallback_mode:
            return self._text_input()
            
        try:
            return self._listen_with_retry()
            
        except Exception as e:
            self.stt_failures += 1
            print(f"❌ STT falhou após retries: {e}")
            
            if self.stt_failures >= self.max_stt_failures:
                self._activate_fallback()
                return self._text_input()
            
            return None  # Permite tentar novamente no próximo loop
    
    def _activate_fallback(self):
        """Ativa modo de fallback para texto"""
        if not self.fallback_mode:
            print("\n🔧 Ativando modo texto (microfone indisponível)...")
            self.fallback_mode = True
            self.speak("Vou usar modo texto por enquanto. Pode digitar seus comandos.")
    
    def _text_input(self):
        """Entrada manual de texto - fallback definitivo"""
        try:
            prompt = f"\n👤 {self.user_name} (digite): "
            text = input(prompt)
            return text.lower().strip() if text else None
        except (EOFError, KeyboardInterrupt):
            return None
    
    def listen_async(self, callback):
        """
        Escuta assíncrona com callback (para interrupções)
        """
        def listen_thread():
            while not self._stop_listening.is_set():
                result = self.listen()
                if result:
                    callback(result)
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Para threads de escuta"""
        self._stop_listening.set()
    
    def get_health_status(self):
        """Retorna status de saúde do componente de voz"""
        return {
            'stt_enabled': self.stt_enabled,
            'tts_enabled': self.tts_enabled,
            'fallback_mode': self.fallback_mode,
            'stt_failures': self.stt_failures,
            'tts_failures': self.tts_failures,
            'status': 'healthy' if not self.fallback_mode else 'degraded'
        }
    
    def reset_fallback(self):
        """Tenta voltar ao modo de voz (usuário pode forçar)"""
        if self.fallback_mode:
            print("🔄 Tentando restaurar modo voz...")
            self.fallback_mode = False
            self.stt_failures = 0
            self.stt_enabled = True
            return True
        return False