"""Dashboard: Compras Públicas, Gênero e Raça (ODS 5 e ODS 18).

Visual baseado na referência escolhida pelo grupo: barra superior, faixa de indicadores,
gráfico de área com painel de barras ao lado e três painéis inferiores.

Rodar localmente (da raiz do repositório):  streamlit run app/app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import carregar_painel, carregar_qualidade

# ---------------- Paleta da referência ----------------
FUNDO = "#EEF0F2"
PAINEL = "#FFFFFF"
LINHA = "#DDE2E6"
LINHA_SUAVE = "#E9EDF0"
TINTA = "#2E3E4C"
TEXTO = "#3F4E5C"
SUAVE = "#5F6F7D"
TITULO = "#3E5A70"
NUMERO = "#4A6075"
TEAL = "#19B394"
TEAL_TEXTO = "#0E8A70"
AREA_CLARA = "#5DD0B4"
SLATE = "#3E7A86"
VERMELHO = "#C93A2F"
CORES_PORTE = ["#2E8BD6", TEAL, "#9B59B6", "#B9C2C9"]
FONTE = "Open Sans, Segoe UI, sans-serif"

ORDEM_FAIXAS = ["até 30%", "30% a 50%", "50% a 70%", "acima de 70%"]
ROTULO_FAIXA = {"até 30%": "Até 30%", "30% a 50%": "30% a 50%", "50% a 70%": "50% a 70%", "acima de 70%": "Acima de 70%"}
ORDEM_PORTE = ["MEI", "ME", "EPP", "Demais"]
NOME_PORTE = {"MEI": "MEI", "ME": "Microempresa", "EPP": "EPP", "Demais": "Demais"}
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

st.set_page_config(page_title="Compras Públicas · Gênero e Raça", layout="wide", initial_sidebar_state="collapsed")

# ---------------- CSS (cores fixas: igual em tema claro ou escuro) ----------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
:root {{ color-scheme: light; }}
html, body, .stApp, [data-testid="stAppViewContainer"] {{ background: {FUNDO} !important; color: {TEXTO} !important; font-family: {FONTE}; }}
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3,
.stApp div[data-testid="stMarkdownContainer"] {{ color: {TEXTO}; font-family: {FONTE}; }}
[data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}
div[data-testid="stToolbar"], div[data-testid="stDecoration"] {{ display: none !important; }}
.block-container {{ padding: 0.9rem 1.4rem 0.8rem 1.4rem; max-width: 1800px; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.75rem; }}

/* Barra lateral e filtros */
section[data-testid="stSidebar"] {{ background: {PAINEL} !important; border-right: 1px solid {LINHA}; }}
section[data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]) {{ color: {TEXTO} !important; }}
section[data-testid="stSidebar"] [data-testid="stIconMaterial"] {{ color: {SUAVE} !important; }}
section[data-testid="stSidebar"] button {{ background: transparent !important; }}
section[data-testid="stSidebar"] label p {{ font-weight: 600; font-size: 0.85rem; }}
[data-testid="stSelectbox"] [role="group"], [data-testid="stMultiSelect"] [role="group"] {{
    background: {PAINEL} !important; border: 1px solid #C3CCD2 !important; border-radius: 4px; }}
[data-testid="stMultiSelect"] [role="group"] *, [data-testid="stSelectbox"] [role="group"] * {{ opacity: 1 !important; }}
[data-testid="stMultiSelect"] [role="group"] div {{ color: {SUAVE} !important; }}
[data-testid="stMultiSelect"] input::placeholder {{ color: {SUAVE} !important; opacity: 1 !important; }}
[role="listbox"], [role="option"], [role="dialog"] {{ background: {PAINEL} !important; color: {TEXTO} !important; }}
[role="option"]:hover, [role="option"][aria-selected="true"] {{ background: {LINHA_SUAVE} !important; }}
*:focus-visible {{ outline: 2px solid {TEAL} !important; outline-offset: 2px; }}

/* Painéis brancos (st.container(border=True)) */
div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {PAINEL} !important; border: 1px solid {LINHA} !important; border-radius: 3px;
    padding: 0.6rem 1rem 0.5rem 1rem !important; gap: 0.3rem !important;
}}

/* Barra superior (container com botão de menu) */
.st-key-topo {{ padding: 0.35rem 1rem !important; border-radius: 0 !important; }}
.st-key-topo div[data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
.dir-topo {{ display: flex; justify-content: flex-end; align-items: center; gap: 14px; font-size: 14px; font-weight: 600; }}
.dir-topo span {{ color: {TINTA} !important; }}
.st-key-menu button, [data-testid="stPopover"] button {{ background: transparent !important; border: none !important;
    box-shadow: none !important; min-height: 40px; }}
[data-testid="stPopover"] button [data-testid="stIconMaterial"] {{ color: #3E6B8A !important; font-size: 26px !important; }}
[data-testid="stPopover"] button:hover {{ background: {LINHA_SUAVE} !important; }}
[data-testid="stPopover"] button > div > div:last-child:not(:first-child) {{ display: none !important; }}
[data-testid="stPopoverBody"] {{ background: {PAINEL} !important; border: 1px solid {LINHA} !important; min-width: 340px; }}
[data-testid="stPopoverBody"] *:not([data-testid="stIconMaterial"]) {{ color: {TEXTO} !important; }}
[data-testid="stPopoverBody"] label p {{ font-weight: 600; font-size: 0.85rem; }}
section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] {{ display: none !important; }}
/* Barra superior antiga */
.topo {{ background: {PAINEL}; border: 1px solid {LINHA}; height: 54px; padding: 0 18px;
        display: flex; align-items: center; justify-content: space-between; }}
.topo .marca {{ display: flex; align-items: center; gap: 14px; font-weight: 700; font-size: 16px; color: {TINTA} !important; }}
.topo .dir {{ display: flex; align-items: center; gap: 14px; font-size: 14px; font-weight: 600; color: {TINTA} !important; }}
.selo {{ background: #FFF4E5; color: #7A4300 !important; border: 1px solid #F0CC92; border-radius: 999px; padding: 3px 12px; font-size: 12px; font-weight: 600; }}

/* Faixa de indicadores */
.kpis {{ background: {PAINEL}; border: 1px solid {LINHA}; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); }}
.kpi {{ padding: 10px 20px 12px 20px; position: relative; }}
.kpi + .kpi::before {{ content: ""; position: absolute; left: 0; top: 18%; height: 64%; border-left: 2px solid {LINHA}; }}
.kpi .rot {{ font-size: 13px; color: {SUAVE} !important; display: flex; align-items: center; gap: 6px; }}
.kpi .val {{ font-size: 32px; font-weight: 600; color: {NUMERO} !important; line-height: 1.25; font-variant-numeric: tabular-nums; }}
.kpi .val.destaque {{ color: {TEAL_TEXTO} !important; font-weight: 700; }}
.kpi .var {{ font-size: 12px; color: {SUAVE} !important; }}
.sobe {{ color: {TEAL_TEXTO} !important; font-weight: 700; }}
.desce {{ color: {VERMELHO} !important; font-weight: 700; }}
@media (max-width: 1100px) {{ .kpis {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
@media (max-width: 640px) {{ .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .kpi .val {{ font-size: 24px; }} }}

/* Cabeçalho dos painéis */
.cab {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
       border-bottom: 1px solid {LINHA_SUAVE}; padding-bottom: 8px; margin-bottom: 4px; }}
.cab .t {{ font-size: 19px; font-weight: 400; color: {TITULO} !important; margin: 0; }}
.cab .t small {{ font-size: 13px; color: {SUAVE} !important; margin-left: 6px; }}
.cab .icones {{ color: #A3AEB7 !important; font-size: 13px; letter-spacing: 8px; }}
.pilula {{ border: 1px solid {LINHA}; border-radius: 3px; padding: 3px 10px; font-size: 12px; color: {SUAVE} !important; white-space: nowrap; }}
.leg {{ font-size: 12px !important; color: {SUAVE} !important; line-height: 1.5 !important; }}
.leg i {{ display: inline-block; width: 10px; height: 10px; margin: 0 5px 0 12px; vertical-align: -1px; }}

/* Barras de progresso (painel lateral) */
.prog {{ margin: 12px 0 0 0; }}
.prog .l {{ display: flex; justify-content: space-between; font-size: 13px; color: {TEXTO} !important; }}
.prog .tr {{ height: 9px; background: {LINHA_SUAVE}; margin-top: 5px; }}
.prog .ch {{ height: 9px; background: {TEAL}; }}

/* Barras com valor grande (modalidades) */
.hb {{ display: grid; grid-template-columns: 104px 1fr 96px; align-items: center; gap: 10px; margin: 13px 0; }}
.hb .n {{ font-size: 12.5px; color: {TEXTO} !important; }}
.hb .tr {{ height: 15px; background: {LINHA_SUAVE}; }}
.hb .ch {{ height: 15px; background: {TEAL}; }}
.hb .v {{ font-size: 17px !important; white-space: nowrap; color: {TEXTO} !important; text-align: right; font-variant-numeric: tabular-nums; }}

/* Legenda da rosca */
.tab {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.tab th {{ text-align: left; font-weight: 600; color: {TITULO} !important; padding: 4px 0 8px 0; border: none; }}
.tab td {{ padding: 6px 0; color: {TEXTO} !important; border: none; white-space: nowrap; }}
.tab td:last-child, .tab th:last-child {{ text-align: right; }}
.tab i {{ display: inline-block; width: 11px; height: 11px; margin-right: 8px; vertical-align: -1px; }}

/* Qualidade */
.lista {{ list-style: none; padding: 0 !important; margin: 10px 0 !important; }}
.lista li {{ color: {TEXTO} !important; font-size: 13px !important; line-height: 2.1 !important; margin: 0 !important; }}
.lista b {{ color: {TEAL} !important; margin-right: 8px; }}
.medidor {{ border: 1px solid #9FD8EC; border-radius: 4px; text-align: center; padding: 6px 4px 0 4px; }}
.medidor .t {{ font-size: 14px; font-weight: 600; color: {TITULO} !important; }}

/* Barra lateral: método */
.lat p {{ font-size: 12.5px; color: {SUAVE} !important; line-height: 1.45; margin: 0.35rem 0; }}
.lat b {{ color: {TEXTO} !important; }}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------- Auxiliares ----------------
def brl(valor: float) -> str:
    if valor >= 1e9:
        return f"R$ {valor / 1e9:.1f} bi".replace(".", ",")
    if valor >= 1e6:
        return f"R$ {valor / 1e6:.0f} mi"
    if valor >= 1e3:
        return f"R$ {valor / 1e3:.0f} mil"
    return f"R$ {valor:.0f}"


def milhar(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def pct(parte: float, total: float) -> float:
    return 100 * parte / total if total else 0.0


def variacao(atual: float, anterior: float | None, pp: bool = False) -> str:
    if anterior is None or (not pp and not anterior):
        return "sem ano anterior"
    dif = atual - anterior if pp else pct(atual - anterior, anterior)
    if abs(dif) < 0.5:
        return "estável vs. ano anterior"
    classe, seta = ("sobe", "▲") if dif > 0 else ("desce", "▼")
    return f'<span class="{classe}">{seta} {abs(dif):.0f}{" p.p." if pp else "%"}</span> vs. ano anterior'


ICONE = {
    "dinheiro": '<path d="M2 4h12v8H2z M5 8h6" />',
    "doc": '<path d="M4 2h6l3 3v9H4z" />',
    "pessoa": '<circle cx="8" cy="6" r="3"/><path d="M3 14c1-3 9-3 10 0"/>',
    "predio": '<path d="M2 14V6l6-4 6 4v8z"/>',
    "alerta": '<circle cx="8" cy="8" r="6"/><path d="M8 5v4M8 11v.5"/>',
}


def icone(nome: str) -> str:
    return (f'<svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true" fill="none" '
            f'stroke="{SUAVE}" stroke-width="1.5">{ICONE[nome]}</svg>')


def cabecalho(titulo: str, sub: str = "", direita: str = '<span class="icones" aria-hidden="true">⌃✕</span>') -> None:
    sub_html = f"<small>{sub}</small>" if sub else ""
    st.markdown(f'<div class="cab"><p class="t">{titulo}{sub_html}</p>{direita}</div>', unsafe_allow_html=True)


def estilo(fig: go.Figure, altura: int) -> go.Figure:
    fig.update_layout(
        height=altura, margin=dict(l=4, r=8, t=6, b=4), plot_bgcolor=PAINEL, paper_bgcolor=PAINEL,
        showlegend=False, font=dict(family=FONTE, color=TEXTO, size=12),
        hoverlabel=dict(bgcolor=PAINEL, bordercolor=LINHA, font=dict(family=FONTE, color=TEXTO)),
    )
    fig.update_layout(dragmode=False)
    fig.update_xaxes(showgrid=False, linecolor=LINHA, tickfont=dict(color=SUAVE), automargin=True, zeroline=False, fixedrange=True)
    fig.update_yaxes(gridcolor="#EEF1F3", tickfont=dict(color=SUAVE), automargin=True, zeroline=False, fixedrange=True)
    return fig


def grafico(fig: go.Figure) -> None:
    st.plotly_chart(fig, config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False},
                    width="stretch", theme=None)


# ---------------- Dados e filtros ----------------
df, eh_amostra = carregar_painel()
qualidade = carregar_qualidade()

# ---------------- Barra superior com menu de filtros ----------------
anos = sorted(df["ano"].unique())
with st.container(border=True, key="topo"):
    c_menu, c_tit, c_dir = st.columns([0.035, 0.62, 0.345], vertical_alignment="center", gap="small")
    with c_menu:
        with st.popover("", icon=":material/menu:", help="Abrir filtros", key="menu"):
            st.markdown(f'<p style="font-size:1.05rem; font-weight:600; color:{TITULO}; margin:0">Filtros</p>',
                        unsafe_allow_html=True)
            f_ano = st.selectbox("Ano", anos, index=len(anos) - 1)
            f_uf = st.multiselect("UF", sorted(df["uf"].unique()), placeholder="Todas")
            f_orgao = st.multiselect("Órgão contratante", sorted(df["orgao"].dropna().unique()), placeholder="Todos")
            f_mod = st.multiselect("Modalidade", sorted(df["modalidade"].unique()), placeholder="Todas")
            f_porte = st.multiselect("Porte da empresa", ORDEM_PORTE, format_func=NOME_PORTE.get, placeholder="Todos")
            st.markdown(
                f"""<div class="lat" style="border-top:1px solid {LINHA}; margin-top:0.6rem; padding-top:0.6rem">
