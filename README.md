# AI-901 — Exemplos práticos (Microsoft Azure AI Fundamentals)

Exemplos práticos para **cada tópico** dos slides oficiais do curso **AI-901T00 — Introdução à IA no Azure** (versão pt-BR).
Cada pasta corresponde a um dos 6 módulos. Cada arquivo traz no cabeçalho o **tópico do slide** que ilustra.

Há dois tipos de exemplo:

| Tipo | Precisa de Azure? | Para que serve |
|---|---|---|
| **Offline** | Não. Só Python + `numpy` | Mostrar *como a técnica funciona por dentro*: tokens, atenção, TF-IDF, CNN, difusão, OCR… Bom para a parte conceitual (cerca de 40% do exame). |
| **Azure / Foundry** | Sim (recurso + projeto do Microsoft Foundry) | Usar os serviços de verdade, com o mesmo SDK e os mesmos padrões dos labs oficiais (cerca de 60% do exame). |

---

## Mapa: tópico do slide → exemplo

Agrupado pelos 3 blocos de conteúdo do `Curso_AI-901_Final.pptx`.

### Bloco 01 — Conceitos e recursos de IA

| Módulo / tópico do slide | Exemplo | Tipo |
|---|---|---|
| **M1** O que é inteligência artificial? | [01_o_que_e_ia.py](01-conceitos-e-azure/01_o_que_e_ia.py): prever, reconhecer padrões e decidir (aluguel de bicicletas) | Offline |
| **M1** Cargas de trabalho de IA | [02_cargas_de_trabalho.py](01-conceitos-e-azure/02_cargas_de_trabalho.py): 12 cenários de negócio + quiz | Offline |
| **M1** Princípios de IA responsável | [03_ia_responsavel.py](01-conceitos-e-azure/03_ia_responsavel.py): auditoria dos 6 princípios num modelo de crédito | Offline |
| **M1** Microsoft Azure (locatário → assinatura → grupo → recurso) | [04_hierarquia_azure.sh](01-conceitos-e-azure/04_hierarquia_azure.sh): criação com a CLI do Azure | Azure CLI |
| **M1** Microsoft Foundry (recurso, projeto, modelos, agentes, ferramentas, conhecimento) | [04_hierarquia_azure.sh](01-conceitos-e-azure/04_hierarquia_azure.sh) e [07_explorar_projeto_foundry.py](01-conceitos-e-azure/07_explorar_projeto_foundry.py) | Azure |
| **M1** Pontos de extremidade (REST, chave x Entra ID, JSON, SDK) | [05_endpoint_rest.py](01-conceitos-e-azure/05_endpoint_rest.py) (REST puro) e [06_endpoint_sdk.py](01-conceitos-e-azure/06_endpoint_sdk.py) (SDK) | Azure |

### Bloco 02 — IA generativa e agentes no Microsoft Foundry

| Módulo / tópico do slide | Exemplo | Tipo |
|---|---|---|
| **M2** O que é a IA generativa? (prever o próximo token) | [03_proximo_token.py](02-ia-generativa-e-agentes/03_proximo_token.py): mini modelo de linguagem e temperatura | Offline |
| **M2** Modelos de IA generativa (tokens, embeddings) | [01_tokens_e_embeddings.py](02-ia-generativa-e-agentes/01_tokens_e_embeddings.py) | Offline |
| **M2** Modelos de IA generativa (atenção) | [02_atencao.py](02-ia-generativa-e-agentes/02_atencao.py): "bark" presta atenção em "dog" | Offline |
| **M2** O que são agentes? (conhecimento) | [06_conhecimento_rag.py](02-ia-generativa-e-agentes/06_conhecimento_rag.py): RAG feito à mão | Offline + Azure |
| **M2** O que são agentes? (ações) | [07_ferramenta_de_acao.py](02-ia-generativa-e-agentes/07_ferramenta_de_acao.py): chamada de função | Azure |
| **M2** O que são agentes? (colaboração entre agentes) | [09_fluxo_multiagente.py](02-ia-generativa-e-agentes/09_fluxo_multiagente.py): triagem → especialista → revisor | Azure |
| **M2** Modelos do Foundry (tipo de implantação, versão, limites de taxa, proteções) | [05_implantacoes_e_limites.py](02-ia-generativa-e-agentes/05_implantacoes_e_limites.py) | Azure |
| **M2** Usar um modelo (instruções, prompts, parâmetros) | [04_prompts_e_parametros.py](02-ia-generativa-e-agentes/04_prompts_e_parametros.py): 7 experimentos | Azure |
| **M2** Criação de agentes (Serviço de Agente do Foundry) | [08_criar_agente.py](02-ia-generativa-e-agentes/08_criar_agente.py) | Azure |

