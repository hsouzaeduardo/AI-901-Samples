"""
Módulo 05 - Ultralytics YOLO em VÍDEO: detecção + RASTREAMENTO de objetos
Tópico: "Análise de gravação de vídeo" (também citado no módulo 06) e detecção de objetos

Detectar = achar objetos em CADA quadro. Rastrear = dar um ID a cada objeto e
segui-lo entre os quadros (algoritmo ByteTrack). Com IDs dá para CONTAR objetos
únicos, medir permanência, cruzamento de linhas etc.

  pip install ultralytics
  python 11_yolo_rastreamento.py --demo            -> gera um vídeo de teste a partir de bus.jpg
  python 11_yolo_rastreamento.py video.mp4         -> um vídeo seu (ou URL de vídeo)
  python 11_yolo_rastreamento.py --webcam          -> câmera ao vivo (tecla q para sair)
  Opções: --sem-janela (não abre janela; só grava saidas/yolo_rastreamento.mp4)
"""
import sys
from collections import defaultdict
from pathlib import Path

import cv2
from ultralytics import YOLO
from ultralytics.utils import ASSETS

AQUI = Path(__file__).parent
MODELOS, SAIDAS = AQUI / "modelos", AQUI / "saidas"
MODELOS.mkdir(exist_ok=True)
SAIDAS.mkdir(exist_ok=True)
CLASSES = [0, 1, 2, 3, 5, 7]          # pessoa, bicicleta, carro, moto, ônibus, caminhão (COCO)


def gerar_video_demo(destino, quadros=60):
    """Simula uma câmera fazendo 'zoom e panorâmica' sobre a foto bus.jpg."""
    img = cv2.imread(str(ASSETS / "bus.jpg"))
    a, l = img.shape[:2]
    out = cv2.VideoWriter(str(destino), cv2.VideoWriter_fourcc(*"mp4v"), 15, (640, 480))
    for i in range(quadros):
        z = 1.0 - 0.25 * i / quadros                     # aproxima aos poucos
        w, h = int(l * z), int(a * z)
        x = int((l - w) * i / quadros)                   # e desliza para a direita
        out.write(cv2.resize(img[a - h:a, x:x + w], (640, 480)))
    out.release()
    return str(destino)


if "--webcam" in sys.argv:
    fonte = 0
elif "--demo" in sys.argv:
    fonte = gerar_video_demo(SAIDAS / "demo_entrada.mp4")
    print("Vídeo de demonstração gerado:", fonte)
else:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    fonte = args[0]
mostrar = "--sem-janela" not in sys.argv

modelo = YOLO(str(MODELOS / "yolo26n.pt"))
ids_por_classe = defaultdict(set)
gravador = None

# stream=True processa quadro a quadro sem acumular tudo na memória;
# persist=True mantém os IDs entre as chamadas (necessário para rastrear)
for n, r in enumerate(modelo.track(source=fonte, stream=True, persist=True, classes=CLASSES,
                                   tracker="bytetrack.yaml", conf=0.3, verbose=False)):
    if r.boxes.id is not None:
        for obj_id, cls in zip(r.boxes.id.int().tolist(), r.boxes.cls.int().tolist()):
            ids_por_classe[r.names[cls]].add(obj_id)
    quadro = r.plot()                                   # caixas + "id:N classe confiança"
    resumo = " | ".join(f"{k}: {len(v)}" for k, v in ids_por_classe.items())
    cv2.putText(quadro, f"unicos -> {resumo}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if gravador is None:
        gravador = cv2.VideoWriter(str(SAIDAS / "yolo_rastreamento.mp4"), cv2.VideoWriter_fourcc(*"mp4v"),
                                   15, (quadro.shape[1], quadro.shape[0]))
    gravador.write(quadro)
    if mostrar:
        cv2.imshow("AI-901 - YOLO rastreamento", quadro)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

if gravador:
    gravador.release()
cv2.destroyAllWindows()
print(f"Quadros processados: {n + 1}")
print("Objetos ÚNICOS rastreados:", {k: len(v) for k, v in ids_por_classe.items()})
print("Vídeo anotado em", SAIDAS / "yolo_rastreamento.mp4")
