# Módulo 04 — Fala de IA

Slides: `AI-901T00-PowerPoint_04.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-ai-speech-concepts> e <https://aka.ms/mslearn-get-started-ai-speech>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | Reconhecimento de fala: do áudio ao texto (5 etapas) | `01_pipeline_reconhecimento.py` | Offline |
| 2 | Sintetização de voz: do texto ao áudio (5 etapas) | `02_pipeline_sintese.py` | Offline |
| 3 | Implementação da sintetização de voz (TTS) | `03_tts.py` | Azure |
| 4 | Implementação do reconhecimento de fala (STT) | `04_stt.py` | Azure |
| 5 | Criação de um agente capaz de falar (Voice Live) | `05_voice_live.py` | Azure |

**Soluções habilitadas para fala (slide 4):** o par `03_tts.py` → `04_stt.py` cobre os dois sentidos. O texto de exemplo é uma notificação de pedido, um caso de uso de TTS. A transcrição é um caso de uso de STT.

## Destaques offline

**`01_pipeline_reconhecimento.py`:** gera a forma de onda com numpy (captura), calcula a FFT em janelas de 25 ms (pré-processamento), mapeia quadros para fonemas (modelo acústico) e escolhe a frase mais provável entre os homófonos (modelo de linguagem):
```
fonemas: /nais/ /tu/ /bi/ /hir/
   nice to be here        P = 0.201600
   nights to be here      P = 0.038400
5) Pós-processamento: 'nice to be here' -> 'Nice to be here!'
```

**`02_pipeline_sintese.py`:** faz a normalização em pt-BR:
```
"Dr. Silva é às 15:30 do dia 03/12. O valor é R$ 250,50."
-> "doutor Silva é às quinze horas e trinta minutos do dia três de dezembro.
    O valor é duzentos e cinquenta reais e cinquenta centavos."
```
Depois aplica regras de grafema → fonema e gera **prosódia em SSML** (pergunta com tom subindo, horário com ênfase). Por fim grava um **WAV PCM16** (codificação da forma de onda).

## Fluxo em aula (Azure)

```bash
python 02_pipeline_sintese.py     # gera saidas/consulta.ssml
python 03_tts.py --ssml           # fala o SSML em saidas/mensagem.wav
python 04_stt.py                  # transcreve o arquivo de volta para texto
python 04_stt.py --microfone      # fale você
python 05_voice_live.py           # conversa em tempo real (precisa de pyaudio e fone de ouvido)
```

`05_voice_live.py` é uma versão compacta do `codeSample.py` do lab. Mostra a conexão em tempo real, o streaming de áudio, a redução de ruído, o cancelamento de eco e as **interrupções**: quando o usuário fala, o áudio do agente é descartado e a resposta é cancelada. Com `--agente NOME --projeto PROJETO`, conecta a um agente do Foundry em vez de um modelo.
