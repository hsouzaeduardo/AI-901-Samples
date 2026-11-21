"""
Módulo 05 - MediaPipe AO VIVO: mãos, contagem de dedos e reconhecimento de GESTOS
Tópicos: detecção + pontos de referência + classificação, em tempo real e no dispositivo

O Gesture Recognizer combina dois modelos: um encontra a mão e os 21 pontos de
referência; outro CLASSIFICA o gesto entre 7 opções. Com os pontos dá para criar
regras próprias, como contar dedos levantados.

Ideia de uso (princípio de INCLUSÃO): controlar uma apresentação ou um quiosque por
gestos, sem tocar em nada. Aqui cada gesto é ligado a uma "ação" de exemplo.

  pip install mediapipe opencv-python
  python 14_mediapipe_maos_webcam.py             -> webcam (tecla q para sair)
  python 14_mediapipe_maos_webcam.py foto.jpg    -> uma foto (gera saidas/mediapipe_gestos.png)
"""
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

AQUI = Path(__file__).parent
MODELOS, SAIDAS = AQUI / "modelos", AQUI / "saidas"
MODELOS.mkdir(exist_ok=True)
SAIDAS.mkdir(exist_ok=True)
URL = ("https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
       "gesture_recognizer/float16/1/gesture_recognizer.task")
ARQUIVO = MODELOS / "gesture_recognizer.task"

GESTOS = {  # gesto do modelo -> (nome em português, ação de exemplo)
    "Thumb_Up": ("joinha", "aprovar"), "Thumb_Down": ("polegar para baixo", "reprovar"),
    "Open_Palm": ("mão aberta", "pausar"), "Closed_Fist": ("punho fechado", "parar"),
    "Pointing_Up": ("apontando para cima", "próximo slide"), "Victory": ("vitória / paz", "tirar foto"),
    "ILoveYou": ("eu te amo (Libras/ASL)", "curtir"), "None": ("nenhum", "-"),
}
PONTAS, ARTICULACOES = [8, 12, 16, 20], [6, 10, 14, 18]     # indicador, médio, anelar, mínimo


def contar_dedos(pontos, lado):
    """Regra simples sobre os pontos: a ponta do dedo está ACIMA da articulação?"""
    dedos = sum(pontos[p].y < pontos[a].y for p, a in zip(PONTAS, ARTICULACOES))
    # polegar: compara no eixo x (depende da mão; a imagem da webcam é espelhada)
    polegar = pontos[4].x < pontos[3].x if lado == "Right" else pontos[4].x > pontos[3].x
    return dedos + int(polegar)


def anotar(quadro, resultado):
    A, L = quadro.shape[:2]
    textos = []
    for pontos, lado, gesto in zip(resultado.hand_landmarks, resultado.handedness, resultado.gestures):
        vision.drawing_utils.draw_landmarks(quadro, pontos, vision.HandLandmarksConnections.HAND_CONNECTIONS)
        nome, acao = GESTOS.get(gesto[0].category_name, (gesto[0].category_name, "-"))
        dedos = contar_dedos(pontos, lado[0].category_name)
        texto = f"{lado[0].category_name}: {nome} ({gesto[0].score:.2f}) | {dedos} dedo(s) | acao: {acao}"
        textos.append(texto)
        x, y = int(pontos[0].x * L), int(pontos[0].y * A)
        cv2.putText(quadro, f"{dedos} dedos", (x - 30, min(A - 10, y + 30)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 255), 2)
    return textos


if not ARQUIVO.exists():
    print("Baixando o modelo de gestos (~8 MB)...")
    urllib.request.urlretrieve(URL, ARQUIVO)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
modo = vision.RunningMode.IMAGE if args else vision.RunningMode.VIDEO
opcoes = vision.GestureRecognizerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(ARQUIVO)),
                                         running_mode=modo, num_hands=2)

with vision.GestureRecognizer.create_from_options(opcoes) as reconhecedor:
    if args:                                                          # ---- modo foto ----
        bgr = cv2.imread(args[0])
        if bgr is None:
            sys.exit(f"Não consegui abrir {args[0]}")
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        textos = anotar(bgr, reconhecedor.recognize(img))
        print(f"{len(textos)} mão(s):", *textos, sep="\n  ")
        cv2.imwrite(str(SAIDAS / "mediapipe_gestos.png"), bgr)
        print("Resultado em", SAIDAS / "mediapipe_gestos.png")
        sys.exit(0)

    cam = cv2.VideoCapture(0)                                         # ---- modo webcam ----
    if not cam.isOpened():
        sys.exit("Webcam não encontrada. Teste com uma foto: python 14_mediapipe_maos_webcam.py foto.jpg")
    inicio = time.monotonic()
    print("Mostre as mãos para a câmera. Tecla q para sair.")
    while True:
        ok, quadro = cam.read()
        if not ok:
            break
        quadro = cv2.flip(quadro, 1)                                  # efeito espelho
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB))
        # no modo VIDEO, cada quadro precisa de um carimbo de tempo crescente (ms)
        resultado = reconhecedor.recognize_for_video(img, int((time.monotonic() - inicio) * 1000))
        for i, t in enumerate(anotar(quadro, resultado)):
            cv2.putText(quadro, t, (10, 25 + 25 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        cv2.imshow("AI-901 - MediaPipe gestos", quadro)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
