"""
Módulo 05 - Tópico: Tarefas e técnicas de visão computacional
  Classificação de imagem ... UM rótulo para a imagem inteira ("é uma fruteira")
  Detecção de objetos ....... O QUÊ e ONDE (caixas delimitadoras)
  Segmentação semântica ..... rótulo para CADA PIXEL
  Análise contextual ........ descrever a cena (relações entre objetos)

Uma imagem sintética (matriz de pixels) com uma "maçã" (vermelha, redonda) e uma
"banana" (amarela, alongada). Tudo em numpy - a visão computacional manipula PIXELS.

  python 01_tarefas_de_visao.py
"""
from collections import deque

import numpy as np

A, L = 14, 32                                   # altura x largura
img = np.zeros((A, L, 3), dtype=np.uint8)       # RGB, fundo preto
img[:] = (30, 30, 30)
yy, xx = np.mgrid[:A, :L]
img[(yy - 7) ** 2 + (xx - 7) ** 2 <= 20] = (210, 30, 40)            # maçã (círculo vermelho)
img[4:10, 16:29] = (240, 220, 50)                                   # banana (retângulo amarelo)
img[4, 16] = img[4, 28] = img[9, 16] = img[9, 28] = (30, 30, 30)    # cantos arredondados

CORES = {"maçã": (210, 30, 40), "banana": (240, 220, 50)}

def cor_mais_proxima(pixel):
    if np.abs(pixel.astype(int) - 30).sum() < 60:
        return "fundo"
    return min(CORES, key=lambda c: np.abs(pixel.astype(int) - CORES[c]).sum())

# ---------- Segmentação semântica: rótulo por pixel ----------
mascara = np.array([[cor_mais_proxima(img[y, x]) for x in range(L)] for y in range(A)])
SIMBOLO = {"fundo": ".", "maçã": "M", "banana": "B"}
print("SEGMENTAÇÃO SEMÂNTICA (cada pixel rotulado):")
for linha in mascara:
    print("   " + "".join(SIMBOLO[p] for p in linha))

# ---------- Detecção de objetos: componentes conectados -> caixas ----------
def componentes(rotulo):
    visitado, caixas = np.zeros((A, L), bool), []
    for y0, x0 in zip(*np.where(mascara == rotulo)):
        if visitado[y0, x0]:
            continue
        fila, pix = deque([(y0, x0)]), []
        visitado[y0, x0] = True
        while fila:
            y, x = fila.popleft()
            pix.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < A and 0 <= nx < L and not visitado[ny, nx] and mascara[ny, nx] == rotulo:
                    visitado[ny, nx] = True
                    fila.append((ny, nx))
        ys, xs = zip(*pix)
        caixas.append({"rotulo": rotulo, "x": min(xs), "y": min(ys),
                       "largura": max(xs) - min(xs) + 1, "altura": max(ys) - min(ys) + 1,
                       "area": len(pix)})
    return caixas

deteccoes = componentes("maçã") + componentes("banana")
print("\nDETECÇÃO DE OBJETOS (o quê + onde):")
for d in deteccoes:
    print(f"   {d['rotulo']:<7} caixa=(x={d['x']}, y={d['y']}, l={d['largura']}, a={d['altura']})")

# ---------- Classificação: um rótulo para a imagem toda ----------
areas = {r: int((mascara == r).sum()) for r in CORES}
classe = "fruteira (várias frutas)" if all(areas.values()) else max(areas, key=areas.get)
print(f"\nCLASSIFICAÇÃO DA IMAGEM: '{classe}'  (pixels por classe: {areas})")

# ---------- Análise contextual: descrever a cena ----------
m, b = deteccoes[0], deteccoes[1]
lado = "à esquerda" if m["x"] < b["x"] else "à direita"
forma_b = "alongada" if b["largura"] > 1.5 * b["altura"] else "compacta"
print(f"\nANÁLISE CONTEXTUAL: 'Uma maçã vermelha {lado} de uma banana {forma_b}, sobre fundo escuro.'")
print("\nModelos multimodais do Foundry fazem essa descrição a partir de fotos reais:")
print("veja 05_analise_imagem.py")