### Bloco 03 — Soluções de IA com o Microsoft Foundry

| Módulo / tópico do slide | Exemplo | Tipo |
|---|---|---|
| **M3** Pré-processamento de texto | [01_preprocessamento.py](03-analise-de-texto/01_preprocessamento.py): discurso "Escolhemos ir para a Lua" | Offline |
| **M3** Análise estatística (TF, TF-IDF, BoW) | [02_analise_estatistica.py](03-analise-de-texto/02_analise_estatistica.py) | Offline |
| **M3** TextRank / resumo extrativo | [03_resumo_extrativo.py](03-analise-de-texto/03_resumo_extrativo.py) | Offline |
| **M3** Modelos semânticos (`dog + young = puppy`) | [04_embeddings_semanticos.py](03-analise-de-texto/04_embeddings_semanticos.py) e [05_embeddings_azure.py](03-analise-de-texto/05_embeddings_azure.py) | Offline / Azure |
| **M3** O que é PLN + análise com modelos de uso geral (API OpenAI) | [06_analise_com_llm.py](03-analise-de-texto/06_analise_com_llm.py) | Azure |
| **M3** Linguagem do Azure (idioma, NER, PII, sentimento, frases-chave, resumo, saúde) | [07_linguagem_azure.py](03-analise-de-texto/07_linguagem_azure.py) | Azure |
| **M3** Escolher o método certo | [08_comparar_metodos.py](03-analise-de-texto/08_comparar_metodos.py): determinismo x variação | Azure |
| **M3** Usar Azure Language num agente (MCP + aprovação) | [09_agente_mcp_linguagem.py](03-analise-de-texto/09_agente_mcp_linguagem.py) | Azure |
| **M4** Reconhecimento de fala (pipeline) | [01_pipeline_reconhecimento.py](04-fala/01_pipeline_reconhecimento.py): "nice to be here" | Offline |
| **M4** Sintetização de voz (pipeline, normalização, prosódia) | [02_pipeline_sintese.py](04-fala/02_pipeline_sintese.py): gera SSML e WAV | Offline |
| **M4** Implementação da síntese (TTS) | [03_tts.py](04-fala/03_tts.py) | Azure |
| **M4** Implementação do reconhecimento (STT) | [04_stt.py](04-fala/04_stt.py) | Azure |
| **M4** Agente capaz de falar (Voice Live) | [05_voice_live.py](04-fala/05_voice_live.py) | Azure |
| **M5** Tarefas de visão (classificação, detecção, segmentação, contexto) | [01_tarefas_de_visao.py](05-visao-computacional/01_tarefas_de_visao.py) | Offline |
| **M5** Modelos: CNN | [02_cnn.py](05-visao-computacional/02_cnn.py): filtros, pooling e classificador treinado | Offline |
| **M5** Modelos: ViT e multimodal | [03_vit_e_multimodal.py](05-visao-computacional/03_vit_e_multimodal.py) | Offline |
| **M5** Geração de imagem e vídeo (difusão) | [04_difusao.py](05-visao-computacional/04_difusao.py) | Offline |
| **M5** Modelos multimodais para análise de imagem | [05_analise_imagem.py](05-visao-computacional/05_analise_imagem.py) | Azure |
| **M5** Geração de imagem | [06_gerar_imagem.py](05-visao-computacional/06_gerar_imagem.py) | Azure |
| **M5** Geração de vídeo (trabalho assíncrono) | [07_gerar_video.py](05-visao-computacional/07_gerar_video.py) | Azure |
| **M6** OCR | [01_ocr_simulado.py](06-extracao-de-informacoes/01_ocr_simulado.py): mini OCR com as 5 etapas | Offline |
| **M6** Extração de campo e mapeamento | [02_mapeamento_campos.py](06-extracao-de-informacoes/02_mapeamento_campos.py): cupom fiscal → JSON/CSV | Offline |
| **M6** O que é extração + IA generativa no mapeamento | [03_extracao_com_llm.py](06-extracao-de-informacoes/03_extracao_com_llm.py) | Azure |
| **M6** Documentos: analisadores pré-definidos (SDK) | [04_content_understanding_sdk.py](06-extracao-de-informacoes/04_content_understanding_sdk.py) | Azure |
| **M6** Documentos: API REST | [05_content_understanding_rest.py](06-extracao-de-informacoes/05_content_understanding_rest.py) | Azure |
| **M6** Documentos: analisador personalizado (esquema) | [06_analisador_personalizado.py](06-extracao-de-informacoes/06_analisador_personalizado.py) | Azure |
| **M6** Áudio e vídeo | [07_audio_e_video.py](06-extracao-de-informacoes/07_audio_e_video.py) | Azure |

