# Módulo 02 — IA generativa e agentes

Slides: `AI-901T00-PowerPoint_02.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-intro-gen-ai> e <https://aka.ms/mslearn-get-started-gen-ai-agents>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | Modelos de IA generativa: tokens e embeddings | `01_tokens_e_embeddings.py` | Offline |
| 2 | Modelos de IA generativa: atenção | `02_atencao.py` | Offline |
| 3 | O que é IA generativa? Prever o próximo token + temperatura | `03_proximo_token.py` | Offline |
| 4 | Usar um modelo: instruções, prompts e parâmetros | `04_prompts_e_parametros.py` | Azure |
| 5 | Modelos do Foundry: implantação, limites de taxa, proteções | `05_implantacoes_e_limites.py` | Azure |
| 6 | Agentes usam ferramentas para **conhecimento** (RAG) | `06_conhecimento_rag.py` | Offline + Azure |
| 7 | Agentes usam ferramentas para **ações** (chamada de função) | `07_ferramenta_de_acao.py` | Azure |
| 8 | Criação de agentes no Serviço de Agente do Foundry | `08_criar_agente.py` | Azure |
| 9 | Agentes colaboram com outros agentes | `09_fluxo_multiagente.py` | Azure |

## Destaques offline

**`01_tokens_e_embeddings.py`:** tokenização (incluindo subpalavras, BPE) e matriz de similaridade do cosseno com os vetores do slide 5. `dog` fica próximo de `cat` e `puppy`, e `skateboard` fica próximo de `car`.

**`02_atencao.py`:** implementa `softmax(Q·Kᵀ)·V` com numpy. Resultado:
```
'bark' presta mais atenção em 'dog' (além de si mesmo)
```
Isso mostra como o contexto desambigua *bark*: aqui é o latido do cão, não a casca da árvore.

**`03_proximo_token.py`:** um modelo de bigramas treinado em 6 frases gera texto token a token. Com **temperatura 0.01**, as 3 gerações saem idênticas. Com **2.0**, saem variadas. É a intuição do parâmetro "criatividade" do slide 11.

## Destaques Azure

- **`04_prompts_e_parametros.py`:** 7 experimentos: com e sem *system prompt*, prompt vago x detalhado, `temperature`, `max_output_tokens`, conversa com `previous_response_id` e geração de código. Modelos de raciocínio (família gpt-5) não aceitam `temperature`; o script avisa e explica.
- **`05_implantacoes_e_limites.py`:** lista as implantações com tipo, versão e capacidade. Também trata o **HTTP 429** com espera exponencial e mostra a **proteção** (Prompt Shields) bloqueando um *jailbreak*.
- **`06_conhecimento_rag.py`:** recupera os trechos da política de despesas por TF-IDF, monta o prompt aumentado e compara a resposta **com e sem conhecimento**. Rode `--sem-azure` para ver só a recuperação.
- **`07_ferramenta_de_acao.py`:** o modelo pede `consultar_reembolso("R-1042")`, o app executa a função e devolve `function_call_output`. O modelo não executa código.
- **`08_criar_agente.py`:** `agents.create_version(PromptAgentDefinition(...))` + `get_openai_client(agent_name=...)` + `conversations`, o mesmo padrão do lab. Com `--web`, adiciona a ferramenta de pesquisa na web.
- **`09_fluxo_multiagente.py`:** **triagem** com saída JSON estruturada → **especialista** (despesas ou TI) → **revisor**.

**Discussão (verificação de conhecimento):** qual linha envia o prompt ao agente? É `responses.create(...)`. As linhas `agents.get(...)`/`create_version(...)` só obtêm ou criam a definição do agente.
