"""
Módulo 05 - Tópico: Modelos de visão computacional - Transformador de Visão (ViT)
e modelos MULTIMODAIS
  - PATCHES da imagem viram vetores de embeddings a partir dos pixels
  - O transformador usa ATENÇÃO para relacionar os patches entre si
  - Atenção entre modalidades combina o espaço vetorial VISUAL com o de LINGUAGEM

Didático (numpy, pesos aleatórios fixos em vez de aprendidos).

  python 03_vit_e_multimodal.py
"""
import numpy as np

rng = np.random.default_rng(3)

# Imagem 8x8: uma barra vertical na coluna 2 e um "ponto" no canto inferior direito
img = np.zeros((8, 8))
img[:, 2] = 1.0
img[6:8, 6:8] = 1.0
print("Imagem 8x8:")
print("\n".join("   " + "".join("#" if v else "." for v in linha) for linha in img))

# 1) Dividir em patches 4x4 -> 4 patches
P = 4
patches = [img[i:i + P, j:j + P] for i in range(0, 8, P) for j in range(0, 8, P)]
nomes = ["sup-esq", "sup-dir", "inf-esq", "inf-dir"]
print(f"\n1) {len(patches)} patches de {P}x{P} pixels -> cada um achatado em {P * P} valores")

# 2) Embedding linear + embedding de POSIÇÃO (o transformador não sabe a ordem sozinho)
D = 6
W_emb = rng.normal(0, 0.5, (P * P, D))
pos_emb = rng.normal(0, 0.1, (len(patches), D))
E = np.array([p.ravel() for p in patches]) @ W_emb + pos_emb
print(f"2) Embeddings dos patches: matriz {E.shape} (patch x dimensão)")

# 3) Autoatenção entre patches
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)
Wq, Wk = rng.normal(0, 0.5, (D, D)), rng.normal(0, 0.5, (D, D))
atencao = softmax((E @ Wq) @ (E @ Wk).T / np.sqrt(D))
print("3) Pesos de atenção entre patches (contexto GLOBAL - uma CNN só vê vizinhos):")
print("            " + "".join(f"{n:>9}" for n in nomes))
for n, linha in zip(nomes, atencao):
    print(f"   {n:<8}" + "".join(f"{v:>9.2f}" for v in linha))
emb_imagem = (atencao @ E).mean(axis=0)          # vetor único que representa a imagem
# (num ViT real, essa saída alimenta uma camada de classificação ou um modelo de linguagem)

# 4) Multimodal: imagem e texto no MESMO espaço vetorial (ideia do CLIP)
# Num modelo real, os dois codificadores são TREINADOS juntos com milhões de pares
# (imagem, legenda) para que cada dimensão signifique o mesmo nas duas modalidades.
# Aqui usamos um espaço interpretável de 3 dimensões: [vertical, horizontal, preenchido].
def codificar_imagem(im):
    colunas, linhas = im.sum(axis=0), im.sum(axis=1)
    total = im.sum() or 1
    return np.array([colunas.max() / total, linhas.max() / total, im.mean()])

VOCAB = {"vertical": [1, 0, 0], "horizontal": [0, 1, 0], "quadrado": [0, 0, 1],
         "cheio": [0, 0, 1], "listra": [0.5, 0.5, 0]}
def codificar_texto(frase):
    return np.sum([VOCAB.get(p, [0, 0, 0]) for p in frase.lower().split()], axis=0).astype(float)

LEGENDAS = ["uma listra vertical", "uma listra horizontal", "um quadrado cheio"]
def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

horizontal = np.zeros((8, 8))
horizontal[5, :] = 1.0
quadrado = np.zeros((8, 8))
quadrado[1:7, 1:7] = 1.0
print("\n4) Multimodal - qual legenda combina com cada imagem?")
for nome, im in (("imagem acima", img), ("barra horizontal", horizontal), ("quadrado", quadrado)):
    v = codificar_imagem(im)
    sims = {leg: cos(v, codificar_texto(leg)) for leg in LEGENDAS}
    melhor = max(sims, key=sims.get)
    print(f"   {nome:<17} -> '{melhor}'  " + "  ".join(f"{k.split()[-1]}={x:.2f}" for k, x in sims.items()))
print("\nÉ assim que modelos multimodais 'entendem' imagens. Com fotos reais: 05_analise_imagem.py")
