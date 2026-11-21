"""
Módulo 01 - Tópico: Microsoft Foundry - uma plataforma unificada
"Em um projeto, você trabalha com: Modelos, Agentes, Ferramentas e Conhecimento"

Conecta-se ao PROJETO do Foundry com o SDK azure-ai-projects e lista o que existe
em cada um dos quatro pilares do slide.

Pré-requisitos:
  - .env com PROJECT_ENDPOINT
  - "az login" (o SDK de projetos usa Microsoft Entra ID - DefaultAzureCredential)

  python 07_explorar_projeto_foundry.py
"""
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint = os.getenv("PROJECT_ENDPOINT") or sys.exit("Defina PROJECT_ENDPOINT no .env")

with DefaultAzureCredential() as credential, \
        AIProjectClient(endpoint=endpoint, credential=credential) as projeto:

    print("=== MODELOS (implantações do projeto) ===")
    for d in projeto.deployments.list():
        sku = getattr(d, "sku", None)
        tipo = f"{sku.name} / capacidade {sku.capacity}" if sku else "-"
        print(f"- {d.name:<28} modelo={getattr(d, 'model_name', '?')} "
              f"v{getattr(d, 'model_version', '?')}  tipo={tipo}")

    print("\n=== AGENTES ===")
    agentes = list(projeto.agents.list())
    for a in agentes:
        print(f"- {a.name}")
    if not agentes:
        print("(nenhum agente ainda - crie um com 02-ia-generativa-e-agentes/08_criar_agente.py)")

    print("\n=== FERRAMENTAS e CONHECIMENTO (conexões do projeto) ===")
    # Conexões ligam o projeto a serviços externos: Azure AI Search (conhecimento),
    # Bing (pesquisa na web), Storage, servidores MCP (ferramentas)...
    for c in projeto.connections.list():
        print(f"- {c.name:<30} tipo={c.type}  destino={c.target}")

    print("\n=== CONHECIMENTO (índices registrados) ===")
    for i in projeto.indexes.list():
        print(f"- {i.name} (versão {getattr(i, 'version', '?')})")
