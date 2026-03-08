#!/usr/bin/env python3
"""
Teste específico para os problemas do log anterior
"""

import sys
import os

# Limpar memória primeiro
print("🧹 Limpando memória antiga...")
os.system("python clean_memory.py")

from lucy_memory import LucyMemory
from lucy_brain import LucyBrain

def test_specific_issues():
    print("\n" + "="*60)
    print("🔍 TESTE DE PROBLEMAS ESPECÍFICOS")
    print("="*60)

    mem = LucyMemory()
    brain = LucyBrain(mem)

    tests = [
        # Problema 1: me chame de
        ('me chame de Rogério', 'deve reconhecer padrão "me chame de"'),

        # Problema 2: evitar extrair de pergunta
        ('quem sou eu?', 'NÃO deve extrair "eu" como fato'),
        ('qual é o meu nome?', 'NÃO deve extrair nada'),

        # Problema 3: ensinar comando limpo
        ('quando eu disser "teste" você deve fazer algo', 'deve limpar aspas'),

        # Problema 4: executar comando
        ('teste', 'deve executar comando ensinado'),

        # Problema 5: validação rigorosa
        ('sou eu', 'NÃO deve extrair "eu" como trabalho'),
        ('trabalho com eu', 'NÃO deve aceitar "eu" como valor'),
    ]

    for user_input, expected in tests:
        print(f"\n📝 Teste: {expected}")
        print(f"   Input: '{user_input}'")

        # Limpar fatos antes de cada teste crítico
        if 'NÃO deve' in expected:
            mem.data['user_facts'] = {}

        response = brain.think(user_input)
        print(f"   Resposta: '{response}'")

        # Verificações
        if 'me chame de' in user_input:
            if 'nome' in mem.data['user_facts']:
                print(f"   ✅ SUCESSO: Nome extraído: {mem.data['user_facts']['nome']}")
            else:
                print(f"   ❌ FALHA: Não extraiu nome")

        if 'NÃO deve extrair' in expected:
            if not mem.data['user_facts']:
                print(f"   ✅ SUCESSO: Não extraiu fato inválido")
            else:
                print(f"   ❌ FALHA: Extraiu: {mem.data['user_facts']}")

        if 'limpar aspas' in expected:
            cmds = mem.data['command_mappings']
            if 'teste' in cmds and '"' not in cmds and "'" not in cmds:
                print(f"   ✅ SUCESSO: Comando limpo: {cmds}")
            else:
                print(f"   ❌ FALHA: Comando com lixo: {cmds}")

    print("\n" + "="*60)
    print("✅ Teste completo!")
    print("="*60)

if __name__ == "__main__":
    test_specific_issues()