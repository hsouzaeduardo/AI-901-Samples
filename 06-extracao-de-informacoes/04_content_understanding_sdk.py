"""
Módulo 06 - Tópico: Extração de informações de documentos
"Compreensão de Conteúdo do Azure nas Foundry Tools: use analisadores PRÉ-DEFINIDOS
para documentos e formulários comuns" - via SDK Python.

Analisadores do lab: prebuilt-read (OCR) -> prebuilt-layout (estrutura) ->
prebuilt-invoice / prebuilt-receipt (campos).
A análise é ASSÍNCRONA: begin_analyze() devolve um "poller" que consulta o serviço
até o trabalho terminar (verificação de conhecimento, questão 3).

  pip install --pre azure-ai-contentunderstanding
  python 04_content_understanding_sdk.py --configurar     (1a vez: liga os modelos padrão)
  python 04_content_understanding_sdk.py                  (fatura de exemplo do lab)
  python 04_content_understanding_sdk.py prebuilt-layout
  python 04_content_understanding_sdk.py prebuilt-receipt https://.../recibo.jpg
"""
import json
import os
import sys
from pathlib import Path

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.credentials import AzureKeyCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
endpoint = os.getenv("AZURE_SERVICES_AI_ENDPOINT")
key = os.getenv("AZURE_FOUNDRY_KEY")
if not (endpoint and key):
    sys.exit("Defina AZURE_SERVICES_AI_ENDPOINT e AZURE_FOUNDRY_KEY no .env")

client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(key))

if "--configurar" in sys.argv:
    # Os analisadores pré-definidos usam modelos generativos implantados no SEU recurso.
    # Informe o nome das implantações (equivale ao set-up-connection.sh do lab).
    padroes = client.update_defaults(model_deployments={
        "gpt-4.1": os.getenv("CU_GPT41_DEPLOYMENT", "gpt-4.1"),
        "gpt-4.1-mini": os.getenv("CU_GPT41_MINI_DEPLOYMENT", "gpt-4.1-mini"),
        "text-embedding-3-large": os.getenv("CU_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
    })
    print("Implantações padrão configuradas:", padroes.as_dict())
    sys.exit(0)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
analisador = args[0] if args else "prebuilt-invoice"
url = args[1] if len(args) > 1 else ("https://raw.githubusercontent.com/MicrosoftLearning/"
                                     "mslearn-ai-fundamentals/refs/heads/main/data/contoso-invoice-1.pdf")

print(f"Analisando com '{analisador}':\n  {url}")
poller = client.begin_analyze(analyzer_id=analisador, inputs=[AnalysisInput(url=url)])
print("Trabalho enviado; aguardando conclusão (polling)...")
resultado = poller.result()

conteudo = resultado.contents[0]
print(f"\nTipo: {conteudo.mime_type}")
print("\n--- Markdown extraído (início) ---")
print((conteudo.markdown or "")[:600])

if conteudo.fields:
    print("\n--- Campos extraídos ---")
    for nome, campo in conteudo.fields.items():
        valor = campo.value
        if isinstance(valor, (list, dict)):
            valor = f"<{type(valor).__name__} com {len(valor)} itens>"
        conf = f"{campo.confidence:.2f}" if campo.confidence is not None else "-"
        print(f"  {nome:<26} {str(valor)[:50]:<52} confiança {conf}")

saida = Path(__file__).parent / "saidas"
saida.mkdir(exist_ok=True)
(saida / f"{analisador}.json").write_text(json.dumps(resultado.as_dict(), indent=2, ensure_ascii=False,
                                                     default=str), encoding="utf-8")
print(f"\nJSON completo salvo em saidas/{analisador}.json")
