# Módulo 05 — Visão computacional

Slides: `AI-901T00-PowerPoint_05.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-ai-vision-concepts> e <https://aka.ms/mslearn-get-started-ai-vision>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | Tarefas: classificação, detecção, segmentação, análise contextual | `01_tarefas_de_visao.py` | Offline |
| 2 | Modelos: CNN (filtros, mapas de recursos, camada totalmente conectada) | `02_cnn.py` | Offline |
| 3 | Modelos: Transformador de Visão (ViT) e multimodal | `03_vit_e_multimodal.py` | Offline |
| 4 | Geração de imagem e vídeo: modelos de difusão | `04_difusao.py` | Offline |
| 5 | Modelos multimodais para análise de imagem | `05_analise_imagem.py` | Azure |
| 6 | Geração de imagem | `06_gerar_imagem.py` | Azure |
| 7 | Geração de vídeo (trabalho assíncrono) | `07_gerar_video.py` | Azure |

## Destaques offline

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

## Fluxo em aula (Azure)

```bash
python 06_gerar_imagem.py "Uma fruteira com maçãs e bananas, foto de estúdio"
python 05_analise_imagem.py                          # analisa a imagem que acabou de gerar
python 05_analise_imagem.py foto.jpg "Que sobremesas posso fazer com isso?"
python 07_gerar_video.py                             # create -> polling -> download
```

**Discussão (verificação de conhecimento, questão 3):** por que o vídeo é assíncrono? Porque a geração consome muitos recursos e demora. A API devolve um ID e o cliente consulta o status (`queued` → `in_progress` → `completed`).
