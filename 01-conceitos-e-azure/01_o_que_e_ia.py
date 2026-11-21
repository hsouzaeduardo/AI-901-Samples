"""
Módulo 01 - Tópico: O que é inteligência artificial?
Slide: "Software que imita as capacidades humanas" -> prever resultados e
reconhecer padrões com base em dados históricos; avaliar e tomar decisões.

Cenário: uma empresa de aluguel de bicicletas quer
  1) PREVER quantas bicicletas serão alugadas amanhã (regressão)
  2) RECONHECER PADRÕES: o dia será de "alta" ou "baixa" demanda? (classificação)
  3) TOMAR UMA DECISÃO: quantos funcionários escalar (ação baseada na previsão)

Executa 100% offline (só numpy). Rode:  python 01_o_que_e_ia.py
"""
import numpy as np

# Dados históricos (fictícios): temperatura (°C), fim de semana (0/1), aluguéis
historico = np.array([
    # temp, fds, alugueis
    [12, 0, 180], [15, 0, 240], [18, 0, 310], [21, 0, 360], [24, 0, 420],
    [27, 0, 470], [30, 0, 450], [14, 1, 330], [19, 1, 450], [23, 1, 560],
    [26, 1, 640], [29, 1, 690], [10, 0, 150], [16, 1, 380], [32, 0, 400],
])
X = np.column_stack([np.ones(len(historico)), historico[:, 0], historico[:, 1]])
y = historico[:, 2]

# 1) PREVER - regressão linear por mínimos quadrados: alugueis = b0 + b1*temp + b2*fds
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
b0, b1, b2 = coef
print("=== 1) Previsão (regressão) ===")
print(f"Modelo aprendido: aluguéis = {b0:.1f} + {b1:.1f}*temperatura + {b2:.1f}*fim_de_semana")

amanha = {"temperatura": 25, "fim_de_semana": 1}
previsao = b0 + b1 * amanha["temperatura"] + b2 * amanha["fim_de_semana"]
print(f"Amanhã ({amanha}): previsão de {previsao:.0f} aluguéis")

# Erro médio nos dados históricos (o modelo nunca é perfeito!)
erro_medio = np.mean(np.abs(X @ coef - y))
print(f"Erro absoluto médio no histórico: {erro_medio:.0f} aluguéis\n")

# 2) RECONHECER PADRÕES - classificação por vizinho mais próximo (k-NN, k=3)
print("=== 2) Reconhecimento de padrões (classificação) ===")
rotulos = np.where(y >= 400, "alta", "baixa")
def classificar(temp, fds, k=3):
    # normaliza a temperatura para que as duas variáveis tenham escalas parecidas
    dist = np.sqrt(((historico[:, 0] - temp) / 10) ** 2 + (historico[:, 1] - fds) ** 2)
    vizinhos = np.argsort(dist)[:k]
    valores, contagens = np.unique(rotulos[vizinhos], return_counts=True)
    return valores[np.argmax(contagens)], rotulos[vizinhos]

for temp, fds in [(25, 1), (13, 0), (28, 0)]:
    classe, viz = classificar(temp, fds)
    print(f"temp={temp}°C fds={fds} -> demanda {classe.upper()} (vizinhos: {list(viz)})")

# 3) TOMAR DECISÃO - regra de negócio sobre a previsão
print("\n=== 3) Tomada de decisão ===")
bicicletas_por_funcionario = 120
funcionarios = int(np.ceil(previsao / bicicletas_por_funcionario))
print(f"Previsão de {previsao:.0f} aluguéis -> escalar {funcionarios} funcionários")
print("\nObservação: isso é Machine Learning clássico. A IA generativa (módulo 02)")
print("vai além: em vez de prever um número, ela GERA conteúdo novo (texto, imagem, código).")
