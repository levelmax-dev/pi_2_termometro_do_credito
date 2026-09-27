"""
api_client.py
Cliente para a API SGS (Sistema Gerenciador de Séries Temporais) do
Banco Central do Brasil, com tratamento de erros, timeout e um
pipeline simples de ETL (extract -> transform -> load no cache SQLite).

Documentação da API: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
"""

from __future__ import annotations

import logging
from datetime import date, datetime

import pandas as pd
import requests

import database

logger = logging.getLogger(__name__)

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
TIMEOUT_SEGUNDOS = 10
MAX_TENTATIVAS = 3


class BacenAPIError(Exception):
    """Erro genérico ao consultar a API do Banco Central."""


def _montar_url(codigo: int, data_inicio: date | None, data_fim: date | None) -> tuple[str, dict]:
    url = BASE_URL.format(codigo=codigo)
    params = {"formato": "json"}
    if data_inicio:
        params["dataInicial"] = data_inicio.strftime("%d/%m/%Y")
    if data_fim:
        params["dataFinal"] = data_fim.strftime("%d/%m/%Y")
    return url, params


def _parse_resposta(payload: list[dict]) -> pd.DataFrame:
    """Converte o JSON da API SGS (lista de {data, valor}) em DataFrame tipado."""
    if not payload:
        return pd.DataFrame(columns=["data", "valor"])

    df = pd.DataFrame(payload)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["valor"]).sort_values("data").reset_index(drop=True)
    return df


def buscar_serie_api(codigo: int, data_inicio: date | None = None,
                      data_fim: date | None = None,
                      session: requests.Session | None = None) -> pd.DataFrame:
    """
    Busca uma série diretamente na API do Bacen, com retentativas simples.
    Lança BacenAPIError se todas as tentativas falharem.
    """
    url, params = _montar_url(codigo, data_inicio, data_fim)
    http = session or requests

    ultimo_erro: Exception | None = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = http.get(url, params=params, timeout=TIMEOUT_SEGUNDOS)
            resp.raise_for_status()
            payload = resp.json()
            return _parse_resposta(payload)
        except (requests.RequestException, ValueError) as exc:
            ultimo_erro = exc
            logger.warning("Tentativa %s/%s falhou para código %s: %s",
                            tentativa, MAX_TENTATIVAS, codigo, exc)

    raise BacenAPIError(
        f"Falha ao consultar a série {codigo} após {MAX_TENTATIVAS} tentativas: {ultimo_erro}"
    )


def obter_serie(codigo: int, data_inicio: date | None = None, data_fim: date | None = None,
                 forcar_atualizacao: bool = False,
                 session: requests.Session | None = None) -> pd.DataFrame:
    """
    Função principal usada pela aplicação: retorna a série pedida,
    usando o cache local sempre que possível e caindo para a API
    apenas quando necessário (cache ausente/expirado ou forçado).

    Em caso de falha na API e cache disponível (mesmo desatualizado),
    retorna o cache como fallback em vez de quebrar a aplicação.
    """
    cache_valido = database.series_esta_atualizada(codigo) and not forcar_atualizacao

    if cache_valido:
        df_cache = database.read_series(
            codigo,
            data_inicio.isoformat() if data_inicio else None,
            data_fim.isoformat() if data_fim else None,
        )
        if not df_cache.empty:
            return df_cache

    try:
        df_api = buscar_serie_api(codigo, data_inicio, data_fim, session=session)
        database.upsert_series(codigo, df_api)
        database.registrar_log_sincronizacao(codigo, sucesso=True)
        return database.read_series(
            codigo,
            data_inicio.isoformat() if data_inicio else None,
            data_fim.isoformat() if data_fim else None,
        )
    except BacenAPIError as exc:
        database.registrar_log_sincronizacao(codigo, sucesso=False, mensagem=str(exc))
        logger.error("Erro ao atualizar série %s via API: %s", codigo, exc)
        # Fallback: retorna o que houver em cache, mesmo desatualizado
        df_fallback = database.read_series(
            codigo,
            data_inicio.isoformat() if data_inicio else None,
            data_fim.isoformat() if data_fim else None,
        )
        return df_fallback
