import logging
import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

logger = logging.getLogger("LucyBrainCloud")

class LucyBrainCloud:
    """
    Cérebro em Nuvem da Lucy (Gemini atualizado).
    """

    def __init__(self, memory_obj, api_key=None):
        self.m = memory_obj
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logger.critical("🚨 Chave da API do Gemini não configurada!")
            raise ValueError("API KEY não encontrada no .env")

        # Cliente oficial novo
        self.client = genai.Client(api_key=self.api_key)

        # Modelo atualizado (2026)
        self.model = "gemini-2.5-flash-lite"

        logger.info("☁️ Cérebro de Nuvem (Gemini) inicializado e pronto.")

    def think(self, user_input, spatial_memory=None, working_memory=None, social_cortex=None):
        if not user_input.strip():
            return "Estou ouvindo..."

        user_name = self.m.data.get("user_facts", {}).get("nome", "humano")

        contexto_recente = "Nenhum contexto anterior."
        if working_memory:
            contexto_recente = working_memory.get_context_string()

        mapa_fisico = "Nenhum objeto mapeado."
        if spatial_memory and spatial_memory.world_map["objects"]:
            mapa_fisico = str(spatial_memory.world_map["objects"])

        agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

        prompt = f"""
Você é a Lucy, uma IA humanoide.

Usuário: {user_name}
Data: {agora}

Mapa físico:
{mapa_fisico}

Contexto recente:
{contexto_recente}

Usuário disse:
"{user_input}"

Responda de forma natural e humana.
"""

        try:
            logger.info("☁️ Enviando contexto para a nuvem...")

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Erro Gemini: {e}")
            return "Minha conexão neural com a nuvem falhou. Estou restrita ao modo offline."