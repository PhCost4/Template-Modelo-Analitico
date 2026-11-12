"""Tipagem, limpeza e atributos derivados (sempre em cópia)."""
import pandas as pd


def para_numero(s, num_br=True):
    """Converte texto em número ('R$ 1.234,56' → 1234.56)."""
    if pd.api.types.is_numeric_dtype(s):
        return s
    s = s.astype(str).str.replace(r"[^\d,.\-]", "", regex=True)
    if num_br:
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def para_data(s, dia_primeiro=True):
    """Converte em data. Textos ISO (2026-01-05) nunca são trocados; os demais respeitam dia_primeiro."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    amostra = s.dropna().astype(str).head(20)
    iso = len(amostra) > 0 and amostra.str.match(r"^\d{4}-\d{2}-\d{2}").all()
    return pd.to_datetime(s, errors="coerce", dayfirst=dia_primeiro and not iso)


def tipar(bruto, cfg):
    """Cópia de trabalho com colunas renomeadas e numéricas convertidas (antes do diagnóstico)."""
    d = bruto.rename(columns=cfg.renomear).copy()
    for c in cfg.numericas:
        d[c] = para_numero(d[c], cfg.num_br)
    return d


def limpar(d, cfg):
    """Remove espaços invisíveis, converte datas e elimina duplicatas exatas (mantém a primeira)."""
    d = d.copy()
    for c in d.columns:
        if pd.api.types.is_string_dtype(d[c]):
            d[c] = d[c].str.strip()
    if cfg.data:
        d[cfg.data] = para_data(d[cfg.data], cfg.dia_primeiro)
    return d.drop_duplicates().reset_index(drop=True)


def preparar(d, cfg):
    """Cria 'flag' (sucesso), aplica os ajustes do caso e cria a coluna 'periodo'."""
    d = d.copy()
    if cfg.sucesso:
        coluna, valores = cfg.sucesso
        d["flag"] = d[coluna].isin(valores).astype(int)
    if cfg.ajustes:
        d = cfg.ajustes(d)
    if cfg.data:
        d["periodo"] = d[cfg.data].dt.to_period(cfg.freq).astype(str)
    return d


def verificar(d, cfg):
    """Falha com mensagem clara se a base tratada violar uma garantia básica."""
    if cfg.id_unico and cfg.id:
        assert d[cfg.id].is_unique, "ainda há IDs repetidos"
    assert d.duplicated().sum() == 0, "ainda há linhas duplicadas"
    if cfg.data and cfg.periodo:
        assert d[cfg.data].between(*cfg.periodo).all(), "há datas inválidas ou fora do período esperado"
