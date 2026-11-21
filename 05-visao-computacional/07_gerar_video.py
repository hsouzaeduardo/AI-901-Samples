"""
Módulo 05 - Tópico: Modelos de geração de imagem e vídeo -> Geração de VÍDEO
"Pesquise nos Modelos do Foundry por modelos de inferência 'geração de vídeo' (ex.: Sora)."

Por que é um TRABALHO ASSÍNCRONO? (verificação de conhecimento, questão 3)
Gerar vídeo exige muito processamento e leva tempo - por isso a API devolve um ID
de trabalho na hora, e o cliente CONSULTA o status até o vídeo ficar pronto.

    create() -> status "queued" -> "in_progress" -> "completed" -> download_content()

Pré-requisito: implantar um modelo de vídeo (ex.: sora-2) e definir
VIDEO_DEPLOYMENT_NAME no .env (sujeito à disponibilidade regional do modelo).

  python 07_gerar_video.py
  python 07_gerar_video.py "Um gato laranja dormindo ao lado de um computador antigo"
"""
import os
import sys
import time
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "VIDEO_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")
client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])

prompt = sys.argv[1] if len(sys.argv) > 1 else (
    "Close de um disquete sendo inserido num computador dos anos 80; a tela acende em verde")

# 1) Enviar o trabalho - a resposta chega imediatamente, mas o vídeo ainda NÃO existe
video = client.videos.create(
    model=os.environ["VIDEO_DEPLOYMENT_NAME"],
    prompt=prompt,
    seconds="4",
    size="1280x720",
)
print(f"Trabalho criado: id={video.id} status={video.status}")

# 2) Consultar (polling) até concluir
inicio = time.time()
while video.status in ("queued", "in_progress"):
    time.sleep(10)
    video = client.videos.retrieve(video.id)
    progresso = getattr(video, "progress", None)
    print(f"  {time.time() - inicio:5.0f}s  status={video.status}" + (f"  {progresso}%" if progresso else ""))

# 3) Baixar o resultado
if video.status == "completed":
    destino = Path(__file__).parent / "saidas"
    destino.mkdir(exist_ok=True)
    arquivo = destino / "video_gerado.mp4"
    client.videos.download_content(video.id).write_to_file(str(arquivo))
    print(f"Vídeo salvo em {arquivo}")
else:
    print("Falhou:", getattr(video, "error", None))
