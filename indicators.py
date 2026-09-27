"""
indicators.py
Configuração central dos indicadores do Termômetro do Crédito e
funções de análise (médias móveis, variação percentual).
"""

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class Indicator:
    codigo: int
    nome: str
    unidade: str
    descricao: str
    categoria: str
    # Quanto maior o valor, pior é o cenário de crédito? (usado no semáforo)
    alta_e_ruim: bool


# Catálogo oficial de indicadores usados no projeto (códigos SGS/Bacen)
INDICATORS: dict[str, Indicator] = {
    "selic": Indicator(
        codigo=432,
        nome="Taxa Selic",
        unidade="% a.a.",
        descricao="Taxa básica de juros da economia, definida pelo Copom.",
        categoria="Juros",
        alta_e_ruim=True,
    ),
    "ipca": Indicator(
        codigo=433,
        nome="IPCA",
        unidade="% a.m.",
        descricao="Índice de Preços ao Consumidor Amplo — inflação oficial do país.",
        categoria="Inflação",
        alta_e_ruim=True,
    ),
    "inadimplencia_pf": Indicator(
        codigo=21082,
        nome="Inadimplência - Pessoa Física",
        unidade="%",
        descricao="Percentual da carteira de crédito PF em atraso acima de 90 dias.",
        categoria="Inadimplência",
        alta_e_ruim=True,
    ),
    "inadimplencia_pj": Indicator(
        codigo=21083,
        nome="Inadimplência - Pessoa Jurídica",
        unidade="%",
        descricao="Percentual da carteira de crédito PJ em atraso acima de 90 dias.",
        categoria="Inadimplência",
        alta_e_ruim=True,
    ),
    "endividamento_familias": Indicator(
        codigo=29034,
        nome="Endividamento das Famílias",
        unidade="%",
        descricao="Relação entre dívida e renda acumulada das famílias.",
        categoria="Endividamento",
        alta_e_ruim=True,
    ),
    "desemprego": Indicator(
        codigo=24369,
        nome="Taxa de Desemprego",
        unidade="%",
        descricao="Taxa de desocupação da PNAD Contínua.",
        categoria="Emprego",
        alta_e_ruim=True,
    ),
}


def get_indicator(key: str) -> Indicator:
    return INDICATORS[key]


def list_indicator_keys() -> list[str]:
    return list(INDICATORS.keys())


# ---------------------------------------------------------------------------
# Análises quantitativas
# ---------------------------------------------------------------------------

def add_moving_averages(df: pd.DataFrame, value_col: str = "valor") -> pd.DataFrame:
    """
    Recebe um DataFrame com colunas ['data', value_col] ordenado por data
    e adiciona colunas 'mm_3m' e 'mm_6m' com médias móveis simples de
    3 e 6 períodos (meses, considerando granularidade mensal).
    """
    df = df.sort_values("data").reset_index(drop=True)
    df["mm_3m"] = df[value_col].rolling(window=3, min_periods=1).mean()
    df["mm_6m"] = df[value_col].rolling(window=6, min_periods=1).mean()
    return df


def variacao_percentual(df: pd.DataFrame, value_col: str = "valor", periodos: int = 3) -> float | None:
    """
    Calcula a variação percentual entre o valor mais recente e o valor
    de N períodos atrás. Retorna None se não houver dados suficientes.
    """
    if df.empty or len(df) <= periodos:
        return None
    atual = df[value_col].iloc[-1]
    anterior = df[value_col].iloc[-1 - periodos]
    if anterior == 0:
        return None
    return ((atual - anterior) / abs(anterior)) * 100


def variacao_pontos(df: pd.DataFrame, value_col: str = "valor", periodos: int = 3) -> float | None:
    """Variação em pontos percentuais/pontos-base entre o valor atual e N períodos atrás."""
    if df.empty or len(df) <= periodos:
        return None
    atual = df[value_col].iloc[-1]
    anterior = df[value_col].iloc[-1 - periodos]
    return atual - anterior


def leitura_simples(nome_indicador: str, unidade: str, variacao: float | None, alta_e_ruim: bool) -> str:
    """Gera uma frase em linguagem simples descrevendo a tendência do indicador."""
    if variacao is None:
        return f"Dados insuficientes para avaliar a tendência de {nome_indicador}."

    direcao = "subiu" if variacao > 0 else "caiu" if variacao < 0 else "permaneceu estável"
    magnitude = abs(round(variacao, 2))

    if variacao == 0:
        return f"{nome_indicador} permaneceu estável no período analisado."

    tendencia = "cenário de mais cautela" if (variacao > 0) == alta_e_ruim else "cenário mais favorável"
    return (
        f"{nome_indicador} {direcao} {magnitude} {unidade} no período — "
        f"indica {tendencia} para quem pensa em crédito ou dívida."
    )