---

## Como rodar

### 1. Exemplos offline (sem Azure)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install numpy
python 03-analise-de-texto/01_preprocessamento.py
```

### 2. Exemplos com Azure / Microsoft Foundry

1. Crie um **projeto do Foundry** em <https://ai.azure.com> (ou use [04_hierarquia_azure.sh](01-conceitos-e-azure/04_hierarquia_azure.sh)).
2. Implante os modelos que for usar: um modelo de chat com visão (ex.: `gpt-4.1-mini`). Opcionais: `text-embedding-3-small`, `gpt-image-1`, `sora-2`.
3. Copie `.env.example` para `.env` **na raiz do repositório** e preencha os valores. O `.env` está no `.gitignore`: nunca o envie ao Git.
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   pip install --pre azure-ai-contentunderstanding    # módulo 06
   pip install pyaudio                                # só para 04-fala/05_voice_live.py
   ```
5. Os exemplos que usam o **SDK de projetos** (agentes) autenticam com Microsoft Entra ID via `DefaultAzureCredential`. Rode `az login` antes.
   > O `DefaultAzureCredential` tenta **primeiro** as variáveis de ambiente `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` e `AZURE_TENANT_ID` (entidade de serviço), e só depois o `az login`. Se essas variáveis estiverem definidas na sua máquina, os scripts usarão aquela identidade, e não a sua.

> **Custos:** os exemplos Azure consomem tokens e recursos. Ao final da aula, exclua o grupo de recursos:
> `az group delete --name rg-ai901-exemplos --yes`.

### Encadeamentos úteis em aula

| Primeiro… | …depois |
|---|---|
| `04-fala/02_pipeline_sintese.py` (gera SSML) | `04-fala/03_tts.py --ssml` |
| `04-fala/03_tts.py` (gera `mensagem.wav`) | `04-fala/04_stt.py` (transcreve) e `06-extracao-de-informacoes/07_audio_e_video.py` |
| `05-visao-computacional/06_gerar_imagem.py` | `05-visao-computacional/05_analise_imagem.py` (analisa a imagem gerada) |
| `06-extracao-de-informacoes/01_ocr_simulado.py` (texto) | `02_mapeamento_campos.py` (significado) → `03_extracao_com_llm.py` (IA generativa) |

## Versões testadas

- Python 3.12. Exemplos offline executados com numpy 1.26 e 2.x.
- SDKs verificados (assinaturas, classes e atributos): `openai` 3.x, `azure-ai-projects` 2.11, `azure-ai-textanalytics` 5.4, `azure-cognitiveservices-speech` 1.53, `azure-ai-voicelive` 1.3, `azure-ai-contentunderstanding` 1.2b3.
- Padrões de código alinhados aos labs oficiais: [MicrosoftLearning/mslearn-ai-fundamentals](https://github.com/MicrosoftLearning/mslearn-ai-fundamentals).

**O que foi verificado e como:**
- Os **18 exemplos offline** foram executados e as saídas citadas nos READMEs são reais.
- Os **exemplos Python com Azure** não foram executados contra uma assinatura real. Foram verificados a sintaxe, os imports e os nomes de classes, métodos e atributos nos SDKs instalados.
- O script **`04_hierarquia_azure.sh`** só teve a sintaxe verificada (`bash -n`). Os comandos e parâmetros foram conferidos na documentação da CLI no Microsoft Learn (requer CLI 2.80+).

Modelos, regiões e versões de API mudam com frequência: se algo falhar, confira a mensagem de erro e o portal do Foundry.
