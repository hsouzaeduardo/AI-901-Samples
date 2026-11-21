"""
Módulo 06 - Tópico: Extração de campo e mapeamento - "Mapeamento de texto
reconhecido para campos de dados"
  1) Ingestão do resultado do OCR
  2) Detecção de campo e identificação de candidatos
  3) Mapeamento de campo e associação
  4) Normalização e padronização de dados
  5) Integração com processos e sistemas de negócio

Entrada: linhas de OCR de um cupom fiscal brasileiro. Saída: JSON + CSV para o ERP.
Offline (stdlib).

  python 02_mapeamento_campos.py
"""
import csv
import json
import re
from pathlib import Path

# ---------- 1) Ingestão: texto + confiança vindos do OCR ----------
OCR = [
    ("SUPERMERCADO BOA COMPRA LTDA", 0.97),
    ("CNPJ: 11.222.333/0001-81", 0.95),
    ("RUA DAS FLORES, 120 - CAMPINAS/SP", 0.93),
    ("CUPOM FISCAL ELETRONICO - SAT", 0.96),
    ("DATA: 05/11/2026  HORA: 18:42", 0.94),
    ("001 CAFE TORRADO 500G      2 x 18,90    37,80", 0.91),
    ("002 LEITE INTEGRAL 1L      6 x 4,79     28,74", 0.90),
    ("003 PAO DE FORMA           1 x 9,50      9,50", 0.92),
    ("TOTAL R$                              76,04", 0.98),
    ("FORMA PAGAMENTO: CARTAO CREDITO", 0.95),
]
print("1) Ingestão:", len(OCR), "linhas de OCR")

# ---------- 2) Detecção de candidatos (padrões) ----------
PADROES = {
    "cnpj":  r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "data":  r"\b\d{2}/\d{2}/\d{4}\b",
    "hora":  r"\b\d{2}:\d{2}\b",
    "valor": r"\b\d{1,3}(?:\.\d{3})*,\d{2}\b",
}
candidatos = []
for n, (texto, conf) in enumerate(OCR):
    for tipo, padrao in PADROES.items():
        for m in re.finditer(padrao, texto):
            candidatos.append({"tipo": tipo, "valor": m.group(), "linha": n, "conf": conf})
print(f"2) {len(candidatos)} candidatos encontrados, ex.: {candidatos[:3]}")

# ---------- 3) Mapeamento: associar candidatos aos campos do esquema ----------
def primeiro(tipo, linha_com=None):
    for c in candidatos:
        if c["tipo"] == tipo and (linha_com is None or linha_com in OCR[c["linha"]][0]):
            return c
    return None

ITEM = re.compile(r"^(\d{3})\s+(.+?)\s+(\d+)\s*x\s*([\d.,]+)\s+([\d.,]+)$")
itens = [m.groups() for texto, _ in OCR if (m := ITEM.match(texto))]
total_cand = primeiro("valor", linha_com="TOTAL")       # o valor NA LINHA do rótulo "TOTAL"
fornecedor = OCR[0][0]                                   # heurística: 1a linha do cupom
pagamento = next(t.split(":", 1)[1] for t, _ in OCR if t.startswith("FORMA PAGAMENTO"))
print("3) Mapeamento: fornecedor, cnpj, data, hora, itens, total, pagamento")

# ---------- 4) Normalização e validação ----------
def valor(txt):                       # "1.234,56" -> 1234.56
    return float(txt.replace(".", "").replace(",", "."))

def data_iso(txt):                    # "05/11/2026" -> "2026-11-05"
    d, m, a = txt.split("/")
    return f"{a}-{m}-{d}"

def cnpj_valido(cnpj):
    n = [int(c) for c in re.sub(r"\D", "", cnpj)]
    if len(n) != 14:
        return False
    for tamanho in (12, 13):
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] if tamanho == 12 else [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        resto = sum(a * b for a, b in zip(n[:tamanho], pesos)) % 11
        if n[tamanho] != (0 if resto < 2 else 11 - resto):
            return False
    return True

cnpj = primeiro("cnpj")["valor"]
registro = {
    "fornecedor": fornecedor.title(),
    "cnpj": re.sub(r"\D", "", cnpj),
    "cnpj_valido": cnpj_valido(cnpj),
    "data": data_iso(primeiro("data")["valor"]),
    "hora": primeiro("hora")["valor"],
    "itens": [{"codigo": c, "descricao": d.title(), "qtd": int(q), "unitario": valor(u), "total": valor(t)}
              for c, d, q, u, t in itens],
    "total": valor(total_cand["valor"]),
    "pagamento": pagamento.strip().title(),
    "confianca_minima": min(c for _, c in OCR),
}
soma = round(sum(i["total"] for i in registro["itens"]), 2)
registro["total_confere"] = soma == registro["total"]
print("4) Normalização (datas ISO, valores numéricos, CNPJ só dígitos) + validações:")
print(json.dumps(registro, indent=2, ensure_ascii=False))

# ---------- 5) Integração: gravar no formato que o ERP importa ----------
saida = Path(__file__).parent / "saidas"
saida.mkdir(exist_ok=True)
arquivo = saida / "despesas.csv"
novo = not arquivo.exists()
with arquivo.open("a", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    if novo:
        w.writerow(["data", "fornecedor", "cnpj", "total", "pagamento"])
    w.writerow([registro["data"], registro["fornecedor"], registro["cnpj"],
                f"{registro['total']:.2f}", registro["pagamento"]])
status = "APROVADO para lançamento" if registro["cnpj_valido"] and registro["total_confere"] else "REVISÃO HUMANA"
print(f"5) Integração: linha adicionada em {arquivo} -> {status}")

# Exemplo do slide (mesmo documento -> dados consistentes)
print("\nExemplo do slide: A: Lorem ipsum | B: $20 | C: 01/01/2025 | D: Libero")
print("   normalizado  -> A: Lorem Ipsum | B: $20.00 | C: 2025-01-01 | D: Libero")
