#!/usr/bin/env python3
"""
Script de limpeza da memória da Lucy
Remove comandos com aspas e fatos inválidos
"""

import json
import os
from collections import defaultdict

def clean_memory():
    print("🧹 Limpando memória da Lucy...")

    memory_file = "lucy_memory.json"

    if not os.path.exists(memory_file):
        print("❌ Arquivo de memória não encontrado!")
        return

    # Carregar
    with open(memory_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📊 Antes da limpeza:")
    print(f"   - Comandos: {len(data.get('command_mappings', {}))}")
    print(f"   - Fatos: {len(data.get('user_facts', {}))}")

    # 1. Limpar comandos (remover aspas)
    cleaned_commands = {}
    removed_commands = []

    for trigger, action in data.get('command_mappings', {}).items():
        # Limpar trigger
        clean_trigger = trigger.replace('"', '').replace("'", "").strip()
        clean_action = action.replace('"', '').replace("'", "").strip()

        # Remover se ficou vazio ou muito curto
        if len(clean_trigger) < 2:
            removed_commands.append(trigger)
            continue

        # Se já existe um comando igual limpo, pular este
        if clean_trigger in cleaned_commands:
            removed_commands.append(trigger)
            continue

        cleaned_commands[clean_trigger] = clean_action

    data['command_mappings'] = cleaned_commands

    # 2. Limpar fatos (remover inválidos)
    cleaned_facts = {}
    removed_facts = []

    invalid_values = ['eu', 'voce', 'lucy', 'vc', 'tu', 'ele', 'ela', '', 'eu ?', '?']

    for category, value in data.get('user_facts', {}).items():
        clean_value = value.strip().lower()

        if clean_value in invalid_values or len(clean_value) < 2:
            removed_facts.append((category, value))
            continue

        cleaned_facts[category] = value

    data['user_facts'] = cleaned_facts

    # 3. Garantir que routines é dict (para JSON)
    if 'routines' in data and isinstance(data['routines'], dict):
        # Já está OK
        pass

    # Salvar
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Depois da limpeza:")
    print(f"   - Comandos: {len(cleaned_commands)}")
    print(f"   - Fatos: {len(cleaned_facts)}")

    if removed_commands:
        print(f"\n🗑️ Comandos removidos: {removed_commands}")
    if removed_facts:
        print(f"🗑️ Fatos removidos: {removed_facts}")

    print("\n💾 Memória limpa e salva!")

if __name__ == "__main__":
    clean_memory()