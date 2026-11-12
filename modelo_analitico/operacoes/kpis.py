"""KPIs genéricos: medidas agregadas e razões entre elas, para qualquer agrupamento."""
import numpy as np
import pandas as pd

from ..utilitarios import fmt, rot


def kpis(d, cfg, por):
    """Calcula todos os KPIs de cfg.medidas e cfg.razoes agrupando por uma ou mais colunas."""
    g = d.groupby(por, observed=True).agg(**{n: pd.NamedAgg(c, f) for n, (c, f, _) in cfg.medidas.items()})
    for nome, (num, den, _) in cfg.razoes.items():
        g[nome] = g[num] / g[den]
    g["participacao"] = g[cfg.kpi_principal] / g[cfg.kpi_principal].sum()
    return g.replace([np.inf, -np.inf], np.nan)


def formula(cfg, nome):
    if nome in cfg.medidas:
        coluna, agg, _ = cfg.medidas[nome]
        return f"{agg}({coluna})"
    num, den, _ = cfg.razoes[nome]
    return f"{num} ÷ {den}"


def tabela_kpis(cfg):
    linhas = [(rot(n), formula(cfg, n), cfg.formato[n]) for n in [*cfg.medidas, *cfg.razoes]]
    linhas.append(("Participação", f"{cfg.kpi_principal} do segmento ÷ total", "pct"))
    return pd.DataFrame(linhas, columns=["KPI", "Fórmula", "Formato"])


def formatar(k, cfg, cols=None):
    """Versão legível (texto no padrão brasileiro) de uma tabela de KPIs."""
    return k[cols or list(k.columns)].apply(
        lambda s: s.map(lambda v: fmt(v, cfg.formato.get(s.name, "num"), cfg.moeda)))
