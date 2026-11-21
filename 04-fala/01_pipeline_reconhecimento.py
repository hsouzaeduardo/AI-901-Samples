"""
Módulo 04 - Tópico: Reconhecimento de fala - "Do áudio ao texto..."
  1) Captura de áudio ....... sinal analógico -> forma de onda digital (amostras)
  2) Pré-processamento ...... intensidade do sinal em faixas de frequência (FFT)
  3) Modelagem acústica ..... características -> fonemas
  4) Modelagem de linguagem . fonemas -> sequência de palavras MAIS PROVÁVEL
  5) Pós-processamento ...... normalizar e formatar o texto

Simulação didática com numpy: cada "fonema" é um som com 2 frequências
características (como os formantes da voz). Reproduz o exemplo do slide:
/nais/ /tu/ /bi/ /hir/ -> "nights two bee hear"?  ou  "nice to be here"?

  python 01_pipeline_reconhecimento.py
"""
import itertools

import numpy as np

TAXA = 16000                     # amostras por segundo (16 kHz, típico em fala)
rng = np.random.default_rng(0)

# "Assinatura" acústica de cada fonema: duas frequências dominantes (Hz)
FONEMAS = {"nais": (300, 2300), "tu": (350, 900), "bi": (280, 2600), "hir": (450, 1800)}

# ---------- 1) Captura: gera a forma de onda digital da frase falada ----------
def som(f1, f2, dur=0.25):
    t = np.arange(int(TAXA * dur)) / TAXA
    return np.sin(2 * np.pi * f1 * t) + 0.6 * np.sin(2 * np.pi * f2 * t)

falado = ["nais", "tu", "bi", "hir"]
onda = np.concatenate([som(*FONEMAS[f]) for f in falado])
onda += rng.normal(0, 0.4, onda.size)        # ruído do ambiente
print(f"1) Captura: {onda.size} amostras ({onda.size / TAXA:.2f}s a {TAXA} Hz). "
      f"Primeiras: {np.round(onda[:5], 2)}")

# ---------- 2) Pré-processamento: janelas de 25 ms + espectro (FFT) ----------
JANELA = int(0.025 * TAXA)
quadros = onda[: onda.size // JANELA * JANELA].reshape(-1, JANELA)
espectro = np.abs(np.fft.rfft(quadros * np.hanning(JANELA), axis=1))
freqs = np.fft.rfftfreq(JANELA, 1 / TAXA)
print(f"2) Pré-processamento: {len(quadros)} quadros de 25 ms -> vetor de {espectro.shape[1]} "
      f"intensidades por faixa de frequência")

# ---------- 3) Modelagem acústica: quadro -> fonema mais compatível ----------
def caracteristica(f1, f2):
    """Vetor de intensidade esperado para um fonema (picos em f1 e f2)."""
    v = np.exp(-((freqs - f1) / 120) ** 2) + 0.6 * np.exp(-((freqs - f2) / 120) ** 2)
    return v / np.linalg.norm(v)

modelos = {f: caracteristica(*fr) for f, fr in FONEMAS.items()}
reconhecidos = []
for q in espectro:
    q = q / np.linalg.norm(q)
    reconhecidos.append(max(modelos, key=lambda f: q @ modelos[f]))
fonemas = [k for k, _ in itertools.groupby(reconhecidos)]     # junta quadros repetidos
print(f"3) Modelagem acústica: quadros -> {reconhecidos[:12]}...")
print(f"   fonemas: {' '.join('/' + f + '/' for f in fonemas)}")

# ---------- 4) Modelagem de linguagem: homófonos -> frase mais provável ----------
CANDIDATOS = {"nais": ["nice", "nights"], "tu": ["to", "two", "too"],
              "bi": ["be", "bee"], "hir": ["here", "hear"]}
# probabilidades de bigramas (aprendidas de muito texto em um modelo real)
BIGRAMA = {("<s>", "nice"): .6, ("<s>", "nights"): .4, ("nice", "to"): .7, ("nice", "two"): .1,
           ("nights", "two"): .3, ("nights", "to"): .2, ("to", "be"): .8, ("two", "bee"): .1,
           ("two", "be"): .05, ("to", "bee"): .05, ("too", "be"): .1, ("be", "here"): .6,
           ("be", "hear"): .05, ("bee", "hear"): .02, ("bee", "here"): .02}
def prob(frase):
    p, ant = 1.0, "<s>"
    for w in frase:
        p *= BIGRAMA.get((ant, w), 0.001)
        ant = w
    return p

opcoes = sorted(itertools.product(*(CANDIDATOS[f] for f in fonemas)), key=prob, reverse=True)
print("4) Modelagem de linguagem - frases candidatas:")
for frase in opcoes[:4]:
    print(f"   {' '.join(frase):<22} P = {prob(frase):.6f}")
melhor = " ".join(opcoes[0])

# ---------- 5) Pós-processamento ----------
final = melhor[0].upper() + melhor[1:] + "!"
print(f"5) Pós-processamento: '{melhor}' -> '{final}'")
