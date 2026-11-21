"""
Módulo 03 - Tópico: Pré-processamento de texto
Tokenização | Normalização | Remoção de palavras irrelevantes (stop words) |
Radicalização (stemming) / Lematização | Marcação de classes gramaticais (POS)

Usa o trecho do discurso "Escolhemos ir para a Lua" do slide 5.
Implementação didática (regras simples), 100% offline. Bibliotecas reais: spaCy, NLTK.

  python 01_preprocessamento.py
"""
import re
import unicodedata
from collections import Counter

TEXTO = ("Escolhemos ir para a Lua! Escolhemos ir à Lua nesta década e fazer as outras coisas, "
         "não porque sejam fáceis, mas porque são difíceis; porque esse objetivo servirá para "
         "organizar e medir o melhor de nossas energias e habilidades, porque esse desafio é algo "
         "que estamos dispostos a aceitar, um que não estamos dispostos a adiar e que pretendemos vencer!")

print("Texto original:\n", TEXTO, "\n")

# 1) TOKENIZAÇÃO - dividir em unidades (palavras e pontuação)
tokens = re.findall(r"\w+|[^\w\s]", TEXTO)
print(f"1) Tokenização ({len(tokens)} tokens):\n  ", tokens[:20], "...\n")

# 2) NORMALIZAÇÃO - minúsculas, sem pontuação (e, opcionalmente, sem acentos)
def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
normalizados = [t.lower() for t in tokens if t.isalnum()]
print("2) Normalização (minúsculas, sem pontuação):\n  ", normalizados[:15], "...")
print("   'à' sem acento ->", sem_acento("à"), "| 'fáceis' ->", sem_acento("fáceis"), "\n")

# 3) STOP WORDS - remover palavras muito comuns que carregam pouco significado
STOP = set("""a à o os as e é de do da dos das em no na nos nas um uma uns umas para por que
porque não mas se esse essa este esta nesta neste nossas nosso nossa ir são sejam algo""".split())
conteudo = [t for t in normalizados if t not in STOP]
print(f"3) Sem stop words ({len(normalizados)} -> {len(conteudo)} termos):\n  ", conteudo, "\n")

# 4a) RADICALIZAÇÃO (stemming) - corta sufixos com regras (rápido, às vezes "feio")
SUFIXOS = sorted(["amos", "emos", "imos", "ando", "endo", "idade", "ades", "ões", "ais", "eis",
                  "ar", "er", "ir", "rá", "as", "os", "es", "a", "o", "s"], key=len, reverse=True)
def radical(p):
    for s in SUFIXOS:
        if p.endswith(s) and len(p) - len(s) >= 3:
            return p[: -len(s)]
    return p
print("4a) Radicalização:")
for p in ("escolhemos", "organizar", "dispostos", "habilidades", "energias", "servirá"):
    print(f"    {p:<12} -> {radical(p)}")

# 4b) LEMATIZAÇÃO - forma de dicionário (usa um léxico; aqui, um mini-dicionário)
LEMAS = {"escolhemos": "escolher", "sejam": "ser", "são": "ser", "servirá": "servir",
         "estamos": "estar", "pretendemos": "pretender", "fáceis": "fácil", "difíceis": "difícil",
         "energias": "energia", "habilidades": "habilidade", "dispostos": "disposto"}
print("4b) Lematização:", {p: LEMAS[p] for p in ("escolhemos", "sejam", "são", "fáceis", "dispostos")})
print("    Radical x lema: 'são' -> radical 'são' | lema 'ser'\n")

# 5) POS TAGGING - classe gramatical (léxico + heurística de sufixo)
LEXICO = {"lua": "S", "década": "S", "coisas": "S", "objetivo": "S", "desafio": "S",
          "melhor": "Adj", "fáceis": "Adj", "difíceis": "Adj", "outras": "Adj", "dispostos": "Adj"}
def pos(p):
    if p in LEXICO:
        return LEXICO[p]
    if re.search(r"(ar|er|ir|amos|emos|imos|rá|am)$", p):
        return "V"
    if re.search(r"(ção|dade|ia|ias|des)$", p):
        return "S"
    return "?"
print("5) Classes gramaticais (V=verbo, S=substantivo, Adj=adjetivo):")
print("  ", [f"{t} ({pos(t)})" for t in dict.fromkeys(conteudo)])

print("\nTermos mais frequentes após o pré-processamento:",
      Counter(LEMAS.get(t, t) for t in conteudo).most_common(4))
print("Nos serviços gerenciados do Azure, essas etapas acontecem nos bastidores.")
