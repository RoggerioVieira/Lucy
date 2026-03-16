import sys
from pathlib import Path

# Garante que o Python encontre a pasta 'core' e 'skills'
sys.path.insert(0, str(Path(__file__).parent))

# Importa a classe correta do arquivo de assistência
from core.lucy_assistant import LucyAssistant

if __name__ == "__main__":
    try:
        # Instancia a Lucy com o novo nome da classe
        lucy = LucyAssistant()
        
        # Inicia o loop principal (Escuta -> Pensa -> Fala)
        lucy.run()
        
    except KeyboardInterrupt:
        print("\n👋 Lucy encerrada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar a Lucy: {e}")
        sys.exit(1)