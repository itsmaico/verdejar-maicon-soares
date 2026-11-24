# Contrato de dados — Verdejar

Este contrato descreve os dados transformados que o ETL entrega para as tabelas
definidas em `insumos/schema.sql` (PostgreSQL, caminho B). Os arquivos são gerados
em `transformados/` pela função `transformar_dados` de `etl/transformacao.py`.

## Regras gerais

- Os arquivos brutos em `brutos/` são preservados e não são alterados.
- Datas são gravadas no formato `AAAA-MM-DD`. Datas em `DD/MM/AAAA` são convertidas.
- Valores monetários são números com duas casas decimais (por exemplo, `125.84`).
- Os pedidos são deduplicados pelo campo `id`, mantendo a primeira ocorrência.
Os repetidos são contados e não entram na saída.
- Os textos (nome, cidade, status, categoria) são mantidos como vieram da fonte.

## Tabela `clientes`

| Campo | Tipo no banco | Admite nulo | Regra |
| --- | --- | --- | --- |
| `id` | INTEGER, chave primária | Não | Identificador do cliente, vindo da API |
| `nome` | TEXT | Não | Mantido como na fonte |
| `email` | TEXT | Sim | E-mail da fonte; vazio ou ausente vira nulo (A1) |
| `cidade` | TEXT | Não | Mantida como na fonte |
| `estado` | CHAR(2) | Não | Sigla convertida para maiúsculas, sem espaços (A2) |
| `cadastro_em` | DATE | Não | Data no formato `AAAA-MM-DD` |

## Tabela `produtos`

| Campo | Tipo no banco | Admite nulo | Regra |
| --- | --- | --- | --- |
| `produto_id` | INTEGER, chave primária | Não | Lido do CSV e convertido para inteiro |
| `nome` | TEXT | Não | Mantido como na fonte |
| `categoria` | TEXT | Não | Mantida como na fonte |
| `preco_base` | NUMERIC(10,2) | Não | Lido do CSV e convertido para número com duas casas |

## Tabela `pedidos`

| Campo | Tipo no banco | Admite nulo | Regra |
| --- | --- | --- | --- |
| `id` | INTEGER, chave primária | Não | Identificador do pedido; repetidos removidos (A5) |
| `cliente_id` | INTEGER, chave estrangeira | Não | Vem da API; a existência em `clientes` é verificada pelo banco na carga |
| `data_pedido` | DATE | Não | Aceita `AAAA-MM-DD` e `DD/MM/AAAA`; grava em `AAAA-MM-DD` (A3) |
| `status` | TEXT | Não | Mantido como na fonte |
| `valor_total` | NUMERIC(12,2) | Não | Aceita número ou texto com vírgula decimal; arredondado em duas casas (A4) |
| `valor_itens` | NUMERIC(12,2) | Não | Soma de quantidade × preço unitário dos itens, arredondada em duas casas |
| `divergente` | BOOLEAN | Não | Verdadeiro quando `valor_total` e `valor_itens` diferem em mais de um centavo (A6) |

## Tabela `itens_pedido`

A chave primária de `itens_pedido` é composta por `pedido_id` e `linha`.

| Campo | Tipo no banco | Admite nulo | Regra |
| --- | --- | --- | --- |
| `pedido_id` | INTEGER, chave estrangeira | Não | Id do pedido ao qual o item pertence |
| `linha` | INTEGER | Não | Posição do item dentro do pedido, começando em 1 |
| `produto_id` | INTEGER, chave estrangeira | Não | Vem da API; a existência em `produtos` é verificada pelo banco na carga |
| `quantidade` | INTEGER | Não | Quantidade da fonte, convertida para inteiro |
| `preco_unitario` | NUMERIC(10,2) | Não | Preço da fonte, arredondado em duas casas |

## Contadores

```python
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```