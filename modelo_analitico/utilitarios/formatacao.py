"""Formatação no padrão brasileiro (sem dependência de outras camadas)."""
import pandas as pd


def num_br(x, casas=0):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rot(nome):
    """Rótulo legível a partir do nome de um KPI (comissão_por_lote → Comissão por lote)."""
    return nome.replace("_", " ").capitalize()


def fmt(x, tipo="num", moeda="R$"):
    """Formata um valor: tipo = num | moeda | pct."""
    if pd.isna(x):
        return "–"
    if tipo == "pct":
        return num_br(x * 100, 1) + "%"
    if tipo == "moeda":
        return f"{moeda} " + num_br(x, 2 if abs(x) < 100 else 0)
    return num_br(x)


def compacto(x, tipo="num", moeda="R$"):
    """Rótulos curtos de eixo: 9,8 mi, 12 mil..."""
    if tipo == "pct":
        return f"{x * 100:.0f}%"
    prefixo = f"{moeda} " if tipo == "moeda" else ""
    for limite, sufixo in ((1e9, " bi"), (1e6, " mi"), (1e3, " mil")):
        if abs(x) >= limite:
            return prefixo + num_br(x / limite, 1) + sufixo
    return prefixo + num_br(x)
