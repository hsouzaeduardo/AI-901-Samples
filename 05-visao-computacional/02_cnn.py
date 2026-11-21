"""
Módulo 05 - Tópico: Modelos de visão computacional - CNN (rede neural convolucional)
  - Imagens com rótulos conhecidos para treinamento
  - FILTROS extraem recursos (bordas, formas) das imagens
  - MAPAS DE RECURSOS são reduzidos (pooling) e combinados
  - Uma camada totalmente conectada prevê a CLASSE
  - Saída: PROBABILIDADE para cada classe

Classes: "barra vertical" x "barra horizontal" (imagens 8x8 com ruído).
Filtros fixos (Sobel) + classificador treinado por gradiente descendente. numpy puro.

  python 02_cnn.py
"""
import numpy as np

rng = np.random.default_rng(1)
CLASSES = ["vertical", "horizontal"]

def gerar(classe):
    img = rng.normal(0, 0.15, (8, 8))
    pos = rng.integers(1, 7)
    if classe == 0:
        img[:, pos] += 1
    else:
        img[pos, :] += 1
    return img

# 1) Dados rotulados
X_img = [gerar(c) for c in (0, 1) for _ in range(30)]
y = np.array([c for c in (0, 1) for _ in range(30)])

# 2) Filtros convolucionais (detectores de borda)
FILTROS = {
    "borda_vertical":   np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float),
    "borda_horizontal": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], float),
}

def convoluir(img, k):
    s = img.shape[0] - 2
    return np.array([[np.sum(img[i:i + 3, j:j + 3] * k) for j in range(s)] for i in range(s)])

def relu(x):
    return np.maximum(x, 0)

def max_pool(m, t=2):
    s = m.shape[0] // t
    return m[:s * t, :s * t].reshape(s, t, s, t).max(axis=(1, 3))

def recursos(img):
    """conv -> ReLU -> pooling -> achatar (flatten). |valor| porque bordas têm 2 lados."""
    return np.concatenate([max_pool(relu(np.abs(convoluir(img, k)))).ravel() for k in FILTROS.values()])

X = np.array([recursos(i) for i in X_img])
print(f"Cada imagem 8x8 virou um vetor de {X.shape[1]} recursos (2 filtros x mapa 3x3 após pooling)")

# 3) Camada totalmente conectada + softmax, treinada por gradiente descendente
W, b = np.zeros((X.shape[1], 2)), np.zeros(2)
def softmax(z):
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)
Y = np.eye(2)[y]
for epoca in range(300):
    P = softmax(X @ W + b)
    W -= 0.05 * X.T @ (P - Y) / len(X)
    b -= 0.05 * (P - Y).mean(axis=0)
    if epoca in (0, 50, 299):
        perda = -np.mean(np.log(P[np.arange(len(y)), y] + 1e-9))
        print(f"  época {epoca:>3}: perda={perda:.3f}  acurácia={np.mean(P.argmax(1) == y):.0%}")

# 4) Inferência em imagens novas
print("\nImagens NOVAS (nunca vistas no treinamento):")
for classe_real in (0, 1, 0):
    img = gerar(classe_real)
    prob = softmax(recursos(img)[None] @ W + b)[0]
    arte = "\n".join("      " + "".join("#" if v > 0.5 else "." for v in linha) for linha in img)
    print(arte)
    print(f"   real={CLASSES[classe_real]:<10} previsto: " +
          ", ".join(f"{c}={p:.0%}" for c, p in zip(CLASSES, prob)) + "\n")
print("Numa CNN real os FILTROS também são aprendidos e há dezenas de camadas.")
