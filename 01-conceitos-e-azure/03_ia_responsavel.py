"""
Módulo 01 - Tópico: Princípios de IA responsável
Imparcialidade | Confiabilidade e segurança | Privacidade e segurança |
Inclusão | Transparência | Responsabilidade

Cenário: um banco usa um modelo simples de pontuação de crédito.
Antes de colocá-lo em produção, fazemos uma "auditoria" verificando
cada princípio com um teste concreto. Executa offline (só numpy/stdlib).

  python 03_ia_responsavel.py
"""
import hashlib
import json
import re
from datetime import datetime

import numpy as np

rng = np.random.default_rng(42)

# --- "Modelo" de crédito: pontuação linear sobre renda e histórico de pagamento ---
PESOS = {"renda_mil": 0.08, "pagamentos_em_dia_pct": 0.05, "dividas_mil": -0.10}
LIMIAR = 3.9

def pontuar(cliente):
    return sum(PESOS[k] * cliente[k] for k in PESOS)

def decidir(cliente):
    return pontuar(cliente) >= LIMIAR

# --- Base de teste fictícia com dois grupos (ex.: região A e região B) ---
def gerar_clientes(n, grupo, renda_media):
    return [{
        "grupo": grupo,
        "renda_mil": max(1, rng.normal(renda_media, 3)),
        "pagamentos_em_dia_pct": rng.uniform(60, 100),
        "dividas_mil": max(0, rng.normal(10, 4)),
    } for _ in range(n)]

clientes = gerar_clientes(200, "A", 12) + gerar_clientes(200, "B", 8)

print("=" * 70)
print("1) IMPARCIALIDADE - taxa de aprovação por grupo (regra dos 80%)")
taxas = {}
for g in ("A", "B"):
    grupo = [c for c in clientes if c["grupo"] == g]
    taxas[g] = np.mean([decidir(c) for c in grupo])
    print(f"   Grupo {g}: {taxas[g]:.0%} aprovados")
razao = min(taxas.values()) / max(taxas.values())
print(f"   Razão de impacto: {razao:.2f} -> {'OK' if razao >= 0.8 else 'ALERTA: possível viés'}")
print("   Ação: investigar se 'renda' está agindo como substituto (proxy) do grupo.")

print("=" * 70)
print("2) CONFIABILIDADE E SEGURANÇA - o modelo se comporta bem com entradas inesperadas?")
casos_limite = [
    {"renda_mil": -5, "pagamentos_em_dia_pct": 90, "dividas_mil": 2},     # renda negativa
    {"renda_mil": 10, "pagamentos_em_dia_pct": 140, "dividas_mil": 2},    # % acima de 100
]
def validar(cliente):
    erros = []
    if cliente["renda_mil"] < 0:
        erros.append("renda negativa")
    if not 0 <= cliente["pagamentos_em_dia_pct"] <= 100:
        erros.append("percentual fora de 0-100")
    return erros
for c in casos_limite:
    print(f"   Entrada {c} -> {validar(c) or 'válida'} (rejeitar em vez de decidir)")
print("   Zona cinzenta: pontuações perto do limiar vão para revisão humana:")
duvidosos = [c for c in clientes if abs(pontuar(c) - LIMIAR) < 0.1]
print(f"   {len(duvidosos)} de {len(clientes)} casos encaminhados para um analista.")

print("=" * 70)
print("3) PRIVACIDADE E SEGURANÇA - mascarar dados pessoais antes de registrar logs")
log_bruto = "Cliente Maria Souza, CPF 123.456.789-09, tel (11) 98765-4321 solicitou crédito."
log_seguro = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "[CPF]", log_bruto)
log_seguro = re.sub(r"\(\d{2}\)\s?\d{4,5}-\d{4}", "[TELEFONE]", log_seguro)
print(f"   Antes : {log_bruto}")
print(f"   Depois: {log_seguro}")
print("   (No Azure, a Linguagem do Azure faz isso com recognize_pii_entities - módulo 03)")

print("=" * 70)
print("4) INCLUSÃO - a explicação da decisão é acessível a todos?")
mensagem = ("Seu pedido não foi aprovado agora. O principal motivo é o valor das dívidas atuais. "
            "Você pode pedir revisão por telefone, chat ou presencialmente.")
palavras = mensagem.split()
media = np.mean([len(p) for p in palavras])
print(f"   Mensagem: {mensagem}")
print(f"   Tamanho médio das palavras: {media:.1f} letras (linguagem simples) e 3 canais de atendimento.")
print("   Dica: ofereça a mensagem também em áudio (síntese de voz - módulo 04).")

print("=" * 70)
print("5) TRANSPARÊNCIA - explicar QUAIS fatores pesaram na decisão")
cliente = clientes[0]
contribuicoes = {k: PESOS[k] * cliente[k] for k in PESOS}
print(f"   Pontuação {pontuar(cliente):.2f} (limiar {LIMIAR}) -> {'APROVADO' if decidir(cliente) else 'NEGADO'}")
for fator, valor in sorted(contribuicoes.items(), key=lambda kv: -abs(kv[1])):
    print(f"   {fator:<24} contribuiu {valor:+.2f}")

print("=" * 70)
print("6) RESPONSABILIDADE - trilha de auditoria de cada decisão")
registro = {
    "data_hora": datetime.now().isoformat(timespec="seconds"),
    "versao_modelo": "credito-v1.3",
    # guarda um hash da entrada (e não os dados pessoais) para auditoria
    "entrada_sha256": hashlib.sha256(json.dumps(cliente, sort_keys=True, default=float).encode()).hexdigest()[:16],
    "decisao": bool(decidir(cliente)),
    "revisado_por_humano": bool(abs(pontuar(cliente) - LIMIAR) < 0.1),
    "responsavel": "Comitê de Risco de Crédito",
}
print("   " + json.dumps(registro, ensure_ascii=False))
print("\nNo Microsoft Foundry: filtros de conteúdo (guardrails), avaliações e")
print("monitoramento ajudam a aplicar esses princípios em aplicativos generativos.")
