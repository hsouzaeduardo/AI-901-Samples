"""
Módulo 05 - Ultralytics YOLO: as tarefas de visão do slide com modelos PRONTOS
Tópicos: "Tarefas e técnicas de visão computacional" e "Modelos (CNN)"

O YOLO ("You Only Look Once") é uma família de CNNs que roda LOCALMENTE (CPU/GPU,
até em celular). A mesma API resolve cada tarefa do slide com um modelo diferente:

  Classificação de imagem ... yolo26n-cls.pt  -> top-5 classes com probabilidade
  Detecção de objetos ....... yolo26n.pt      -> caixas + classe + confiança (80 classes COCO)
  Segmentação ............... yolo26n-seg.pt  -> máscara de pixels por objeto (instâncias)
  Segmentação semântica ..... yolo26n-sem.pt  -> uma classe para cada pixel (cenas de rua)
  Pose (pontos-chave) ....... yolo26n-pose.pt -> 17 pontos do corpo por pessoa
  Análise contextual ........ montada a partir das detecções

Os pesos (~6 MB cada) são baixados na 1a execução para a pasta modelos/.

  pip install ultralytics
  python 10_yolo_tarefas.py                 -> usa a foto de exemplo do Ultralytics (bus.jpg)
  python 10_yolo_tarefas.py foto.jpg
  python 10_yolo_tarefas.py foto.jpg --modelo yolo26s     (modelo maior: mais preciso, mais lento)

Licença: o Ultralytics é AGPL-3.0. Uso comercial fechado exige licença Enterprise.
"""
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils import ASSETS

AQUI = Path(__file__).parent
MODELOS, SAIDAS = AQUI / "modelos", AQUI / "saidas"
MODELOS.mkdir(exist_ok=True)
SAIDAS.mkdir(exist_ok=True)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
base = sys.argv[sys.argv.index("--modelo") + 1] if "--modelo" in sys.argv else "yolo26n"
if base in args:
    args.remove(base)
imagem = args[0] if args else str(ASSETS / "bus.jpg")
print(f"Imagem: {imagem}\n")


def modelo(sufixo=""):
    return YOLO(str(MODELOS / f"{base}{sufixo}.pt"))     # baixa automaticamente se não existir


def salvar(resultado, nome):
    cv2.imwrite(str(SAIDAS / f"yolo_{nome}.png"), resultado.plot())   # plot() devolve a imagem anotada


# ---------- 1) Classificação: UM rótulo para a imagem inteira ----------
r = modelo("-cls")(imagem, verbose=False)[0]
print("1) CLASSIFICAÇÃO (top-5 classes do ImageNet):")
for i, p in zip(r.probs.top5, r.probs.top5conf.tolist()):
    print(f"   {r.names[i]:<24} {p:.1%}")

# ---------- 2) Detecção: O QUÊ e ONDE ----------
r = modelo()(imagem, conf=0.4, verbose=False)[0]
print(f"\n2) DETECÇÃO: {len(r.boxes)} objetos  (velocidade: {r.speed['inference']:.0f} ms de inferência)")
deteccoes = []
for caixa, cls, conf in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist()):
    x1, y1, x2, y2 = map(int, caixa)
    deteccoes.append((r.names[int(cls)], conf, (x1, y1, x2, y2)))
    print(f"   {r.names[int(cls)]:<10} confiança {conf:.2f}  caixa=({x1}, {y1}) -> ({x2}, {y2})")
salvar(r, "deteccao")

# ---------- 3) Segmentação: QUAIS PIXELS pertencem a cada objeto ----------
r = modelo("-seg")(imagem, conf=0.4, verbose=False)[0]
print("\n3) SEGMENTAÇÃO (máscara por objeto):")
if r.masks is not None:
    total = r.masks.data.shape[1] * r.masks.data.shape[2]
    for m, cls in zip(r.masks.data, r.boxes.cls.tolist()):
        print(f"   {r.names[int(cls)]:<10} ocupa {int(m.sum()) / total:.1%} da imagem")
salvar(r, "segmentacao")

# ---------- 3b) Segmentação SEMÂNTICA: uma classe para CADA pixel (como no slide) ----------
# Diferença: a de instâncias separa "pessoa 1", "pessoa 2"; a semântica só diz "pixel de pessoa".
# O modelo -sem do YOLO26 foi treinado em cenas de rua (19 classes do Cityscapes).
if base.startswith("yolo26"):
    r = modelo("-sem")(imagem, verbose=False)[0]
    mapa = r.semantic_mask.data
    mapa = mapa.cpu().numpy() if hasattr(mapa, "cpu") else mapa
    classes, contagens = np.unique(mapa, return_counts=True)
    print("\n3b) SEGMENTAÇÃO SEMÂNTICA (classe de cada pixel):")
    for c, n in sorted(zip(classes, contagens), key=lambda t: -t[1])[:6]:
        print(f"   {r.names[int(c)]:<12} {n / mapa.size:.1%} dos pixels")
    print("   Repare: o modelo nano pode chamar o ônibus de 'train' (trem) - modelos erram!")
    salvar(r, "semantica")

# ---------- 4) Pose: pontos-chave do corpo ----------
r = modelo("-pose")(imagem, conf=0.4, verbose=False)[0]
PONTOS = ["nariz", "olho esq.", "olho dir.", "orelha esq.", "orelha dir.", "ombro esq.", "ombro dir.",
          "cotovelo esq.", "cotovelo dir.", "pulso esq.", "pulso dir.", "quadril esq.", "quadril dir.",
          "joelho esq.", "joelho dir.", "tornozelo esq.", "tornozelo dir."]
print(f"\n4) POSE: {len(r.boxes)} pessoa(s), 17 pontos cada")
if r.keypoints is not None and len(r.keypoints):
    xy = r.keypoints.xy[0].tolist()
    print("   1a pessoa: " + ", ".join(f"{PONTOS[i]}=({int(x)},{int(y)})" for i, (x, y) in enumerate(xy[:6])) + ", ...")
salvar(r, "pose")

# ---------- 5) Análise contextual: descrever a cena a partir das detecções ----------
PT = {"person": ("pessoa", "pessoas"), "bus": ("ônibus", "ônibus"), "car": ("carro", "carros"),
      "truck": ("caminhão", "caminhões"), "bicycle": ("bicicleta", "bicicletas"), "dog": ("cachorro", "cachorros"),
      "tie": ("gravata", "gravatas"), "motorcycle": ("moto", "motos"), "traffic light": ("semáforo", "semáforos")}
contagem = Counter(nome for nome, _, _ in deteccoes)
descricao = ", ".join(f"{n} {PT.get(nome, (nome, nome))[n > 1]}" for nome, n in contagem.most_common())
print(f"\n5) ANÁLISE CONTEXTUAL: a cena contém {descricao}.")
pessoas = [c for nome, _, c in deteccoes if nome == "person"]
veiculos = [c for nome, _, c in deteccoes if nome in ("bus", "car", "truck")]
if pessoas and veiculos:
    base_veiculo = max(c[3] for c in veiculos)
    na_frente = sum(1 for c in pessoas if c[3] >= base_veiculo - 40)
    print(f"   {na_frente} pessoa(s) parecem estar à frente do veículo (pés abaixo da base dele).")
print("   (Um modelo multimodal do Foundry gera descrições muito mais ricas: 05_analise_imagem.py)")
print(f"\nImagens anotadas em {SAIDAS}: yolo_deteccao.png, yolo_segmentacao.png, yolo_semantica.png, yolo_pose.png")
