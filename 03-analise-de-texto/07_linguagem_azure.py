"""
Módulo 03 - Tópicos: "Linguagem do Azure nas Foundry Tools", "Usar o Azure Language
SDK" e "Uma análise mais detalhada dos métodos do SDK"

Percorre os recursos da Linguagem do Azure (resultado ESTRUTURADO + CONFIANÇA):
  1) Detecção de idioma ............ detect_language
  2) Reconhecimento de entidades .... recognize_entities
  3) Detecção/redação de PII ........ recognize_pii_entities
  4) Sentimento + mineração de opinião analyze_sentiment
  5) Frases-chave ................... extract_key_phrases
  6) Resumo extrativo e abstrativo .. begin_extract_summary / begin_abstract_summary
  7) Análise de texto para SAÚDE .... begin_analyze_healthcare_entities
     (no slide 11 aparece traduzido como "integridade" - o original é "Text Analytics for Health")

  pip install azure-ai-textanalytics
  python 07_linguagem_azure.py
"""
import os
import sys

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT")
key = os.getenv("AZURE_FOUNDRY_KEY")
if not (endpoint and key):
    sys.exit("Defina AZURE_AI_SERVICES_ENDPOINT e AZURE_FOUNDRY_KEY no .env")

# O objeto cliente cuida da comunicação com o serviço (autenticação, HTTP, JSON)
client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def titulo(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


titulo("1) Detecção de idioma")
amostras = ["Hola mundo",
            "CPC 464 Art.-Nr.: 31020 Hergestellt in Korea SCHNEIDER RUNDFUNKWERKE AG Bundesrepublik Deutschland",
            "Bom dia! Gostaria de saber o status do meu pedido.",
            "Bonjour, je voudrais réserver une table pour deux."]
for texto, doc in zip(amostras, client.detect_language(amostras)):
    idioma = doc.primary_language
    print(f"{texto[:45]:<47} -> {idioma.name} ({idioma.iso6391_name}) confiança {idioma.confidence_score:.2f}")

titulo("2) Reconhecimento de entidades nomeadas (NER)")
documentos = ["Alex e eu participamos de uma conferência da Microsoft AI. "
              "Foi em Las Vegas no dia 21 de setembro e durou 3 dias."]
resultado = client.recognize_entities(documents=documentos, language="pt")[0]
for e in resultado.entities:
    sub = f"/{e.subcategory}" if e.subcategory else ""
    print(f"- {e.text:<22} {e.category}{sub:<14} confiança {e.confidence_score:.2f}")

titulo("3) Detecção e redação de PII")
fatura = ("Fatura da Tailspin Toys, 14/09/2025. Cliente: Margarida Elias, CPF 123.456.789-09, "
          "Rua Alta 128, São Paulo - SP. Telefone (11) 98765-4321, e-mail margarida@exemplo.com.")
doc = client.recognize_pii_entities([fatura], language="pt")[0]
print("Texto redigido:\n ", doc.redacted_text)
for e in doc.entities:
    print(f"- {e.text:<26} {e.category:<22} confiança {e.confidence_score:.2f}")

titulo("4) Análise de sentimento com mineração de opinião")
avaliacoes = ["O risoto estava delicioso, mas o atendimento foi muito lento.",
              "Lugar lindo e garçom simpático. Voltarei com certeza!"]
for texto, doc in zip(avaliacoes, client.analyze_sentiment(avaliacoes, language="pt",
                                                           show_opinion_mining=True)):
    s = doc.confidence_scores
    print(f"{texto}\n  -> {doc.sentiment} (pos {s.positive:.2f} | neu {s.neutral:.2f} | neg {s.negative:.2f})")
    for frase in doc.sentences:
        for op in frase.mined_opinions or []:   # mineração de opinião varia por idioma
            avaliacoes_alvo = ", ".join(f"{a.text}={a.sentiment}" for a in op.assessments)
            print(f"     alvo '{op.target.text}': {avaliacoes_alvo}")

titulo("5) Extração de frases-chave")
for doc in client.extract_key_phrases(avaliacoes + documentos, language="pt"):
    print("-", doc.key_phrases)

titulo("6) Resumo: extrativo (copia frases) x abstrativo (reescreve)")
artigo = [("O Commodore 64 chegou às lojas com preço agressivo e 64K de memória. Seus gráficos "
           "coloridos e o chip de som SID impressionam. Desenvolvedores de jogos já demonstram "
           "interesse. O teclado e a documentação, porém, deixam a desejar. Mesmo assim, é um dos "
           "computadores domésticos mais atraentes do mercado.")]
for doc in client.begin_extract_summary(artigo, language="pt", max_sentence_count=2).result():
    if not doc.is_error:
        print("Extrativo :", " ".join(s.text for s in doc.sentences))
for doc in client.begin_abstract_summary(artigo, language="pt").result():
    if not doc.is_error:
        print("Abstrativo:", " ".join(s.text for s in doc.summaries))

titulo("7) Análise de texto para saúde (Text Analytics for Health)")
nota_clinica = ["Patient was prescribed 100mg ibuprofen twice daily for knee pain after surgery."]
for doc in client.begin_analyze_healthcare_entities(nota_clinica).result():
    if doc.is_error:
        print("Erro:", doc.error.message)
        continue
    for e in doc.entities:
        print(f"- {e.text:<14} {e.category:<22} confiança {e.confidence_score:.2f}")
