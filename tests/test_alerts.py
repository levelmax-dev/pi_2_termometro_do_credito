import pandas as pd

from alerts import calcular_semaforo


def _serie(valores):
    return pd.DataFrame({
        "data": pd.date_range("2025-01-01", periods=len(valores), freq="MS"),
        "valor": valores,
    })


def test_semaforo_verde_quando_tudo_melhora():
    series = {
        "selic": _serie([14, 13.5, 13, 12.5]),
        "inadimplencia_pf": _serie([5.0, 4.8, 4.6, 4.4]),
        "inadimplencia_pj": _serie([3.0, 2.9, 2.8, 2.7]),
        "endividamento_familias": _serie([48, 47.5, 47, 46.5]),
        "desemprego": _serie([8.0, 7.8, 7.6, 7.4]),
    }
    resultado = calcular_semaforo(series, periodos=3)
    assert resultado.nivel == "verde"
    assert resultado.pontos == 0


def test_semaforo_amarelo_com_dois_sinais():
    series = {
        "selic": _serie([12, 12.5, 13, 13.5]),          # subiu -> sinal
        "inadimplencia_pf": _serie([4.0, 4.2, 4.4, 4.6]),  # subiu -> sinal
        "inadimplencia_pj": _serie([3.0, 2.9, 2.8, 2.7]),  # caiu
        "endividamento_familias": _serie([48, 47.5, 47, 46.5]),  # caiu
        "desemprego": _serie([8.0, 7.8, 7.6, 7.4]),        # caiu
    }
    resultado = calcular_semaforo(series, periodos=3)
    assert resultado.nivel == "amarelo"
    assert resultado.pontos == 2


def test_semaforo_vermelho_com_tres_ou_mais_sinais():
    series = {
        "selic": _serie([12, 12.5, 13, 13.5]),
        "inadimplencia_pf": _serie([4.0, 4.2, 4.4, 4.6]),
        "inadimplencia_pj": _serie([2.7, 2.8, 2.9, 3.0]),
        "endividamento_familias": _serie([46.5, 47, 47.5, 48]),
        "desemprego": _serie([7.4, 7.6, 7.8, 8.0]),
    }
    resultado = calcular_semaforo(series, periodos=3)
    assert resultado.nivel == "vermelho"
    assert resultado.pontos == 5


def test_semaforo_ignora_indicadores_ausentes():
    series = {"selic": _serie([12, 12.5, 13, 13.5])}
    resultado = calcular_semaforo(series, periodos=3)
    assert resultado.pontos == 1
    assert resultado.nivel == "amarelo"


def test_semaforo_com_dicionario_vazio_retorna_verde():
    resultado = calcular_semaforo({}, periodos=3)
    assert resultado.nivel == "verde"
    assert resultado.pontos == 0
