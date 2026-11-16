"""Inferência de gênero pelo primeiro nome.

Usa uma tabela de frequência de nomes por sexo derivada do Censo (IBGE).
Fonte sugerida: dataset "Gênero dos Nomes" do Brasil.IO (baseado no IBGE),
salvo em data/ref/nomes.csv com as colunas:
    first_name, frequency_female, frequency_male

A inferência é feita só no agregado: o nome completo do sócio não é guardado.
"""
from __future__ import annotations

import unicodedata

import pandas as pd

LIMIAR = 0.90  # proporção mínima de um sexo para classificar o nome


def normalizar(nome: str | None) -> str:
    if not nome or not isinstance(nome, str):
        return ""
    primeiro = nome.strip().split(" ")[0]
    sem_acento = unicodedata.normalize("NFKD", primeiro).encode("ascii", "ignore").decode()
    return sem_acento.upper()


def carregar_tabela(caminho: str = "data/ref/nomes.csv") -> pd.DataFrame:
    t = pd.read_csv(caminho)
    t["first_name"] = t["first_name"].map(normalizar)
    t[["frequency_female", "frequency_male"]] = t[["frequency_female", "frequency_male"]].fillna(0)
    total = t["frequency_female"] + t["frequency_male"]
    t["prop_f"] = t["frequency_female"] / total.where(total > 0)
    return t.groupby("first_name", as_index=False)["prop_f"].mean()


def inferir(socios: pd.DataFrame, tabela: pd.DataFrame, coluna_nome: str = "nome_socio") -> pd.DataFrame:
    """Adiciona primeiro_nome, genero_inferido ('F','M','indeterminado') e confianca_inferencia."""
    df = socios.copy()
    df["primeiro_nome"] = df[coluna_nome].map(normalizar)
    df = df.merge(tabela, how="left", left_on="primeiro_nome", right_on="first_name")
    df["genero_inferido"] = "indeterminado"
    df.loc[df["prop_f"] >= LIMIAR, "genero_inferido"] = "F"
    df.loc[df["prop_f"] <= 1 - LIMIAR, "genero_inferido"] = "M"
    df["confianca_inferencia"] = df["prop_f"].where(df["genero_inferido"] == "F", 1 - df["prop_f"]).round(3)
    df.loc[df["genero_inferido"] == "indeterminado", "confianca_inferencia"] = None
    return df.drop(columns=["first_name", "prop_f", coluna_nome])


if __name__ == "__main__":
    tabela = pd.DataFrame(
        {"first_name": ["MARIA", "JOAO", "ARIEL"], "prop_f": [0.996, 0.004, 0.55]}
    )
    teste = pd.DataFrame({"nome_socio": ["Maria da Silva", "João Souza", "Ariel Lima", "Xyz"]})
    print(inferir(teste, tabela))
