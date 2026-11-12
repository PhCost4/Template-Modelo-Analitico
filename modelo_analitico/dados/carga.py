"""Acesso à base: leitura de qualquer formato e exportação das saídas."""
import sqlite3
from pathlib import Path

import pandas as pd


def carregar(fonte, tipo="auto", consulta=None, **op):
    """Lê CSV, Excel, JSON, JSONL, Parquet, Feather, Pickle ou banco de dados."""
    if isinstance(fonte, pd.DataFrame):
        return fonte.copy()
    f = str(fonte)
    suf = Path(f.split("?")[0]).suffix.lower().lstrip(".")
    banco = suf in ("db", "sqlite", "sqlite3") or ("://" in f and not f.startswith(("http", "ftp")))
    if tipo == "auto":
        apelidos = {"txt": "csv", "tsv": "csv", "xls": "xlsx", "xlsm": "xlsx", "ndjson": "jsonl", "pkl": "pickle"}
        tipo = "sql" if banco else apelidos.get(suf, suf)
    if tipo == "csv":
        op.setdefault("sep", "\t" if suf == "tsv" else None)      # sep=None → o pandas detecta o separador
        motor = "python" if op["sep"] is None else "c"
        try:
            return pd.read_csv(f, engine=motor, **op)
        except UnicodeDecodeError:
            return pd.read_csv(f, engine=motor, encoding="latin-1", **op)
    if tipo == "sql":
        if suf in ("db", "sqlite", "sqlite3"):
            return pd.read_sql(consulta, sqlite3.connect(f), **op)
        from sqlalchemy import create_engine                      # postgresql://, mysql+pymysql://, mssql+pyodbc://...
        return pd.read_sql(consulta, create_engine(f), **op)
    if tipo == "jsonl":
        return pd.read_json(f, lines=True, **op)
    leitores = {"xlsx": pd.read_excel, "json": pd.read_json, "parquet": pd.read_parquet,
                "feather": pd.read_feather, "pickle": pd.read_pickle}
    if tipo not in leitores:
        raise ValueError(f"Tipo de fonte não suportado: '{tipo}'")
    return leitores[tipo](f, **op)                                # JSON aninhado: passe fonte=pd.json_normalize(dados)


def exportar(tratada, resultados, pasta):
    """Grava a base tratada (CSV) e todas as tabelas geradas (um Excel, uma aba por tabela)."""
    pasta = Path(pasta)
    pasta.mkdir(exist_ok=True)
    tratada.to_csv(pasta / "base_tratada.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(pasta / "resultados.xlsx") as xl:
        for nome, t in resultados.items():
            (t if nome == "qualidade" else t.reset_index()).to_excel(xl, sheet_name=nome[:31], index=False)
    print("Arquivos gerados em:", pasta.resolve())
    for f in sorted(pasta.iterdir()):
        print(" -", f.name)
