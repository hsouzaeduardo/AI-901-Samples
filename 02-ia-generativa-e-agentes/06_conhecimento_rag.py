"""
Módulo 02 - Tópico: O que são agentes? -> "Ferramentas para encontrar CONHECIMENTO
que contextualiza o trabalho" (e "Conhecimento" no projeto do Foundry)

RAG (Retrieval-Augmented Generation) feito à mão, em 3 passos:
  1) RECUPERAR: buscar na base de conhecimento os trechos mais relevantes
  2) AUMENTAR : colocar esses trechos no prompt
  3) GERAR    : o modelo responde FUNDAMENTADO nos trechos (e cita a fonte)

A recuperação é offline (TF-IDF com numpy). A geração usa o Foundry.
  python 06_conhecimento_rag.py               -> RAG completo (precisa do .env)
  python 06_conhecimento_rag.py --sem-azure   -> mostra só a recuperação e o prompt montado

No Foundry, isso vem pronto: ferramenta de busca em arquivos (file search),
Azure AI Search ou Foundry IQ conectados ao agente.
"""
import math
import os
import re
import sys
from collections import Counter

BASE = {
    "politica-despesas.md#1": "Despesas de viagem devem ser enviadas em até 30 dias após a viagem, "
                              "pelo portal Reembolsa, com os recibos digitalizados.",
    "politica-despesas.md#2": "O limite diário para refeições em viagens nacionais é de R$ 120 e "
                              "em viagens internacionais é de US$ 60.",
    "politica-despesas.md#3": "Hospedagem acima de R$ 450 por noite exige aprovação prévia do gestor.",
    "manual-ti.md#1": "Para redefinir sua senha, acesse senha.contoso.com e confirme o código "
                      "enviado ao celular cadastrado.",
    "manual-ti.md#2": "Notebooks corporativos devem ter o BitLocker ativado e não podem ser "
                      "emprestados a terceiros.",
}
PERGUNTA = "Qual é o limite para refeição numa viagem para o exterior e até quando envio o pedido?"
STOP = {"o", "a", "os", "as", "de", "do", "da", "em", "para", "e", "é", "um", "uma", "ao", "com",
        "qual", "até", "quando", "numa", "pelo", "por", "se", "que", "no", "na", "eu"}


def termos(texto):
    return [t for t in re.findall(r"\w+", texto.lower()) if t not in STOP]


# ---------- 1) RECUPERAR (TF-IDF + similaridade do cosseno) ----------
docs = {k: Counter(termos(v)) for k, v in BASE.items()}
df = Counter(t for c in docs.values() for t in c)
idf = {t: math.log((1 + len(docs)) / (1 + n)) + 1 for t, n in df.items()}

def vetor(contagem):
    return {t: f * idf.get(t, 0) for t, f in contagem.items()}

def cosseno(a, b):
    num = sum(a[t] * b.get(t, 0) for t in a)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0

q = vetor(Counter(termos(PERGUNTA)))
ranking = sorted(((cosseno(q, vetor(c)), k) for k, c in docs.items()), reverse=True)
print("Relevância de cada trecho para a pergunta:")
for score, k in ranking:
    print(f"  {score:.2f}  {k}")
top = [k for score, k in ranking[:2] if score > 0]

# ---------- 2) AUMENTAR ----------
contexto = "\n".join(f"[{k}] {BASE[k]}" for k in top)
instrucoes = ("Você é o assistente de despesas da Contoso. Responda SOMENTE com base no contexto. "
              "Cite a fonte entre colchetes. Se a resposta não estiver no contexto, diga que não sabe.")
prompt = f"Contexto:\n{contexto}\n\nPergunta: {PERGUNTA}"
print("\nPrompt aumentado enviado ao modelo:\n" + "-" * 60 + f"\n{prompt}\n" + "-" * 60)

if "--sem-azure" in sys.argv:
    sys.exit(0)

# ---------- 3) GERAR ----------
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "MODEL_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env (ou rode com --sem-azure)")
client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])
modelo = os.environ["MODEL_DEPLOYMENT_NAME"]

r = client.responses.create(model=modelo, instructions=instrucoes, input=prompt)
print("\nResposta fundamentada:\n" + r.output_text)

# Contraprova: a mesma pergunta SEM contexto -> o modelo não conhece a política da Contoso
r2 = client.responses.create(model=modelo, input=PERGUNTA)
print("\nSem conhecimento (resposta genérica, possivelmente inventada):\n" + r2.output_text)
