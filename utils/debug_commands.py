#!/usr/bin/env python3
"""
Script de debug para testar comandos específicos que falharam no log
"""

import sys
sys.path.insert(0, '.')

from lucy_memory import LucyMemory
from lucy_brain import LucyBrain

def test_commands():
    print("="*60)
    print("🔍 TESTE DE COMANDOS ESPECÍFICOS")
    print("="*60)

    mem = LucyMemory()
    brain = LucyBrain(mem)

    test_cases = [
        # (input, descrição)
        ('qual é o seu nome', 'Perguntar nome da Lucy'),
        ('estou muito feliz hoje', 'Detectar humor positivo'),
        ('quando eu disser modo foco você deve tocar música', 'Ensinar comando'),
        ('modo foco', 'Executar comando aprendido'),
        ('modo Foco', 'Testar case insensitive'),
        ('"modo foco"', 'Testar com aspas'),
        ('estou cansado', 'Detectar humor negativo/cansado'),
        ('me chame de Rogério', 'Extrair nome'),
        ('meu nome é Rogério', 'Extrair nome padrão'),
        ('qual é o meu nome', 'Perguntar nome do usuário'),
        ('quem sou eu', 'Perguntar identidade'),
        ('o que você sabe sobre mim', 'Listar fatos'),
    ]

    for user_input, desc in test_cases:
        print(f"\n📝 Teste: {desc}")
        print(f"   Input: '{user_input}'")

        response = brain.think(user_input)
        print(f"   Resposta: '{response}'")

        # Verificar se extraiu fatos
        if mem.data['user_facts']:
            print(f"   Fatos na memória: {mem.data['user_facts']}")

        # Verificar comandos aprendidos
        if mem.data['command_mappings']:
            print(f"   Comandos: {mem.data['command_mappings']}")

    print("\n" + "="*60)
    print("✅ Teste completo!")
    print("="*60)

if __name__ == "__main__":
    test_commands()