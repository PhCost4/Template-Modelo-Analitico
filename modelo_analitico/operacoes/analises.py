"""Leituras automáticas e testes estatísticos."""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from ..utilitarios import fmt, rot
from .kpis import kpis


def destaques(k, cfg, m):
    """Resumo em texto simples: líder, último, amplitude e concentração."""
    s = k[m].dropna().sort_values(ascending=False)
    t = cfg.formato[m]
    nome = lambda i: " · ".join(map(str, i if isinstance(i, tuple) else (i,)))
    linha = (f"{rot(m)}: maior = {nome(s.index[0])} ({fmt(s.iloc[0], t, cfg.moeda)}); "
             f"menor = {nome(s.index[-1])} ({fmt(s.iloc[-1], t, cfg.moeda)})")
    if s.iloc[-1] > 0:
        linha += f"; amplitude {s.iloc[0] / s.iloc[-1]:.1f}x"
    if m in cfg.medidas and cfg.medidas[m][1] == "sum":
        linha += f"; o líder concentra {fmt(s.iloc[0] / s.sum(), 'pct')} do total"
    print(linha)


def teste_chi2(d, cfg, dim):
    """O sucesso (flag) depende do segmento? Qui-quadrado com V de Cramér."""
    if not cfg.sucesso:
        return print("Sem coluna de sucesso (sucesso=None).")
    tab = pd.crosstab(d[dim], d["flag"])
    chi2, p, _, _ = chi2_contingency(tab)
    v = np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape) - 1)))
    print(f"Qui-quadrado = {chi2:.1f} | p-valor = {p:.2e} | V de Cramér = {v:.2f} → "
          + ("diferença significativa (p < 0,05)" if p < 0.05 else "sem diferença significativa"))


def ultimo_vs_anteriores(d, cfg, dim, m):
    """Último período contra a média dos anteriores, por segmento."""
    ult = d["periodo"].max()
    atual, antes = d[d["periodo"] == ult], d[d["periodo"] < ult]
    base = kpis(antes, cfg, dim)[m] / (antes["periodo"].nunique() if m in cfg.medidas else 1)  # somas viram média por período
    c = pd.DataFrame({"média_anteriores": base, ult: kpis(atual, cfg, dim)[m]})
    c["variação"] = c[ult] / c["média_anteriores"] - 1
    return c
