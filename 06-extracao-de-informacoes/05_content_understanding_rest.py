"""
Módulo 06 - Tópico: Extração de informações de documentos -
"Use a API REST para recuperar resultados JSON de analisadores"

Mesmo fluxo dos scripts extract-data.sh e get-results.sh do laboratório, em Python:
  1) POST .../analyzers/{id}:analyze  -> 202 Accepted + cabeçalho Operation-Location
  2) GET  Operation-Location           -> repetir até status = Succeeded
  3) Ler result.contents[0].fields

  python 05_content_understanding_rest.py
  python 05_content_understanding_rest.py prebuilt-receipt https://.../recibo.jpg
"""
import json
import os
import sys
import time

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint = (os.getenv("AZURE_SERVICES_AI_ENDPOINT") or "").rstrip("/")
key = os.getenv("AZURE_FOUNDRY_KEY")
if not (endpoint and key):
    sys.exit("Defina AZURE_SERVICES_AI_ENDPOINT e AZURE_FOUNDRY_KEY no .env")

API = "2025-11-01"
analisador = sys.argv[1] if len(sys.argv) > 1 else "prebuilt-invoice"
url_doc = sys.argv[2] if len(sys.argv) > 2 else ("https://raw.githubusercontent.com/MicrosoftLearning/"
                                                 "mslearn-ai-fundamentals/refs/heads/main/data/contoso-invoice-1.pdf")
headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"}

# 1) Enviar
r = requests.post(f"{endpoint}/contentunderstanding/analyzers/{analisador}:analyze?api-version={API}",
                  headers=headers, json={"inputs": [{"url": url_doc}]}, timeout=60)
print("POST ->", r.status_code)
if r.status_code != 202:
    sys.exit(r.text)
operacao = r.headers["Operation-Location"]
print("Operation-Location:", operacao)

# 2) Consultar até terminar
while True:
    status = requests.get(operacao, headers=headers, timeout=60).json()
    print("  status:", status.get("status"))
    if status.get("status") in ("Succeeded", "Failed", "Canceled"):
        break
    time.sleep(10)

if status["status"] != "Succeeded":
    sys.exit(json.dumps(status, indent=2))

# 3) Campos: cada um tem "type" e o valor em valueString/valueNumber/valueDate/...
def valor(campo):
    for k, v in campo.items():
        if k.startswith("value"):
            if k == "valueObject":
                return {n: valor(c) for n, c in v.items()}
            if k == "valueArray":
                return [valor(c) for c in v]
            return v
    return None

conteudo = status["result"]["contents"][0]
print("\nCampos extraídos:")
for nome, campo in conteudo.get("fields", {}).items():
    print(f"  {nome:<24} ({campo.get('type')}) = {json.dumps(valor(campo), ensure_ascii=False)[:70]}"
          f"  conf={campo.get('confidence', '-')}")
