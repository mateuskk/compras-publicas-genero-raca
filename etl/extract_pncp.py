"""Extrai contratos da API de Consulta do PNCP e salva em Parquet bruto.

Uso:
    python etl/extract_pncp.py --inicio 20240101 --fim 20240131

Documentação: https://pncp.gov.br/api/consulta/swagger-ui/index.html
Confira no Swagger os nomes exatos dos parâmetros e campos antes de rodar o recorte completo.
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratos"
SAIDA = Path("data/raw/pncp")
TAMANHO_PAGINA = 500


def buscar_pagina(data_ini: str, data_fim: str, pagina: int, tentativas: int = 5) -> dict:
    params = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": pagina,
        "tamanhoPagina": TAMANHO_PAGINA,
    }
    for tentativa in range(1, tentativas + 1):
        try:
            r = requests.get(BASE_URL, params=params, timeout=60)
            if r.status_code == 204:
                return {"data": [], "totalPaginas": 0}
            r.raise_for_status()
            return r.json()
        except requests.RequestException as erro:
            espera = 2 ** tentativa
            print(f"  erro na página {pagina} ({erro}); nova tentativa em {espera}s")
            time.sleep(espera)
    raise RuntimeError(f"Falha ao baixar página {pagina} de {data_ini}-{data_fim}")


def extrair_periodo(data_ini: str, data_fim: str) -> pd.DataFrame:
    primeira = buscar_pagina(data_ini, data_fim, 1)
    registros = list(primeira.get("data", []))
    total = primeira.get("totalPaginas", 1) or 1
    for pagina in range(2, total + 1):
        registros.extend(buscar_pagina(data_ini, data_fim, pagina).get("data", []))
        time.sleep(0.3)  # gentileza com a API
    return pd.json_normalize(registros)


def dias(inicio: str, fim: str, passo: int = 7):
    """Quebra o período em janelas pequenas (extração incremental)."""
    d = datetime.strptime(inicio, "%Y%m%d")
    f = datetime.strptime(fim, "%Y%m%d")
    while d <= f:
        j = min(d + timedelta(days=passo - 1), f)
        yield d.strftime("%Y%m%d"), j.strftime("%Y%m%d")
        d = j + timedelta(days=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inicio", required=True, help="AAAAMMDD")
    parser.add_argument("--fim", required=True, help="AAAAMMDD")
    args = parser.parse_args()

    SAIDA.mkdir(parents=True, exist_ok=True)
    for ini, fim in dias(args.inicio, args.fim):
        arquivo = SAIDA / f"contratos_{ini}_{fim}.parquet"
        if arquivo.exists():
            print(f"já existe, pulando: {arquivo.name}")
            continue
        print(f"baixando {ini} a {fim}...")
        df = extrair_periodo(ini, fim)
        df.to_parquet(arquivo, index=False)
        print(f"  {len(df)} contratos salvos")


if __name__ == "__main__":
    main()
