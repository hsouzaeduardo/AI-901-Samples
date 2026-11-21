"""
Módulo 03 - Tópico: Análise estatística -> "Classificação de texto (TextRank):
pontuação de relevância de frases com base em termos comuns. Baseado no algoritmo
PageRank de pesquisa na Web. Comumente usado para RESUMO EXTRATIVO: extraia as
{n} frases mais relevantes."

  python 03_resumo_extrativo.py
"""
import math
import re
from collections import Counter

TEXTO = """O Commodore 64 finalmente chegou às lojas e as primeiras impressões sugerem um grande sucesso.
Com preço agressivo e 64K de memória, o computador oferece especificações notáveis para uma máquina doméstica.
Seus gráficos coloridos e o som impressionante colocam o computador entre os melhores sistemas de entretenimento.
O gerador de som SID produz efeitos e música muito acima do esperado nesta faixa de preço.
Desenvolvedores de jogos já demonstram forte interesse pela máquina por causa dos gráficos e do som.
O teclado, porém, não tem a mesma firmeza dos concorrentes.
A documentação também pouco ajuda quem está começando na computação.
Mesmo assim, o Commodore 64 chega como um dos computadores domésticos mais atraentes do mercado."""

STOP = set("o a os as e é de do da dos das em no na um uma para por com que se seus sua mais "
           "muito pouco também mesmo porém nesta quem está já pela pelo às ao".split())
frases = [f.strip() for f in TEXTO.split("\n") if f.strip()]
bags = [Counter(p for p in re.findall(r"\w+", f.lower()) if p not in STOP) for f in frases]

def similaridade(a, b):
    comuns = sum((a & b).values())
    return comuns / (math.log(1 + sum(a.values())) + math.log(1 + sum(b.values())))

n = len(frases)
W = [[similaridade(bags[i], bags[j]) if i != j else 0 for j in range(n)] for i in range(n)]

# PageRank: cada frase "vota" nas frases parecidas; votos de frases importantes valem mais
d, score = 0.85, [1.0] * n
for _ in range(50):
    score = [(1 - d) + d * sum(W[j][i] / (sum(W[j]) or 1) * score[j] for j in range(n))
             for i in range(n)]

print("Pontuação de cada frase:")
for s, f in sorted(zip(score, frases), reverse=True):
    print(f"  {s:.3f}  {f[:80]}")

N_FRASES = 2
escolhidas = sorted(sorted(range(n), key=lambda i: -score[i])[:N_FRASES])  # mantém a ordem original
print(f"\nResumo extrativo ({N_FRASES} frases):")
print(" ".join(frases[i] for i in escolhidas))
print("\nResumo EXTRATIVO copia frases do texto. Um LLM faz resumo ABSTRATIVO (reescreve).")
print("A Linguagem do Azure oferece os dois: begin_extract_summary e begin_abstract_summary.")
