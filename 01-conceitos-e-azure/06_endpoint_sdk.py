"""
Módulo 01 - Tópico: Pontos de extremidade do Microsoft Foundry (continuação)
"APIs REST são tipicamente abstraídas por SDKs específicos de linguagem."

Mesma chamada do exemplo 05, agora com o SDK da OpenAI. Compare a quantidade de
código! Mostra as duas formas de autenticação:
  - chave de API (simples, boa para laboratório)
  - Microsoft Entra ID (recomendado em produção: sem segredo no código)

  python 06_endpoint_sdk.py
  python 06_endpoint_sdk.py --entra   (requer "az login" ou identidade gerenciada)
"""
import os
import sys

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())


def env(nome):
    valor = os.getenv(nome)
    if not valor:
        sys.exit(f"Defina {nome} no arquivo .env (veja .env.example)")
    return valor


if "--entra" in sys.argv:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    # o SDK chama esta função sempre que precisar de um token novo
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    client = OpenAI(base_url=env("AZURE_OPENAI_ENDPOINT"), api_key=token_provider)
    print("Autenticado com Microsoft Entra ID")
else:
    client = OpenAI(base_url=env("AZURE_OPENAI_ENDPOINT"), api_key=env("AZURE_FOUNDRY_KEY"))
    print("Autenticado com chave de API")

response = client.responses.create(
    model=env("MODEL_DEPLOYMENT_NAME"),   # nome da IMPLANTAÇÃO, não necessariamente do modelo
    input="Explique em uma frase o que é o Teste de Turing.",
)

# output_text junta todo o texto gerado (mais seguro que response.output[0]...)
print("Resposta:", response.output_text)
print("ID da resposta:", response.id)
print("Tokens - entrada:", response.usage.input_tokens, "| saída:", response.usage.output_tokens)
