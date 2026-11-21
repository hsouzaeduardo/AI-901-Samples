"""
Módulo 05 - Google MediaPipe: tarefas de visão PRONTAS, leves, que rodam no dispositivo
Tópicos: "Tarefas e técnicas de visão computacional" e "Modelos (CNN)"

O MediaPipe empacota modelos pequenos (TFLite) para celular, navegador e desktop.
Usa a API "Tasks" (mediapipe.tasks.python.vision). A antiga mp.solutions foi removida
nas versões novas, e muitos tutoriais da internet ainda usam a API antiga.

  Classificação ......... EfficientNet-Lite0 -> top-5 classes (ImageNet)
  Detecção .............. EfficientDet-Lite0 -> caixas (80 classes COCO)
  Segmentação semântica . DeepLab v3          -> classe por pixel (21 classes)
  Pose .................. Pose Landmarker     -> 33 pontos do corpo (x, y, z)
  Mãos .................. Hand Landmarker     -> 21 pontos por mão + mão esquerda/direita

Os modelos (~3 a 18 MB) são baixados na 1a execução para a pasta modelos/.

  pip install mediapipe opencv-python
  python 13_mediapipe_tarefas.py                -> foto de exemplo (jogador de futebol)
  python 13_mediapipe_tarefas.py foto.jpg       -> sua foto (ou uma URL)
Licença: Apache 2.0.
"""
import sys
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

AQUI = Path(__file__).parent
MODELOS, SAIDAS = AQUI / "modelos", AQUI / "saidas"
MODELOS.mkdir(exist_ok=True)
SAIDAS.mkdir(exist_ok=True)
BASE = "https://storage.googleapis.com/mediapipe-models/"
URLS = {
    "classificador": "image_classifier/efficientnet_lite0/float32/1/efficientnet_lite0.tflite",
    "detector": "object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite",
    "segmentador": "image_segmenter/deeplab_v3/float32/1/deeplab_v3.tflite",
    "pose": "pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    "maos": "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
}
IMAGEM_EXEMPLO = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/messi5.jpg"


def modelo(nome):
    arquivo = MODELOS / Path(URLS[nome]).name
    if not arquivo.exists():
        print(f"   (baixando {arquivo.name}...)")
        urllib.request.urlretrieve(BASE + URLS[nome], arquivo)
    return mp_tasks.BaseOptions(model_asset_path=str(arquivo))


def carregar(origem):
    if origem.startswith(("http://", "https://")):
        dados = urllib.request.urlopen(origem, timeout=30).read()
        return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)
    return cv2.imread(origem)


origem = sys.argv[1] if len(sys.argv) > 1 else IMAGEM_EXEMPLO
bgr = carregar(origem)
if bgr is None:
    sys.exit(f"Não consegui abrir {origem}")
A, L = bgr.shape[:2]
# O MediaPipe trabalha em RGB; o OpenCV lê em BGR
imagem = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
print(f"Imagem: {origem} ({L}x{A})\n")

# ---------- 1) Classificação ----------
opcoes = vision.ImageClassifierOptions(base_options=modelo("classificador"), max_results=5)
with vision.ImageClassifier.create_from_options(opcoes) as classificador:
    resultado = classificador.classify(imagem)
print("1) CLASSIFICAÇÃO (top-5):")
for c in resultado.classifications[0].categories:
    print(f"   {c.category_name:<24} {c.score:.1%}")

# ---------- 2) Detecção ----------
opcoes = vision.ObjectDetectorOptions(base_options=modelo("detector"), score_threshold=0.4, max_results=10)
with vision.ObjectDetector.create_from_options(opcoes) as detector:
    resultado = detector.detect(imagem)
