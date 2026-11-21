"""
Módulo 03 - Tópico: Análise de texto e modelos de linguagem - MODELOS SEMÂNTICOS
"Tokens são vetorizados; o modelo é treinado para encapsular relações semânticas.
Essa é a base dos LLMs modernos."

Reproduz a tabela do slide 6 e verifica:
    dog + young = puppy      cat + young = kitten
Depois faz uma "busca semântica" pelo vizinho mais próximo. Offline (numpy).

  python 04_embeddings_semanticos.py
"""
import numpy as np

V = {
    "dog":    np.array([0.8, 0.6, 0.1]),
    "puppy":  np.array([0.9, 0.7, 0.4]),
    "cat":    np.array([0.7, 0.5, 0.2]),
    "kitten": np.array([0.8, 0.6, 0.5]),
    "young":  np.array([0.1, 0.1, 0.3]),
    "ball":   np.array([0.3, 0.9, 0.1]),
    "tree":   np.array([0.2, 0.1, 0.9]),
}

def cosseno(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def mais_proximo(vetor, excluir=()):
    candidatos = [p for p in V if p not in excluir]
    return max(candidatos, key=lambda p: cosseno(vetor, V[p]))

print("Aritmética de vetores (o significado vira matemática):")
for a, b in (("dog", "young"), ("cat", "young")):
    soma = V[a] + V[b]
    print(f"  {a} + {b} = {np.round(soma, 2)} -> palavra mais próxima: "
          f"{mais_proximo(soma, excluir=(a, b))}")

print("\nAnalogia - 'puppy está para dog assim como ? está para cat':")
r = V["puppy"] - V["dog"] + V["cat"]
print(f"  puppy - dog + cat = {np.round(r, 2)} -> {mais_proximo(r, excluir=('puppy', 'dog', 'cat'))}")

print("\nSimilaridade do cosseno com 'dog':")
for p in sorted(V, key=lambda p: -cosseno(V["dog"], V[p])):
    print(f"  {p:<7} {cosseno(V['dog'], V[p]):.3f}")
print("\nNa prática, use um modelo de embeddings do Foundry: 05_embeddings_azure.py")
