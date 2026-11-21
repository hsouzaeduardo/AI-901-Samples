"""
Módulo 06 - Tópico: Extração de campo e mapeamento com IA GENERATIVA
(verificação de conhecimento: "Como a IA generativa aprimora o processo de extração?
 -> usando modelos de linguagem semântica para combinar valores extraídos com campos")

O texto de OCR abaixo vem "sujo" (O/0 trocados, abreviações, rótulos diferentes).
Regras fixas (02_mapeamento_campos.py) quebrariam; o modelo entende o SIGNIFICADO e
preenche um esquema JSON estrito.

  python 03_extracao_com_llm.py              -> texto de OCR embutido
  python 03_extracao_com_llm.py recibo.jpg   -> foto de um recibo (modelo multimodal)
"""
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "MODEL_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")
client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])

OCR_SUJO = """PADARIA E C0NFEITARIA P0NTO D0CE
CNPJ 11.222.333/0001-81
Emissao 5 de nov. de 2026 - 07h15
2un PA0 FRANCES ......... 1,60
1un CAFE C/ LEITE GDE ... 7,90
1 SALGAD0 ASSAD0 ........ 8,50
VLR A PAGAR ............ R$ 18,00
PIX"""

ESQUEMA = {
    "type": "json_schema", "name": "recibo", "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False,
        "required": ["fornecedor", "cnpj", "data", "itens", "total", "forma_pagamento", "categoria"],
        "properties": {
            "fornecedor": {"type": "string"},
            "cnpj": {"type": "string", "description": "apenas dígitos"},
            "data": {"type": "string", "description": "formato AAAA-MM-DD"},
            "itens": {"type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["descricao", "quantidade", "valor"],
                "properties": {"descricao": {"type": "string"}, "quantidade": {"type": "number"},
                               "valor": {"type": "number"}}}},
            "total": {"type": "number"},
            "forma_pagamento": {"type": "string"},
            "categoria": {"type": "string", "enum": ["alimentação", "transporte", "hospedagem", "outros"]},
        },
    },
}
INSTRUCOES = ("Você extrai dados de recibos. Corrija erros óbvios de OCR (ex.: 0 no lugar de O). "
              "Se um campo não existir no documento, use string vazia ou 0.")

if len(sys.argv) > 1:
    caminho = Path(sys.argv[1])
    mime = mimetypes.guess_type(caminho)[0] or "image/jpeg"
    conteudo = [{"type": "input_text", "text": "Extraia os dados deste recibo."},
                {"type": "input_image",
                 "image_url": f"data:{mime};base64,{base64.b64encode(caminho.read_bytes()).decode()}"}]
    entrada = [{"role": "user", "content": conteudo}]
    print("Entrada: imagem", caminho)
else:
    entrada = f"Extraia os dados deste texto de OCR:\n{OCR_SUJO}"
    print("Entrada (OCR com erros):\n" + OCR_SUJO)

r = client.responses.create(model=os.environ["MODEL_DEPLOYMENT_NAME"], instructions=INSTRUCOES,
                            input=entrada, text={"format": ESQUEMA})
dados = json.loads(r.output_text)
print("\nSaída estruturada:\n" + json.dumps(dados, indent=2, ensure_ascii=False))
soma = round(sum(i["valor"] for i in dados["itens"]), 2)
print(f"\nValidação: soma dos itens = {soma} | total = {dados['total']} -> "
      f"{'OK' if soma == dados['total'] else 'DIVERGENTE - revisar'}")
print("Para produção com confiança por campo e fundamentação na fonte, use o")
print("Content Understanding: 04_content_understanding_sdk.py")
