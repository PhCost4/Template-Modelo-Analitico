import pandas as pd
import pytest

from modelo_analitico import Config
from modelo_analitico.dados import carregar
from modelo_analitico.operacoes import limpeza
from modelo_analitico.operacoes.kpis import kpis
from modelo_analitico.utilitarios import compacto, fmt


def test_formatacao_brasileira():
    assert fmt(1234567, "moeda") == "R$ 1.234.567"
    assert fmt(0.1234, "pct") == "12,3%"
    assert fmt(float("nan")) == "–"
    assert compacto(9_800_000, "moeda") == "R$ 9,8 mi"


def test_config_rejeita_kpi_inexistente(cfg):
    with pytest.raises(ValueError, match="não definidos"):
        Config(fonte=cfg.fonte, medidas=cfg.medidas, razoes=cfg.razoes, kpi_principal="valor", metricas_rank=["inexistente"])


def test_config_rejeita_razao_com_referencia_invalida(cfg):
    with pytest.raises(ValueError, match="Razão"):
        Config(fonte=cfg.fonte, medidas=cfg.medidas, razoes={"x": ("nada", "linhas", "pct")}, kpi_principal="valor")


def test_limpeza_remove_duplicatas_e_cria_flag_e_periodo(cfg):
    d = limpeza.limpar(limpeza.tipar(cfg.fonte, cfg), cfg)
    assert len(d) == 4
    d = limpeza.preparar(d, cfg)
    assert d["flag"].tolist() == [1, 0, 1, 1]
    assert d["periodo"].tolist() == ["2026-01", "2026-01", "2026-02", "2026-02"]
    limpeza.verificar(d, cfg)


def test_kpis_por_grupo(cfg):
    d = limpeza.preparar(limpeza.limpar(limpeza.tipar(cfg.fonte, cfg), cfg), cfg)
    k = kpis(d, cfg, "grupo")
    assert k.loc["X", "linhas"] == 2 and k.loc["X", "taxa"] == 0.5
    assert k.loc["Y", "valor"] == 500 and k.loc["Y", "participacao"] == pytest.approx(500 / 600)


def test_para_numero_formato_brasileiro():
    s = pd.Series(["R$ 1.234,56", "2,5", "abc"])
    assert limpeza.para_numero(s).tolist()[:2] == [1234.56, 2.5]


@pytest.mark.parametrize("ext", ["csv", "json", "parquet", "xlsx"])
def test_carga_em_varios_formatos(base, tmp_path, ext):
    arq = tmp_path / f"b.{ext}"
    {"csv": lambda: base.to_csv(arq, index=False), "json": lambda: base.to_json(arq, orient="records"),
     "parquet": lambda: base.to_parquet(arq), "xlsx": lambda: base.to_excel(arq, index=False)}[ext]()
    assert carregar(arq).shape == base.shape


def test_carga_sqlite(base, tmp_path):
    import sqlite3
    arq = tmp_path / "b.db"
    con = sqlite3.connect(arq); base.to_sql("t", con, index=False); con.close()
    assert carregar(arq, consulta="SELECT * FROM t").shape == base.shape


def test_data_iso_nao_e_trocada_e_formato_br_respeita_dia_primeiro():
    iso = limpeza.para_data(pd.Series(["2026-01-05"]), dia_primeiro=True)
    br = limpeza.para_data(pd.Series(["05/01/2026"]), dia_primeiro=True)
    assert iso[0] == pd.Timestamp("2026-01-05") and br[0] == pd.Timestamp("2026-01-05")
