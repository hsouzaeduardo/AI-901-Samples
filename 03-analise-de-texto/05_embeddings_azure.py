"""
Módulo 03 - Tópico: Modelos semânticos com um modelo REAL de embeddings do Foundry
(e Módulo 02: "tokens semanticamente semelhantes têm direções semelhantes")

Busca semântica numa FAQ: a pergunta do usuário não compartilha palavras com a
resposta certa, mas os embeddings capturam o SIGNIFICADO.

Pré-requisitos: implantar um modelo de embeddings (ex.: text-embedding-3-small)
e preencher EMBEDDING_DEPLOYMENT_NAME no .env.

  python 05_embeddings_azure.py
"""
import os
import sys

import numpy as np
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "EMBEDDING_DEPLOYMENT_NAME"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")
client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])
MODELO = os.environ["EMBEDDING_DEPLOYMENT_NAME"]

FAQ = [
    "Como faço para trocar minha senha de acesso?",
    "Qual o prazo para pedir reembolso de despesas de viagem?",
    "A empresa oferece auxílio para cursos e certificações?",
    "Posso trabalhar remotamente às sextas-feiras?",
    "Como solicito um notebook novo?",
]
PERGUNTAS = [
    "esqueci o código para entrar no sistema",          # -> senha
    "a Microsoft vai pagar minha prova AI-901?",          # -> certificações
    "meu computador quebrou, o que fazer?",              # -> notebook
]

def embed(textos):
    r = client.embeddings.create(model=MODELO, input=textos)
    return np.array([d.embedding for d in r.data])

E_faq = embed(FAQ)
print(f"Cada texto virou um vetor de {E_faq.shape[1]} dimensões.\n")
E_faq /= np.linalg.norm(E_faq, axis=1, keepdims=True)

for pergunta, e in zip(PERGUNTAS, embed(PERGUNTAS)):
    sims = E_faq @ (e / np.linalg.norm(e))
    i = int(np.argmax(sims))
    print(f"Pergunta: {pergunta}")
    print(f"  -> FAQ mais próxima ({sims[i]:.2f}): {FAQ[i]}")
    print(f"     2a opção ({np.sort(sims)[-2]:.2f}): {FAQ[int(np.argsort(sims)[-2])]}\n")

# Palavras do slide: semelhantes apontam na mesma direção
palavras = ["cachorro", "filhote", "gato", "skate", "carro"]
W = embed(palavras)
W /= np.linalg.norm(W, axis=1, keepdims=True)
print("Similaridade do cosseno entre palavras:")
print(" " * 10 + "".join(f"{p:>10}" for p in palavras))
for p, linha in zip(palavras, W @ W.T):
    print(f"{p:<10}" + "".join(f"{v:>10.2f}" for v in linha))
