"""Modelo analítico parametrizado: da base bruta à decisão, para qualquer setor."""
from .config import Config
from .operacoes import Modelo
from .operacoes.kpis import tabela_kpis

__all__ = ["Config", "Modelo", "tabela_kpis"]
