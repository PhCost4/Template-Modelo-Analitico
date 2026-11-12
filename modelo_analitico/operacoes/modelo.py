"""Orquestrador: guarda o estado (bruto, tratada, resultados) e expõe cada etapa em uma linha."""
import sys
import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import display

from ..config import Config
from ..dados import carregar, exportar
from ..utilitarios import fmt, rot
from . import analises, graficos, kpis as kp, limpeza, qualidade


class Modelo:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.resultados = {}                       # tabelas geradas (exportadas ao final)
        self.bruto = self.df = self.tratada = None
        warnings.filterwarnings("ignore")
        np.random.seed(cfg.seed)
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({"figure.figsize": (12, 6), "axes.titlesize": 13})
        cfg.pasta_saida.mkdir(exist_ok=True)
        print(f"Python {sys.version.split()[0]} | pandas {pd.__version__} | numpy {np.__version__} | "
              f"seaborn {sns.__version__} | matplotlib {matplotlib.__version__}")

    # ── carga e exploração ──
    def carregar(self):
        c = self.cfg
        self.bruto = carregar(c.fonte, c.tipo, c.consulta, **c.leitura)    # base bruta, nunca regravada
        self.df = limpeza.tipar(self.bruto, c)
        print("Linhas, colunas:", self.df.shape)
        display(self.df.head()); self.df.info()
        return self.df

    def explorar(self):
        display(self.df.describe(include="all").T)
        for col in self.cfg.dimensoes:
            print(self.df[col].value_counts(dropna=False).to_string(), "\n")

    # ── qualidade e tratamento ──
    def diagnosticar(self):
        c = self.cfg
        qualidade.diagnostico(self.df, c)
        base = self.df.drop_duplicates()
        for col in c.outlier_cols:
            print(f"\nOutliers de {col} por {c.outlier_grupo}:")
            display(qualidade.outliers(base, col, c.outlier_grupo, c.z_limite, c.iqr_fator))
        if c.outlier_cols:
            sns.boxplot(data=base, x=c.outlier_grupo, y=c.outlier_cols[0]); plt.yscale("log")
            plt.title(f"{rot(c.outlier_cols[0])} por {c.outlier_grupo} (escala log)"); plt.xticks(rotation=20); plt.show()

    def tratar(self):
        c = self.cfg
        limpa = limpeza.limpar(self.df, c)
        print(f"Duplicatas removidas: {len(self.df) - len(limpa)}")
        self.tratada = limpeza.preparar(limpa, c)
        limpeza.verificar(self.tratada, c)
        print("Todas as verificações passaram.")
        self.resultados["qualidade"] = qualidade.relatorio_qualidade(self.df, self.tratada, c)
        return self.resultados["qualidade"]

    # ── KPIs e análises ──
    def kpis(self, por):
        return kp.kpis(self.tratada, self.cfg, por)

    def mostrar(self, nome, k, cols=None):
        self.resultados[nome] = k
        display(kp.formatar(k, self.cfg, cols))
        return k

    def geral(self):
        g = kp.kpis(self.tratada.assign(total="Total"), self.cfg, "total").iloc[0]
        for n, v in g.drop("participacao").items():
            print(f"{rot(n):<22}: {fmt(v, self.cfg.formato[n], self.cfg.moeda)}")

    def ranking(self, dim=None, metricas=None):
        c = self.cfg; dim = dim or c.dim_a; metricas = metricas or c.metricas_rank
        k = self.mostrar(f"por_{dim}", self.kpis(dim).sort_values(c.kpi_principal, ascending=False))
        for m in metricas:
            analises.destaques(k, c, m)
        graficos.barras(k, c, metricas, f"grafico_{dim}.png")
        return k

    def comparar(self, dim=None):
        dim = dim or self.cfg.dim_b
        k = self.mostrar(f"por_{dim}", self.kpis(dim))
        analises.teste_chi2(self.tratada, self.cfg, dim)
        return k

    def cruzar(self, x=None, hue=None, metrica=None, titulo=""):
        c = self.cfg; x = x or c.dim_a; hue = hue or c.dim_b; metrica = metrica or c.metrica_cruz
        k = graficos.cruzar(self.tratada, c, x, hue, metrica, titulo, "grafico_principal.png")
        return self.mostrar(f"{x}_x_{hue}", k)

    def evolucao(self, metricas=None):
        k = graficos.evolucao(self.tratada, self.cfg, metricas or self.cfg.metricas_tempo, "grafico_evolucao.png")
        return self.mostrar("por_periodo", k, [col for col in k.columns if col != "participacao"])

    def ultimo_vs_anteriores(self, dim=None, metrica=None):
        c = self.cfg
        comp = analises.ultimo_vs_anteriores(self.tratada, c, dim or c.dim_a, metrica or c.metrica_cruz)
        self.resultados["ultimo_vs_anteriores"] = comp
        return comp.assign(variação=comp["variação"].map(lambda v: fmt(v, "pct"))).round(3)

    def demais_dimensoes(self):
        c = self.cfg
        for dim in [d for d in c.dimensoes if d not in (c.dim_a, c.dim_b)]:
            print(f"\nPor {dim}:")
            self.mostrar(f"por_{dim}", self.kpis(dim).sort_values(c.kpi_principal, ascending=False),
                         [c.kpi_principal, "participacao", *c.metricas_rank[1:]])

    def exportar(self):
        exportar(self.tratada, self.resultados, self.cfg.pasta_saida)