anotada = bgr.copy()
print(f"\n2) DETECÇÃO: {len(resultado.detections)} objeto(s)")
for d in resultado.detections:
    b, cat = d.bounding_box, d.categories[0]
    print(f"   {cat.category_name:<12} confiança {cat.score:.2f}  caixa=({b.origin_x}, {b.origin_y}, {b.width}x{b.height})")
    cv2.rectangle(anotada, (b.origin_x, b.origin_y), (b.origin_x + b.width, b.origin_y + b.height), (0, 255, 0), 2)
    cv2.putText(anotada, f"{cat.category_name} {cat.score:.2f}", (b.origin_x, max(15, b.origin_y - 6)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

# ---------- 3) Segmentação semântica ----------
opcoes = vision.ImageSegmenterOptions(base_options=modelo("segmentador"), output_category_mask=True)
with vision.ImageSegmenter.create_from_options(opcoes) as segmentador:
    resultado = segmentador.segment(imagem)
    rotulos = segmentador.labels
mapa = np.squeeze(resultado.category_mask.numpy_view())     # (A, L, 1) -> (A, L)
classes, contagens = np.unique(mapa, return_counts=True)
print("\n3) SEGMENTAÇÃO SEMÂNTICA (classe de cada pixel):")
for c, n in sorted(zip(classes, contagens), key=lambda t: -t[1])[:4]:
    print(f"   {rotulos[int(c)]:<12} {n / mapa.size:.1%} dos pixels")
cores = np.random.default_rng(3).integers(0, 255, (256, 3), dtype=np.uint8)
cores[0] = 0                                            # fundo sem cor
segmentada = cv2.addWeighted(bgr, 0.5, cores[mapa], 0.5, 0)

# ---------- 4) Pose: 33 pontos do corpo ----------
opcoes = vision.PoseLandmarkerOptions(base_options=modelo("pose"), num_poses=3)
with vision.PoseLandmarker.create_from_options(opcoes) as pose:
    resultado = pose.detect(imagem)
print(f"\n4) POSE: {len(resultado.pose_landmarks)} pessoa(s), 33 pontos cada (coordenadas normalizadas 0-1)")
NOMES_POSE = {0: "nariz", 11: "ombro esq.", 12: "ombro dir.", 15: "pulso esq.", 16: "pulso dir.",
              25: "joelho esq.", 26: "joelho dir.", 27: "tornozelo esq.", 28: "tornozelo dir."}
for pessoa in resultado.pose_landmarks:
    print("   " + ", ".join(f"{n}=({pessoa[i].x * L:.0f},{pessoa[i].y * A:.0f})" for i, n in list(NOMES_POSE.items())[:5]) + ", ...")
    vision.drawing_utils.draw_landmarks(anotada, pessoa, vision.PoseLandmarksConnections.POSE_LANDMARKS)

# ---------- 5) Mãos: 21 pontos por mão ----------
opcoes = vision.HandLandmarkerOptions(base_options=modelo("maos"), num_hands=4,
                                      min_hand_detection_confidence=0.3)
with vision.HandLandmarker.create_from_options(opcoes) as maos:
    resultado = maos.detect(imagem)
print(f"\n5) MÃOS: {len(resultado.hand_landmarks)} mão(s) encontrada(s)")
for pontos, lado in zip(resultado.hand_landmarks, resultado.handedness):
    print(f"   mão {lado[0].category_name} (confiança {lado[0].score:.2f}), "
          f"pulso em ({pontos[0].x * L:.0f}, {pontos[0].y * A:.0f})")
    vision.drawing_utils.draw_landmarks(anotada, pontos, vision.HandLandmarksConnections.HAND_CONNECTIONS)

cv2.imwrite(str(SAIDAS / "mediapipe_anotada.png"), anotada)
cv2.imwrite(str(SAIDAS / "mediapipe_segmentacao.png"), segmentada)
print(f"\nImagens em {SAIDAS}: mediapipe_anotada.png (caixas, pose, mãos) e mediapipe_segmentacao.png")
print("Webcam ao vivo com gestos: python 14_mediapipe_maos_webcam.py")
