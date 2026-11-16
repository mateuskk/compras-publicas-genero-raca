"""Único ponto de acesso a dados do dashboard.

- Se houver credenciais em st.secrets["postgres"], lê a view mv_painel da Aiven.
- Senão, usa a amostra sintética em app/sample/painel.csv.
Trocar a fonte não muda nada no app.py.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

AMOSTRA = Path(__file__).parent / "sample" / "painel.csv"


def _tem_banco() -> bool:
    try:
        return "postgres" in st.secrets
    except Exception:
        return False


@st.cache_data(ttl=600, show_spinner="Carregando dados...")
def carregar_painel() -> tuple[pd.DataFrame, bool]:
    """Retorna (dados, eh_amostra)."""
    if _tem_banco():
        from sqlalchemy import create_engine

        s = st.secrets["postgres"]
        url = (
            f"postgresql+psycopg2://{s['user']}:{s['password']}@{s['host']}:{s['port']}"
            f"/{s.get('dbname', 'defaultdb')}?sslmode=require"
        )
        df = pd.read_sql("SELECT * FROM mv_painel", create_engine(url))
        return df, False
    return pd.read_csv(AMOSTRA), True


@st.cache_data(ttl=600)
def carregar_qualidade() -> dict:
    if _tem_banco():
        from sqlalchemy import create_engine

        s = st.secrets["postgres"]
        url = (
            f"postgresql+psycopg2://{s['user']}:{s['password']}@{s['host']}:{s['port']}"
            f"/{s.get('dbname', 'defaultdb')}?sslmode=require"
        )
        linha = pd.read_sql("SELECT * FROM vw_qualidade_genero", create_engine(url)).iloc[0]
        return {"pct_inferido": float(linha["pct_inferido"] or 0)}
    return {"pct_inferido": 96.0}
