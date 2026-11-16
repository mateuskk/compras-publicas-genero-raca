"""Dashboard: Compras Públicas, Gênero e Raça (ODS 5 e ODS 18).

Rodar localmente:  streamlit run app/app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import carregar_painel, carregar_qualidade

TEAL, TEAL_ESCURO, SLATE = "#19B394", "#0E8A70", "#3E7A86"
AREA_CLARA = "#5DD0B4"
ORDEM_FAIXAS = ["até 30%", "30% a 50%", "50% a 70%", "acima de 70%"]
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

st.set_page_config(page_title="Compras Públicas · Gênero e Raça", layout="wide")

st.markdown(
    """
    <style>
    .stApp {background:#EEF0F2;}
    div[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #DDE2E6; padding:14px 18px;}
    div[data-testid="stMetricValue"] {color:#4A6075; font-weight:600;}
    .painel {background:#FFFFFF; border:1px solid #DDE2E6; padding:4px 16px 8px 16px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def brl(valor: float) -> str:
    if valor >= 1e9:
        return f"R$ {valor / 1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if valor >= 1e6:
        return f"R$ {valor / 1e6:,.0f} mi".replace(",", ".")
    return f"R$ {valor:,.0f}".replace(",", ".")


def pct(parte: float, total: float) -> float:
    return 100 * parte / total if total else 0.0


def estilo(fig: go.Figure, altura: int = 300) -> go.Figure:
    fig.update_layout(
        height=altura, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Open Sans, sans-serif", color="#3F4E5C"),
        legend=dict(orientation="h", y=-0.15),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF1F3")
    return fig


df, eh_amostra = carregar_painel()
qualidade = carregar_qualidade()

# ---------------- Cabeçalho ----------------
col_t, col_b = st.columns([4, 1])
col_t.markdown("### Compras Públicas · Gênero e Raça")
col_t.caption("Participação de empresas com sócias mulheres nos contratos públicos · ODS 5 e ODS 18")
if eh_amostra:
    col_b.warning("Dados sintéticos de exemplo")

# ---------------- Filtros ----------------
with st.sidebar:
    st.header("Filtros")
    anos = sorted(df["ano"].unique())
    f_ano = st.multiselect("Ano", anos, default=anos)
    f_uf = st.multiselect("UF", sorted(df["uf"].unique()))
    f_orgao = st.multiselect("Órgão", sorted(df["orgao"].dropna().unique()))
    f_mod = st.multiselect("Modalidade", sorted(df["modalidade"].unique()))
    f_porte = st.multiselect("Porte", sorted(df["porte"].unique()))

filtro = df["ano"].isin(f_ano) if f_ano else pd.Series(True, index=df.index)
for coluna, escolha in [("uf", f_uf), ("orgao", f_orgao), ("modalidade", f_mod), ("porte", f_porte)]:
    if escolha:
        filtro &= df[coluna].isin(escolha)
d = df[filtro]

if d.empty:
    st.info("Nenhum dado para os filtros escolhidos.")
    st.stop()

# ---------------- Indicadores ----------------
ano_atual = max(f_ano) if f_ano else d["ano"].max()
atual, anterior = d[d["ano"] == ano_atual], d[d["ano"] == ano_atual - 1]


def delta(serie_atual: float, serie_ant: float, pp: bool = False) -> str | None:
    if anterior.empty:
        return None
    if pp:
        return f"{serie_atual - serie_ant:+.1f} p.p. vs. ano anterior"
    return f"{pct(serie_atual - serie_ant, serie_ant):+.0f}% vs. ano anterior"


tot, tot_ant = atual["valor_total"].sum(), anterior["valor_total"].sum()
soc = pct(atual["valor_com_socia"].sum(), tot)
soc_ant = pct(anterior["valor_com_socia"].sum(), tot_ant)
mai = pct(atual["valor_maioria_feminina"].sum(), tot)
mai_ant = pct(anterior["valor_maioria_feminina"].sum(), tot_ant)

k = st.columns(6)
k[0].metric("Valor contratado", brl(tot), delta(tot, tot_ant))
k[1].metric("Contratos", f"{atual['qtd_contratos'].sum():,}".replace(",", "."),
            delta(atual["qtd_contratos"].sum(), anterior["qtd_contratos"].sum()))
k[2].metric("% com sócia mulher", f"{soc:.0f}%", delta(soc, soc_ant, pp=True))
k[3].metric("% maioria feminina", f"{mai:.0f}%", delta(mai, mai_ant, pp=True))
k[4].metric("Fornecedores (soma)", f"{atual['qtd_fornecedores'].sum():,}".replace(",", "."))
k[5].metric("Gênero inferido", f"{qualidade['pct_inferido']:.0f}%", help="% de sócios com gênero classificado")

# ---------------- Bloco central ----------------
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("#### Valor contratado por mês")
    mensal = atual.groupby("mes", as_index=False)[["valor_total", "valor_com_socia"]].sum()
    mensal["mes_nome"] = mensal["mes"].map(lambda m: MESES[m - 1])
    fig = go.Figure()
    fig.add_scatter(x=mensal["mes_nome"], y=mensal["valor_total"], name="Valor total",
                    fill="tozeroy", line=dict(color=AREA_CLARA, shape="spline"))
    fig.add_scatter(x=mensal["mes_nome"], y=mensal["valor_com_socia"], name="Empresas com sócias mulheres",
                    fill="tozeroy", line=dict(color=SLATE, shape="spline"))
    st.plotly_chart(estilo(fig, 320), width="stretch")

with c2:
    st.markdown("#### Participação por perfil racial do município")
    st.caption("% do valor com empresas com sócias, por faixa de população preta e parda (Censo 2022)")
    faixa = d.groupby("faixa_racial")[["valor_com_socia", "valor_total"]].sum().reindex(ORDEM_FAIXAS).dropna()
    for nome, linha in faixa.iterrows():
        valor = pct(linha["valor_com_socia"], linha["valor_total"])
        st.markdown(f"**{nome}** — {valor:.0f}%")
        st.progress(min(valor / 100 * 2, 1.0))  # escala x2 para dar leitura visual

# ---------------- Painéis inferiores ----------------
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("#### Modalidades")
    mod = d.groupby("modalidade", as_index=False)["valor_com_socia"].sum().sort_values("valor_com_socia")
    fig = px.bar(mod, x="valor_com_socia", y="modalidade", orientation="h",
                 color_discrete_sequence=[TEAL], labels={"valor_com_socia": "R$", "modalidade": ""})
    st.plotly_chart(estilo(fig, 260), width="stretch")

with p2:
    st.markdown("#### Porte das empresas")
    por = d.groupby("porte", as_index=False)["valor_com_socia"].sum()
    fig = px.pie(por, names="porte", values="valor_com_socia", hole=0.55,
                 color_discrete_sequence=["#2E8BD6", TEAL, "#9B59B6", "#B9C2C9"])
    st.plotly_chart(estilo(fig, 260), width="stretch")

with p3:
    st.markdown("#### Qualidade dos dados")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=qualidade["pct_inferido"], number={"suffix": "%"},
        title={"text": "Sócios com gênero inferido"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": TEAL}},
    ))
    st.plotly_chart(estilo(fig, 220), width="stretch")

st.caption(
    "**Nota metodológica.** Gênero inferido pelo primeiro nome do sócio (base de nomes do IBGE); "
    "nomes ambíguos ficam como indeterminados. Raça representada pelo contexto territorial "
    "(% de população preta e parda do município, Censo 2022), sem classificar pessoas ou empresas. "
    "Fontes: PNCP, Receita Federal (CNPJ) e IBGE. Apenas dados agregados."
)
