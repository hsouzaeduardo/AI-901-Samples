"""
Módulo 02 - Tópico: O que são agentes? -> "Agentes colaboram com outros agentes,
para criar fluxos de trabalho de agentes especializados, cada um com as próprias
responsabilidades"

Fluxo de 3 agentes especializados (cada um = modelo + instruções próprias):

   pedido -> [TRIAGEM] --despesas--> [ESPECIALISTA DESPESAS] --+
                       \\--ti------> [ESPECIALISTA TI] ---------+--> [REVISOR] -> resposta

A triagem devolve JSON estruturado (structured output) para o roteamento ser
confiável. No Foundry, o mesmo padrão pode ser montado com Workflows de agentes.

  python 09_fluxo_multiagente.py
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

AGENTES = {
    "triagem": "Classifique o pedido do funcionário. Categorias: 'despesas', 'ti' ou 'outro'.",
    "despesas": ("Você é especialista na política de despesas da Contoso: refeição até R$ 120/dia "
                 "(nacional) e US$ 60/dia (exterior); pedidos em até 30 dias no portal Reembolsa."),
    "ti": ("Você é o suporte de TI da Contoso. Senhas: senha.contoso.com. Hardware com defeito: "
           "abra chamado no portal Ajuda TI. Seja prático, em passos numerados."),
    "revisor": ("Revise a resposta abaixo: deixe-a cordial, em no máximo 4 frases, sem inventar "
                "informações novas. Devolva apenas o texto final."),
}

ESQUEMA_TRIAGEM = {
    "type": "json_schema", "name": "triagem", "strict": True,
    "schema": {"type": "object", "additionalProperties": False,
               "properties": {"categoria": {"type": "string", "enum": ["despesas", "ti", "outro"]},
                              "motivo": {"type": "string"}},
               "required": ["categoria", "motivo"]},
}


def agente(nome, entrada, **extra):
    return client.responses.create(model=MODELO, instructions=AGENTES[nome], input=entrada, **extra)


def atender(pedido):
    print(f"\n### Pedido: {pedido}")
    tri = json.loads(agente("triagem", pedido, text={"format": ESQUEMA_TRIAGEM}).output_text)
    print(f"[triagem]  -> {tri['categoria']} ({tri['motivo']})")
    if tri["categoria"] == "outro":
        print("[fluxo]    -> encaminhado para um atendente humano")
        return
    rascunho = agente(tri["categoria"], pedido).output_text
    print(f"[{tri['categoria']}] rascunho: {rascunho[:160]}...")
    final = agente("revisor", f"Pedido: {pedido}\n\nResposta a revisar:\n{rascunho}").output_text
    print(f"[revisor]  -> {final}")


for p in ("Jantei em Buenos Aires e gastei 75 dólares. Vou ser reembolsado integralmente?",
          "Esqueci minha senha e o sistema bloqueou meu acesso.",
          "Quero sugerir um happy hour na sexta."):
    atender(p)
