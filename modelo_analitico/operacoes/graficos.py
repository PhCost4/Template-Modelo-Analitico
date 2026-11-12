"""Gráficos padronizados (barras, barras agrupadas e evolução temporal)."""
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

from ..utilitarios import compacto, fmt, rot
from .kpis import kpis


def salvar(cfg, arquivo=None):
    plt.tight_layout()
    if arquivo:
        plt.savefig(cfg.pasta_saida / arquivo, dpi=150, bbox_inches="tight")
    plt.show()


def barras(k, cfg, metricas, arquivo=None):
    """Um painel de barras horizontais por métrica, com rótulos formatados."""
    fig, ax = plt.subplots(1, len(metricas), figsize=(5.5 * len(metricas), 4.5), squeeze=False)
    for a, m, cor in zip(ax[0], metricas, sns.color_palette("deep")):
        t = cfg.formato[m]
        k[m].plot.barh(ax=a, color=cor)
        a.invert_yaxis(); a.set_title(rot(m)); a.set_ylabel(""); a.margins(x=0.22)
        a.bar_label(a.containers[0], labels=[fmt(v, t, cfg.moeda) for v in k[m]], padding=3)
        a.xaxis.set_major_formatter(FuncFormatter(lambda x, _, t=t: compacto(x, t, cfg.moeda)))
    salvar(cfg, arquivo)


def cruzar(d, cfg, x, hue, m, titulo="", arquivo=None):
    """Barras agrupadas: métrica m por x e hue, com x ordenado pelo KPI principal."""
    k = kpis(d, cfg, [x, hue]).reset_index()
    t = cfg.formato[m]
    ordem = kpis(d, cfg, x).sort_values(cfg.kpi_principal, ascending=False).index
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(data=k, x=x, y=m, hue=hue, order=ordem, errorbar=None, ax=ax)
    for c in ax.containers:
        ax.bar_label(c, labels=[fmt(v, t, cfg.moeda) for v in c.datavalues], padding=3)
    ax.set_title(titulo or f"{rot(m)} por {x} e {hue}")
    ax.set_xlabel(f"{x} (do maior ao menor {rot(cfg.kpi_principal).lower()})"); ax.set_ylabel(rot(m))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: compacto(v, t, cfg.moeda)))
    sns.despine(); salvar(cfg, arquivo)
    return k.set_index([x, hue])


def evolucao(d, cfg, metricas, arquivo=None):
    """Linhas ao longo dos períodos, duas colunas de painéis."""
    k = kpis(d, cfg, "periodo")
    n = len(metricas); linhas = (n + 1) // 2
    fig, ax = plt.subplots(linhas, 2, figsize=(14, 4 * linhas), squeeze=False)
    for a, m, cor in zip(ax.flat, metricas, sns.color_palette("deep")):
        t = cfg.formato[m]
        k[m].plot(marker="o", ax=a, color=cor); a.set_title(rot(m)); a.set_xlabel("")
        a.yaxis.set_major_formatter(FuncFormatter(lambda v, _, t=t: compacto(v, t, cfg.moeda)))
    for a in ax.flat[n:]:
        a.axis("off")
    salvar(cfg, arquivo)
    return k
