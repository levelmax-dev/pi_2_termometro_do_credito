"""
app.py
Termômetro do Crédito — Projeto Integrador II (Univesp)

Aplicação Streamlit que consome a API SGS do Banco Central, armazena os
dados em cache local (SQLite), calcula médias móveis e variações, e
apresenta um painel visual e acessível para apoiar decisões de crédito
de pessoas físicas e pequenos empreendedores.

Integrantes do Grupo PJI240 - A2026S2N3 - Grupo 18:

Adriano Neves de Oliveira
Diogo Jaderson Ferreira Santos
Francislene Oliveira Gomes
Luís Alberto Costa da Conceição
Marcos Patrick da Costa Cerbino
Pedro Henrique Alencar Barbosa
Ramon Galana Luglio
Rudnei Augusto de Paula Santos

"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import database
from api_client import obter_serie
from alerts import calcular_semaforo
from components.semaforo_widget import render_semaforo_gauge_html
from indicators import (
    INDICATORS,
    add_moving_averages,
    get_indicator,
    leitura_simples,
    list_indicator_keys,
    variacao_percentual,
)
from utils import dataframe_para_csv_bytes, formatar_numero_br, formatar_variacao, rotulo_acessivel

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Termômetro do Crédito",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

database.init_db()

PALETA = {
    "fundo": "#F7F8FA",
    "cartao": "#FFFFFF",
    "texto_principal": "#1A1A2E",
    "texto_secundario": "#4A4A5A",
    "primaria": "#123C69",
    "primaria_clara": "#1F5D9C",
    "acento": "#0E9F6E",
    "borda": "#E2E5EB",
}

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {PALETA['fundo']};
    }}
    h1, h2, h3 {{
        color: {PALETA['texto_principal']};
        font-weight: 700;
    }}
    p, span, label, div {{
        color: {PALETA['texto_principal']};
    }}
    .tc-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 4px 0 18px 0;
        border-bottom: 1px solid {PALETA['borda']};
        margin-bottom: 22px;
    }}
    .tc-header h1 {{
        font-size: 1.9rem;
        margin: 0;
    }}
    .tc-header p {{
        color: {PALETA['texto_secundario']};
        margin: 2px 0 0 0;
        font-size: 0.95rem;
    }}
    .tc-card {{
        background-color: {PALETA['cartao']};
        border: 1px solid {PALETA['borda']};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(20, 30, 60, 0.06);
        height: 100%;
    }}
    .tc-card .tc-kpi-nome {{
        font-size: 0.85rem;
        color: {PALETA['texto_secundario']};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .tc-card .tc-kpi-valor {{
        font-size: 2rem;
        font-weight: 800;
        color: {PALETA['primaria']};
        margin: 4px 0 2px 0;
    }}
    .tc-card .tc-kpi-variacao {{
        font-size: 0.88rem;
        font-weight: 600;
    }}
    .tc-card .tc-kpi-leitura {{
        font-size: 0.85rem;
        color: {PALETA['texto_secundario']};
        margin-top: 8px;
        line-height: 1.4;
    }}
    .tc-badge-alta {{ color: #B3261E; }}
    .tc-badge-baixa {{ color: #0E7C3A; }}
    .tc-badge-estavel {{ color: {PALETA['texto_secundario']}; }}
    section[data-testid="stSidebar"] {{
        background-color: #101A2B;
    }}
    section[data-testid="stSidebar"] * {{
        color: #EAF0FB !important;
    }}
    .tc-footer {{
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid {PALETA['borda']};
        color: {PALETA['texto_secundario']};
        font-size: 0.82rem;
    }}
    /* Foco visível para navegação por teclado (acessibilidade) */
    a:focus, button:focus, input:focus, select:focus {{
        outline: 3px solid {PALETA['primaria_clara']} !important;
        outline-offset: 2px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Funções auxiliares de dados
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def carregar_indicador(chave: str, data_inicio: date, data_fim: date,
                        forcar: bool = False) -> pd.DataFrame:
    ind = get_indicator(chave)
    df = obter_serie(ind.codigo, data_inicio=data_inicio, data_fim=data_fim, forcar_atualizacao=forcar)
    if not df.empty:
        df = add_moving_averages(df)
    return df


def carregar_varios(chaves: list[str], data_inicio: date, data_fim: date) -> dict[str, pd.DataFrame]:
    return {chave: carregar_indicador(chave, data_inicio, data_fim) for chave in chaves}


# ---------------------------------------------------------------------------
# Sidebar — filtros e preferências
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🌡️ Termômetro do Crédito")
    st.caption("Indicadores do Banco Central traduzidos para o dia a dia.")
    st.markdown("---")

    opcoes = list_indicator_keys()
    nomes = {chave: get_indicator(chave).nome for chave in opcoes}

    padrao_pref = database.ler_preferencia("ultimos_indicadores", "selic,inadimplencia_pf")
    padrao_selecionados = [c for c in padrao_pref.split(",") if c in opcoes] or opcoes[:2]

    selecionados = st.multiselect(
        "Indicadores",
        options=opcoes,
        default=padrao_selecionados,
        format_func=lambda c: nomes[c],
        help="Escolha um ou mais indicadores para acompanhar.",
    )

    st.markdown("**Período**")
    col_a, col_b = st.columns(2)
    hoje = date.today()
    with col_a:
        data_inicio = st.date_input("De", value=hoje - timedelta(days=365 * 3),
                                     max_value=hoje, format="DD/MM/YYYY")
    with col_b:
        data_fim = st.date_input("Até", value=hoje, max_value=hoje, format="DD/MM/YYYY")

    granularidade = st.selectbox("Granularidade", options=["Mensal"], index=0,
                                  help="A API SGS fornece os indicadores deste projeto em base mensal.")

    mostrar_mm = st.checkbox("Mostrar médias móveis (3 e 6 meses)", value=True)

    modo_comparacao = False
    if len(selecionados) >= 2:
        modo_comparacao = st.checkbox(
            "Comparar 2 indicadores no mesmo gráfico (eixo duplo)", value=False
        )

    st.markdown("---")
    atualizar_agora = st.button("🔄 Atualizar dados agora", use_container_width=True)

    if selecionados:
        database.salvar_preferencia("ultimos_indicadores", ",".join(selecionados))

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="tc-header">
        <div style="font-size: 2.4rem;">🌡️</div>
        <div>
            <h1>Termômetro do Crédito</h1>
            <p>Leitura simples dos indicadores econômicos do Banco Central para
               apoiar decisões de crédito, dívida e investimento.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not selecionados:
    st.info("Selecione ao menos um indicador na barra lateral para começar.")
    st.stop()

if data_inicio >= data_fim:
    st.error("A data inicial precisa ser anterior à data final.")
    st.stop()

with st.spinner("Consultando indicadores…"):
    series = carregar_varios(selecionados, data_inicio, data_fim)
    if atualizar_agora:
        st.cache_data.clear()
        series = {chave: carregar_indicador(chave, data_inicio, data_fim, forcar=True)
                  for chave in selecionados}

series_vazias = [chave for chave, df in series.items() if df.empty]
if series_vazias:
    nomes_vazios = ", ".join(nomes[c] for c in series_vazias)
    st.warning(
        f"Não foi possível obter dados para: {nomes_vazios}. "
        "Exibindo os demais indicadores disponíveis (a API do Bacen pode estar "
        "temporariamente indisponível — os dados em cache serão usados quando existirem)."
    )

series_validas = {k: v for k, v in series.items() if not v.empty}
if not series_validas:
    st.error("Nenhum dado disponível para os indicadores e período selecionados.")
    st.stop()

# ---------------------------------------------------------------------------
# Semáforo + cartões de indicadores (KPIs)
# ---------------------------------------------------------------------------

col_semaforo, col_kpis = st.columns([1, 2.2], gap="large")

with col_semaforo:
    st.markdown("#### Painel de alerta")
    # Para o semáforo, tentamos usar o conjunto completo de indicadores
    # (mesmo os não selecionados na tela) para uma leitura mais completa.
    chaves_semaforo = list_indicator_keys()
    series_semaforo = carregar_varios(chaves_semaforo, hoje - timedelta(days=365), hoje)
    resultado = calcular_semaforo(series_semaforo)

    html_gauge = render_semaforo_gauge_html(
        pontos=resultado.pontos,
        nivel=resultado.nivel,
        titulo=resultado.titulo,
        mensagem=resultado.mensagem,
        cor_hex=resultado.cor_hex,
    )
    st.components.v1.html(html_gauge, height=270)

with col_kpis:
    st.markdown("#### Leitura simples")
    n_cols = min(3, len(series_validas))
    cols = st.columns(n_cols)
    for i, (chave, df) in enumerate(series_validas.items()):
        ind = get_indicator(chave)
        valor_atual = df["valor"].iloc[-1]
        variacao = variacao_percentual(df, periodos=3)
        texto_leitura = leitura_simples(ind.nome, ind.unidade, variacao, ind.alta_e_ruim)

        if variacao is None:
            classe = "tc-badge-estavel"
        elif variacao > 0:
            classe = "tc-badge-alta"
        elif variacao < 0:
            classe = "tc-badge-baixa"
        else:
            classe = "tc-badge-estavel"

        with cols[i % n_cols]:
            st.markdown(
                f"""
                <div class="tc-card">
                    <div class="tc-kpi-nome">{ind.nome}</div>
                    <div class="tc-kpi-valor">{formatar_numero_br(valor_atual)} {ind.unidade}</div>
                    <div class="tc-kpi-variacao {classe}">{formatar_variacao(variacao, '% (3m)')}</div>
                    <div class="tc-kpi-leitura">{texto_leitura}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

