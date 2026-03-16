"""
Health Check - Diagnóstico completo do sistema Lucy
"""

import sys
import json
from pathlib import Path

# Adicionar pasta raiz ao path (para importar skills de utils/)
current_dir = Path(__file__).parent  # utils/
root_dir = current_dir.parent  # Lucy/
sys.path.insert(0, str(root_dir))


def check_system_health():
    """Executa diagnóstico completo"""
    print("🔍 HEALTH CHECK - Lucy Assistant")
    print("=" * 50)
    
    results = {
        'status': 'healthy',
        'components': {},
        'recommendations': []
    }
    
    # 1. Verificar estrutura de pastas
    required_paths = [
        'core', 'skills', 'utils', 'data',
        'core/lucy_assistant.py',
        'core/lucy_brain.py',
        'core/lucy_memory.py',
        'core/lucy_voice.py',
        'core/circuit_breaker.py',
        'skills/skill_manager.py',
    ]
    
    missing = []
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)
    
    if missing:
        results['components']['structure'] = 'missing_files'
        results['recommendations'].append(f"Criar arquivos: {', '.join(missing)}")
        print(f"❌ Estrutura: Faltam {len(missing)} arquivos")
    else:
        results['components']['structure'] = 'ok'
        print("✅ Estrutura: OK")
    
    # 2. Verificar dependências
    try:
        import speech_recognition
        import pyttsx3
        import sklearn
        results['components']['dependencies'] = 'ok'
        print("✅ Dependências: OK")
    except ImportError as e:
        results['components']['dependencies'] = f'missing: {e}'
        results['recommendations'].append("Run: pip install -r requirements.txt")
        print(f"❌ Dependências: {e}")
    
    # 3. Verificar dados
    data_files = ['data/lucy_memory.json', 'data/lucy_personality.json']
    data_ok = all(Path(f).exists() for f in data_files)
    results['components']['data'] = 'ok' if data_ok else 'missing'
    print(f"{'✅' if data_ok else '⚠️ '} Dados: {'OK' if data_ok else 'Serão criados automaticamente'}")
    
    # 4. Verificar configuração de skills (agora com path correto)
    try:
        from skills import AVAILABLE_SKILLS
        results['components']['skills'] = f"{len(AVAILABLE_SKILLS)} skills"
        print(f"✅ Skills: {len(AVAILABLE_SKILLS)} disponíveis")
    except Exception as e:
        results['components']['skills'] = f'error: {e}'
        print(f"❌ Skills: {e}")
    
    # Summary
    print("=" * 50)
    if results['recommendations']:
        print("🔧 RECOMENDAÇÕES:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
        results['status'] = 'degraded'
    else:
        print("🎉 Sistema pronto para uso!")
    
    # Salvar relatório
    with open('data/health_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results['status'] == 'healthy'


if __name__ == "__main__":
    healthy = check_system_health()
    sys.exit(0 if healthy else 1)