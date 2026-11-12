"""Diagnóstico de qualidade, outliers e relatório antes × depois."""
import numpy as np
import pandas as pd
from IPython.display import display

from ..utilitarios import fmt
from .limpeza import para_data


def n_viola(d, expr):
    """Quantidade de linhas que satisfazem a expressão de invalidez."""
    return int(d.query(expr, engine="python").shape[0])


def diagnostico(d, cfg):
    display(pd.DataFrame({"tipo": d.dtypes.astype(str), "nulos": d.isna().sum(),
                          "% nulos": (d.isna().mean() * 100).round(1), "únicos": d.nunique()}))
    dup = int(d.duplicated().sum())
    print(f"Linhas duplicadas (excedentes): {dup}")
    if cfg.id:
        rep = int(d[cfg.id].duplicated().sum())
        print(f"IDs repetidos (excedentes): {rep} | repetidos que NÃO são cópia exata: {rep - dup}")
    if cfg.data:
        dt = para_data(d[cfg.data], cfg.dia_primeiro)
        fora = int((~dt.between(*cfg.periodo)).sum()) if cfg.periodo else 0
        print(f"Datas: {dt.min():%d/%m/%Y} a {dt.max():%d/%m/%Y} | inválidas: {int(dt.isna().sum())} | fora do período esperado: {fora}")
    if cfg.regras:
        print("\nRegras de negócio (linhas inválidas):")
        for nome, expr in cfg.regras.items():
            print(f"  {n_viola(d, expr):>6}  {nome}")


def outliers(d, col, grupo, z_limite=3, iqr_fator=1.5):
    """Outliers por z-score e IQR calculados dentro de cada grupo (compara cada linha com o próprio grupo)."""
    def resumo(x):
        x = x.dropna()
        z = ((x - x.mean()) / x.std()).abs()
        q1, q3 = x.quantile([.25, .75])
        i = q3 - q1
        return pd.Series({"n": len(x), "média": x.mean(), "mediana": x.median(), "mín": x.min(), "máx": x.max(),
                          "assimetria": x.skew(), "outliers_z": int((z > z_limite).sum()),
                          "outliers_iqr": int(((x < q1 - iqr_fator * i) | (x > q3 + iqr_fator * i)).sum())})
    return pd.DataFrame({g: resumo(x) for g, x in d.groupby(grupo)[col]}).T.round(2)


def relatorio_qualidade(antes, depois, cfg):
    itens = {"Linhas": (len(antes), len(depois), "num"),
             "Linhas duplicadas": (antes.duplicated().sum(), depois.duplicated().sum(), "num"),
             "Células nulas": (antes.isna().sum().sum(), depois.isna().sum().sum(), "num")}
    for nome, expr in cfg.regras.items():
        itens[nome] = (n_viola(antes, expr), n_viola(depois, expr), "num")
    if "flag_ajuste" in depois:
        itens["Linhas ajustadas por regra do caso"] = (0, depois["flag_ajuste"].sum(), "num")
    for c in cfg.conferir:
        itens[f"Soma de {c}"] = (antes[c].sum() if c in antes else np.nan, depois[c].sum() if c in depois else np.nan, "moeda")
    return pd.DataFrame([[k, fmt(x, t, cfg.moeda), fmt(y, t, cfg.moeda)] for k, (x, y, t) in itens.items()],
                        columns=["Item", "Antes", "Depois"])
