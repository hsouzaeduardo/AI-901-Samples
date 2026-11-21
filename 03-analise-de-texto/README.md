# Módulo 03 — Análise de texto e linguagem (PLN)

Slides: `AI-901T00-PowerPoint_03.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-nlp-concepts> e <https://aka.ms/mslearn-get-started-ai-text>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | Pré-processamento de texto | `01_preprocessamento.py` | Offline |
| 2 | Análise estatística: TF, TF-IDF, Bag of Words | `02_analise_estatistica.py` | Offline |
| 3 | Classificação de texto (TextRank) → resumo extrativo | `03_resumo_extrativo.py` | Offline |
| 4 | Modelos semânticos: `dog + young = puppy` | `04_embeddings_semanticos.py` | Offline |
| 5 | Modelos semânticos com um modelo real de embeddings | `05_embeddings_azure.py` | Azure |
| 6 | Análise de texto com modelos de uso geral (API OpenAI) | `06_analise_com_llm.py` | Azure |
| 7 | Linguagem do Azure: idioma, NER, PII, sentimento, frases-chave, resumo, saúde | `07_linguagem_azure.py` | Azure |
| 8 | Escolher o método certo | `08_comparar_metodos.py` | Azure |
| 9 | Usar Azure Language num agente (MCP + aprovação) | `09_agente_mcp_linguagem.py` | Azure |

## Destaques offline

- **`01_preprocessamento.py`:** aplica cada etapa do slide ao discurso da Lua: tokenização (67 tokens), normalização, remoção de stop words (60 → 26 termos), radical x lema (`são` → lema `ser`) e classes gramaticais.
- **`02_analise_estatistica.py`:** com 4 avaliações de restaurante, a TF mostra os tópicos (`jantar`, `risoto`, `garçom`). A TF-IDF mostra o que **distingue** cada avaliação. O BoW classifica o sentimento. Mostra também a limitação: "não foi ótimo" contaria como positivo.
- **`03_resumo_extrativo.py`:** PageRank sobre a similaridade entre frases da resenha do Commodore 64. Escolhe as 2 frases mais centrais.
- **`04_embeddings_semanticos.py`:** reproduz a tabela do slide 6:
  ```
  dog + young = [0.9 0.7 0.4] -> palavra mais próxima: puppy
  cat + young = [0.8 0.6 0.5] -> palavra mais próxima: kitten
  puppy - dog + cat = [0.8 0.6 0.5] -> kitten
  ```

## Destaques Azure

- **`06_analise_com_llm.py`:** segue os 5 passos do slide 14 (importar → `.env` → cliente → `responses.create` → resultado). Um único prompt devolve **JSON estrito** com sentimento, termos-chave, entidades e resumo. Roda 2 vezes para mostrar a variação.
- **`07_linguagem_azure.py`:** todos os métodos do SDK `TextAnalyticsClient`. Inclui `detect_language` (com a etiqueta alemã do CPC 464 do lab), `recognize_pii_entities` com `redacted_text` (CPF, telefone, e-mail), sentimento com mineração de opinião, resumo extrativo x abstrativo e **Text Analytics for Health**.
- **`08_comparar_metodos.py`:** analisa o mesmo texto 3 vezes com cada abordagem. A Linguagem do Azure devolve sempre o mesmo resultado, com confiança. O LLM varia na redação.
- **`09_agente_mcp_linguagem.py`:** agente com `MCPTool(require_approval="always")`. O app recebe `mcp_approval_request` e oferece as 3 opções do slide 17: **uma vez**, **sempre para essa ferramenta** e **sempre para todas**.

> Para o exemplo 9, copie a URL do servidor MCP da Linguagem do Azure no portal do Foundry (Ferramentas) para `LANGUAGE_MCP_URL` no `.env`.
