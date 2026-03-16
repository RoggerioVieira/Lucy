"""
Skill Manager com Circuit Breaker e Fallbacks
"""

from skills import AVAILABLE_SKILLS, BaseSkill
from core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException


class SkillManager:
    """
    Gerencia todas as skills com proteção de Circuit Breaker
    """
    
    # Configurações de circuit breaker por skill
    CB_CONFIG = {
        'spotify': {'failure_threshold': 2, 'recovery_timeout': 60},    # API externa - sensível
        'weather': {'failure_threshold': 3, 'recovery_timeout': 45},    # API externa
        'reminder': {'failure_threshold': 5, 'recovery_timeout': 10}, # Local - tolerante
        'email': {'failure_threshold': 2, 'recovery_timeout': 120},   # SMTP - sensível
        'smart_home': {'failure_threshold': 2, 'recovery_timeout': 30} # Hardware
    }
    
    def __init__(self, memory=None):
        self.memory = memory
        self.instances = {}
        self.circuit_breakers = {}
        self._initialize_skills()
    
    def _initialize_skills(self):
        """Inicializa skills com seus circuit breakers"""
        for name, skill_class in AVAILABLE_SKILLS.items():
            cb_config = self.CB_CONFIG.get(name, {})
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=cb_config.get('failure_threshold', 3),
                recovery_timeout=cb_config.get('recovery_timeout', 30)
            )
            # Instanciação lazy - só cria quando necessário
    
    def _get_skill_instance(self, name):
        """Lazy loading de instâncias de skills"""
        if name not in self.instances:
            skill_class = AVAILABLE_SKILLS.get(name)
            if skill_class:
                try:
                    self.instances[name] = skill_class(self.memory)
                except Exception as e:
                    print(f"⚠️  Falha ao inicializar {name}: {e}")
                    return None
        return self.instances.get(name)
    
    def execute(self, name, user_input):
        """
        Executa skill protegida por circuit breaker
        Retorna string de resposta ou None se não executou
        """
        skill = self._get_skill_instance(name)
        if not skill:
            return f"⚠️  Skill {name} não disponível"
        
        cb = self.circuit_breakers[name]
        
        try:
            # Verificar se skill pode handle este input
            if not skill.can_handle(user_input):
                return None
            
            # Executar com proteção
            result = cb.call(skill.handle, user_input)
            return result
            
        except CircuitBreakerOpenException as e:
            # Circuito aberto - retorna mensagem amigável
            return f"⏳ {self._get_friendly_name(name)} está temporariamente indisponível. {str(e)}"
        
        except Exception as e:
            # Outra falha - log e retorna erro genérico
            print(f"❌ Erro em {name}: {e}")
            return f"❌ Algo deu errado no {self._get_friendly_name(name)}. Tente novamente."
    
    def find_and_execute(self, user_input):
        """
        Encontra a primeira skill que pode processar e executa
        Retorna (resposta, skill_name) ou (None, None)
        """
        for name in AVAILABLE_SKILLS.keys():
            result = self.execute(name, user_input)
            if result and not result.startswith("⚠️") and not result.startswith("⏳"):
                return result, name
        
        # Nenhuma skill executou com sucesso
        return None, None
    
    def get_skill_status(self):
        """Retorna status de todas as skills para diagnóstico"""
        return {
            name: {
                'circuit_status': cb.get_status(),
                'instance_ready': name in self.instances
            }
            for name, cb in self.circuit_breakers.items()
        }
    
    def _get_friendly_name(self, skill_name):
        """Nomes amigáveis para exibição"""
        names = {
            'spotify': '🎵 Spotify',
            'weather': '🌤️ Previsão do Tempo',
            'reminder': '⏰ Lembretes',
            'email': '📧 Email',
            'smart_home': '🏠 Casa Inteligente'
        }
        return names.get(skill_name, skill_name)
    
    def force_skill_reset(self, skill_name):
        """Força reset manual de um circuit breaker (para testes)"""
        if skill_name in self.circuit_breakers:
            cb = self.circuit_breakers[skill_name]
            cb._reset()
            return True
        return False