<p style="font-weight:600; color:{TITULO}">Como ler este painel</p>
<p><b>Gênero.</b> Inferido pelo primeiro nome do sócio, com a frequência de nomes do IBGE. Nomes usados por
homens e mulheres ficam fora do cálculo.</p>
<p><b>Raça.</b> Não é atribuída a pessoas nem a empresas. Os municípios são comparados pelo percentual de
população preta e parda do Censo 2022.</p>
<p><b>Privacidade.</b> Só totais agregados. Fontes: PNCP, Receita Federal e IBGE.</p></div>""",
                unsafe_allow_html=True,
            )
    with c_tit:
        st.markdown(f'<p style="font-weight:700; font-size:16px; color:{TINTA}; margin:0">Compras Públicas · Gênero e Raça</p>',
                    unsafe_allow_html=True)
    with c_dir:
        selo = '<span class="selo">Dados sintéticos de exemplo</span>' if eh_amostra else ""
        st.markdown(f'<div class="dir-topo">{selo}<span>ODS 5 · ODS 18</span></div>', unsafe_allow_html=True)

filtro = pd.Series(True, index=df.index)
for coluna, escolha in [("uf", f_uf), ("orgao", f_orgao), ("modalidade", f_mod), ("porte", f_porte)]:
    if escolha:
        filtro &= df[coluna].isin(escolha)
base = df[filtro]
atual = base[base["ano"] == f_ano]
anterior = base[base["ano"] == f_ano - 1]
tem_ant = not anterior.empty

if atual.empty:
    st.info("Nenhum contrato para esses filtros. Remova algum filtro na barra lateral.")
    st.stop()

# ---------------- Indicadores ----------------
tot = atual["valor_total"].sum()
tot_ant = anterior["valor_total"].sum() if tem_ant else None
soc = pct(atual["valor_com_socia"].sum(), tot)
soc_ant = pct(anterior["valor_com_socia"].sum(), tot_ant) if tem_ant else None
mai = pct(atual["valor_maioria_feminina"].sum(), tot)
mai_ant = pct(anterior["valor_maioria_feminina"].sum(), tot_ant) if tem_ant else None
ctr = atual["qtd_contratos"].sum()
ctr_ant = anterior["qtd_contratos"].sum() if tem_ant else None
forn = atual["qtd_fornecedores"].sum()
forn_ant = anterior["qtd_fornecedores"].sum() if tem_ant else None
indet = 100 - qualidade["pct_inferido"]

kpis = [
    ("dinheiro", "Valor contratado", brl(tot), "", variacao(tot, tot_ant)),
    ("doc", "Contratos", milhar(ctr), "", variacao(ctr, ctr_ant)),
    ("pessoa", "% com sócia mulher", f"{soc:.0f}%", "destaque", variacao(soc, soc_ant, pp=True)),
    ("pessoa", "% maioria feminina", f"{mai:.0f}%", "", variacao(mai, mai_ant, pp=True)),
    ("predio", "Fornecedores", milhar(forn), "", variacao(forn, forn_ant)),
    ("alerta", "Gênero indeterminado", f"{indet:.0f}%", "", "dos sócios do recorte"),
]
st.markdown(
    '<div class="kpis">' + "".join(
        f'<div class="kpi"><div class="rot">{icone(i)}{r}</div><div class="val {c}">{v}</div><div class="var">{d}</div></div>'
        for i, r, v, c, d in kpis
    ) + "</div>",
    unsafe_allow_html=True,
)

# ---------------- Bloco central: área + barras de progresso ----------------
with st.container(border=True):
    esq, dir_ = st.columns([2.3, 1], gap="large")
    with esq:
        cabecalho("Valor contratado por mês", "total × empresas com sócias mulheres",
                  direita=f'<span class="pilula">Jan a Dez de {f_ano}</span>')
        mensal = (atual.groupby("mes")[["valor_total", "valor_com_socia"]].sum()
                  .reindex(range(1, 13), fill_value=0))
        x = [MESES[m - 1] for m in mensal.index]
        fig = go.Figure()
        fig.add_scatter(x=x, y=mensal["valor_total"] / 1e6, mode="lines", fill="tozeroy",
                        line=dict(color=AREA_CLARA, shape="spline", width=1.5), fillcolor="rgba(93,208,180,0.70)",
                        hovertemplate="%{x}: R$ %{y:.0f} mi<extra>Valor total</extra>")
        fig.add_scatter(x=x, y=mensal["valor_com_socia"] / 1e6, mode="lines", fill="tozeroy",
                        line=dict(color=SLATE, shape="spline", width=1.5), fillcolor="rgba(62,122,134,0.85)",
                        hovertemplate="%{x}: R$ %{y:.0f} mi<extra>Com sócias</extra>")
        fig.update_yaxes(tickprefix="R$ ", ticksuffix=" mi", rangemode="tozero")
        fig.update_xaxes(showgrid=True, gridcolor="#F1F3F5")
        grafico(estilo(fig, 255))
        st.markdown(f'<span class="leg"><i style="background:{AREA_CLARA}; margin-left:0"></i>Valor total'
                    f'<i style="background:{SLATE}"></i>Empresas com sócias mulheres</span>', unsafe_allow_html=True)

    with dir_:
        cabecalho("Participação por perfil racial", direita="")
        st.markdown('<span class="leg">% do valor para empresas com sócias, por faixa de população preta e '
                    "parda do município (Censo 2022)</span>", unsafe_allow_html=True)
        faixa = atual.groupby("faixa_racial")[["valor_com_socia", "valor_total"]].sum().reindex(ORDEM_FAIXAS).dropna()
        barras = "".join(
            f'<div class="prog"><div class="l"><span>{ROTULO_FAIXA[n]}</span><b>{pct(r["valor_com_socia"], r["valor_total"]):.0f}%</b></div>'
            f'<div class="tr"><div class="ch" style="width:{min(2 * pct(r["valor_com_socia"], r["valor_total"]), 100):.0f}%"></div></div></div>'
            for n, r in faixa.iterrows()
        )
        st.markdown(barras + '<p class="leg" style="margin-top:10px">Escala das barras: 0 a 50%.</p>', unsafe_allow_html=True)

# ---------------- Painéis inferiores ----------------
p1, p2, p3 = st.columns(3, gap="medium")

with p1:
    with st.container(border=True):
        cabecalho("Modalidades")
        mod = atual.groupby("modalidade")["valor_com_socia"].sum().sort_values(ascending=False)
        maximo = mod.max() or 1
        linhas = "".join(
            f'<div class="hb"><span class="n">{n}</span><div class="tr"><div class="ch" style="width:{100 * v / maximo:.0f}%"></div></div>'
            f'<span class="v">{brl(v)}</span></div>'
            for n, v in mod.items()
        )
        st.markdown(f'<p style="font-size:13px; font-weight:600; color:{TITULO}; margin:4px 0 2px 0">'
                    f"Valor para empresas com sócias</p>{linhas}", unsafe_allow_html=True)

with p2:
    with st.container(border=True):
        cabecalho("Porte das empresas")
        por = atual.groupby("porte")["valor_com_socia"].sum().reindex(ORDEM_PORTE).fillna(0)
        total_por = por.sum() or 1
        g, leg = st.columns([1, 1.1])
        with g:
            fig = go.Figure(go.Pie(labels=[NOME_PORTE[p] for p in por.index], values=por.values, hole=0.5, sort=False,
                                   direction="clockwise", marker=dict(colors=CORES_PORTE, line=dict(color="white", width=2)),
                                   textinfo="none", hovertemplate="%{label}: %{percent}<extra></extra>"))
            fig = estilo(fig, 175)
            fig.update_layout(margin=dict(l=0, r=0, t=4, b=4))
            grafico(fig)
        with leg:
            linhas = "".join(f'<tr><td><i style="background:{c}"></i>{NOME_PORTE[p]}</td><td>{100 * v / total_por:.0f}%</td></tr>'
                             for (p, v), c in zip(por.items(), CORES_PORTE))
            st.markdown(f'<table class="tab"><tr><th>Porte</th><th>% do valor</th></tr>{linhas}</table>', unsafe_allow_html=True)

with p3:
    with st.container(border=True):
        cabecalho("Qualidade dos dados")
        lst, med = st.columns([1, 1.05])
        with lst:
            st.markdown(
                '<ul class="lista"><li><b>●</b>Gênero pelo nome</li><li><b>●</b>Raça por município</li>'
                "<li><b>●</b>Fontes: PNCP e CNPJ</li><li><b>●</b>Só dados agregados</li></ul>",
                unsafe_allow_html=True,
            )
        with med:
            st.markdown(f'<p style="text-align:center; font-size:14px; font-weight:600; color:{TITULO}; margin:6px 0 0 0">'
                        "Confiança do gênero</p>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=qualidade["pct_inferido"],
                number=dict(suffix="%", font=dict(size=22, color=TEAL_TEXTO, family=FONTE)),
                gauge=dict(axis=dict(range=[0, 100], visible=False), bar=dict(color=TEAL, thickness=0.8),
                           bgcolor=LINHA_SUAVE, borderwidth=0),
            ))
            fig = estilo(fig, 120)
            fig.update_layout(margin=dict(l=14, r=14, t=10, b=0))
            grafico(fig)
