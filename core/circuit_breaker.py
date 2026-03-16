"""
Circuit Breaker Pattern para a Lucy
Protege contra falhas em cascata em componentes externos (skills, APIs)
"""

import time
import threading
from enum import Enum
from datetime import datetime


class State(Enum):
    CLOSED = "closed"       # Normal - permite execução
    OPEN = "open"          # Falhou - bloqueia execução
    HALF_OPEN = "half_open"  # Testando recuperação


class CircuitBreaker:
    """
    Circuit Breaker implementa o padrão de Michael Nygard
    """
    
    def __init__(self, name, failure_threshold=3, recovery_timeout=30, 
                 half_open_max_calls=1):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # segundos
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = State.CLOSED
        self.half_open_calls = 0
        self.lock = threading.Lock()
        
        # Estatísticas
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
    
    def call(self, func, *args, **kwargs):
        """
        Executa função protegida pelo circuit breaker
        """
        with self.lock:
            self.total_calls += 1
            
            # Verificar estado
            if self.state == State.OPEN:
                if self._should_attempt_reset():
                    self.state = State.HALF_OPEN
                    self.half_open_calls = 0
                    print(f"🔧 Circuit {self.name}: Testando recuperação...")
                else:
                    remaining = self.recovery_timeout - (time.time() - self.last_failure_time)
                    raise CircuitBreakerOpenException(
                        f"⏳ {self.name} indisponível. Tente em {int(remaining)}s"
                    )
            
            if self.state == State.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpenException(
                        f"⏳ {self.name} testando recuperação, aguarde..."
                    )
                self.half_open_calls += 1
        
        # Executar função
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Verifica se pode tentar reset após timeout"""
        if not self.last_failure_time:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        with self.lock:
            self.total_successes += 1
            
            if self.state == State.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    print(f"✅ Circuit {self.name}: Recuperado!")
                    self._reset()
            else:
                # Em CLOSED, reseta contador de falhas gradualmente
                self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        with self.lock:
            self.total_failures += 1
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == State.HALF_OPEN:
                # Falhou no teste, volta para OPEN
                print(f"❌ Circuit {self.name}: Falhou na recuperação")
                self.state = State.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = State.OPEN
                print(f"🚨 Circuit {self.name}: ABERTO após {self.failure_count} falhas")
    
    def _reset(self):
        """Reseta para estado normal"""
        self.state = State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
    
    def get_status(self):
        """Retorna status atual para monitoramento"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'total_calls': self.total_calls,
            'failure_rate': round(self.total_failures / max(self.total_calls, 1) * 100, 2),
            'last_failure': datetime.fromtimestamp(self.last_failure_time).isoformat() 
                           if self.last_failure_time else None
        }


class CircuitBreakerOpenException(Exception):
    """Exceção quando circuito está aberto"""
    pass