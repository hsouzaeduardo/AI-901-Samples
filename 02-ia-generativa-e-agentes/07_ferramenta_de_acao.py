"""
Módulo 02 - Tópico: O que são agentes? -> "Ferramentas para EXECUTAR AÇÕES e
automatizar tarefas"

Chamada de função (function calling): o modelo NÃO executa código; ele decide
QUAL função chamar e com QUAIS argumentos. O seu aplicativo executa a função e
devolve o resultado para o modelo redigir a resposta final.

    usuário -> modelo -> function_call(consultar_reembolso, {"protocolo": "R-1042"})
            -> app executa a função -> function_call_output -> modelo -> resposta

  python 07_ferramenta_de_acao.py
"""
import json
import os
import sys

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "MODEL_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")

client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])
MODELO = os.environ["MODEL_DEPLOYMENT_NAME"]

# ---- "Sistema" da empresa (simulado) ----
REEMBOLSOS = {"R-1042": {"status": "aprovado", "valor": 356.90, "pagamento": "2026-11-28"},
              "R-1043": {"status": "pendente de recibo", "valor": 89.00, "pagamento": None}}

def consultar_reembolso(protocolo: str) -> dict:
    return REEMBOLSOS.get(protocolo.upper(), {"erro": f"protocolo {protocolo} não encontrado"})

def abrir_chamado(assunto: str, prioridade: str) -> dict:
    return {"chamado": "INC-77821", "assunto": assunto, "prioridade": prioridade}

FUNCOES = {"consultar_reembolso": consultar_reembolso, "abrir_chamado": abrir_chamado}

# ---- Descrição das ferramentas para o modelo (JSON Schema) ----
TOOLS = [
    {"type": "function", "name": "consultar_reembolso",
     "description": "Consulta o status de um pedido de reembolso pelo número do protocolo.",
     "parameters": {"type": "object", "properties": {
         "protocolo": {"type": "string", "description": "Ex.: R-1042"}},
         "required": ["protocolo"], "additionalProperties": False},
     "strict": True},
    {"type": "function", "name": "abrir_chamado",
     "description": "Abre um chamado no suporte de TI.",
     "parameters": {"type": "object", "properties": {
         "assunto": {"type": "string"},
         "prioridade": {"type": "string", "enum": ["baixa", "media", "alta"]}},
         "required": ["assunto", "prioridade"], "additionalProperties": False},
     "strict": True},
]
INSTRUCOES = "Você é o assistente interno da Contoso. Use as ferramentas quando necessário."


def conversar(pergunta):
    print(f"\n> Usuário: {pergunta}")
    resposta = client.responses.create(model=MODELO, instructions=INSTRUCOES,
                                       input=pergunta, tools=TOOLS)
    # o modelo pode pedir várias chamadas de função antes de responder
    while chamadas := [i for i in resposta.output if i.type == "function_call"]:
        saidas = []
        for c in chamadas:
            args = json.loads(c.arguments)
            resultado = FUNCOES[c.name](**args)
            print(f"  [ação] {c.name}({args}) -> {resultado}")
            saidas.append({"type": "function_call_output", "call_id": c.call_id,
                           "output": json.dumps(resultado, ensure_ascii=False)})
        resposta = client.responses.create(model=MODELO, instructions=INSTRUCOES, tools=TOOLS,
                                           input=saidas, previous_response_id=resposta.id)
    print(f"< Assistente: {resposta.output_text}")


conversar("Qual o status do meu reembolso R-1042? Quando vou receber?")
conversar("Meu notebook não liga desde hoje cedo e tenho uma apresentação ao cliente em 1 hora.")
conversar("Quem descobriu o Brasil?")   # não precisa de ferramenta
