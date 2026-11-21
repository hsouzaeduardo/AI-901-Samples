"""
Módulo 03 - Tópicos: "Entender a análise de texto no Foundry: modelos de IA de uso
geral" e "Usar a API OpenAI com modelos de IA de uso geral"

Um único prompt faz VÁRIAS tarefas de PLN de uma vez (sentimento, termos-chave,
entidades e resumo) e devolve JSON estruturado (structured outputs).
Rodamos 2 vezes para observar a variação entre chamadas (geração probabilística).

  python 06_analise_com_llm.py
"""
import json
import os
import sys

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

# Passo 1-2: importar pacotes e carregar variáveis de ambiente
load_dotenv(find_dotenv())
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_FOUNDRY_KEY")
deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")
if not all((endpoint, api_key, deployment_name)):
    sys.exit("Defina AZURE_OPENAI_ENDPOINT, AZURE_FOUNDRY_KEY e MODEL_DEPLOYMENT_NAME no .env")

# Passo 3: criar o cliente
client = OpenAI(base_url=endpoint, api_key=api_key)

TEXTO = ("Alex e eu participamos de uma conferência da Microsoft AI. Foi em Las Vegas no dia 21 "
         "de setembro. Foi uma ótima oportunidade para conhecer as tecnologias mais recentes. Os "
         "avanços na tecnologia de IA são incríveis. É muito empolgante!")

ESQUEMA = {
    "type": "json_schema", "name": "analise_texto", "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False,
        "required": ["sentimento", "termos_chave", "entidades", "resumo"],
        "properties": {
            "sentimento": {"type": "string", "enum": ["positivo", "negativo", "neutro", "misto"]},
            "termos_chave": {"type": "array", "items": {"type": "string"}},
            "entidades": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["texto", "categoria"],
                "properties": {"texto": {"type": "string"},
                               "categoria": {"type": "string",
                                             "enum": ["pessoa", "organização", "lugar", "data", "outro"]}}}},
            "resumo": {"type": "string"},
        },
    },
}

for rodada in (1, 2):
    # Passo 4: fazer a solicitação
    resposta = client.responses.create(
        model=deployment_name,
        instructions="Você é um analisador de textos. Responda em português.",
        input=f"Analise o texto: sentimento, termos-chave, entidades nomeadas e resumo em 1 frase.\n\n{TEXTO}",
        text={"format": ESQUEMA},
    )
    # Passo 5: lidar com os resultados
    analise = json.loads(resposta.output_text)
    print(f"=== Rodada {rodada} ===")
    print(json.dumps(analise, indent=2, ensure_ascii=False))

print("\nCompare as rodadas: termos-chave e resumo podem mudar de uma chamada para outra.")
print("Para resultados determinísticos e com pontuação de confiança: 07_linguagem_azure.py")
