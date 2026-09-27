import pandas as pd
import pytest

import database


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "termometro_teste.db"
    database.init_db(path)
    return path


def test_upsert_e_read_series(db_path):
    df = pd.DataFrame({
        "data": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01"]),
        "valor": [13.25, 13.00, 12.75],
    })

    linhas_gravadas = database.upsert_series(432, df, db_path=db_path)
    assert linhas_gravadas == 3

    resultado = database.read_series(432, db_path=db_path)
    assert len(resultado) == 3
    assert list(resultado["valor"]) == [13.25, 13.00, 12.75]


def test_upsert_series_atualiza_valor_existente(db_path):
    df1 = pd.DataFrame({"data": pd.to_datetime(["2026-01-01"]), "valor": [10.0]})
    df2 = pd.DataFrame({"data": pd.to_datetime(["2026-01-01"]), "valor": [11.5]})

    database.upsert_series(432, df1, db_path=db_path)
    database.upsert_series(432, df2, db_path=db_path)

    resultado = database.read_series(432, db_path=db_path)
    assert len(resultado) == 1
    assert resultado["valor"].iloc[0] == pytest.approx(11.5)


def test_read_series_filtra_por_periodo(db_path):
    df = pd.DataFrame({
        "data": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01"]),
        "valor": [1.0, 2.0, 3.0],
    })
    database.upsert_series(432, df, db_path=db_path)

    resultado = database.read_series(432, data_inicio="2026-02-01", db_path=db_path)
    assert len(resultado) == 2


def test_series_esta_atualizada_falso_quando_nao_existe(db_path):
    assert database.series_esta_atualizada(999, db_path=db_path) is False


def test_series_esta_atualizada_verdadeiro_apos_upsert(db_path):
    df = pd.DataFrame({"data": pd.to_datetime(["2026-01-01"]), "valor": [1.0]})
    database.upsert_series(432, df, db_path=db_path)
    assert database.series_esta_atualizada(432, dias_tolerancia=1, db_path=db_path) is True


def test_preferencias_usuario(db_path):
    assert database.ler_preferencia("tema", padrao="claro", db_path=db_path) == "claro"

    database.salvar_preferencia("tema", "escuro", db_path=db_path)
    assert database.ler_preferencia("tema", db_path=db_path) == "escuro"

    # sobrescreve preferência existente
    database.salvar_preferencia("tema", "claro", db_path=db_path)
    assert database.ler_preferencia("tema", db_path=db_path) == "claro"
