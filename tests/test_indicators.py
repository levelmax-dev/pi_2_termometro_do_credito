import pandas as pd
import pytest

from indicators import (
    add_moving_averages,
    leitura_simples,
    variacao_percentual,
    variacao_pontos,
)


def _serie(valores):
    return pd.DataFrame({
        "data": pd.date_range("2025-01-01", periods=len(valores), freq="MS"),
        "valor": valores,
    })


def test_add_moving_averages_3_e_6_meses():
    df = _serie([1, 2, 3, 4, 5, 6, 7])
    resultado = add_moving_averages(df)

    assert "mm_3m" in resultado.columns
    assert "mm_6m" in resultado.columns
    # média móvel de 3 no 3º ponto (1,2,3) = 2.0
    assert resultado["mm_3m"].iloc[2] == pytest.approx(2.0)
    # média móvel de 6 no 6º ponto (1..6) = 3.5
    assert resultado["mm_6m"].iloc[5] == pytest.approx(3.5)


def test_add_moving_averages_preenche_com_min_periods():
    df = _serie([10, 20])
    resultado = add_moving_averages(df)
    # com apenas 2 pontos, min_periods=1 evita NaN
    assert not resultado["mm_3m"].isna().any()


def test_variacao_percentual_positiva():
    df = _serie([100, 100, 100, 110])
    variacao = variacao_percentual(df, periodos=3)
    assert variacao == pytest.approx(10.0)


def test_variacao_percentual_dados_insuficientes_retorna_none():
    df = _serie([100, 105])
    assert variacao_percentual(df, periodos=3) is None


def test_variacao_pontos():
    df = _serie([13.75, 13.50, 13.25, 13.00])
    assert variacao_pontos(df, periodos=3) == pytest.approx(-0.75)


def test_leitura_simples_alta_ruim():
    texto = leitura_simples("Taxa Selic", "% a.a.", 0.5, alta_e_ruim=True)
    assert "subiu" in texto
    assert "cautela" in texto


def test_leitura_simples_baixa_quando_alta_e_ruim():
    texto = leitura_simples("Inadimplência", "%", -1.2, alta_e_ruim=True)
    assert "caiu" in texto
    assert "favorável" in texto


def test_leitura_simples_sem_dados():
    texto = leitura_simples("IPCA", "%", None, alta_e_ruim=True)
    assert "insuficientes" in texto
