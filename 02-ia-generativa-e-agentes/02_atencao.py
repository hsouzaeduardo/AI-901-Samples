"""
Módulo 02 - Tópico: Modelos de IA generativa (atenção no transformador)
"Os valores de embeddings são codificados com atenção - para cada token, os valores
têm como base a influência avaliada dos tokens ao seu redor."

Implementa a atenção por produto escalar (scaled dot-product attention) em numpy:
    Atenção(Q, K, V) = softmax(Q·Kᵀ / √d) · V
Para simplificar, Q = K = V = embeddings normalizados (sem pesos aprendidos) e usamos
uma escala fixa no lugar de √d (num transformador real, Q, K e V vêm de projeções
aprendidas no treinamento).

  python 02_atencao.py
"""
import numpy as np

tokens = ["I", "heard", "a", "dog", "bark"]
E = np.array([
    [-5, -1, 1],   # I
    [-3, 5, 5],    # heard
    [2, 0, -1],    # a
    [10, 3, 2],    # dog
    [9, 2, 10],    # bark
], dtype=float)

def softmax(x):
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)

En = E / np.linalg.norm(E, axis=1, keepdims=True)   # vetores unitários
ESCALA = 0.2
pontuacoes = En @ En.T / ESCALA          # quanto cada token "presta atenção" nos outros
pesos = softmax(pontuacoes)              # cada linha soma 1
contextual = pesos @ E                   # novo vetor = média ponderada dos vetores

print("Pesos de atenção (linha = token que olha, coluna = token observado)")
print(" " * 8 + "".join(f"{t:>8}" for t in tokens))
for t, linha in zip(tokens, pesos):
    print(f"{t:<8}" + "".join(f"{p:>8.2f}" for p in linha))

i = tokens.index("bark")
foco = tokens[int(np.argmax(np.where(np.arange(len(tokens)) == i, -1, pesos[i])))]
print(f"\n'bark' presta mais atenção em '{foco}' (além de si mesmo):")
print("  é assim que o modelo entende que 'bark' aqui é o LATIDO do cão, não a casca da árvore.")
print(f"\nVetor original de 'bark'   : {E[i]}")
print(f"Vetor contextual de 'bark' : {np.round(contextual[i], 2)}")
