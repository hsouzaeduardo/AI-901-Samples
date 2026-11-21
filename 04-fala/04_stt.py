"""
Módulo 04 - Tópico: Implementação do reconhecimento de fala (fala -> texto)
"Use o SDK de Fala do Azure para transcrever a fala de arquivos de áudio ou da
entrada do microfone."

  python 04_stt.py                       -> transcreve saidas/mensagem.wav (gerado por 03_tts.py)
  python 04_stt.py --arquivo meu.wav     -> outro arquivo WAV (PCM 16 kHz mono recomendado)
  python 04_stt.py --microfone           -> fala uma frase no microfone
  python 04_stt.py --continuo            -> reconhecimento contínuo (áudios longos, reuniões)
"""
import os
import sys
import threading
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
key = os.getenv("AZURE_FOUNDRY_KEY")
endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT")
if not (key and endpoint):
    sys.exit("Defina AZURE_FOUNDRY_KEY e AZURE_AI_SERVICES_ENDPOINT no .env")

speech_config = speechsdk.SpeechConfig(subscription=key, endpoint=endpoint)
speech_config.speech_recognition_language = "pt-BR"

if "--microfone" in sys.argv:
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    print("Fale agora...")
else:
    arquivo = (sys.argv[sys.argv.index("--arquivo") + 1] if "--arquivo" in sys.argv
               else str(Path(__file__).parent / "saidas" / "mensagem.wav"))
    if not Path(arquivo).exists():
        sys.exit(f"Arquivo {arquivo} não encontrado. Gere um com: python 03_tts.py")
    audio_config = speechsdk.audio.AudioConfig(filename=arquivo)
    print("Transcrevendo", arquivo)

recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

if "--continuo" not in sys.argv:
    # recognize_once: até a primeira pausa (~15 s no máximo) - bom para comandos de voz
    r = recognizer.recognize_once_async().get()
    if r.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Texto reconhecido:", r.text)
    elif r.reason == speechsdk.ResultReason.NoMatch:
        print("Nenhuma fala reconhecida.")
    elif r.reason == speechsdk.ResultReason.Canceled:
        print("Cancelado:", r.cancellation_details.reason, r.cancellation_details.error_details)
else:
    # reconhecimento contínuo: eventos a cada frase reconhecida
    fim = threading.Event()
    recognizer.recognizing.connect(lambda e: print(f"  (parcial) {e.result.text}", end="\r"))
    recognizer.recognized.connect(lambda e: print(f"Frase: {e.result.text}" + " " * 20))
    recognizer.session_stopped.connect(lambda e: fim.set())
    recognizer.canceled.connect(lambda e: fim.set())
    recognizer.start_continuous_recognition()
    fim.wait()
    recognizer.stop_continuous_recognition()
