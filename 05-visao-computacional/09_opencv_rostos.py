"""
Módulo 05 - Detecção de rostos com OpenCV (+ IA responsável: privacidade)
Tópicos: "Detecção de objetos" e "Modelos de visão computacional (CNN)"

Dois detectores, duas gerações da visão computacional:
  --haar  (padrão) Haar Cascade (2001): características desenhadas à mão + classificador em cascata.
          Rápido, mas erra com rosto de lado ou pouca luz. Só existe no OpenCV 4.x.
  --yunet YuNet: uma CNN pequena treinada para rostos. Também devolve 5 pontos de
          referência (olhos, nariz, cantos da boca). Funciona no OpenCV 4.8+ e 5.x.
          O modelo .onnx (~230 KB) é baixado do OpenCV Zoo na primeira execução.

--anonimizar: pixeliza os rostos encontrados. É o princípio de PRIVACIDADE do módulo 01
              aplicado na prática (ex.: publicar fotos de eventos ou imagens de câmeras).

  pip install "opencv-python>=4.8"
  python 09_opencv_rostos.py foto.jpg
  python 09_opencv_rostos.py https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/lena.jpg --yunet
  python 09_opencv_rostos.py foto.jpg --yunet --anonimizar
  python 09_opencv_rostos.py --webcam --yunet        (tecla q para sair)
"""
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).parent
SAIDAS = AQUI / "saidas"
SAIDAS.mkdir(exist_ok=True)
YUNET_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/"
             "face_detection_yunet/face_detection_yunet_2023mar.onnx")
YUNET_ARQ = AQUI / "modelos" / "face_detection_yunet_2023mar.onnx"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
usar_yunet = "--yunet" in sys.argv
anonimizar = "--anonimizar" in sys.argv


# ---------------- Detectores ----------------
def criar_detector():
    if usar_yunet:
        if not YUNET_ARQ.exists():
            print(f"Baixando o modelo YuNet do OpenCV Zoo para {YUNET_ARQ} ...")
            YUNET_ARQ.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(YUNET_URL, YUNET_ARQ)
        det = cv2.FaceDetectorYN.create(str(YUNET_ARQ), "", (320, 320), 0.8)

        def detectar(img):
            det.setInputSize((img.shape[1], img.shape[0]))
            _, faces = det.detect(img)
            if faces is None:
                return []
            # cada linha: x, y, l, a, 5 pares (x, y) de pontos de referência, confiança
            return [(tuple(map(int, f[:4])), f[4:14].reshape(5, 2).astype(int), float(f[14]))
                    for f in faces]
        return "YuNet (CNN)", detectar

    if not hasattr(cv2, "CascadeClassifier"):
        sys.exit("Este OpenCV (5.x) não tem mais Haar Cascade. Use --yunet ou instale opencv-python<5.")
    cascata = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detectar(img):
        cinza = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        caixas = cascata.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        return [(tuple(map(int, c)), None, None) for c in caixas]
    return "Haar Cascade (clássico)", detectar


def pixelizar(img, x, y, w, h, blocos=8):
    x, y = max(x, 0), max(y, 0)
    roi = img[y:y + h, x:x + w]
    if roi.size:
        pequeno = cv2.resize(roi, (blocos, blocos), interpolation=cv2.INTER_LINEAR)
        img[y:y + h, x:x + w] = cv2.resize(pequeno, (roi.shape[1], roi.shape[0]),
                                           interpolation=cv2.INTER_NEAREST)


def desenhar(img, rostos):
    for (x, y, w, h), pontos, conf in rostos:
        if anonimizar:
            pixelizar(img, x, y, w, h)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if conf is not None:
            cv2.putText(img, f"{conf:.2f}", (x, max(15, y - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 1, cv2.LINE_AA)
        if pontos is not None and not anonimizar:
            for (px, py), cor in zip(pontos, [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255), (0, 255, 255)]):
                cv2.circle(img, (int(px), int(py)), 3, cor, -1)   # olhos, nariz, cantos da boca
    return img


def carregar(origem):
    if origem.startswith(("http://", "https://")):
        dados = urllib.request.urlopen(origem, timeout=30).read()
        return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)
    return cv2.imread(origem)


nome, detectar = criar_detector()

if "--webcam" in sys.argv:
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        sys.exit("Webcam não encontrada.")
    print(f"Detector: {nome}. Tecla q para sair.")
    while True:
        ok, quadro = cam.read()
        if not ok:
            break
        t0 = time.perf_counter()
        rostos = detectar(quadro)
        fps = 1 / max(time.perf_counter() - t0, 1e-6)
        desenhar(quadro, rostos)
        cv2.putText(quadro, f"{nome} | {len(rostos)} rosto(s) | {fps:.0f} FPS", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("AI-901 - rostos", quadro)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    sys.exit(0)

if not args:
    sys.exit(__doc__)
img = carregar(args[0])
if img is None:
    sys.exit(f"Não consegui abrir {args[0]}")

t0 = time.perf_counter()
rostos = detectar(img)
ms = (time.perf_counter() - t0) * 1000
print(f"Detector: {nome} | imagem {img.shape[1]}x{img.shape[0]} | {len(rostos)} rosto(s) em {ms:.0f} ms")
for (x, y, w, h), pontos, conf in rostos:
    extra = f"  confiança={conf:.2f}" if conf is not None else ""
    print(f"  rosto em x={x}, y={y}, {w}x{h}{extra}")

sufixo = "yunet" if usar_yunet else "haar"
arquivo = SAIDAS / f"rostos_{sufixo}{'_anonimizado' if anonimizar else ''}.png"
cv2.imwrite(str(arquivo), desenhar(img, rostos))
print(f"Resultado salvo em {arquivo}")
