"""
Módulo 03 - Tópico: Usar Azure Language em um agente (servidor MCP)
"Conecte agentes à ferramenta Azure Language usando o protocolo de contexto de
modelo (MCP)... Aprove o acesso à ferramenta: Única | Sempre para essa ferramenta |
Sempre para todas as ferramentas"

O agente recebe a ferramenta MCP da Linguagem do Azure com require_approval="always".
Cada vez que o modelo quiser chamar uma função do servidor MCP, o serviço devolve um
"mcp_approval_request" e o APLICATIVO decide se aprova - governança explícita.

Pré-requisitos (.env): PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME, LANGUAGE_MCP_URL
  - LANGUAGE_MCP_URL: no portal do Foundry > Ferramentas > Azure Language (MCP) > copie a URL
  - LANGUAGE_MCP_CONNECTION_ID (opcional): conexão do projeto que guarda a chave do recurso
  - "az login"

  python 09_agente_mcp_linguagem.py
"""
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
for v in ("PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME", "LANGUAGE_MCP_URL"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")

NOME = "agente-linguagem"
ferramenta = MCPTool(
    server_label="azure_language",
    server_url=os.environ["LANGUAGE_MCP_URL"],
    require_approval="always",               # o app precisa aprovar cada chamada
    project_connection_id=os.getenv("LANGUAGE_MCP_CONNECTION_ID") or None,
)

TEXTO = ("Olá, sou Ricardo Gomes, cliente 88231. Meu CPF é 123.456.789-09 e meu telefone é "
         "(31) 91234-5678. O produto chegou quebrado e estou muito decepcionado!")
PEDIDO = f"Detecte o idioma, redija os dados pessoais e diga o sentimento do texto:\n{TEXTO}"

aprovadas_sempre: set[str] = set()      # "Sempre para essa ferramenta"
aprovar_tudo = False                    # "Sempre para todas as ferramentas"


def decidir(req) -> bool:
    global aprovar_tudo
    if aprovar_tudo or req.name in aprovadas_sempre:
        print(f"  [auto-aprovado] {req.name}")
        return True
    print(f"\n  O agente quer chamar '{req.name}' em '{req.server_label}' com {req.arguments}")
    op = input("  Aprovar? [u]ma vez / [f]erramenta sempre / [t]odas sempre / [n]ão: ").strip().lower()
    if op == "f":
        aprovadas_sempre.add(req.name)
    elif op == "t":
        aprovar_tudo = True
    return op in ("u", "f", "t")


with DefaultAzureCredential() as cred, \
        AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=cred,
                        allow_preview=True) as projeto:
    agente = projeto.agents.create_version(
        agent_name=NOME,
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            instructions="Você analisa textos usando SEMPRE a ferramenta Azure Language. Responda em português.",
            tools=[ferramenta]),
    )
    print(f"Agente {agente.name} v{agente.version} criado com a ferramenta MCP da Linguagem do Azure.")

    client = projeto.get_openai_client(agent_name=NOME)
    conversa = client.conversations.create()          # mesmo padrão do lab e de 08_criar_agente.py
    resposta = client.responses.create(conversation=conversa.id,
                                       input=[{"role": "user", "content": PEDIDO}])

    # Enquanto houver pedidos de aprovação, responda-os na mesma conversa
    while pedidos := [i for i in resposta.output if i.type == "mcp_approval_request"]:
        respostas = [{"type": "mcp_approval_response", "approval_request_id": p.id,
                      "approve": decidir(p)} for p in pedidos]
        resposta = client.responses.create(conversation=conversa.id, input=respostas)

    for item in resposta.output:
        if item.type == "mcp_call":
            print(f"  [chamada MCP executada] {item.name}")
    print("\nResposta do agente:\n" + resposta.output_text)
