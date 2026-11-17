"""Gera dados SINTÉTICOS no mesmo formato da view mv_painel, para desenvolver o
dashboard antes do banco estar pronto. Não são dados reais.

Uso: python app/gerar_amostra.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

municipios = [
    ("Município A", "até 30%"), ("Município B", "até 30%"),
    ("Município C", "30% a 50%"), ("Município D", "30% a 50%"),
    ("Município E", "50% a 70%"), ("Município F", "50% a 70%"),
    ("Município G", "acima de 70%"), ("Município H", "acima de 70%"),
]
orgaos = ["Órgão 1", "Órgão 2", "Órgão 3"]
modalidades = ["Pregão", "Dispensa", "Concorrência", "Inexigibilidade"]
portes = ["MEI", "ME", "EPP", "Demais"]
base_socia = {"até 30%": 0.31, "30% a 50%": 0.28, "50% a 70%": 0.24, "acima de 70%": 0.19}

linhas = []
for ano in (2022, 2023, 2024):
    for mes in range(1, 13):
        for mun, faixa in municipios:
            for orgao in orgaos:
                for mod in modalidades:
                    for porte in portes:
                        valor = float(rng.gamma(2.0, 400_000))
                        p = np.clip(base_socia[faixa] + rng.normal(0, 0.05) + {2022: -0.02, 2023: 0, 2024: 0.02}[ano], 0, 1)
                        linhas.append({
                            "uf": "XX", "municipio": mun, "faixa_racial": faixa,
                            "ano": ano, "mes": mes, "orgao": orgao,
                            "modalidade": mod, "porte": porte,
                            "qtd_contratos": int(rng.integers(1, 6)),
                            "qtd_fornecedores": int(rng.integers(1, 4)),
                            "valor_total": round(valor, 2),
                            "valor_com_socia": round(valor * p, 2),
                            "valor_maioria_feminina": round(valor * p * 0.45, 2),
                        })

saida = Path(__file__).parent / "sample" / "painel.csv"
saida.parent.mkdir(exist_ok=True)
pd.DataFrame(linhas).to_csv(saida, index=False)
print(f"{len(linhas)} linhas sintéticas em {saida}")
