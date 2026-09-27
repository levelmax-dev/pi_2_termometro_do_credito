"""
alerts.py
Painel de alerta ("semáforo") do Termômetro do Crédito.

Aplica regras simples e transparentes (sem IA pesada) sobre a variação
recente dos indicadores para sinalizar o momento para crédito/dívida:
verde (favorável), amarelo (atenção) ou vermelho (cautela).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from indicators import variacao_pontos


@dataclass
class ResultadoSemaforo:
    nivel: str          # "verde", "amarelo" ou "vermelho"
    cor_hex: str
    titulo: str
    mensagem: str
    pontos: int          # quantidade de sinais negativos identificados


NIVEL_CORES = {
    "verde": "#1E8E3E",
    "amarelo": "#F2A600",
    "vermelho": "#D93025",
}


def calcular_semaforo(series: dict[str, pd.DataFrame], periodos: int = 3) -> ResultadoSemaforo:
    """
    Recebe um dicionário {chave_indicador: DataFrame} com pelo menos
    'selic' e 'inadimplencia_pf' (idealmente todos os indicadores
    disponíveis) e aplica um conjunto de regras simples:

      +1 sinal de alerta se a Selic subiu nos últimos `periodos` meses
      +1 sinal de alerta se a inadimplência PF subiu
      +1 sinal de alerta se a inadimplência PJ subiu
      +1 sinal de alerta se o endividamento das famílias subiu
      +1 sinal de alerta se o desemprego subiu

    0 sinais -> verde | 1-2 sinais -> amarelo | 3+ sinais -> vermelho
    """
    sinais = 0
    motivos = []

    regras = [
        ("selic", "a Selic está em alta"),
        ("inadimplencia_pf", "a inadimplência de pessoas físicas está subindo"),
        ("inadimplencia_pj", "a inadimplência de empresas está subindo"),
        ("endividamento_familias", "o endividamento das famílias está subindo"),
        ("desemprego", "o desemprego está subindo"),
    ]

    for chave, motivo in regras:
        df = series.get(chave)
        if df is None or df.empty:
            continue
        variacao = variacao_pontos(df, periodos=periodos)
        if variacao is not None and variacao > 0:
            sinais += 1
            motivos.append(motivo)

    if sinais == 0:
        nivel = "verde"
        titulo = "Cenário favorável"
        mensagem = ("Os indicadores acompanhados não mostram piora recente. "
                    "Pode ser um momento razoável para avaliar crédito, "
                    "mas sempre compare taxas antes de decidir.")
    elif sinais <= 2:
        nivel = "amarelo"
        titulo = "Atenção"
        detalhes = " e ".join(motivos) if motivos else "alguns indicadores pioraram"
        mensagem = f"Sinal de atenção: {detalhes}. Vale pesquisar bem antes de contrair novas dívidas."
    else:
        nivel = "vermelho"
        titulo = "Cautela recomendada"
        mensagem = ("Vários indicadores pioraram ao mesmo tempo (" + ", ".join(motivos) +
                    "). É um momento de maior cautela para crédito, financiamentos e novas dívidas.")

    return ResultadoSemaforo(
        nivel=nivel,
        cor_hex=NIVEL_CORES[nivel],
        titulo=titulo,
        mensagem=mensagem,
        pontos=sinais,
    )
