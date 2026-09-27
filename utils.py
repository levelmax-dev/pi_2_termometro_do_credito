"""
utils.py
Funções utilitárias compartilhadas: formatação de números/datas,
exportação para CSV e pequenos helpers de acessibilidade.
"""

from __future__ import annotations

import io

import pandas as pd


def formatar_numero_br(valor: float, casas: int = 2) -> str:
    """Formata um número no padrão brasileiro (vírgula decimal, ponto de milhar)."""
    if valor is None:
        return "-"
    texto = f"{valor:,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto


def formatar_variacao(valor: float | None, sufixo: str = "p.p.") -> str:
    if valor is None:
        return "sem dado"
    sinal = "+" if valor > 0 else ""
    return f"{sinal}{formatar_numero_br(valor)} {sufixo}"


def dataframe_para_csv_bytes(df: pd.DataFrame) -> bytes:
    """Converte um DataFrame em CSV (utf-8-sig, separador ';') pronto para download."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")


def rotulo_acessivel(nome_indicador: str, unidade: str) -> str:
    """Gera um rótulo textual descritivo, útil para leitores de tela em gráficos/controles."""
    return f"{nome_indicador} ({unidade})"
