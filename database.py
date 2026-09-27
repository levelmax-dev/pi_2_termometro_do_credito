"""
database.py
Camada de persistência (SQLite) do Termômetro do Crédito.

Responsabilidades:
- Cache dos dados baixados da API SGS/Bacen (evita bater na API toda hora)
- Registro de preferências do usuário (últimos indicadores/período usados)

O schema é criado automaticamente na primeira execução (init_db).
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "data" / "termometro_credito.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS indicador_cache (
    codigo INTEGER NOT NULL,
    data TEXT NOT NULL,           -- formato YYYY-MM-DD
    valor REAL NOT NULL,
    atualizado_em TEXT NOT NULL,  -- timestamp UTC ISO 8601
    PRIMARY KEY (codigo, data)
);

CREATE INDEX IF NOT EXISTS idx_indicador_cache_codigo_data
    ON indicador_cache (codigo, data);

CREATE TABLE IF NOT EXISTS preferencias_usuario (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS log_sincronizacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER NOT NULL,
    sucesso INTEGER NOT NULL,
    mensagem TEXT,
    executado_em TEXT NOT NULL
);
"""


def init_db(db_path: Path | None = None) -> None:
    """Cria o schema do banco de dados caso ainda não exista."""
    if db_path is None:
        db_path = DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def get_connection(db_path: Path | None = None):
    if db_path is None:
        db_path = DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Cache de indicadores
# ---------------------------------------------------------------------------

def upsert_series(codigo: int, df: pd.DataFrame, db_path: Path | None = None) -> int:
    """
    Insere/atualiza uma série de dados no cache.
    Espera um DataFrame com colunas ['data', 'valor'], onde 'data' é
    datetime ou string YYYY-MM-DD.
    Retorna o número de linhas gravadas.
    """
    if df.empty:
        return 0

    registros = []
    now = _now_iso()
    for _, row in df.iterrows():
        data_str = pd.to_datetime(row["data"]).strftime("%Y-%m-%d")
        registros.append((codigo, data_str, float(row["valor"]), now))

    with get_connection(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO indicador_cache (codigo, data, valor, atualizado_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(codigo, data) DO UPDATE SET
                valor = excluded.valor,
                atualizado_em = excluded.atualizado_em
            """,
            registros,
        )
        conn.commit()
    return len(registros)


def read_series(codigo: int, data_inicio: str | None = None,
                 data_fim: str | None = None, db_path: Path | None = None) -> pd.DataFrame:
    """Lê uma série do cache, opcionalmente filtrando por período (YYYY-MM-DD)."""
    query = "SELECT data, valor FROM indicador_cache WHERE codigo = ?"
    params: list = [codigo]

    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)

    query += " ORDER BY data ASC"

    with get_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=params, parse_dates=["data"])
    return df


def series_esta_atualizada(codigo: int, dias_tolerancia: int = 1, db_path: Path | None = None) -> bool:
    """Verifica se já existe um registro de cache atualizado nas últimas N horas para o código."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT MAX(atualizado_em) FROM indicador_cache WHERE codigo = ?", (codigo,)
        )
        row = cur.fetchone()

    if not row or not row[0]:
        return False

    ultima_atualizacao = datetime.fromisoformat(row[0])
    agora = datetime.now(timezone.utc)
    return (agora - ultima_atualizacao).total_seconds() < dias_tolerancia * 86400


def registrar_log_sincronizacao(codigo: int, sucesso: bool, mensagem: str = "",
                                 db_path: Path | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO log_sincronizacao (codigo, sucesso, mensagem, executado_em) VALUES (?, ?, ?, ?)",
            (codigo, int(sucesso), mensagem, _now_iso()),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Preferências do usuário
# ---------------------------------------------------------------------------

def salvar_preferencia(chave: str, valor: str, db_path: Path | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO preferencias_usuario (chave, valor, atualizado_em)
            VALUES (?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor, atualizado_em = excluded.atualizado_em
            """,
            (chave, valor, _now_iso()),
        )
        conn.commit()


def ler_preferencia(chave: str, padrao: str | None = None, db_path: Path | None = None) -> str | None:
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT valor FROM preferencias_usuario WHERE chave = ?", (chave,))
        row = cur.fetchone()
    return row[0] if row else padrao
