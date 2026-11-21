"""
Módulo 06 - Tópico: Extração de informações de documentos -
"Defina o ESQUEMA com base em amostras para criar ANALISADORES PERSONALIZADOS"

Cria um analisador próprio (a partir do prebuilt-document) com um esquema de campos.
Cada campo declara um MÉTODO:
  extract  -> copia o valor que está no documento
  classify -> escolhe uma opção de uma lista (enum)
  generate -> o modelo gera o valor (ex.: um resumo)
O analisador define COMO o conteúdo é processado e QUAIS dados estruturados voltam
(verificação de conhecimento, questão 2).

  python 06_analisador_personalizado.py            -> cria/atualiza e testa na fatura do lab
  python 06_analisador_personalizado.py --excluir  -> remove o analisador
"""
import os
import sys

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (AnalysisInput, ContentAnalyzer, ContentAnalyzerConfig,
                                                  ContentFieldDefinition, ContentFieldSchema)
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint, key = os.getenv("AZURE_SERVICES_AI_ENDPOINT"), os.getenv("AZURE_FOUNDRY_KEY")
if not (endpoint and key):
    sys.exit("Defina AZURE_SERVICES_AI_ENDPOINT e AZURE_FOUNDRY_KEY no .env")
client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(key))

ID = "fatura_contas_a_pagar"
if "--excluir" in sys.argv:
    client.delete_analyzer(ID)
    sys.exit(f"Analisador {ID} excluído.")

def campo(tipo, metodo, descricao, **extra):
    return ContentFieldDefinition(type=tipo, method=metodo, description=descricao, **extra)

esquema = ContentFieldSchema(
    name="fatura_contas_a_pagar",
    description="Campos que o setor de contas a pagar precisa lançar no ERP",
    fields={
        "fornecedor": campo("string", "extract", "Nome da empresa que emitiu a fatura"),
        "numero_fatura": campo("string", "extract", "Número/ID da fatura"),
        "data_vencimento": campo("date", "extract", "Data de vencimento do pagamento"),
        "valor_total": campo("number", "extract", "Valor total a pagar"),
        "moeda": campo("string", "extract", "Código da moeda, ex.: USD, BRL"),
        "categoria": campo("string", "classify", "Categoria de gasto da fatura",
                           enum=["hardware", "software", "serviços", "outros"]),
        "resumo": campo("string", "generate", "Resumo em português, em uma frase, do que foi cobrado"),
    },
)

analisador = ContentAnalyzer(
    base_analyzer_id="prebuilt-document",
    description="Analisador personalizado do curso AI-901",
    config=ContentAnalyzerConfig(return_details=True, estimate_field_source_and_confidence=True),
    field_schema=esquema,
    # NOME DO MODELO (não da implantação): o serviço resolve a implantação pelos
    # padrões configurados com  04_content_understanding_sdk.py --configurar
    models={"completion": "gpt-4.1"},
)

print(f"Criando/atualizando o analisador '{ID}'...")
client.begin_create_analyzer(ID, resource=analisador, allow_replace=True).result()

url = ("https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-fundamentals/"
       "refs/heads/main/data/contoso-invoice-2.pdf")
print("Analisando", url)
resultado = client.begin_analyze(analyzer_id=ID, inputs=[AnalysisInput(url=url)]).result()

for nome, c in (resultado.contents[0].fields or {}).items():
    conf = f"{c.confidence:.2f}" if c.confidence is not None else "-"
    print(f"  {nome:<16} = {c.value!s:<55} confiança {conf}")
