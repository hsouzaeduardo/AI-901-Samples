"""
Módulo 05 - Tópico: Modelos multimodais para análise de imagem (imagem -> texto)
"Modelos multimodais dão suporte para entrada de várias partes: texto + imagem.
Imagens podem ser URLs ou dados codificados em base64."

  python 05_analise_imagem.py foto.jpg                     -> arquivo local (base64)
  python 05_analise_imagem.py https://.../foto.jpg          -> URL pública
  python 05_analise_imagem.py foto.jpg "Que sobremesas posso fazer com isso?"
Sem argumentos, usa saidas/imagem_gerada.png (crie com 06_gerar_imagem.py).
"""
import base64
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

origem = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "saidas" / "imagem_gerada.png")
pergunta = sys.argv[2] if len(sys.argv) > 2 else (
    "Descreva a imagem em 2 frases, liste os objetos que aparecem e sugira um texto alternativo "
    "(alt text) para acessibilidade.")

if origem.startswith(("http://", "https://")):
    image_url = origem
else:
    if not Path(origem).exists():
        sys.exit(f"Imagem {origem} não encontrada. Passe um caminho/URL ou rode 06_gerar_imagem.py")
    mime = mimetypes.guess_type(origem)[0] or "image/png"
    dados = base64.b64encode(Path(origem).read_bytes()).decode("utf-8")
    image_url = f"data:{mime};base64,{dados}"

response = client.responses.create(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],        # precisa ser um modelo com visão (ex.: gpt-4.1-mini)
    instructions="Você é um assistente que descreve imagens em português.",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": pergunta},
            {"type": "input_image", "image_url": image_url},
        ],
    }],
)
print(f"Imagem: {origem}\nPergunta: {pergunta}\n")
print(response.output_text)        # mais robusto que response.output[0].content[0].text
