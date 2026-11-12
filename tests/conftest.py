import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # permite importar modelo_analitico a partir da raiz

from modelo_analitico import Config


@pytest.fixture
def base():
    return pd.DataFrame({
        "id": ["a", "b", "c", "d", "d"],
        "data": ["2026-01-05", "2026-01-20", "2026-02-03", "2026-02-10", "2026-02-10"],
        "grupo": ["X", "X", "Y", "Y", "Y"],
        "status": ["ok", "falhou", "ok", "ok", "ok"],
        "valor": [100.0, None, 200.0, 300.0, 300.0],
    })


@pytest.fixture
def cfg(base):
    return Config(
        fonte=base, id="id", data="data", dimensoes=["grupo"], sucesso=("status", ["ok"]),
        medidas={"linhas": ("id", "count", "num"), "ok": ("flag", "sum", "num"), "valor": ("valor", "sum", "moeda")},
        razoes={"taxa": ("ok", "linhas", "pct")}, kpi_principal="valor",
        regras={"Valor negativo": "valor < 0"}, dim_a="grupo", dim_b="grupo",
        metricas_rank=["valor", "taxa"], metricas_tempo=["valor", "taxa"], metrica_cruz="taxa",
    )
