"""
Módulo 04 - Tópico: Implementação da sintetização de voz (texto -> fala)
"Use o SDK de Fala do Azure para gerar saída de alto-falante ou arquivo de áudio
a partir do texto." Escolher a VOZ faz parte da configuração.

  python 03_tts.py                 -> texto simples para saidas/mensagem.wav
  python 03_tts.py --ssml          -> usa saidas/consulta.ssml (gerado por 02_pipeline_sintese.py)
  python 03_tts.py --alto-falante  -> toca no alto-falante padrão
  python 03_tts.py --voz pt-BR-AntonioNeural

  pip install azure-cognitiveservices-speech
"""
import os
import sys
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
key = os.getenv("AZURE_FOUNDRY_KEY")
endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT")
if not (key and endpoint):
    sys.exit("Defina AZURE_FOUNDRY_KEY e AZURE_AI_SERVICES_ENDPOINT no .env")

SAIDAS = Path(__file__).parent / "saidas"
SAIDAS.mkdir(exist_ok=True)
voz = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else os.getenv("VOICE_NAME", "pt-BR-FranciscaNeural")

speech_config = speechsdk.SpeechConfig(subscription=key, endpoint=endpoint)
speech_config.speech_synthesis_voice_name = voz

if "--alto-falante" in sys.argv:
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    destino = "alto-falante"
else:
    arquivo = SAIDAS / "mensagem.wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(arquivo))
    destino = str(arquivo)

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

if "--ssml" in sys.argv:
    ssml_path = SAIDAS / "consulta.ssml"
    if not ssml_path.exists():
        sys.exit("Rode antes: python 02_pipeline_sintese.py")
    resultado = synthesizer.speak_ssml_async(ssml_path.read_text(encoding="utf-8")).get()
else:
    texto = ("Olá! Seu pedido número 4 5 2 1 foi confirmado e será entregue amanhã, "
             "entre nove e doze horas. Obrigado por comprar com a Contoso.")
    resultado = synthesizer.speak_text_async(texto).get()

if resultado.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"Áudio gerado com a voz {voz} -> {destino} ({len(resultado.audio_data)} bytes)")
    print("Dica: transcreva este arquivo de volta com:  python 04_stt.py")
elif resultado.reason == speechsdk.ResultReason.Canceled:
    det = resultado.cancellation_details
    print("Síntese cancelada:", det.reason, det.error_details)
