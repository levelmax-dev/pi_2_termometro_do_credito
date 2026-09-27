from datetime import date

import pandas as pd
import pytest
import responses

import api_client
from api_client import BacenAPIError, buscar_serie_api, _parse_resposta


SGS_URL_432 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"


@responses.activate
def test_buscar_serie_api_sucesso():
    payload = [
        {"data": "01/01/2026", "valor": "13.25"},
        {"data": "01/02/2026", "valor": "13.00"},
    ]
    responses.add(responses.GET, SGS_URL_432, json=payload, status=200)

    df = buscar_serie_api(432, date(2026, 1, 1), date(2026, 2, 1))

    assert list(df.columns) == ["data", "valor"]
    assert len(df) == 2
    assert df["valor"].iloc[0] == pytest.approx(13.25)
    assert pd.api.types.is_datetime64_any_dtype(df["data"])


@responses.activate
def test_buscar_serie_api_erro_http_levanta_bacen_api_error():
    responses.add(responses.GET, SGS_URL_432, status=500)

    with pytest.raises(BacenAPIError):
        buscar_serie_api(432, date(2026, 1, 1), date(2026, 2, 1))


@responses.activate
def test_buscar_serie_api_timeout_levanta_bacen_api_error():
    responses.add(
        responses.GET, SGS_URL_432,
        body=__import__("requests").exceptions.Timeout(),
    )

    with pytest.raises(BacenAPIError):
        buscar_serie_api(432, date(2026, 1, 1), date(2026, 2, 1))


def test_parse_resposta_lista_vazia():
    df = _parse_resposta([])
    assert df.empty
    assert list(df.columns) == ["data", "valor"]


def test_parse_resposta_ignora_valores_invalidos():
    payload = [
        {"data": "01/01/2026", "valor": "13.25"},
        {"data": "01/02/2026", "valor": "não-numérico"},
    ]
    df = _parse_resposta(payload)
    assert len(df) == 1
    assert df["valor"].iloc[0] == pytest.approx(13.25)


@responses.activate
def test_obter_serie_usa_fallback_do_cache_quando_api_falha(tmp_path, monkeypatch):
    import database

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db(db_path)

    df_cache = pd.DataFrame({
        "data": pd.to_datetime(["2026-01-01", "2026-02-01"]),
        "valor": [13.25, 13.00],
    })
    database.upsert_series(432, df_cache, db_path=db_path)

    # Força a rota "cache desatualizado" para simular obter_serie indo para a API
    monkeypatch.setattr(database, "series_esta_atualizada", lambda *a, **k: False)
    responses.add(responses.GET, SGS_URL_432, status=500)

    df_resultado = api_client.obter_serie(432, date(2026, 1, 1), date(2026, 2, 1))

    # Mesmo com a API falhando, o cache anterior deve ser retornado
    assert not df_resultado.empty
    assert len(df_resultado) == 2
