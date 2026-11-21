"""
Módulo 01 - Tópico: Cargas de trabalho de inteligência artificial
Slide: Machine Learning | Agentes e IA generativa | Idioma e texto |
       Fala no computador | Pesquisa Visual Computacional | Extração de informações

Exercício: para cada cenário de negócio, identifique a carga de trabalho.
  python 02_cargas_de_trabalho.py          -> mostra o gabarito comentado
  python 02_cargas_de_trabalho.py --quiz   -> modo quiz interativo
"""
import random
import sys

CARGAS = {
    "ML": "Machine Learning",
    "GEN": "Agentes e IA generativa",
    "TXT": "Idioma e texto (PLN)",
    "FALA": "Fala no computador",
    "VISAO": "Visão computacional",
    "EXT": "Extração de informações",
}

CENARIOS = [
    ("Prever a demanda de energia elétrica da próxima semana com base em 5 anos de medições.",
     "ML", "Previsão numérica a partir de dados históricos (regressão)."),
    ("Um assistente que, a partir de um pedido em linguagem natural, abre um chamado no ServiceNow e responde ao usuário.",
     "GEN", "Agente: usa um modelo + instruções + ferramentas para agir em nome do usuário."),
    ("Classificar milhares de avaliações de clientes como positivas, negativas ou neutras.",
     "TXT", "Análise de sentimento é uma tarefa clássica de PLN."),
    ("Gerar legendas automáticas em tempo real para uma transmissão ao vivo.",
     "FALA", "Reconhecimento de fala (speech-to-text)."),
    ("Contar quantos carros entram em um estacionamento a partir das câmeras.",
     "VISAO", "Detecção de objetos em imagens/vídeo."),
    ("Ler notas fiscais em PDF e preencher automaticamente o ERP com CNPJ, data e valor total.",
     "EXT", "OCR + mapeamento de campos para um esquema estruturado."),
    ("Detectar transações de cartão de crédito potencialmente fraudulentas.",
     "ML", "Classificação/detecção de anomalias com base em padrões históricos."),
    ("Criar 10 variações de texto publicitário para uma campanha de Black Friday.",
     "GEN", "Geração de conteúdo original a partir de um prompt."),
    ("Remover CPF, telefone e e-mail de transcrições antes de armazená-las.",
     "TXT", "Detecção/redação de PII é um recurso da Linguagem do Azure."),
    ("Um leitor de tela que lê o conteúdo do site em voz alta para pessoas com deficiência visual.",
     "FALA", "Síntese de voz (text-to-speech)."),
    ("Inspecionar peças em uma linha de produção e identificar arranhões.",
     "VISAO", "Classificação/segmentação de imagens para controle de qualidade."),
    ("Resumir gravações de chamadas do call center e extrair motivo do contato e satisfação.",
     "EXT", "Extração de informações de áudio (Content Understanding) - combina fala + PLN."),
]


def gabarito():
    for i, (cenario, chave, porque) in enumerate(CENARIOS, 1):
        print(f"{i:2}. {cenario}\n    -> {CARGAS[chave]}: {porque}\n")


def quiz():
    opcoes = list(CARGAS.items())
    acertos = 0
    perguntas = random.sample(CENARIOS, k=6)
    for i, (cenario, chave, porque) in enumerate(perguntas, 1):
        print(f"\n[{i}/{len(perguntas)}] {cenario}")
        for n, (_, nome) in enumerate(opcoes, 1):
            print(f"   {n}) {nome}")
        resp = input("Sua resposta (1-6): ").strip()
        escolhida = opcoes[int(resp) - 1][0] if resp.isdigit() and 1 <= int(resp) <= 6 else None
        if escolhida == chave:
            acertos += 1
            print("   Correto!", porque)
        else:
            print(f"   Resposta: {CARGAS[chave]}. {porque}")
    print(f"\nVocê acertou {acertos} de {len(perguntas)}.")


if __name__ == "__main__":
    quiz() if "--quiz" in sys.argv else gabarito()
