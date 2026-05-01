import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega a sua chave secreta
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔎 Conectando ao Google e buscando modelos disponíveis para a sua conta...\n")

try:
    for m in genai.list_models():
        # Filtra apenas os modelos que servem para gerar texto/conversa
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Nome exato do modelo: {m.name}")
except Exception as e:
    print(f"❌ Erro ao listar: {e}")