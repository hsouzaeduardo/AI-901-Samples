# Módulo 05 — Visão computacional

Slides: `AI-901T00-PowerPoint_05.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-ai-vision-concepts> e <https://aka.ms/mslearn-get-started-ai-vision>

O módulo tem **quatro camadas**. A mesma tarefa do slide ("detectar a fruta", "segmentar a pessoa") é resolvida de jeitos cada vez mais poderosos:

| Camada | Onde roda | Arquivos |
|---|---|---|
| **A. Por dentro** (numpy puro) | sua máquina | 01 a 04 |
| **B. Visão clássica** (OpenCV: filtros e regras escritas à mão) | sua máquina | 08, 09 |
| **C. Modelos prontos e leves** (YOLO e MediaPipe: CNNs pré-treinadas) | sua máquina, celular, edge | 10 a 14 |
| **D. Modelos multimodais e generativos** (Microsoft Foundry) | nuvem Azure | 05 a 07 |

| # | Tópico do slide | Arquivo | Camada |
|---|---|---|---|
| 1 | Tarefas: classificação, detecção, segmentação, análise contextual | `01_tarefas_de_visao.py` | A |
| 2 | Modelos: CNN (filtros, mapas de recursos, camada totalmente conectada) | `02_cnn.py` | A |
| 3 | Modelos: Transformador de Visão (ViT) e multimodal | `03_vit_e_multimodal.py` | A |
| 4 | Geração de imagem e vídeo: modelos de difusão | `04_difusao.py` | A |
| 5 | Modelos multimodais para análise de imagem | `05_analise_imagem.py` | D |
| 6 | Geração de imagem | `06_gerar_imagem.py` | D |
| 7 | Geração de vídeo (trabalho assíncrono) | `07_gerar_video.py` | D |
| 8 | Tarefas + filtros da CNN com **OpenCV** | `08_opencv_tarefas.py` | B |
| 9 | Detecção de rostos: **Haar (clássico) x YuNet (CNN)** + anonimização | `09_opencv_rostos.py` | B/C |
| 10 | Tarefas com **YOLO**: classificação, detecção, segmentação (instância e semântica), pose | `10_yolo_tarefas.py` | C |
| 11 | **YOLO em vídeo**: detecção + rastreamento + contagem | `11_yolo_rastreamento.py` | C |
| 12 | **Treinar o YOLO** (imagens rotuladas → mAP → ONNX) | `12_yolo_treinar.py` | C |
| 13 | Tarefas com **MediaPipe**: classificação, detecção, segmentação, pose, mãos | `13_mediapipe_tarefas.py` | C |
| 14 | **MediaPipe ao vivo**: gestos e contagem de dedos na webcam | `14_mediapipe_maos_webcam.py` | C |

## A. Por dentro (numpy)

**`01_tarefas_de_visao.py`:** uma imagem sintética com maçã e banana passa pelas 4 tarefas:
```
SEGMENTAÇÃO: cada pixel vira M, B ou .
DETECÇÃO:    maçã caixa=(x=3, y=3, l=9, a=9) | banana caixa=(x=16, y=4, l=13, a=6)
CLASSIFICAÇÃO: 'fruteira (várias frutas)'
CONTEXTO:    'Uma maçã vermelha à esquerda de uma banana alongada, sobre fundo escuro.'
```

**`02_cnn.py`:** usa filtros Sobel → ReLU → max-pooling → camada totalmente conectada treinada por gradiente descendente. A acurácia vai de 50% para 100% e o script mostra **probabilidades por classe** em imagens novas.

**`03_vit_e_multimodal.py`:** divide a imagem em patches, gera embeddings com posição e calcula a autoatenção entre patches (contexto global). Depois coloca imagem e legenda num **espaço vetorial compartilhado** e escolhe a legenda certa para 3 imagens.

**`04_difusao.py`:** no processo direto, mostra a imagem virando ruído. No processo reverso, parte de ruído aleatório e remove o ruído guiado pelo **prompt** ("um círculo" x "uma cruz").

## B. Visão clássica com OpenCV

```bash
pip install -r requirements-visao.txt
python 08_opencv_tarefas.py                 # cena sintética (offline)
python 08_opencv_tarefas.py foto.jpg        # sua foto
```

**`08_opencv_tarefas.py`:** aplica os mesmos kernels Sobel do `02_cnn.py` com `cv2.filter2D`, depois Canny, segmentação por cor em **HSV**, contornos → caixas, circularidade (redondo x alongado), classificação e frase de contexto:
```
3) Detecção: 3 objetos
   maca    caixa(x,y,l,a)=(56, 146, 109, 110)  circularidade=0.89 (redondo)
   maca    caixa(x,y,l,a)=(203, 183, 95, 96)   circularidade=0.89 (redondo)
   banana  caixa(x,y,l,a)=(302, 131, 236, 111) circularidade=0.25 (alongado)
