"""
Módulo 04 - Tópico: Criação de um agente capaz de falar (Voice Live)
"Fala em tempo real com um modelo de IA generativa que tem instruções e ferramentas.
Suporte a fluxo contínuo de conversa, com INTERRUPÇÕES e REDUÇÃO DE RUÍDO."

Versão compacta do exemplo do laboratório (data/voice-live/codeSample.py do repo
MicrosoftLearning/mslearn-ai-fundamentals). O SDK azure-ai-voicelive:
  - abre uma conexão WebSocket em tempo real
  - transmite o áudio do microfone e recebe o áudio da resposta
  - detecta quando o usuário começa a falar (VAD) -> permite interromper o agente

  pip install "azure-ai-voicelive[aiohttp]" pyaudio
  python 05_voice_live.py                                   -> modo MODELO (chave de API)
  python 05_voice_live.py --agente agente-despesas --projeto meu-projeto
                                                            -> modo AGENTE do Foundry (az login)
Ctrl+C para sair. Use fone de ouvido para evitar eco.
"""
import asyncio
import base64
import os
import queue
import sys

import pyaudio
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (AudioEchoCancellation, AudioInputTranscriptionOptions,
                                       AudioNoiseReduction, AzureStandardVoice, InputAudioFormat,
                                       Modality, OutputAudioFormat, RequestSession,
                                       ServerEventType, ServerVad)
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
ENDPOINT = os.getenv("AZURE_SERVICES_AI_ENDPOINT") or sys.exit("Defina AZURE_SERVICES_AI_ENDPOINT no .env")
VOZ = os.getenv("VOICE_NAME", "pt-BR-FranciscaNeural")
TAXA, BLOCO = 24000, 1200                       # PCM16, 24 kHz, mono, blocos de 50 ms


def argumento(nome):
    return sys.argv[sys.argv.index(nome) + 1] if nome in sys.argv else None


class Audio:
    """Captura do microfone e reprodução no alto-falante (threads do PyAudio)."""

    def __init__(self, conexao, loop):
        self.pa, self.conexao, self.loop = pyaudio.PyAudio(), conexao, loop
        self.fila: queue.Queue[bytes] = queue.Queue()
        self.restante = b""
        self.entrada = self.saida = None

    def iniciar_microfone(self):
        def captura(dados, *_):
            b64 = base64.b64encode(dados).decode()
            asyncio.run_coroutine_threadsafe(self.conexao.input_audio_buffer.append(audio=b64), self.loop)
            return None, pyaudio.paContinue
        self.entrada = self.pa.open(format=pyaudio.paInt16, channels=1, rate=TAXA, input=True,
                                    frames_per_buffer=BLOCO, stream_callback=captura)

    def iniciar_alto_falante(self):
        def reproducao(_, n_quadros, *__):
            precisa = n_quadros * 2
            while len(self.restante) < precisa and not self.fila.empty():
                self.restante += self.fila.get_nowait()
            saida, self.restante = self.restante[:precisa], self.restante[precisa:]
            return saida.ljust(precisa, b"\0"), pyaudio.paContinue
        self.saida = self.pa.open(format=pyaudio.paInt16, channels=1, rate=TAXA, output=True,
                                  frames_per_buffer=BLOCO, stream_callback=reproducao)

    def interromper(self):
        """Usuário começou a falar: descarta o áudio pendente do agente."""
        self.restante = b""
        while not self.fila.empty():
            self.fila.get_nowait()

    def encerrar(self):
        for s in (self.entrada, self.saida):
            if s:
                s.stop_stream()
                s.close()
        self.pa.terminate()


async def main():
    agente, projeto = argumento("--agente"), argumento("--projeto")
    if agente:
        from azure.identity.aio import DefaultAzureCredential
        credencial = DefaultAzureCredential()
        conexao_ctx = connect(endpoint=ENDPOINT, credential=credencial,
                              agent_name=agente, project_name=projeto)
        instrucoes = None          # as instruções e ferramentas vêm do AGENTE
    else:
        credencial = AzureKeyCredential(os.getenv("AZURE_FOUNDRY_KEY") or sys.exit("Defina AZURE_FOUNDRY_KEY"))
        conexao_ctx = connect(endpoint=ENDPOINT, credential=credencial,
                              model=os.getenv("VOICELIVE_MODEL", "gpt-realtime"))
        instrucoes = ("Você é um assistente simpático da Contoso. Responda em português do Brasil, "
                      "com frases curtas, como numa conversa por telefone.")

    async with conexao_ctx as conexao:
        audio = Audio(conexao, asyncio.get_running_loop())
        sessao = dict(
            modalities=[Modality.TEXT, Modality.AUDIO],
            voice=AzureStandardVoice(name=VOZ),
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
            input_audio_echo_cancellation=AudioEchoCancellation(),
            input_audio_noise_reduction=AudioNoiseReduction(type="azure_deep_noise_suppression"),
            input_audio_transcription=AudioInputTranscriptionOptions(model="azure-speech", language="pt-BR"),
        )
        if instrucoes:
            sessao["instructions"] = instrucoes
        await conexao.session.update(session=RequestSession(**sessao))
        audio.iniciar_alto_falante()
        respondendo = False
        print("Conectado. Pode falar! (Ctrl+C para sair)")

        try:
            async for evento in conexao:
                if evento.type == ServerEventType.SESSION_UPDATED:
                    audio.iniciar_microfone()
                elif evento.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                    print("[ouvindo...]")
                    audio.interromper()                      # INTERRUPÇÃO (barge-in)
                    if respondendo:
                        try:
                            await conexao.response.cancel()
                        except Exception:
                            pass
                elif evento.type == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                    print("Você  :", evento.transcript)
                elif evento.type == ServerEventType.RESPONSE_CREATED:
                    respondendo = True
                elif evento.type == ServerEventType.RESPONSE_AUDIO_DELTA:
                    audio.fila.put(evento.delta)
                elif evento.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                    print("Agente:", evento.transcript)
                elif evento.type == ServerEventType.RESPONSE_DONE:
                    respondendo = False
                elif evento.type == ServerEventType.ERROR:
                    print("Erro:", evento.error.message)
        finally:
            audio.encerrar()
            if agente:
                await credencial.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAté logo!")
