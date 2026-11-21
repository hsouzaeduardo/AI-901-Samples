"""
Módulo 05 - Ultralytics YOLO: TREINAR (ajuste fino) um detector
Tópico: "CNN - imagens com rótulos conhecidos para treinamento de modelos"

Ajuste fino (fine-tuning) do yolo26n no conjunto coco8: 8 imagens rotuladas que o
Ultralytics baixa automaticamente (~1 MB). Mostra o ciclo completo:
  dados rotulados -> treino (épocas, perda) -> validação (mAP) -> inferência -> exportação

Formato dos rótulos YOLO (um .txt por imagem, uma linha por objeto):
    <classe> <x_centro> <y_centro> <largura> <altura>      (valores de 0 a 1)
    ex.: 0 0.481 0.634 0.690 0.713
Para o SEU conjunto: rotule as imagens (ex.: Label Studio, CVAT, Roboflow) e crie um
YAML com path/train/val/names - veja o README do módulo.

Onde ficam os dados: o coco8 é baixado na pasta "datasets_dir" das configurações GLOBAIS
do Ultralytics (veja/altere com:  yolo settings). Os resultados do treino ficam em saidas/treinos/.

  pip install ultralytics
  python 12_yolo_treinar.py                 -> 3 épocas na CPU (~30 s a 3 min)
  python 12_yolo_treinar.py --epocas 20
  python 12_yolo_treinar.py --exportar      -> também exporta para ONNX (roda em OpenCV, celular, edge)
"""
import sys
from pathlib import Path

from ultralytics import YOLO
from ultralytics.utils import ASSETS

AQUI = Path(__file__).parent
MODELOS, SAIDAS = AQUI / "modelos", AQUI / "saidas"
MODELOS.mkdir(exist_ok=True)
epocas = int(sys.argv[sys.argv.index("--epocas") + 1]) if "--epocas" in sys.argv else 3

modelo = YOLO(str(MODELOS / "yolo26n.pt"))          # parte de pesos PRÉ-TREINADOS (transfer learning)

print(f"=== 1) Treino: {epocas} época(s) no coco8 ===")
modelo.train(data="coco8.yaml", epochs=epocas, imgsz=320, batch=8, device="cpu", workers=0,
             project=str(SAIDAS / "treinos"), name="coco8", exist_ok=True, plots=False, verbose=False)
pesos = Path(modelo.trainer.best)
print("Melhores pesos salvos em:", pesos)

print("\n=== 2) Validação: quão bem o modelo acerta caixas e classes? ===")
metricas = YOLO(str(pesos)).val(data="coco8.yaml", imgsz=320, device="cpu", workers=0, plots=False,
                                verbose=False, project=str(SAIDAS / "treinos"), name="validacao", exist_ok=True)
print(f"   mAP50     = {metricas.box.map50:.3f}   (acerto com sobreposição >= 50%)")
print(f"   mAP50-95  = {metricas.box.map:.3f}   (média com exigências de 50% a 95%)")
print(f"   precisão  = {metricas.box.mp:.3f}   | revocação = {metricas.box.mr:.3f}")

print("\n=== 3) Inferência com o modelo treinado ===")
r = YOLO(str(pesos))(str(ASSETS / "bus.jpg"), conf=0.4, verbose=False)[0]
for cls, conf in zip(r.boxes.cls.tolist(), r.boxes.conf.tolist()):
    print(f"   {r.names[int(cls)]:<10} {conf:.2f}")

if "--exportar" in sys.argv:
    print("\n=== 4) Exportação para ONNX (formato aberto, roda fora do Python/PyTorch) ===")
    caminho = YOLO(str(pesos)).export(format="onnx", imgsz=320)
    print("   Modelo exportado:", caminho)
    print("   Pode ser carregado com YOLO(caminho), onnxruntime ou cv2.dnn.readNetFromONNX(caminho).")

print("\nNo Azure, treinos maiores rodam em GPUs do Azure Machine Learning e o modelo pode")
print("ser publicado como ponto de extremidade gerenciado.")
