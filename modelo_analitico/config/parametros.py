"""Parâmetros do modelo: tudo o que muda de um projeto para outro fica aqui."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class Config:
    # Fonte de dados
    fonte: Any                                    # arquivo, URL, string de conexão ou DataFrame
    tipo: str = "auto"                            # auto | csv | xlsx | json | jsonl | parquet | feather | pickle | sql
    leitura: dict = field(default_factory=dict)   # extras do leitor do pandas (sep=, encoding=, sheet_name=...)
    consulta: Optional[str] = None                # SQL, quando a fonte é banco

    # Esquema (nomes das colunas DEPOIS de renomear)
    renomear: dict = field(default_factory=dict)
    id: Optional[str] = None
    data: Optional[str] = None
    freq: str = "M"                               # D | W | M | Q | Y
    dimensoes: list = field(default_factory=list)
    sucesso: Optional[tuple] = None               # (coluna, [valores de sucesso]) → cria a coluna "flag"
    numericas: list = field(default_factory=list)  # colunas de texto a converter em número
    num_br: bool = True                           # números no padrão brasileiro (1.234,56)
    dia_primeiro: bool = True                     # datas dd/mm/aaaa
    id_unico: bool = True
    periodo: Optional[tuple] = None               # (início, fim) esperado da base

    # KPIs
    moeda: str = "R$"
    medidas: dict = field(default_factory=dict)   # nome: (coluna, agregação, formato)
    razoes: dict = field(default_factory=dict)    # nome: (numerador, denominador, formato)
    kpi_principal: str = ""

    # Qualidade
    regras: dict = field(default_factory=dict)    # nome: expressão que identifica linhas INVÁLIDAS
    outlier_cols: list = field(default_factory=list)
    outlier_grupo: Optional[str] = None
    z_limite: float = 3
    iqr_fator: float = 1.5
    conferir: list = field(default_factory=list)  # somas comparadas antes × depois da limpeza
    ajustes: Optional[Callable] = None            # função específica do caso: recebe e devolve o DataFrame

    # Análises
    dim_a: Optional[str] = None
    dim_b: Optional[str] = None
    metricas_rank: list = field(default_factory=list)
    metricas_tempo: list = field(default_factory=list)
    metrica_cruz: Optional[str] = None

    # Saídas
    pasta_saida: Path = Path("saidas")
    seed: int = 42

    def __post_init__(self):
        self.pasta_saida = Path(self.pasta_saida)
        if not self.medidas or not self.kpi_principal:
            raise ValueError("Defina 'medidas' e 'kpi_principal'.")
        for nome, (num, den, _) in self.razoes.items():
            for ref in (num, den):
                if ref not in self.formato:
                    raise ValueError(f"Razão '{nome}' usa '{ref}', que não está em medidas/razoes (ou vem depois dela).")
        pedidos = [self.kpi_principal, self.metrica_cruz, *self.metricas_rank, *self.metricas_tempo]
        faltam = [m for m in pedidos if m and m not in self.formato]
        if faltam:
            raise ValueError(f"KPIs usados nas análises mas não definidos: {faltam}")

    @property
    def formato(self) -> dict:
        """Formato (num | moeda | pct) de cada KPI."""
        return {**{n: v[2] for n, v in self.medidas.items()},
                **{n: v[2] for n, v in self.razoes.items()}, "participacao": "pct"}
