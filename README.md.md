# Modelo Analítico Parametrizado

Notebook reutilizável para ir da base bruta à decisão em qualquer setor. A lógica fica no pacote
`modelo_analitico/`; o notebook só contém parâmetros, análises e os textos de leitura.

## Como usar
1. Copie esta pasta para o novo projeto e renomeie `Modelo_Analitico.ipynb`.
2. Abra o notebook, preencha a seção 1 e edite **apenas a célula de parâmetros (seção 2)**.
3. `Run All`, escreva a leitura de cada análise e a conclusão.
4. Instalação: `pip install -r requirements.txt`. Testes: `pytest`.

## Estrutura (mesmo padrão modular dos outros projetos)
```
README.md · requirements.txt · .gitignore
Modelo_Analitico.ipynb        ← ponto de entrada (parâmetros + análises + textos)
modelo_analitico/
├── config/       parametros.py   Config: todos os parâmetros e a validação dos nomes de KPIs
├── dados/        carga.py        carregar() de CSV/Excel/JSON/Parquet/Feather/Pickle/bancos; exportar()
├── operacoes/    limpeza.py      tipos, datas, duplicatas, flag de sucesso, ajustes do caso
│                 qualidade.py    diagnóstico, regras de negócio, outliers por grupo, relatório antes × depois
│                 kpis.py         KPIs genéricos (medidas + razões) para qualquer agrupamento
│                 graficos.py     barras, barras agrupadas, evolução temporal
│                 analises.py     destaques em texto, qui-quadrado, último período × anteriores
│                 modelo.py       classe Modelo: guarda o estado e expõe cada etapa em uma linha
└── utilitarios/  formatacao.py   formatação no padrão brasileiro
tests/                           testes automatizados
```
Regra de dependência: notebook → operacoes → (dados, config) → utilitarios, sempre em um único sentido.
Não há `entidades/` nem `frontend/` porque o modelo não tem dados cadastrais nem interface própria.

## O que muda de um projeto para outro
| Quero... | Altero em `Config` |
|---|---|
| Trocar a base | `fonte`, `tipo`, `leitura`, `consulta` |
| Descrever as colunas | `renomear`, `id`, `data`, `freq`, `dimensoes`, `sucesso`, `numericas` |
| Definir KPIs | `medidas` (coluna, agregação, formato) e `razoes` (numerador ÷ denominador) |
| Validar a base | `regras` (expressões que identificam linhas inválidas), `outlier_cols`, `outlier_grupo` |
| Corrigir algo específico do caso | função `ajustes(d)` |
| Escolher as análises | `dim_a`, `dim_b`, `metricas_rank`, `metricas_tempo`, `metrica_cruz` |

Para uma análise nova, chame `m.kpis("coluna")` e `m.mostrar("nome", tabela)`, ou use as funções de `operacoes/`.

## Observações
- Em Markdown, escreva `R\$` (com barra): dois `$` no mesmo parágrafo viram fórmula matemática.
- CSV: sem `sep`, o separador é detectado automaticamente; se travar, informe `leitura={"sep": ";"}`.
- Datas ISO (`2026-01-05`) nunca são trocadas; as demais seguem `dia_primeiro` (padrão dd/mm/aaaa).
- JSON aninhado: passe `fonte=pd.json_normalize(dados)`.
