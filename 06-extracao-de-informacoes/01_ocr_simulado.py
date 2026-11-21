"""
Módulo 06 - Tópico: OCR (reconhecimento óptico de caracteres) - "Leitura de texto
de documentos e imagens"
  1) Aquisição e entrada de imagens
  2) Pré-processamento e aprimoramento de imagem
  3) Detecção de região de texto
  4) Reconhecimento e classificação de caracteres
  5) Geração de saída e pós-processamento

Um mini-OCR com numpy: "imprime" um recibo numa imagem com uma fonte 3x5, adiciona
ruído (como num scanner/celular) e depois LÊ o texto de volta, com confiança.

  python 01_ocr_simulado.py
"""
import json

import numpy as np

FONTE = {  # cada caractere = 5 linhas x 3 colunas
    "0": "###|#.#|#.#|#.#|###", "1": ".#.|##.|.#.|.#.|###", "2": "###|..#|###|#..|###",
    "5": "###|#..|###|..#|###", "7": "###|..#|.#.|.#.|.#.", "T": "###|.#.|.#.|.#.|.#.",
    "O": "###|#.#|#.#|#.#|###",  # idêntico ao zero! o pós-processamento resolve pelo contexto
    "A": ".#.|#.#|###|#.#|#.#", "L": "#..|#..|#..|#..|###", "R": "##.|#.#|##.|#.#|#.#",
    "D": "##.|#.#|#.#|#.#|##.", "$": ".##|##.|.#.|.##|##.", ",": "...|...|...|.#.|#..",
    "/": "..#|..#|.#.|#..|#..",
}
GLIFOS = {c: np.array([[p == "#" for p in linha] for linha in g.split("|")], float)
          for c, g in FONTE.items()}

# ---------- 1) Aquisição: "fotografar" um recibo ----------
LINHAS = ["DATA 07/10/2025", "TOTAL R$ 20,50"]
def renderizar(linhas):
    largura = max(len(t) for t in linhas) * 4 + 2
    img = np.zeros((len(linhas) * 8 + 2, largura))
    for i, texto in enumerate(linhas):
        y, x = 1 + i * 8, 1
        for c in texto:
            if c != " ":
                img[y:y + 5, x:x + 3] = GLIFOS[c]
            x += 4
    return img

rng = np.random.default_rng(11)
limpa = renderizar(LINHAS)
foto = limpa * rng.uniform(0.6, 1.0, limpa.shape) + rng.normal(0.15, 0.12, limpa.shape)  # tinta irregular + ruído
foto[rng.random(foto.shape) < 0.03] = 1.0                                                # "sujeira" do papel

def mostrar(m, titulo):
    print(titulo)
    print("\n".join("   " + "".join("#" if v > 0.5 else "." for v in linha) for linha in m))
mostrar(foto, "1) Imagem adquirida (com ruído):")

# ---------- 2) Pré-processamento: binarizar + remover pixels isolados ----------
binaria = (foto > 0.5).astype(int)
viz = sum(np.roll(np.roll(binaria, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - binaria
limpa_proc = binaria * (viz > 0)            # pixel sem nenhum vizinho = ruído
mostrar(limpa_proc, "\n2) Após binarização e remoção de ruído:")

# ---------- 3) Detecção de regiões: linhas e caracteres (projeções) ----------
def segmentos(perfil):
    seg, ini = [], None
    for i, v in enumerate(list(perfil) + [0]):
        if v and ini is None:
            ini = i
        elif not v and ini is not None:
            seg.append((ini, i))
            ini = None
    return seg

# Linhas: faixas horizontais com tinta (perfil de projeção das linhas da imagem).
# Dentro de cada faixa, a janela de 5 pixels de altura com mais tinta é a linha de texto.
faixas = [s for s in segmentos(limpa_proc.sum(axis=1) >= 2) if s[1] - s[0] >= 4]
linhas_texto = []
for y0, y1 in faixas:
    y = max(range(y0, max(y0, y1 - 5) + 1), key=lambda t: limpa_proc[t:t + 5].sum())
    linhas_texto.append(y)
print(f"\n3) {len(linhas_texto)} linhas de texto detectadas (topo nas linhas {linhas_texto})")

# Caracteres: fonte MONOESPAÇADA (como impressoras de cupom) -> células de 3 colunas a cada 4.
# Isso evita que um pixel de ruído no espaço entre letras "cole" dois caracteres.
PASSO = 4

def ler_linha(faixa, x0):
    texto, confs = "", []
    for x in range(x0, faixa.shape[1] - 2, PASSO):
        celula = faixa[:, x:x + 3].astype(float)
        if celula.sum() <= 1:                            # célula vazia = espaço
            texto += " "
            continue
        # ---------- 4) Reconhecimento: comparar a célula com cada modelo (template) ----------
        distancias = {c: np.abs(celula - g).sum() for c, g in GLIFOS.items()}
        c = min(distancias, key=distancias.get)
        texto += c
        confs.append(1 - distancias[c] / 15)
    return texto.strip(), float(np.mean(confs)) if confs else 0.0

resultado = []
for y in linhas_texto:
    faixa = limpa_proc[y:y + 5]
    # alinhamento da grade: testa os 4 deslocamentos possíveis e fica com o mais confiável
    texto, conf = max((ler_linha(faixa, x0) for x0 in range(PASSO)), key=lambda r: r[1])
    resultado.append({"texto_bruto": texto, "confianca": round(conf, 2)})
print("4) Reconhecimento (caractere mais parecido com cada célula):")
for r in resultado:
    print(f"   {r['texto_bruto']!r}  confiança média {r['confianca']}")

# ---------- 5) Pós-processamento: correções por contexto ----------
def corrigir(palavra):
    digitos = sum(ch.isdigit() for ch in palavra)
    if digitos >= len(palavra) / 2:                    # palavra "numérica": O -> 0
        return palavra.replace("O", "0")
    return palavra.replace("0", "O")                   # palavra alfabética: 0 -> O
for r in resultado:
    r["texto"] = " ".join(corrigir(p) for p in r["texto_bruto"].split())
print("\n5) Saída final (JSON):")
print(json.dumps(resultado, indent=2, ensure_ascii=False))
print("\nO OCR entrega TEXTO, não SIGNIFICADO. Qual valor é o total? -> 02_mapeamento_campos.py")
