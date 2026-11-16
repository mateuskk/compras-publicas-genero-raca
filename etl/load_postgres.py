"""Carrega tabelas tratadas (Parquet em data/processed/) no PostgreSQL da Aiven.

Ordem: dimensões primeiro, depois o fato. Ao final atualiza a view do painel.
Uso:
    python etl/load_postgres.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

PROCESSADOS = Path("data/processed")
ORDEM = ["dim_municipio", "dim_orgao", "dim_fornecedor", "dim_socio", "fato_contrato"]


def engine():
    url = (
        f"postgresql+psycopg2://{os.environ['PG_USER']}:{os.environ['PG_PASSWORD']}"
        f"@{os.environ['PG_HOST']}:{os.environ['PG_PORT']}/{os.environ.get('PG_DB', 'defaultdb')}"
        f"?sslmode={os.environ.get('PG_SSLMODE', 'require')}"
    )
    return create_engine(url, pool_pre_ping=True)


def main() -> None:
    eng = engine()
    with eng.begin() as con:
        for tabela in reversed(ORDEM):
            con.execute(text(f"TRUNCATE {tabela} CASCADE"))
    for tabela in ORDEM:
        arquivo = PROCESSADOS / f"{tabela}.parquet"
        if not arquivo.exists():
            print(f"ausente, pulando: {arquivo}")
            continue
        df = pd.read_parquet(arquivo)
        df.to_sql(tabela, eng, if_exists="append", index=False, chunksize=5000, method="multi")
        print(f"{tabela}: {len(df)} linhas")
    with eng.begin() as con:
        con.execute(text("REFRESH MATERIALIZED VIEW mv_painel"))
        tamanho = con.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))")).scalar()
    print(f"Pronto. Tamanho do banco: {tamanho}")


if __name__ == "__main__":
    main()
