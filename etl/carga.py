import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg

# Carrega as variaveis de ambiente do arquivo .env
load_dotenv(override=True)

PASTA_TRANSFORMADOS = Path("transformados")

# Ordem respeitando as chaves estrangeiras.
ORDEM = ["produtos", "clientes", "pedidos", "itens_pedido"]

COLUNAS = {
    "produtos": ["produto_id", "nome", "categoria", "preco_base"],
    "clientes": ["id", "nome", "email", "cidade", "estado", "cadastro_em"],
    "pedidos": ["id", "cliente_id", "data_pedido", "status",
                "valor_total", "valor_itens", "divergente"],
    "itens_pedido": ["pedido_id", "linha", "produto_id", "quantidade", "preco_unitario"],
}


def ler_tabela(nome):
    """Le o JSON transformado de uma tabela."""
    with (PASTA_TRANSFORMADOS / f"{nome}.json").open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def inserir(cur, tabela, registros):
    """Insere os registros usando parametros (%s), nunca texto montado com os dados."""
    colunas = COLUNAS[tabela]
    sql = (f"INSERT INTO {tabela} ({', '.join(colunas)}) "
           f"VALUES ({', '.join(['%s'] * len(colunas))})")
    cur.executemany(sql, [[registro[c] for c in colunas] for registro in registros])


def carregar(conn, dados):
    """Apaga as tabelas e recarrega tudo. Idempotente: rodar de novo nao duplica."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE itens_pedido, pedidos, clientes, produtos")
        for tabela in ORDEM:
            inserir(cur, tabela, dados[tabela])


def contar(conn):
    """Conta os registros de cada tabela no banco."""
    with conn.cursor() as cur:
        contagens = {}
        for tabela in ORDEM:
            cur.execute(f"SELECT COUNT(*) FROM {tabela}")
            contagens[tabela] = cur.fetchone()[0]
        return contagens


def main():
    dados = {tabela: ler_tabela(tabela) for tabela in ORDEM}

    # A conexao usa as variaveis PGHOST, PGPORT, PGUSER e PGPASSWORD do ambiente.
    # O bloco 'with' confirma a transacao ao final, ou desfaz tudo se houver erro.
    with psycopg.connect() as conn:
        carregar(conn, dados)
        total = contar(conn)

    print(f"carga: clientes={total['clientes']} produtos={total['produtos']} "
          f"pedidos={total['pedidos']} itens={total['itens_pedido']}")


if __name__ == "__main__":
    main()