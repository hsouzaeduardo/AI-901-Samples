"""
Módulo 04 - Tópico: Sintetização de voz - "De texto para áudio..."
  1) Texto fonte ............ documento ou saída de um app/modelo
  2) Normalização ........... expandir abreviações, soletrar números, horas, datas, moedas
  3) Modelagem linguística .. texto normalizado -> fonemas
  4) Geração de prosódia .... tom, ritmo, pausas e ênfase (aqui: SSML)
  5) Codificação de forma de onda -> sinal de áudio digital (.wav)

Gera:  saidas/consulta.ssml (use com 03_tts.py --ssml)  e  saidas/prosodia_demo.wav
Offline (numpy + stdlib).

  python 02_pipeline_sintese.py
"""
import re
import wave
from pathlib import Path

import numpy as np

SAIDAS = Path(__file__).parent / "saidas"
SAIDAS.mkdir(exist_ok=True)

# ---------- 1) Texto fonte ----------
texto = "Sua consulta com o Dr. Silva é às 15:30 do dia 03/12. O valor é R$ 250,50. Confirma?"
print("1) Texto fonte:\n  ", texto)

# ---------- 2) Normalização ----------
UNID = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze " \
       "dezesseis dezessete dezoito dezenove".split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
CEM = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()
MESES = "_ janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()

def extenso(n: int) -> str:
    if n < 20:
        return UNID[n]
    if n < 100:
        return DEZ[n // 10] + ("" if n % 10 == 0 else " e " + UNID[n % 10])
    if n == 100:
        return "cem"
    if n < 1000:
        return CEM[n // 100] + ("" if n % 100 == 0 else " e " + extenso(n % 100))
    mil = "mil" if n // 1000 == 1 else extenso(n // 1000) + " mil"
    return mil + ("" if n % 1000 == 0 else " e " + extenso(n % 1000))

def normalizar(t: str) -> str:
    t = re.sub(r"\bDr\.", "doutor", t)
    t = re.sub(r"\bSra\.", "senhora", t)
    t = re.sub(r"(\d{1,2}):(\d{2})",
               lambda m: f"{extenso(int(m[1]))} horas" + (f" e {extenso(int(m[2]))} minutos" if int(m[2]) else ""), t)
    t = re.sub(r"(\d{1,2})/(\d{1,2})", lambda m: f"{extenso(int(m[1]))} de {MESES[int(m[2])]}", t)
    t = re.sub(r"R\$ ?(\d+),(\d{2})",
               lambda m: f"{extenso(int(m[1]))} reais" + (f" e {extenso(int(m[2]))} centavos" if int(m[2]) else ""), t)
    return t

normalizado = normalizar(texto)
print("2) Normalização:\n  ", normalizado)
print("   (exemplo do slide em inglês: 'Dr. ... 3:00pm' -> 'doctor ... three o'clock P M')")

# ---------- 3) Modelagem linguística (regras simplificadas de grafema -> fonema) ----------
# A ORDEM importa: dígrafos primeiro; "s" entre vogais vira /z/ antes de "ss" virar /s/.
REGRAS = [("ch", "x"), ("lh", "lj"), ("nh", "nj"), ("ão", "aw~"), ("qu", "k"), ("ç", "s"),
          (r"c(?=[eiéí])", "s"), ("c", "k"), (r"(?<=[aeiou])s(?=[aeiou])", "z"), ("ss", "s"),
          ("rr", "R"), (r"e\b", "i"), (r"o\b", "u")]
def fonemas(palavra):
    p = palavra.lower()
    for padrao, som in REGRAS:
        p = re.sub(padrao, som, p)
    return "/" + p + "/"
amostra = "o carro chegou cedo à casa nessa manhã de trabalho".split()
print("3) Modelagem linguística (exemplo):", " ".join(fonemas(p) for p in amostra))

# ---------- 4) Prosódia em SSML ----------
frases = [f.strip() for f in re.split(r"(?<=[.?!])\s+", normalizado) if f.strip()]
corpo = []
for f in frases:
    if f.endswith("?"):
        corpo.append(f'<prosody pitch="+15%" rate="-5%">{f}</prosody>')      # pergunta: tom sobe
    elif "horas" in f:
        hora = re.search(r"às (.+? minutos|.+? horas)", f)
        f = f.replace(hora[1], f'<emphasis level="strong">{hora[1]}</emphasis>') if hora else f
        corpo.append(f'<prosody rate="-10%">{f}</prosody>')                    # informação crítica: devagar
    else:
        corpo.append(f)
    corpo.append('<break time="400ms"/>')
ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">\n'
        '  <voice name="pt-BR-FranciscaNeural">\n    ' + "\n    ".join(corpo) +
        "\n  </voice>\n</speak>\n")
(SAIDAS / "consulta.ssml").write_text(ssml, encoding="utf-8")
print("4) Prosódia (SSML salvo em saidas/consulta.ssml):\n" + ssml)

# ---------- 5) Codificação de forma de onda ----------
# Demonstração: "melodia" da frase - tom estável na afirmação e subindo na pergunta.
TAXA = 16000
def tom(freq_ini, freq_fim, dur):
    t = np.arange(int(TAXA * dur)) / TAXA
    freq = np.linspace(freq_ini, freq_fim, t.size)
    return 0.4 * np.sin(2 * np.pi * np.cumsum(freq) / TAXA)
sinal = np.concatenate([tom(200, 190, 0.6), np.zeros(int(0.2 * TAXA)), tom(200, 320, 0.6)])
amostras = (sinal * 32767).astype(np.int16)
with wave.open(str(SAIDAS / "prosodia_demo.wav"), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)          # 16 bits por amostra (PCM16)
    w.setframerate(TAXA)
    w.writeframes(amostras.tobytes())
print(f"5) Forma de onda: {amostras.size} amostras PCM16 em saidas/prosodia_demo.wav "
      "(ouça: afirmação x pergunta)")
