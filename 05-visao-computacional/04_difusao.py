"""
Módulo 05 - Tópico: Geração de imagem e vídeo - MODELOS DE DIFUSÃO
  TREINO: adiciona "ruído" visual às imagens aos poucos e o modelo aprende como o
          ruído altera a imagem associada a uma descrição.
  GERAÇÃO: o processo é invertido - começa com pixels ALEATÓRIOS e remove, passo a
           passo, o ruído "aprendido" associado à descrição (o prompt).

Simulação com numpy em uma imagem 10x10. O "modelo" aqui é um denoiser ideal que
conhece as imagens de cada prompt - num modelo real, uma rede neural PREVÊ o ruído.

  python 04_difusao.py
"""
import numpy as np

rng = np.random.default_rng(5)
yy, xx = np.mgrid[:10, :10]
CONCEITOS = {
    "um círculo": ((yy - 4.5) ** 2 + (xx - 4.5) ** 2 <= 14).astype(float),
    "uma cruz": ((np.abs(yy - 4.5) < 1) | (np.abs(xx - 4.5) < 1)).astype(float),
}

def mostrar(imgs, titulos):
    print("   " + "".join(f"{t:<14}" for t in titulos))
    for linha in range(10):
        print("   " + "".join("".join("#" if v > 0.5 else "+" if v > 0.25 else "." for v in im[linha]) + "    "
                              for im in imgs))
    print()

# ---------- Processo DIRETO (treinamento): adicionar ruído aos poucos ----------
T = 10
alphas = np.linspace(1.0, 0.0, T + 1)          # quanto da imagem original sobra em cada passo
x0 = CONCEITOS["um círculo"]
ruido = rng.normal(0.5, 0.5, x0.shape)
etapas = [alphas[t] * x0 + (1 - alphas[t]) * ruido for t in (0, 3, 6, 10)]
print("PROCESSO DIRETO (treino): imagem + ruído crescente")
mostrar(etapas, ["t=0", "t=3", "t=6", "t=10 (ruído)"])

# ---------- Processo REVERSO (geração): ruído -> imagem guiada pelo prompt ----------
def gerar(prompt, passos=T):
    x = rng.normal(0.5, 0.5, (10, 10))          # começa com pixels aleatórios
    alvo = CONCEITOS[prompt]
    historico = [x.copy()]
    for t in range(passos, 0, -1):
        ruido_previsto = (x - alphas[t] * alvo) / max(1 - alphas[t], 1e-6)   # "modelo" prevê o ruído
        x = alphas[t - 1] * alvo + (1 - alphas[t - 1]) * ruido_previsto     # remove parte dele
        if t in (7, 4, 1):
            historico.append(x.copy())
    return historico

for prompt in CONCEITOS:
    print(f"PROCESSO REVERSO (geração) para o prompt: '{prompt}'")
    mostrar(gerar(prompt), ["ruído inicial", "passo 3", "passo 6", "final"])
print("O PROMPT decide qual ruído remover. Modelos reais (ex.: gpt-image, FLUX, Sora)")
print("aplicam a mesma ideia em milhões de pixels e, no vídeo, também ao longo do tempo.")
