import json
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from etl.transformacao import calcular_valor_itens, remover_repetidos

load_dotenv()

TOLERANCIA = 0.01
BRUTOS = Path("brutos")


def origem_pedidos():
    """Conta e soma os pedidos unicos a partir dos dados brutos."""
    pedidos = json.loads((BRUTOS / "pedidos.json").read_text(encoding="utf-8"))
    unicos, _ = remover_repetidos(pedidos)
    soma = round(sum(calcular_valor_itens(p["itens"]) for p in unicos), 2)
    return len(unicos), soma


def test_reconciliacao_contagem_e_soma_de_itens():
    qtd_origem, soma_origem = origem_pedidos()
    with psycopg.connect(dbname="verdejar") as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_itens), 0) FROM pedidos")
        qtd_destino, soma_destino = cur.fetchone()

    print(f"\nreconciliacao: pedidos origem={qtd_origem} destino={qtd_destino}")
    print(f"reconciliacao: soma_valor_itens origem={soma_origem:.2f} "
          f"destino={float(soma_destino):.2f}")

    assert qtd_origem == qtd_destino
    assert abs(soma_origem - float(soma_destino)) <= TOLERANCIA


def test_consulta_vendas_por_mes_soma_igual_ao_total():
    with psycopg.connect(dbname="verdejar") as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT DATE_TRUNC('month', data_pedido)::DATE AS mes, SUM(valor_total) AS total "
            "FROM pedidos GROUP BY 1 ORDER BY 1"
        )
        meses = cur.fetchall()

        cur.execute("SELECT COALESCE(SUM(valor_total), 0) FROM pedidos")
        soma_geral = float(cur.fetchone()[0])

    soma_meses = float(sum(total for _, total in meses))

    print("\nconsulta (a) vendas por mes:")
    for mes, total in meses:
        print(f"  {mes} {float(total):.2f}")
    print(f"teste de consulta: soma_dos_meses={soma_meses:.2f} "
          f"soma_geral={soma_geral:.2f} diferenca={soma_meses - soma_geral:.2f}")

    assert abs(soma_meses - soma_geral) <= TOLERANCIA, (
        f"soma dos meses ({soma_meses:.2f}) diferente da soma geral ({soma_geral:.2f})"
    )