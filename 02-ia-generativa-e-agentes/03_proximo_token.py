"""
Módulo 02 - Tópicos: "O que é a IA generativa?" e o parâmetro de "criatividade"
"LLMs preveem o que virá a seguir, um token por vez - parecido com o texto
preditivo superpotente do seu celular."

Treina um modelo de linguagem minúsculo (bigramas) num corpus de 6 frases e gera
texto token a token. Mostra o efeito da TEMPERATURA (o parâmetro "criatividade"
do slide "Usar um modelo de IA generativa"). Offline, só numpy.

  python 03_proximo_token.py
"""
from collections import Counter, defaultdict

import numpy as np

corpus = [
    "o agente consulta a base de conhecimento e responde ao usuário",
    "o agente usa ferramentas para executar ações",
    "o modelo gera texto a partir de um prompt",
    "o modelo gera código a partir de instruções",
    "o usuário envia um prompt e o modelo responde",
    "o agente responde ao usuário com base nas instruções",
]

# "Treinamento": conta quantas vezes cada palavra vem depois de outra
contagens = defaultdict(Counter)
for frase in corpus:
    palavras = ["<início>"] + frase.split() + ["<fim>"]
    for atual, proxima in zip(palavras, palavras[1:]):
        contagens[atual][proxima] += 1

def distribuicao(palavra, temperatura):
    candidatos = list(contagens[palavra])
    freq = np.array([contagens[palavra][c] for c in candidatos], dtype=float)
    logits = np.log(freq)
    probs = np.exp(logits / temperatura)
    return candidatos, probs / probs.sum()

print("Probabilidades do próximo token depois de 'modelo' e 'agente':")
for p in ("modelo", "agente"):
    cands, probs = distribuicao(p, 1.0)
    print(f"  {p!r}: " + ", ".join(f"{c}={pr:.0%}" for c, pr in zip(cands, probs)))

def gerar(inicio, temperatura, rng, max_tokens=12):
    saida, atual = [inicio], inicio
    for _ in range(max_tokens):        # max_tokens = limite de tamanho da resposta
        if not contagens[atual]:
            break
        cands, probs = distribuicao(atual, temperatura)
        atual = cands[int(np.argmax(probs))] if temperatura < 0.05 else rng.choice(cands, p=probs)
        if atual == "<fim>":
            break
        saida.append(atual)
    return " ".join(saida)

rng = np.random.default_rng(7)
for temp in (0.01, 1.0, 2.0):
    print(f"\nTemperatura {temp}:")
    for _ in range(3):
        print("   ", gerar("o", temp, rng))
print("\nTemperatura baixa = respostas previsíveis e repetidas;")
print("temperatura alta = mais variedade (e mais risco de incoerência).")
