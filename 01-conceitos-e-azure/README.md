# Módulo 01 — Introdução à IA e à IA no Azure

Slides: `AI-901T00-PowerPoint_01.pt-BR.pptx` · Learn: <https://aka.ms/mslearn-ai-concepts> e <https://aka.ms/mslearn-get-started-azure-ai>

| # | Tópico do slide | Arquivo | Tipo |
|---|---|---|---|
| 1 | O que é inteligência artificial? | `01_o_que_e_ia.py` | Offline |
| 2 | Cargas de trabalho de IA | `02_cargas_de_trabalho.py` | Offline |
| 3 | Princípios de IA responsável | `03_ia_responsavel.py` | Offline |
| 4 | Microsoft Azure + Microsoft Foundry (hierarquia e implantação) | `04_hierarquia_azure.sh` | Azure CLI |
| 5 | Pontos de extremidade: REST "na mão" | `05_endpoint_rest.py` | Azure |
| 6 | Pontos de extremidade: SDK + chave x Entra ID | `06_endpoint_sdk.py` | Azure |
| 7 | Foundry: modelos, agentes, ferramentas e conhecimento do projeto | `07_explorar_projeto_foundry.py` | Azure |

## 1. O que é IA? — `01_o_que_e_ia.py`
**Cenário:** uma locadora de bicicletas usa dados históricos para **prever** a demanda (regressão), **reconhecer padrões** de dia de alta ou baixa demanda (k-NN) e **decidir** quantos funcionários escalar.

```
Modelo aprendido: aluguéis = -19.9 + 16.7*temperatura + 174.4*fim_de_semana
Amanhã ({'temperatura': 25, 'fim_de_semana': 1}): previsão de 572 aluguéis
temp=25°C fds=1 -> demanda ALTA (vizinhos: ['alta', 'alta', 'alta'])
Previsão de 572 aluguéis -> escalar 5 funcionários
```

## 2. Cargas de trabalho — `02_cargas_de_trabalho.py`
São 12 cenários reais, cada um ligado a uma das 6 cargas de trabalho do slide, com justificativa. Use `--quiz` para a turma responder no terminal.

## 3. IA responsável — `03_ia_responsavel.py`
Cada princípio vira um **teste concreto** num modelo de crédito fictício:

| Princípio | Verificação no código |
|---|---|
| Imparcialidade | taxa de aprovação por grupo + regra dos 80% (o modelo **falha**: razão de 0,70) |
| Confiabilidade e segurança | validação de entradas absurdas + casos na zona cinzenta vão para revisão humana |
| Privacidade e segurança | mascarar CPF e telefone antes de gravar logs |
| Inclusão | linguagem simples + múltiplos canais |
| Transparência | contribuição de cada fator na decisão |
| Responsabilidade | trilha de auditoria (versão do modelo, hash da entrada, responsável) |

## 4. Hierarquia do Azure — `04_hierarquia_azure.sh`
Cria **grupo de recursos → recurso do Foundry → projeto → implantação de modelo** e imprime as variáveis do `.env`. Os comentários ligam cada parâmetro aos slides: `--sku-name` é o *tipo de implantação*, `--sku-capacity` é o *limite de taxa* (mil TPM) e `--model-version` é a *versão*.

> Requer Azure CLI 2.80.0 ou superior (`az upgrade`). Se a criação do projeto falhar, o script avisa e continua: crie o projeto no portal.

## 5 e 6. Pontos de extremidade
- `05_endpoint_rest.py` mostra a **requisição** (URL, cabeçalhos, corpo JSON) e a **resposta** (status, cabeçalhos, JSON), sem SDK. Rode também com `--entra` para trocar a chave por um token do Microsoft Entra ID.
- `06_endpoint_sdk.py` faz a mesma chamada com o SDK da OpenAI em 3 linhas. É o "SDK abstrai a API REST" do slide.

**Discussão (verificação de conhecimento, questão 2):** o ponto de extremidade é a **URL** do modelo implantado. A chave **autentica** a requisição. Em produção, prefira Entra ID com `DefaultAzureCredential`.