5) Análise contextual: 'A imagem mostra 2 maçãs e 1 banana; as maçãs estão à esquerda da banana.'
```
Bom gancho para discussão: no `opencv_filtros.png`, a banana quase **some** das bordas, porque amarelo e bege têm brilho parecido em tons de cinza. Por isso o script segmenta por **cor**.

**`09_opencv_rostos.py`:** compara duas gerações de detector com resultados reais nas fotos de exemplo do OpenCV e do Ultralytics:

| Foto | Haar Cascade (2001, características manuais) | YuNet (CNN) |
|---|---|---|
| `messi5.jpg` (1 rosto) | 1 caixa, **no lugar errado** (camisa/torcida) | 1 rosto correto, confiança 0,92 + 5 pontos (olhos, nariz, boca) |
| `zidane.jpg` (2 rostos) | 3 caixas (**1 falso positivo**) | 2 rostos corretos (0,94 e 0,90) |

Use `--anonimizar` para pixelizar os rostos. É o princípio de **privacidade** do módulo 01 na prática. Use `--webcam` para a demonstração ao vivo.
> O **OpenCV 5 removeu o Haar Cascade**: o script avisa e sugere `--yunet` (ou `opencv-python<5`).

## C. Modelos prontos: Ultralytics YOLO e MediaPipe

### YOLO (`10` a `12`)

```bash
python 10_yolo_tarefas.py                    # foto de exemplo bus.jpg (vem com o pacote)
python 11_yolo_rastreamento.py --demo        # gera um vídeo e rastreia (ou: video.mp4 / --webcam)
python 12_yolo_treinar.py --exportar         # treina 3 épocas na CPU e exporta ONNX
```

Resultados reais com YOLO26 nano na CPU:
```
1) CLASSIFICAÇÃO: minibus 51.6% | police_van 36.9% | trolleybus 9.6%
2) DETECÇÃO: bus 0.88 | person 0.87 | person 0.86 | person 0.85 | person 0.66   (~70 ms)
3b) SEGMENTAÇÃO SEMÂNTICA: train 30.9% | road 27.6% | building 19.3% | person 14.6%
5) ANÁLISE CONTEXTUAL: a cena contém 4 pessoas, 1 ônibus.
11) Objetos ÚNICOS rastreados em 60 quadros: {'person': 4, 'bus': 1}
12) Treino coco8, 3 épocas: mAP50 = 0.796 | mAP50-95 = 0.586
```
Pontos para discussão:
- **Instância x semântica:** o `-seg` separa "pessoa 1, pessoa 2". O `-sem` só diz "pixel de pessoa", que é o conceito do slide.
- **Modelos erram:** o modelo semântico (treinado em cenas de rua) chamou o ônibus de **"train"**. O de detecção acertou "bus".
- **Detectar x rastrear:** sem IDs, uma pessoa em 60 quadros seria contada 60 vezes.
- **Treino:** rótulos no formato YOLO (`classe x_centro y_centro largura altura`, de 0 a 1), mAP como métrica e ONNX para rodar fora do Python.

**Para treinar com SUAS imagens**, rotule-as (Label Studio, CVAT, Roboflow) e crie um YAML:
```yaml
path: C:/dados/frutas          # pasta do conjunto
train: images/train            # imagens de treino (rótulos em labels/train)
val: images/val
names: {0: maca, 1: banana}
```
Depois: `YOLO("yolo26n.pt").train(data="frutas.yaml", epochs=50)`.

> - Os pesos são baixados para `modelos/`.
> - O coco8 vai para o `datasets_dir` das configurações **globais** do Ultralytics (`yolo settings`).
> - **Licença:** o Ultralytics é **AGPL-3.0**. Uso comercial em software fechado exige licença Enterprise.

### MediaPipe (`13` e `14`)

```bash
python 13_mediapipe_tarefas.py               # foto de exemplo (baixada do repositório do OpenCV)
python 14_mediapipe_maos_webcam.py           # webcam: gestos + dedos (ou passe uma foto)
```
Resultados reais na foto `messi5.jpg`:
```
1) CLASSIFICAÇÃO: soccer ball 37.3%
2) DETECÇÃO: person 0.92 | sports ball 0.68 | person 0.41 (torcedor ao fundo)
3) SEGMENTAÇÃO SEMÂNTICA: background 90.3% | person 9.7%
4) POSE: 1 pessoa, 33 pontos   5) MÃOS: 1 mão (Left, 0.79)
```
O `14` reconhece 7 gestos (joinha, mão aberta, punho, vitória, apontar, "eu te amo"…), conta dedos levantados e liga cada gesto a uma ação de exemplo, como controlar uma apresentação sem tocar em nada (princípio de **inclusão**).

> - Use a API **Tasks** (`mediapipe.tasks.python.vision`). A antiga `mp.solutions`, de muitos tutoriais, **não existe mais** nas versões 1.x.
> - As mensagens `INFO: ... LiteRT` no terminal são normais. Para escondê-las, acrescente `2>/dev/null` (PowerShell: `2>$null`).
> - **Licença:** Apache 2.0.

**Discussão: quando usar cada camada?**

| Precisa de… | Use |
|---|---|
| Tempo real, offline, baixo custo, privacidade (nada sai do dispositivo) | YOLO / MediaPipe / OpenCV (camadas B e C) |
| Classes próprias (ex.: defeitos da SUA linha de produção) | YOLO treinado com suas imagens (`12`) |
| Entender a cena, responder perguntas abertas, gerar imagens ou vídeos | Modelos multimodais do Foundry (camada D) |
| Melhor dos dois mundos | Detectar e recortar localmente com YOLO, e enviar só o recorte ao modelo multimodal |

## D. Fluxo em aula (Azure)

```bash
python 06_gerar_imagem.py "Uma fruteira com maçãs e bananas, foto de estúdio"
python 05_analise_imagem.py                          # analisa a imagem que acabou de gerar
python 05_analise_imagem.py foto.jpg "Que sobremesas posso fazer com isso?"
python 07_gerar_video.py                             # create -> polling -> download
```

**Discussão (verificação de conhecimento, questão 3):** por que o vídeo é assíncrono? Porque a geração consome muitos recursos e demora. A API devolve um ID e o cliente consulta o status (`queued` → `in_progress` → `completed`).
