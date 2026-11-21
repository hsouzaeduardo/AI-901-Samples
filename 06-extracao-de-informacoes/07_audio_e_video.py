"""
Módulo 06 - Tópico: Extração de informações de ÁUDIO e VÍDEO
"Use analisadores pré-definidos e personalizados em cenários de áudio e vídeo:
análise pós-chamada, automação de mensagens de voz, transcrição e resumo de
chamadas de vídeo, análise de gravação de vídeo..."

1) Lista os analisadores disponíveis para áudio/vídeo no seu recurso.
2) Analisa um áudio:
   - padrão: o WAV gerado no módulo 04 (04-fala/saidas/mensagem.wav) enviado em binário
   - ou uma URL pública de áudio/vídeo passada como argumento

  python 07_audio_e_video.py
  python 07_audio_e_video.py prebuilt-callCenter https://.../ligacao.wav
"""
import os
import sys
from pathlib import Path

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint, key = os.getenv("AZURE_SERVICES_AI_ENDPOINT"), os.getenv("AZURE_FOUNDRY_KEY")
if not (endpoint and key):
    sys.exit("Defina AZURE_SERVICES_AI_ENDPOINT e AZURE_FOUNDRY_KEY no .env")
client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(key))

print("Analisadores de áudio/vídeo disponíveis:")
for a in client.list_analyzers():
    if any(k in a.analyzer_id.lower() for k in ("audio", "video", "call")):
        print(f"  - {a.analyzer_id:<28} {(a.description or '')[:70]}")

analisador = sys.argv[1] if len(sys.argv) > 1 else "prebuilt-callCenter"
if len(sys.argv) > 2:
    print(f"\nAnalisando URL com {analisador}...")
    poller = client.begin_analyze(analyzer_id=analisador, inputs=[AnalysisInput(url=sys.argv[2])])
else:
    wav = Path(__file__).parents[1] / "04-fala" / "saidas" / "mensagem.wav"
    if not wav.exists():
        sys.exit(f"{wav} não existe. Gere com: python 04-fala/03_tts.py  (ou passe uma URL)")
    print(f"\nAnalisando {wav.name} com {analisador}...")
    poller = client.begin_analyze_binary(analyzer_id=analisador, binary_input=wav.read_bytes(),
                                         content_type="audio/wav")

conteudo = poller.result().contents[0]
print("\n--- Transcrição (markdown) ---")
print((conteudo.markdown or "")[:800])
print("\n--- Campos (resumo, tópicos, sentimento...) ---")
for nome, c in (conteudo.fields or {}).items():
    print(f"  {nome:<18} {str(c.value)[:90]}")
