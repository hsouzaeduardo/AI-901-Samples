# Módulo 06 — Extração de informações

Slides: `AI-901T00-PowerPoint_06.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-ai-info-concepts> e <https://aka.ms/mslearn-get-started-information-extraction>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | OCR: 5 etapas | `01_ocr_simulado.py` | Offline |
| 2 | Extração de campo e mapeamento: 5 etapas | `02_mapeamento_campos.py` | Offline |
| 3 | O que é extração + IA generativa no mapeamento | `03_extracao_com_llm.py` | Azure |
| 4 | Documentos: analisadores pré-definidos (SDK Python) | `04_content_understanding_sdk.py` | Azure |
| 5 | Documentos: API REST e resultado JSON | `05_content_understanding_rest.py` | Azure |
| 6 | Documentos: analisador personalizado (esquema de campos) | `06_analisador_personalizado.py` | Azure |
| 7 | Áudio e vídeo | `07_audio_e_video.py` | Azure |

## A história do módulo, em 3 scripts

1. **`01_ocr_simulado.py`:** um mini OCR "imprime" um recibo numa imagem, adiciona ruído e lê o texto de volta. As 5 etapas são aquisição, pré-processamento (binarização e limpeza), detecção de regiões, reconhecimento por templates com confiança e pós-processamento por contexto:
   ```
   'T0TAL R$ 20,50'  confiança média 0.98     <- O e 0 são idênticos na fonte!
   "texto": "TOTAL R$ 20,50"                   <- corrigido pelo contexto
   ```
   *"O OCR entrega texto, não significado."*
2. **`02_mapeamento_campos.py`:** um cupom fiscal passa pela detecção de candidatos (regex), pelo mapeamento por rótulo ("TOTAL" → total) e pela normalização (`05/11/2026` → `2026-11-05`, `76,04` → `76.04`). Depois vêm as validações (dígitos verificadores do **CNPJ** e soma dos itens = total). Por fim, a **integração**: uma linha em `saidas/despesas.csv`.
3. **`03_extracao_com_llm.py`:** um OCR "sujo" (`P0NTO D0CE`, `VLR A PAGAR`, `5 de nov.`) quebraria as regras fixas. O modelo entende o significado e preenche um **esquema JSON estrito**. Aceita também a foto de um recibo.

## Content Understanding (Azure)

```bash
python 04_content_understanding_sdk.py --configurar     # 1a vez: implantações padrão (gpt-4.1, gpt-4.1-mini, embeddings)
python 04_content_understanding_sdk.py                  # prebuilt-invoice na fatura do lab
python 04_content_understanding_sdk.py prebuilt-layout  # compare: read -> layout -> invoice
python 05_content_understanding_rest.py                 # mesmo fluxo via REST (POST + Operation-Location + GET)
python 06_analisador_personalizado.py                   # esquema próprio: extract / classify / generate
python 07_audio_e_video.py                              # analisa o WAV gerado no módulo 04
```

**Discussão (verificação de conhecimento):**
- A vantagem sobre o OCR básico é que o Content Understanding entende a **estrutura** e mapeia os dados para um **esquema**.
- O **analisador** define como o conteúdo é processado e quais dados estruturados voltam.
- Depois de enviar o conteúdo, o cliente **consulta (polling)** até o trabalho terminar. No SDK, isso é `poller.result()`. Na API REST, é o loop sobre `Operation-Location`.
