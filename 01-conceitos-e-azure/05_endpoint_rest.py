"""
Módulo 01 - Tópico: Pontos de extremidade do Microsoft Foundry
"Um ponto de extremidade é um endereço HTTP... requisições incluem cabeçalhos
de metadados e dados em JSON; respostas incluem cabeçalhos e resultados em JSON."

Este exemplo NÃO usa SDK: faz a chamada REST "na mão" com a biblioteca requests,
para mostrar exatamente o que trafega entre o aplicativo e o Foundry.

Pré-requisitos: .env com AZURE_OPENAI_ENDPOINT, AZURE_FOUNDRY_KEY, MODEL_DEPLOYMENT_NAME
  python 05_endpoint_rest.py            -> autenticação por CHAVE (cabeçalho api-key)
  python 05_endpoint_rest.py --entra    -> autenticação por TOKEN do Microsoft Entra ID
"""
import json
import os
import sys

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def env(nome):
    valor = os.getenv(nome)
    if not valor:
        sys.exit(f"Defina {nome} no arquivo .env (veja .env.example)")
    return valor


url = env("AZURE_OPENAI_ENDPOINT").rstrip("/") + "/responses"

# ---- Cabeçalhos (metadados + autenticação) ----
headers = {"Content-Type": "application/json"}
if "--entra" in sys.argv:
    from azure.identity import DefaultAzureCredential
    token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default")
    headers["Authorization"] = f"Bearer {token.token}"
    modo = "Token do Microsoft Entra ID (Authorization: Bearer ...)"
else:
    headers["api-key"] = env("AZURE_FOUNDRY_KEY")
    modo = "Chave de autorização (api-key: ...)"

# ---- Corpo da requisição (JSON) ----
corpo = {
    "model": env("MODEL_DEPLOYMENT_NAME"),
    "input": "Explique em uma frase o que é o Teste de Turing.",
}

print("=== REQUISIÇÃO ===")
print("POST", url)
print("Autenticação:", modo)
print(json.dumps(corpo, indent=2, ensure_ascii=False))

resposta = requests.post(url, headers=headers, json=corpo, timeout=60)

print("\n=== RESPOSTA ===")
print("Status HTTP:", resposta.status_code)
for h in ("content-type", "x-request-id", "apim-request-id", "x-ratelimit-remaining-tokens"):
    if h in resposta.headers:
        print(f"{h}: {resposta.headers[h]}")

dados = resposta.json()
if resposta.ok:
    # o texto gerado fica dentro de output -> item do tipo "message" -> content -> output_text
    textos = [c["text"] for item in dados.get("output", []) if item.get("type") == "message"
              for c in item.get("content", []) if c.get("type") == "output_text"]
    print("\nTexto gerado:", " ".join(textos))
    print("Uso de tokens:", dados.get("usage"))
else:
    print(json.dumps(dados, indent=2, ensure_ascii=False))
