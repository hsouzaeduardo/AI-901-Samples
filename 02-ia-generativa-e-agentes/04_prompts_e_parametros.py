"""
Módulo 02 - Tópico: Usar um modelo de IA generativa
"Configurar comportamento de modelo com:
   Instruções (prompts do sistema) - contexto e diretrizes
   Entrada (prompts do usuário)   - detalhes suficientes para a saída desejada
   Parâmetros                     - 'criatividade' e duração da resposta"

Experimentos (cada um é uma função - comente/descomente à vontade):
  A) só o prompt do usuário
  B) mesmo prompt + instruções do sistema (persona e restrições)
  C) prompt vago x prompt detalhado
  D) temperatura 0 x temperatura alta
  E) limite de tamanho (max_output_tokens)
  F) conversa com memória (previous_response_id)
  G) a saída pode ser CÓDIGO

  python 04_prompts_e_parametros.py
"""
import os
import sys

import openai
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())


def env(nome):
    valor = os.getenv(nome)
    if not valor:
        sys.exit(f"Defina {nome} no arquivo .env (veja .env.example)")
    return valor


client = OpenAI(base_url=env("AZURE_OPENAI_ENDPOINT"), api_key=env("AZURE_FOUNDRY_KEY"))
MODELO = env("MODEL_DEPLOYMENT_NAME")

INSTRUCOES = ("Você é um historiador da computação. Responda apenas sobre história da "
              "computação, em português, com no máximo 3 frases. Se a pergunta for de outro "
              "assunto, recuse educadamente.")


def titulo(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def a_sem_instrucoes():
    titulo("A) Só o prompt do usuário")
    r = client.responses.create(model=MODELO, input="Quem foi Alan Turing?")
    print(r.output_text)


def b_com_instrucoes():
    titulo("B) Com instruções do sistema (persona + escopo)")
    for pergunta in ("Quem foi Alan Turing?", "Qual a melhor receita de bolo de cenoura?"):
        r = client.responses.create(model=MODELO, instructions=INSTRUCOES, input=pergunta)
        print(f"> {pergunta}\n{r.output_text}\n")


def c_prompt_vago_x_detalhado():
    titulo("C) Prompt vago x prompt detalhado")
    vago = "Escreva sobre o ENIAC."
    detalhado = ("Escreva um parágrafo de 50 palavras sobre o ENIAC para alunos do ensino médio, "
                 "citando o ano de conclusão e uma curiosidade. Termine com uma pergunta.")
    for p in (vago, detalhado):
        r = client.responses.create(model=MODELO, input=p)
        print(f"> {p}\n{r.output_text}\n")


def d_temperatura():
    titulo("D) Parâmetro de 'criatividade': temperatura")
    prompt = "Invente um nome para uma loja de computadores antigos. Responda só o nome."
    for temp in (0.0, 1.5):
        try:
            nomes = [client.responses.create(model=MODELO, input=prompt, temperature=temp).output_text
                     for _ in range(3)]
            print(f"temperature={temp}: {nomes}")
        except openai.BadRequestError as e:
            # Modelos de RACIOCÍNIO (ex.: família gpt-5, o-series) não aceitam temperature:
            # neles o controle é feito por reasoning={"effort": "low|medium|high"}.
            print(f"Este modelo não aceita 'temperature' ({e.code}). Use um gpt-4.1-mini para o teste.")
            return


def e_tamanho_da_resposta():
    titulo("E) Parâmetro de tamanho: max_output_tokens")
    r = client.responses.create(model=MODELO, input="Conte a história completa da computação.",
                                max_output_tokens=60)
    print(r.output_text)
    print(f"[status={r.status}; motivo={getattr(r.incomplete_details, 'reason', None)}]")


def f_conversa_com_memoria():
    titulo("F) Conversa com memória - previous_response_id")
    r1 = client.responses.create(model=MODELO, instructions=INSTRUCOES,
                                 input="Quem criou a linguagem COBOL?")
    print("> Quem criou a linguagem COBOL?\n" + r1.output_text)
    r2 = client.responses.create(model=MODELO, instructions=INSTRUCOES,
                                 input="E em que ano ela nasceu?",       # "ela" = pessoa anterior
                                 previous_response_id=r1.id)
    print("> E em que ano ela nasceu?\n" + r2.output_text)


def g_gerar_codigo():
    titulo("G) A saída também pode ser código")
    r = client.responses.create(
        model=MODELO,
        input="Escreva uma consulta SQL que retorne os 5 produtos mais vendidos em 2025 "
              "a partir das tabelas pedidos(id, data) e itens(pedido_id, produto, qtd). Só o SQL.")
    print(r.output_text)


if __name__ == "__main__":
    a_sem_instrucoes()
    b_com_instrucoes()
    c_prompt_vago_x_detalhado()
    d_temperatura()
    e_tamanho_da_resposta()
    f_conversa_com_memoria()
    g_gerar_codigo()
