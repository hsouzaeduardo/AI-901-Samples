"""
Módulo 02 - Tópico: Criação de agentes (Serviço de Agente do Foundry)
"Salve uma configuração de modelo como um agente nomeado... Adicione ferramentas...
Use a API do projeto Foundry para se conectar ao agente a partir do código."

Este script:
  1) CRIA (ou atualiza) o agente "agente-despesas" com modelo + instruções
     (+ ferramenta de pesquisa na web, se usar --web)
  2) CONVERSA com o agente usando a API Responses (duas perguntas, mesma conversa)

Pré-requisitos: .env com PROJECT_ENDPOINT e MODEL_DEPLOYMENT_NAME; "az login".
  python 08_criar_agente.py
  python 08_criar_agente.py --web       (adiciona a ferramenta de pesquisa na web)

Nota: o slide 12 usa extra_body={"agent": {...}}, forma de versões beta do SDK.
No azure-ai-projects 2.x, use get_openai_client(agent_name=...) (como no lab)
ou extra_body={"agent_reference": {"name": ..., "type": "agent_reference"}}.
"""
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool
from azure.identity import DefaultAzureCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint = os.getenv("PROJECT_ENDPOINT") or sys.exit("Defina PROJECT_ENDPOINT no .env")
modelo = os.getenv("MODEL_DEPLOYMENT_NAME") or sys.exit("Defina MODEL_DEPLOYMENT_NAME no .env")
NOME = "agente-despesas"

INSTRUCOES = """Você é o assistente de despesas da Contoso.
- Responda em português, de forma objetiva.
- Regras: refeições até R$ 120/dia (nacional) e US$ 60/dia (internacional);
  pedidos em até 30 dias pelo portal Reembolsa; hotel acima de R$ 450/noite exige aprovação.
- Se a pergunta não for sobre despesas corporativas, diga que não pode ajudar."""

ferramentas = [WebSearchTool()] if "--web" in sys.argv else []

with DefaultAzureCredential() as credential, \
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as projeto:

    # 1) Criar uma nova VERSÃO do agente (se já existir, vira a versão seguinte)
    agente = projeto.agents.create_version(
        agent_name=NOME,
        definition=PromptAgentDefinition(model=modelo, instructions=INSTRUCOES, tools=ferramentas),
        description="Responde dúvidas sobre a política de despesas (exemplo AI-901)",
    )
    print(f"Agente '{agente.name}' versão {agente.version} criado. Ferramentas: "
          f"{[t.type for t in ferramentas] or 'nenhuma'}")

    # 2) Conversar: o cliente OpenAI fica "ligado" ao ponto de extremidade do agente
    openai_client = projeto.get_openai_client(agent_name=NOME)
    conversa = openai_client.conversations.create()     # guarda o histórico no serviço

    perguntas = ["Como envio um pedido de reembolso?",
                 "E qual o limite de refeição se a viagem for para Lisboa?"]
    if ferramentas:
        perguntas.append("Qual a cotação do euro hoje? Converta o limite para euros.")
    for pergunta in perguntas:
        r = openai_client.responses.create(
            conversation=conversa.id,
            input=[{"role": "user", "content": pergunta}],
        )
        print(f"\n> {pergunta}\n{r.output_text}")

    print("\nAbra o portal do Foundry > Agentes para ver o agente, testar no playground")
    print("e consultar rastreamento (traces) e uso de tokens.")
    # Para excluir: projeto.agents.delete(agent_name=NOME)
