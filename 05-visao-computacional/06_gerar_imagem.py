"""
Módulo 05 - Tópico: Modelos de geração de imagem e vídeo -> Geração de IMAGEM
"Pesquise nos Modelos do Foundry por modelos de inferência 'texto para imagem'
(ex.: modelos de imagem GPT da OpenAI, MAI-Image, FLUX)."

Pré-requisito: implantar um modelo de texto-para-imagem (ex.: gpt-image-1) e
definir IMAGE_DEPLOYMENT_NAME no .env.

  python 06_gerar_imagem.py
  python 06_gerar_imagem.py "Um computador antigo com monitor CRT verde, foto de estúdio"

A imagem é salva em saidas/imagem_gerada.png. Depois analise-a com 05_analise_imagem.py
"""
import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "IMAGE_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")
client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])

prompt = sys.argv[1] if len(sys.argv) > 1 else (
    "Uma fruteira de madeira com maçãs vermelhas e bananas, luz natural de janela, estilo fotográfico")

img = client.images.generate(
    model=os.environ["IMAGE_DEPLOYMENT_NAME"],
    prompt=prompt,
    n=1,
    size="1024x1024",
)

saida = Path(__file__).parent / "saidas"
saida.mkdir(exist_ok=True)
arquivo = saida / "imagem_gerada.png"
dado = img.data[0]
if dado.b64_json:                                   # modelos gpt-image devolvem base64
    arquivo.write_bytes(base64.b64decode(dado.b64_json))
else:                                               # outros modelos podem devolver uma URL
    arquivo.write_bytes(requests.get(dado.url, timeout=60).content)
print(f"Prompt: {prompt}\nImagem salva em {arquivo}")
if getattr(dado, "revised_prompt", None):
    print("Prompt revisado pelo modelo:", dado.revised_prompt)
