"""
Módulo 02 - Tópico: Modelos de IA generativa (tokens e embeddings)
"Tokens são codificados como embeddings baseados em vetor... Tokens semanticamente
semelhantes têm direções semelhantes."

Parte 1: tokenização - texto vira uma sequência de IDs numéricos.
Parte 2: embeddings - cada token vira um vetor; mede-se a semelhança pelo cosseno.
Usa a frase e vetores ilustrativos do slide 5. Executa offline (numpy).

  python 01_tokens_e_embeddings.py
"""
import re

import numpy as np

frase = "I heard a dog bark at a cat"

# ---------------- Parte 1: tokenização ----------------
print("=== 1) Tokenização ===")
tokens = re.findall(r"\w+|[^\w\s]", frase.lower())
vocabulario = {tok: i for i, tok in enumerate(dict.fromkeys(tokens))}
print("Tokens  :", tokens)
print("IDs     :", [vocabulario[t] for t in tokens])
print("Vocab.  :", vocabulario)

# Modelos reais usam SUBPALAVRAS (BPE): palavras raras são quebradas em pedaços.
def subpalavras(palavra, conhecidas=("skate", "board", "pup", "py", "un", "believ", "able")):
    pedacos, resto = [], palavra
    while resto:
        for p in sorted(conhecidas, key=len, reverse=True):
            if resto.startswith(p):
                pedacos.append(p)
                resto = resto[len(p):]
                break
        else:
            pedacos.append(resto[0])
            resto = resto[1:]
    return pedacos
for p in ("skateboard", "puppy", "unbelievable"):
    print(f"Subpalavras de '{p}': {subpalavras(p)}")

# ---------------- Parte 2: embeddings ----------------
print("\n=== 2) Embeddings (vetores ilustrativos de 3 dimensões, como no slide) ===")
emb = {
    "dog":        np.array([10, 3, 2]),
    "puppy":      np.array([5, 3, 2]),
    "cat":        np.array([10, 3, 1]),
    "bark":       np.array([9, 2, 10]),
    "heard":      np.array([-3, 5, 5]),
    "skateboard": np.array([-3, -2, 2]),
    "car":        np.array([-5, -1, 1]),
}

def cosseno(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

palavras = list(emb)
print(" " * 11 + "".join(f"{p[:9]:>10}" for p in palavras))
for p1 in palavras:
    print(f"{p1:<11}" + "".join(f"{cosseno(emb[p1], emb[p2]):>10.2f}" for p2 in palavras))

print("\nVizinhos mais próximos (mesma DIREÇÃO = significado parecido):")
for alvo in ("dog", "skateboard"):
    ranking = sorted((p for p in palavras if p != alvo), key=lambda p: -cosseno(emb[alvo], emb[p]))
    print(f"  {alvo:<11} -> {ranking[:3]}")

print("\nEm modelos reais os embeddings têm centenas/milhares de dimensões e são")
print("aprendidos no treinamento. Veja 03-analise-de-texto/05_embeddings_azure.py.")
