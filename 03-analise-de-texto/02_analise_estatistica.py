"""
Módulo 03 - Tópico: Análise de texto e modelos de linguagem - ANÁLISE ESTATÍSTICA
- Frequência de termos (TF): termos mais comuns indicam os tópicos de um documento
- TF-IDF: frequência no documento x raridade na coleção
- Conjunto de palavras (Bag of Words): palavras associadas a classes -> sentimento

Coleção: avaliações de um restaurante. Offline (stdlib).

  python 02_analise_estatistica.py
"""
import math
import re
from collections import Counter

AVALIACOES = {
    "av1": "O risoto de cogumelos estava fantástico e o garçom foi muito atencioso. Ótimo jantar!",
    "av2": "Jantar caro e demorado. O risoto chegou frio e o garçom esqueceu a bebida. Péssimo.",
    "av3": "Ambiente agradável, sobremesa ótima: o cheesecake de morango é fantástico.",
    "av4": "O restaurante é bonito, mas o jantar demorou e a comida estava fria. Ruim.",
}
STOP = set("o a os as e é de do da em um uma muito foi estava mas chegou".split())

def termos(t):
    return [p for p in re.findall(r"\w+", t.lower()) if p not in STOP]

docs = {k: termos(v) for k, v in AVALIACOES.items()}

print("=== 1) TF - termos mais frequentes na coleção (indicam os tópicos-chave) ===")
todos = Counter(t for ts in docs.values() for t in ts)
print("  ", todos.most_common(6))

print("\n=== 2) TF-IDF - termos que DISTINGUEM cada avaliação ===")
N = len(docs)
df = Counter(t for ts in docs.values() for t in set(ts))
for k, ts in docs.items():
    tf = Counter(ts)
    tfidf = {t: (f / len(ts)) * math.log(N / df[t]) for t, f in tf.items()}
    top = sorted(tfidf.items(), key=lambda kv: -kv[1])[:3]
    print(f"  {k}: " + ", ".join(f"{t}={v:.2f}" for t, v in top))
print("  'jantar' e 'risoto' aparecem em várias avaliações -> IDF baixo (pouco distintivos).")

print("\n=== 3) Bag of Words - classificação de sentimento ===")
POSITIVAS = {"fantástico", "ótimo", "ótima", "atencioso", "agradável", "bonito"}
NEGATIVAS = {"caro", "demorado", "demorou", "frio", "fria", "péssimo", "ruim", "esqueceu"}
for k, ts in docs.items():
    pos = sum(t in POSITIVAS for t in ts)
    neg = sum(t in NEGATIVAS for t in ts)
    rotulo = "positivo" if pos > neg else "negativo" if neg > pos else "misto/neutro"
    print(f"  {k}: +{pos} / -{neg} -> {rotulo:<12} | {AVALIACOES[k][:55]}...")
print("\nLimitação: 'não foi ótimo' contaria como positivo. Modelos SEMÂNTICOS (embeddings)")
print("capturam contexto - veja 04_embeddings_semanticos.py e os serviços do Azure.")
