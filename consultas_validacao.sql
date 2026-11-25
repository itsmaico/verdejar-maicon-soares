-- (a) Total de vendas por mes
SELECT DATE_TRUNC('month', data_pedido)::DATE AS mes,
       SUM(valor_total) AS total_vendas
FROM pedidos
GROUP BY DATE_TRUNC('month', data_pedido)::DATE
ORDER BY mes;

-- (a2) Teste de consulta: a soma dos meses deve bater com a soma geral da tabela.
-- A coluna diferenca deve ser 0.00.
WITH vendas_mes AS (
    SELECT DATE_TRUNC('month', data_pedido)::DATE AS mes,
           SUM(valor_total) AS total_vendas
    FROM pedidos
    GROUP BY DATE_TRUNC('month', data_pedido)::DATE
)
SELECT (SELECT SUM(total_vendas) FROM vendas_mes) AS soma_dos_meses,
       (SELECT SUM(valor_total) FROM pedidos) AS soma_geral,
       ROUND((SELECT SUM(total_vendas) FROM vendas_mes) - (SELECT SUM(valor_total) FROM pedidos), 2) AS diferenca;

-- (b) Quantidade de pedidos e valor total de pedidos por estado do cliente
SELECT c.estado,
       COUNT(*) AS quantidade_pedidos,
       SUM(p.valor_total) AS valor_total_pedidos
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY c.estado;

-- (c) Pedidos divergentes, com a diferenca entre valor_total e valor_itens
SELECT id,
       cliente_id,
       valor_total,
       valor_itens,
       ROUND(valor_total - valor_itens, 2) AS diferenca
FROM pedidos
WHERE divergente
ORDER BY id;

-- (d) Soma de valor_itens ao lado da soma dos totais de vendas por mes
WITH vendas_mes AS (
    SELECT DATE_TRUNC('month', data_pedido)::DATE AS mes,
           SUM(valor_total) AS total_vendas
    FROM pedidos
    GROUP BY DATE_TRUNC('month', data_pedido)::DATE
)
SELECT (SELECT SUM(valor_itens) FROM pedidos) AS soma_valor_itens,
       (SELECT SUM(total_vendas) FROM vendas_mes) AS soma_total_vendas_meses,
       ROUND((SELECT SUM(valor_total) FROM pedidos) - (SELECT SUM(valor_itens) FROM pedidos), 2) AS diferenca_total;