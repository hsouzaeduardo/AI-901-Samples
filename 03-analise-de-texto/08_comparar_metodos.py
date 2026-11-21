"""
Módulo 03 - Tópico: Escolher o método certo
  Modelos de IA de uso geral -> flexíveis, conversacionais, resultados podem VARIAR
  Linguagem do Azure          -> estruturados, DETERMINÍSTICOS, com pontuação de confiança

Experimento: o mesmo texto é analisado 3 vezes por cada abordagem.
Observe qual delas devolve sempre a mesma coisa - é isso que um pipeline de
produção (ex.: redação de PII para conformidade) precisa.

  python 08_comparar_metodos.py
"""
import os
import sys

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_KEY", "MODEL_DEPLOYMENT_NAME", "AZURE_AI_SERVICES_ENDPOINT"):
    os.getenv(v) or sys.exit(f"Defina {v} no .env")

llm = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_FOUNDRY_KEY"])
lang = TextAnalyticsClient(os.environ["AZURE_AI_SERVICES_ENDPOINT"],
                           AzureKeyCredential(os.environ["AZURE_FOUNDRY_KEY"]))

TEXTO = ("A entrega atrasou dois dias, mas o suporte resolveu tudo rapidinho. "
         "Ligue para Carla no (21) 99876-5432 se precisar.")

print("TEXTO:", TEXTO, "\n")
print("--- Modelo de uso geral (prompt) ---")
for i in range(3):
    r = llm.responses.create(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        input=f"Qual o sentimento deste texto e quais dados pessoais ele contém? Responda em 1 linha.\n{TEXTO}")
    print(f"  chamada {i + 1}: {r.output_text.strip()}")

print("\n--- Linguagem do Azure (SDK) ---")
for i in range(3):
    s = lang.analyze_sentiment([TEXTO], language="pt")[0]
    p = lang.recognize_pii_entities([TEXTO], language="pt")[0]
    pii = [(e.category, round(e.confidence_score, 2)) for e in p.entities]
    print(f"  chamada {i + 1}: sentimento={s.sentiment} "
          f"(pos {s.confidence_scores.positive:.2f}/neg {s.confidence_scores.negative:.2f}) PII={pii}")

print("""
Conclusão (slide 'Escolher o método certo'):
  - Exploração, várias tarefas numa chamada, resposta em linguagem natural -> modelo de uso geral
  - Pipeline automatizado, dados regulados (PII), confiança e repetibilidade -> Linguagem do Azure""")
