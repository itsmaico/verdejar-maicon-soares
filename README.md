# README

![Banner da Verdejar](https://app.notion.comassets/verdejar\_banner\_github.png)

Projeto do Desafio Final do Bootcamp (Fellowship OCT26 AI-Driven Data Engineering, Fase 1).

A Verdejar é uma loja virtual fictícia de hortifrúti. Este projeto implementa um ETL em Python que extrai clientes e pedidos de uma API local e o catálogo de produtos de um CSV, trata seis problemas de qualidade declarados nos dados, carrega tudo em um banco PostgreSQL (rodando em Docker) e confere se a carga está correta.

Todos os dados são sintéticos, gerados com seed fixa (2026), e nenhuma informação real de pessoas está envolvida.

## O que ele faz ?

- **Extração:** consome a API paginada (`/clientes` e `/pedidos`) e lê o `produtos.csv`, guardando os dados brutos em `brutos/`.
- **Transformação:** trata seis problemas de qualidade declarados nos dados (e-mails ausentes, UF em caixa mista, datas em dois formatos, valores com vírgula, pedidos repetidos e totais divergentes).
- **Carga:** grava as tabelas `clientes`, `produtos`, `pedidos` e `itens\_pedido` no PostgreSQL, de forma idempotente.
- **Validação:** testes com pytest, reconciliação entre origem e destino e consultas SQL de conferência.

## Estrutura do projeto

```
desafio-final/
 assets/
		 verdejar_banner_github
 etl/
     extracao.py
     transformacao.py
     carga.py
     __init__.py
 insumos/
     dados/
     gerar_dados.py
     api_verdejar.py
     schema.sql
     README_insumos.md
 tests/
     test_transformacao.py
     test_reconciliacao.py
 COMO_USEI_IA.md
 CONTRATO_DE_DADOS.md
 README.md
 consultas_validacao.sql
 brutos/           dados extraídos da API (gerado, fora do Git)
 transformados/    tabelas prontas para carga (gerado, fora do Git)
 .gitignore
```

## Pré-requisitos

- Python 3.15
- Git com acesso ao GitHub
- Docker Desktop instalado e em execução
- VScode *para facilitar a organização e execução*

## Caminho do banco escolhido

Caminho B: PostgreSQL 16 em contêiner Docker. O esquema usado está em `insumos/schema.sql`.

## Bibliotecas

| Biblioteca | Uso | Instalação |
| --- | --- | --- |
| `urllib` | Consumo da API | Biblioteca padrão |
| `csv`, `json` | Leitura do CSV e dos JSON | Biblioteca padrão |
| `psycopg` | Conexão e carga no PostgreSQL | `python -m pip install "psycopg\[binary]"` |
| `pytest` | Testes automatizados | `python -m pip install pytest` |

Versões instaladas no ambiente de execução: psycopg 3.3.9 e pytest 9.2.0.

## Como rodar

Todos os comandos são para o PowerShell do Windows, executados na raiz do projeto, salvo indicação em contrário.

**1. Gerar os dados de origem** (dentro de `insumos/`):

```powershell
cd insumos
python gerar\_dados.py
cd ..
```

**2. Subir a API** (em um terminal que ficará aberto):

```powershell
cd insumos
python api_verdejar.py
```

Em outro terminal, confirme que ela responde:

```powershell
curl.exe "http://127.0.0.1:8000/saude"
```

**3. Subir o PostgreSQL no Docker.** Troque a senha por uma de sua escolha e não a grave em nenhum arquivo:

```powershell
docker run --name verdejar-pg -e POSTGRES_PASSWORD=troque_esta_senha -e POSTGRES_DB=verdejar -p
5432:5432 -d postgres:16
```

Se o contêiner já existir, use `docker start (nome_do_container)`.

**4. Aplicar o esquema** (dentro de `insumos/`):

```powershell
cd insumos
docker cp schema.sql verdejar-pg:/schema.sql
docker exec verdejar-pg psql -U postgres -d verdejar -f /schema.sql
cd ..
```

**5. Definir a senha na sessão do terminal** (não é gravada em arquivo):

```powershell
$env:PGPASSWORD="SENHA\_ESCOLHIDA"
```

A biblioteca `psycopg` lê essa variável automaticamente. Ela vale só para o terminal em que foi definida e, caso fechado, será necessário informar a senha novamente com o comando.

**6. Executar o ETL**, na ordem:

```powershell
python -m etl.extracao
python -m etl.transformacao
python -m etl.carga
```

**7. Executar os testes:**

```powershell
pytest
```

**8. Executar as consultas de validação:**

```powershell
docker cp consultas\_validacao.sql verdejar-pg:/consultas.sql
docker exec verdejar-pg psql -U postgres -d verdejar -f /consultas.sql
```

## Extração

`etl/extracao.py` percorre as rotas `/clientes` e `/pedidos` da API com `page_size=50`, até a última página indicada em `total_pages`. Confere o código de status de cada resposta e compara a quantidade de registros recebidos com `total_items`. Se algo falhar, nada é gravado em `brutos/`. O CSV de produtos é lido com o módulo `csv`. Os dados são gravados sem alteração em `brutos/`.

Resultado da execução:

```
extracao: clientes paginas=20 registros=1000
extracao: pedidos paginas=102 registros_brutos=5100
extracao: produtos registros=12
```

## Transformação

`etl/transformacao.py` aplica as regras de cada armadilha em funções pequenas e puras, e grava as tabelas em `transformados/`.

| Código | Problema nos dados | Tratamento | Função |
| --- | --- | --- | --- |
| A1 | E-mail ausente ou vazio | Gravado como nulo | `tratar_email` |
| A2 | Sigla do estado em caixa mista | Convertida para maiúsculas | `padronizar_estado` |
| A3 | Data em `AAAA-MM-DD` ou `DD/MM/AAAA` | Convertida para `AAAA-MM-DD` | `converter_data` |
| A4 | Valor com vírgula decimal ou número | Convertido para número com duas casas | `converter_valor` |
| A5 | Pedido repetido (mesmo `id`) | Mantida a primeira ocorrência | `remover_repetidos` |
| A6 | Valor total diferente da soma dos itens | Os dois valores são gravados e marcados quando a diferença passa de um centavo | `calcular_valor_itens`, `divergente` |

Contadores impressos pela transformação:

```
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

## Carga

`etl/carga.py` lê os JSON de `transformados/` e carrega as tabelas na ordem `produtos`, `clientes`, `pedidos`, `itens_pedido`, respeitando as chaves estrangeiras. Os valores são enviados por parâmetros (`%s`), nunca por texto montado com os dados.

Resultado da primeira execução:

```
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
```

Resultado da segunda execução, sem alterar nada:

```
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
```

## Estratégia de idempotência

A carga apaga o conteúdo das quatro tabelas com um único `TRUNCATE` e insere tudo de novo, em uma única transação. Por isso, rodar a carga duas vezes deixa o banco com as mesmas contagens. Se algum passo falhar, a transação é desfeita e o banco fica como estava antes.

A extração sobrescreve `brutos/` a cada execução, e a transformação sobrescreve `transformados/`, então também são reexecutáveis.

Esta estratégia apaga e recarrega os dados a cada vez. Não é uma carga incremental.

## Reconciliação

O teste `tests/test_reconciliacao.py` compara, depois da carga:

- a quantidade de pedidos únicos da origem (`brutos/`) com a quantidade na tabela `pedidos`;
- a soma de `valor_itens` da origem com a soma na tabela `pedidos`, com tolerância de um centavo.

Resultado:

```
=========================================================== test session starts ===========================================================
platform win32 -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0
collected 2 items

tests\test_reconciliacao.py 
reconciliacao: pedidos origem=5000 destino=5000
reconciliacao: soma_valor_itens origem=311228.75 destino=311228.75
.
consulta (a) vendas por mes:
  2026-01-01 30449.02
  2026-02-01 33923.86
  2026-03-01 30678.70
  2026-04-01 31253.96
  2026-05-01 30890.02
  2026-06-01 31627.73
  2026-07-01 32796.17
  2026-08-01 29328.04
  2026-09-01 29995.71
  2026-10-01 31104.54
teste de consulta: soma_dos_meses=312047.75 soma_geral=312047.75 diferenca=0.00
.

============================================================ 2 passed in 0.21s ============================================================
```

## Testes

Os testes são executados com `pytest`, a partir da raiz do projeto.

- `tests/test_transformacao.py`: um teste para cada armadilha A1 a A6, mais um teste da soma dos itens. Não precisam do banco.
- `tests/test_reconciliacao.py`: a reconciliação e o teste de consulta da soma mensal. Precisam do banco ligado.

Saída do pytest:

```
=========================================================== test session starts ===========================================================
platform win32 -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0
collected 14 items

tests\test_reconciliacao.py 
reconciliacao: pedidos origem=5000 destino=5000
reconciliacao: soma_valor_itens origem=311228.75 destino=311228.75
.
consulta (a) vendas por mes:
  2026-01-01 30449.02
  2026-02-01 33923.86
  2026-03-01 30678.70
  2026-04-01 31253.96
  2026-05-01 30890.02
  2026-06-01 31627.73
  2026-07-01 32796.17
  2026-08-01 29328.04
  2026-09-01 29995.71
  2026-10-01 31104.54
teste de consulta: soma_dos_meses=312047.75 soma_geral=312047.75 diferenca=0.00
.
tests\test_transfomacao.py ............

=========================================================== 14 passed in 0.26s ============================================================
```

## Consultas de validação

O arquivo `consultas_validacao.sql` contém três consultas:

- **(a) Total de vendas por mês.** A soma dos meses é conferida contra a soma geral no teste de consulta.
- **(b) Quantidade de pedidos por estado** do cliente.
- **(c) Pedidos divergentes**, com `valor_total` diferente da soma dos itens.

Resultado da consulta (a):

```
    mes     | total_vendas 
------------+--------------
 2026-01-01 |     30449.02
 2026-02-01 |     33923.86
 2026-03-01 |     30678.70
 2026-04-01 |     31253.96
 2026-05-01 |     30890.02
 2026-06-01 |     31627.73
 2026-07-01 |     32796.17
 2026-08-01 |     29328.04
 2026-09-01 |     29995.71
 2026-10-01 |     31104.54
(10 rows)

 soma_dos_meses | soma_geral | diferenca 
----------------+------------+-----------
      312047.75 |  312047.75 |      0.00
```

Resultado da consulta (b):

```
estado | quantidade_pedidos | valor_total_pedidos 
--------+--------------------+---------------------
 MG     |                476 |            30088.68
 PR     |                974 |            59552.74
 RS     |               1543 |            96565.95
 SC     |               1127 |            71386.58
 SP     |                880 |            54453.80
(5 rows)
```

Resultado da consulta (c):
*Exibindo apenas os 5 primeiros id’s*

```
  id  | cliente_id | valor_total | valor_itens | diferenca 
------+------------+-------------+-------------+-----------
    1 |        303 |      125.84 |      130.84 |     -5.00
   51 |         23 |       26.58 |       23.58 |      3.00
   71 |        962 |      144.35 |      134.35 |     10.00
   81 |        198 |       -1.84 |        3.16 |     -5.00
  106 |        973 |       47.78 |       44.78 |      3.00
(238 rows)

 soma_valor_itens | soma_total_vendas_meses | diferenca_total 
------------------+-------------------------+-----------------
        311228.75 |               312047.75 |          819.00
(1 row)
```

## Decisões de projeto

- **Caminho B (Docker)** para o banco, por já ter feito a configuração prévia.
- **`psycopg` versão 3** como biblioteca de conexão.
- **`TRUNCATE` seguido de recarga** em vez de inserir ignorando chaves existentes, por ser simples de explicar e de verificar.
- **Brutos separados das tabelas transformadas**, para reprocessar sem chamar a API de novo.
- **Pedidos repetidos ficam nos brutos** e são removidos só na transformação.
- **Senhas fora do código e do Git**, lidas da variável de ambiente `PGPASSWORD`, definida no terminal.

## Stretch

Não realizado

## Limitações conhecidas

- A API é local, sintética e não serve para uso em produção.
- Os testes de reconciliação exigem o banco ligado e o esquema aplicado. Sem eles, falham por erro de conexão, e os testes de transformação continuam passando.
- Os comandos deste README são para PowerShell no Windows. Em Linux ou macOS, troque `$env:PGPASSWORD="..."` por `export PGPASSWORD="..."`, e `curl.exe` por `curl`.

## Registro de uso da IA

O registro completo está em [COMO_USEI_IA.md](COMO_USEI_IA.md).