st.markdown("#### Evolução histórica")

if modo_comparacao and len(selecionados) >= 2:
    chave_a, chave_b = selecionados[0], selecionados[1]
    df_a, df_b = series.get(chave_a), series.get(chave_b)

    if df_a is not None and df_b is not None and not df_a.empty and not df_b.empty:
        ind_a, ind_b = get_indicator(chave_a), get_indicator(chave_b)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_a["data"], y=df_a["valor"], name=rotulo_acessivel(ind_a.nome, ind_a.unidade),
            line=dict(color=PALETA["primaria"], width=2.5), yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=df_b["data"], y=df_b["valor"], name=rotulo_acessivel(ind_b.nome, ind_b.unidade),
            line=dict(color=PALETA["acento"], width=2.5), yaxis="y2",
        ))
        fig.update_layout(
            yaxis=dict(title=f"{ind_a.nome} ({ind_a.unidade})", color=PALETA["primaria"]),
            yaxis2=dict(title=f"{ind_b.nome} ({ind_b.unidade})", overlaying="y", side="right",
                        color=PALETA["acento"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor=PALETA["cartao"], paper_bgcolor=PALETA["cartao"],
            margin=dict(l=10, r=10, t=40, b=10), height=440,
            font=dict(color=PALETA["texto_principal"]),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não é possível comparar: um dos indicadores selecionados não tem dados.")
else:
    for chave, df in series_validas.items():
        ind = get_indicator(chave)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["data"], y=df["valor"], name=ind.nome,
            line=dict(color=PALETA["primaria"], width=2.5),
        ))
        if mostrar_mm:
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["mm_3m"], name="Média móvel 3 meses",
                line=dict(color=PALETA["acento"], width=1.6, dash="dot"),
            ))
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["mm_6m"], name="Média móvel 6 meses",
                line=dict(color="#7A5AF8", width=1.6, dash="dash"),
            ))
        fig.update_layout(
            title=f"{ind.nome} ({ind.unidade})",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor=PALETA["cartao"], paper_bgcolor=PALETA["cartao"],
            margin=dict(l=10, r=10, t=60, b=10), height=380,
            font=dict(color=PALETA["texto_principal"]),
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Tabela de dados + exportação CSV
# ---------------------------------------------------------------------------

with st.expander("📄 Ver dados em tabela e exportar CSV"):
    for chave, df in series_validas.items():
        ind = get_indicator(chave)
        st.markdown(f"**{ind.nome}**")
        df_exibicao = df.rename(columns={
            "data": "Data", "valor": f"Valor ({ind.unidade})",
            "mm_3m": "Média móvel 3m", "mm_6m": "Média móvel 6m",
        })
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        st.download_button(
            label=f"Baixar CSV — {ind.nome}",
            data=dataframe_para_csv_bytes(df_exibicao),
            file_name=f"termometro_credito_{chave}.csv",
            mime="text/csv",
            key=f"csv_{chave}",
        )

# ---------------------------------------------------------------------------
# Rodapé
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="tc-footer">
        Fonte dos dados: Sistema Gerenciador de Séries Temporais (SGS) — Banco Central do Brasil.
        Este painel tem finalidade educativa e não constitui recomendação financeira.
        Desenvolvido como Projeto Integrador II — Univesp.
    </div>
    """,
    unsafe_allow_html=True,
)
