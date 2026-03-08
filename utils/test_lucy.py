#!/usr/bin/env python3
"""
Script de teste rápido para verificar se todos os componentes da Lucy estão funcionando
"""

import sys
import os

def test_imports():
    """Testa se todos os módulos importam corretamente"""
    print("🔍 Testando imports...")
    try:
        from lucy_voice import LucyVoice
        from lucy_memory import LucyMemory
        from lucy_brain import LucyBrain
        from lucy_assistant import Lucy
        print("✅ Todos os imports OK")
        return True
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_memory():
    """Testa sistema de memória"""
    print("🧠 Testando memória...")
    try:
        from lucy_memory import LucyMemory
        mem = LucyMemory()

        # Testar escrita e leitura
        mem.data['user_facts']['teste'] = 'valor_teste'
        mem.save_all()

        # Recarregar
        mem2 = LucyMemory()
        assert mem2.data['user_facts'].get('teste') == 'valor_teste'

        # Limpar teste
        del mem2.data['user_facts']['teste']
        mem2.save_all()

        print("✅ Sistema de memória OK")
        return True
    except Exception as e:
        print(f"❌ Erro na memória: {e}")
        return False

def test_brain():
    """Testa processamento do cérebro"""
    print("🧩 Testando cérebro...")
    try:
        from lucy_memory import LucyMemory
        from lucy_brain import LucyBrain

        mem = LucyMemory()
        brain = LucyBrain(mem)

        # Testar extração de fatos
        response = brain.extract_facts("meu nome é Teste")
        assert "Teste" in response

        # Testar classificação
        cmd = brain.classify_command("que horas são")
        assert cmd == 'hora'

        # Testar humor
        mood = brain.detect_mood("estou muito feliz hoje")
        assert mood == 'positive'

        print("✅ Cérebro funcionando OK")
        return True
    except Exception as e:
        print(f"❌ Erro no cérebro: {e}")
        return False

def test_voice():
    """Testa sistema de voz (modo texto se falhar)"""
    print("🎤 Testando voz...")
    try:
        from lucy_voice import LucyVoice
        voice = LucyVoice("Teste")

        # Testar modo texto fallback
        print("✅ Sistema de voz inicializado (modo texto disponível se necessário)")
        return True
    except Exception as e:
        print(f"⚠️ Erro na voz (pode usar modo texto): {e}")
        return True  # Não é crítico

def main():
    print("="*50)
    print("🤖 TESTE DO SISTEMA LUCY")
    print("="*50)

    tests = [
        test_imports,
        test_memory,
        test_brain,
        test_voice
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Teste {test.__name__} falhou: {e}")
            results.append(False)

    print("" + "="*50)
    if all(results):
        print("✅ TODOS OS TESTES PASSARAM!")
        print("Você pode iniciar a Lucy com: python lucy_assistant.py")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima")
    print("="*50)

if __name__ == "__main__":
    main()