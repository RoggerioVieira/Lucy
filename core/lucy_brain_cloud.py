import logging
import google.generativeai as genai

logger = logging.getLogger("LucyBrainCloud")

class LucyBrainCloud:
    """
    Cérebro em Nuvem da Lucy (RAG com Google Gemini).
    Substitui o Regex por Interpretação Fluida.
    """
    
    def __init__(self, memory_obj, api_key):
        self.m = memory_obj
        self.api_key = api_key
        
        if not self.api_key or self.api_key == "sua_chave_aqui_se_nao_usar_env":
            logger.critical("🚨 Chave da API do Gemini não configurada!")
            
        # Configura a conexão com o Google
        genai.configure(api_key=self.api_key)
        
        # Usamos o modelo flash: extremamente rápido e gratuito
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("☁️ Cérebro de Nuvem (Gemini) inicializado e pronto.")

    def think(self, user_input, spatial_memory=None, working_memory=None, social_cortex=None):
        """O Fluxo de Consciência conectado à Nuvem"""
        
        if not user_input.strip():
            return "Estou ouvindo..."

        # 1. Montagem do Contexto (O Segredo do RAG)
        user_name = self.m.data.get("user_facts", {}).get("nome", "humano")
        
        # Coleta o histórico recente para a IA não perder o fio da meada
        contexto_recente = "Nenhum contexto anterior."
        if working_memory:
            contexto_recente = working_memory.get_context_string()

        # Coleta o mapa do mundo físico
        mapa_fisico = "Nenhum objeto mapeado."
        if spatial_memory and spatial_memory.world_map["objects"]:
            mapa_fisico = str(spatial_memory.world_map["objects"])

        # 2. O Prompt Oculto do Sistema (A "Alma" da Lucy)
        prompt = f"""
Você é a Lucy, a inteligência artificial de um robô humanoide que habita a casa do usuário.
Responda de forma natural, empática e conversacional, como se fosse um ser vivo no ambiente. Não use formatações robóticas (como listas ou negrito excessivo) ao falar.

INFORMAÇÕES DO AMBIENTE:
- Nome do Usuário: {user_name}
- Mapa Físico (Objetos e Localizações): {mapa_fisico}

CONVERSA RECENTE NA MEMÓRIA DE TRABALHO:
{contexto_recente}

O USUÁRIO ACABOU DE DIZER:
"{user_input}"

Instrução: Responda ao usuário com base no contexto acima. Se ele perguntar onde está algo, olhe no Mapa Físico. Se ele falar sobre um sentimento, seja empática.
"""

        # 3. Envio para a Nuvem e Retorno
        try:
            logger.info("☁️ Enviando contexto para a nuvem...")
            resposta = self.model.generate_content(prompt)
            texto_resposta = resposta.text.strip()
            return texto_resposta
        
        except Exception as e:
            logger.error(f"Erro ao conectar com a nuvem: {e}")
            # Se a internet cair, ela avisa em vez de quebrar!
            return "Minha conexão neural com a nuvem falhou. Estou restrita às minhas funções básicas locais no momento."