"""
Módulo 05 - Visão computacional com OpenCV
Tópicos: "Tarefas e técnicas de visão computacional" e "Modelos (CNN): filtros
extraem recursos das imagens" - agora com a biblioteca de visão mais usada do mundo.

  0) Aquisição ............ a imagem é uma MATRIZ DE PIXELS (altura x largura x canais BGR)
  1) Filtros .............. desfoque, Sobel (os MESMOS kernels de 02_cnn.py) e Canny
  2) Segmentação semântica  cada pixel vira maçã / banana / fundo (limiar de cor no HSV)
  3) Detecção de objetos .. contornos -> caixas delimitadoras + forma (circularidade)
  4) Classificação ........ um rótulo para a imagem inteira
  5) Análise contextual ... frase descrevendo a cena

É visão computacional "clássica": regras e filtros escolhidos à mão, sem treinamento.
Compare com os modelos multimodais do Foundry (05_analise_imagem.py), que aprendem
tudo isso a partir de dados e descrevem fotos reais com muito mais riqueza.

  pip install "opencv-python>=4.8"
  python 08_opencv_tarefas.py               -> cena sintética gerada pelo script (offline)
  python 08_opencv_tarefas.py foto.jpg      -> sua foto (procura objetos vermelhos e amarelos)
Resultados: saidas/opencv_filtros.png, opencv_segmentacao.png e opencv_deteccao.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np

SAIDAS = Path(__file__).parent / "saidas"
SAIDAS.mkdir(exist_ok=True)


def gerar_cena():
    """Mesa clara com 2 maçãs vermelhas e 1 banana amarela (com ruído de câmera)."""
    img = np.full((360, 560, 3), (205, 215, 225), np.uint8)          # BGR: fundo bege-claro
    for (x, y, r) in ((110, 200, 55), (250, 230, 48)):                 # maçãs
        cv2.circle(img, (x, y), r, (40, 30, 200), -1)
        cv2.circle(img, (x - r // 3, y - r // 3), r // 5, (120, 120, 245), -1)   # brilho
        cv2.line(img, (x, y - r), (x + 6, y - r - 18), (30, 60, 90), 4)          # cabinho
    cv2.ellipse(img, (420, 170), (110, 45), -20, 15, 190, (40, 210, 235), 28)    # banana (arco)
    ruido = np.random.default_rng(0).normal(0, 6, img.shape)
    return np.clip(img + ruido, 0, 255).astype(np.uint8)


def legenda(img, texto):
    """Escreve um título na imagem (as fontes do OpenCV não têm acentos)."""
    out = img.copy() if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    (w, h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(out, (0, 0), (w + 16, h + 14), (40, 40, 40), -1)          # tarja escura
    cv2.putText(out, texto, (8, h + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return out


# ---------------- 0) Aquisição ----------------
if len(sys.argv) > 1:
    img = cv2.imread(sys.argv[1])
    if img is None:
        sys.exit(f"Não consegui abrir a imagem {sys.argv[1]}")
    escala = 560 / img.shape[1]                    # padroniza a largura para 560 px
    img = cv2.resize(img, None, fx=escala, fy=escala)
    origem = sys.argv[1]
else:
    img = gerar_cena()
    origem = "cena sintética"
A, L = img.shape[:2]
print(f"0) Aquisição ({origem}): matriz {img.shape} do tipo {img.dtype}")
print(f"   pixel no centro (B, G, R) = {tuple(int(v) for v in img[A // 2, L // 2])}")

# ---------------- 1) Filtros (o que a 1a camada de uma CNN aprende a fazer) ----------------
cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
suave = cv2.GaussianBlur(cinza, (5, 5), 0)
SOBEL_V = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)     # = 02_cnn.py
SOBEL_H = SOBEL_V.T
bordas_v = cv2.convertScaleAbs(cv2.filter2D(suave, cv2.CV_32F, SOBEL_V))
bordas_h = cv2.convertScaleAbs(cv2.filter2D(suave, cv2.CV_32F, SOBEL_H))
canny = cv2.Canny(suave, 50, 150)
painel = cv2.vconcat([cv2.hconcat([legenda(img, "original"), legenda(bordas_v, "Sobel vertical")]),
                      cv2.hconcat([legenda(bordas_h, "Sobel horizontal"), legenda(canny, "Canny")])])
cv2.imwrite(str(SAIDAS / "opencv_filtros.png"), painel)
print(f"1) Filtros: convolução 3x3 com cv2.filter2D + Canny ({int((canny > 0).sum())} pixels de borda)")
print("   Repare em opencv_filtros.png: em tons de cinza, amarelo e bege têm brilho parecido e a")
print("   banana quase some das bordas. Por isso a segmentação a seguir usa COR (espaço HSV).")

# ---------------- 2) Segmentação semântica por cor (HSV) ----------------
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)       # matiz separa a COR da iluminação
vermelho = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255)) | cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
amarelo = cv2.inRange(hsv, (18, 100, 100), (35, 255, 255))
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
mascaras = {}
for nome, m in (("maca", vermelho), ("banana", amarelo)):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, kernel)       # remove pontinhos (ruído)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kernel)      # fecha buracos (brilho da maçã)
    mascaras[nome] = m
CORES = {"maca": (0, 0, 255), "banana": (0, 220, 255)}
rotulos = np.zeros_like(img)
for nome, m in mascaras.items():
    rotulos[m > 0] = CORES[nome]
sobreposicao = cv2.addWeighted(img, 0.5, rotulos, 0.5, 0)
cv2.imwrite(str(SAIDAS / "opencv_segmentacao.png"),
            cv2.hconcat([legenda(rotulos, "mascara por pixel"), legenda(sobreposicao, "sobreposicao")]))
total = A * L
print("2) Segmentação: " + ", ".join(f"{n}={int((m > 0).sum()) / total:.1%} dos pixels" for n, m in mascaras.items()))

# ---------------- 3) Detecção: contornos -> caixas + características de forma ----------------
deteccoes = []
anotada = img.copy()
for nome, m in mascaras.items():
    contornos = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    for c in contornos:
        area = cv2.contourArea(c)
        if area < 0.002 * total:                         # ignora manchas pequenas
            continue
        x, y, w, h = cv2.boundingRect(c)
        perimetro = cv2.arcLength(c, True)
        circularidade = 4 * np.pi * area / (perimetro ** 2)   # 1.0 = círculo perfeito
        deteccoes.append({"rotulo": nome, "caixa": (x, y, w, h), "area": int(area),
                          "circularidade": round(float(circularidade), 2)})
        cv2.rectangle(anotada, (x, y), (x + w, y + h), CORES[nome], 2)
        cv2.putText(anotada, f"{nome} circ={circularidade:.2f}", (x, max(15, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CORES[nome], 2)
deteccoes.sort(key=lambda d: d["caixa"][0])               # da esquerda para a direita
print(f"3) Detecção: {len(deteccoes)} objetos")
for d in deteccoes:
    forma = "redondo" if d["circularidade"] > 0.75 else "alongado"
    print(f"   {d['rotulo']:<7} caixa(x,y,l,a)={d['caixa']}  área={d['area']:>6}  "
          f"circularidade={d['circularidade']} ({forma})")

# ---------------- 4) Classificação da imagem inteira ----------------
contagem = {n: sum(d["rotulo"] == n for d in deteccoes) for n in mascaras}
if all(contagem.values()):
    classe = "fruteira (frutas variadas)"
elif any(contagem.values()):
    classe = max(contagem, key=contagem.get)
else:
    classe = "nenhuma fruta reconhecida"
print(f"4) Classificação: '{classe}'  {contagem}")

# ---------------- 5) Análise contextual ----------------
NOMES = {"maca": ("maçã", "maçãs"), "banana": ("banana", "bananas")}
partes = [f"{n} {NOMES[k][n > 1]}" for k, n in contagem.items() if n]
frase = "A imagem mostra " + " e ".join(partes) if partes else "Nenhum objeto reconhecido"
if contagem["maca"] and contagem["banana"]:
    x_maca = np.mean([d["caixa"][0] for d in deteccoes if d["rotulo"] == "maca"])
    x_banana = np.mean([d["caixa"][0] for d in deteccoes if d["rotulo"] == "banana"])
    frase += f"; as maçãs estão à {'esquerda' if x_maca < x_banana else 'direita'} da banana"
print(f"5) Análise contextual: '{frase}.'")

cv2.imwrite(str(SAIDAS / "opencv_deteccao.png"), legenda(anotada, classe.split(" (")[0]))
print(f"\nImagens salvas em {SAIDAS}: opencv_filtros.png, opencv_segmentacao.png, opencv_deteccao.png")
