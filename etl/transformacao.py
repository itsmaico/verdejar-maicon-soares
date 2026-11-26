import json
from datetime import datetime
from pathlib import Path

PASTA_BRUTOS = Path("brutos")
PASTA_TRANSFORMADOS = Path("transformados")
TOLERANCIA = 0.01


def converter_data(texto):
    """A3: aceita AAAA-MM-DD ou DD/MM/AAAA e devolve sempre AAAA-MM-DD."""
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"data invalida: {texto}")


def converter_valor(valor):
    """A4: aceita numero ou texto com virgula decimal e devolve float com 2 casas."""
    if isinstance(valor, (int, float)):
        return round(float(valor), 2)
    return round(float(valor.replace(",", ".")), 2)


def padronizar_estado(uf):
    """A2: sigla do estado em maiusculas, sem espacos."""
    return uf.strip().upper()


def tratar_email(email):
    """A1: e-mail vazio ou ausente vira None (NULL no banco)."""
    return email or None


def calcular_valor_itens(itens):
    """Soma quantidade x preco_unitario de todos os itens do pedido."""
    return round(sum(item["quantidade"] * item["preco_unitario"] for item in itens), 2)


def divergente(valor_total, valor_itens):
    """A6: True quando a diferenca entre os dois valores passa de um centavo."""
    return round(abs(valor_total - valor_itens), 2) > TOLERANCIA


def remover_repetidos(pedidos):
    """A5: mantem a primeira ocorrencia de cada id. Devolve (unicos, quantos_descartados)."""
    vistos = set()
    unicos = []
    for pedido in pedidos:
        if pedido["id"] not in vistos:
            vistos.add(pedido["id"])
            unicos.append(pedido)
    return unicos, len(pedidos) - len(unicos)


def tratar_cliente(cliente):
    return {
        "id": cliente["id"],
        "nome": cliente["nome"],
        "email": tratar_email(cliente["email"]),
        "cidade": cliente["cidade"],
        "estado": padronizar_estado(cliente["estado"]),
        "cadastro_em": converter_data(cliente["cadastro_em"]),
    }


def tratar_pedido(pedido):
    valor_total = converter_valor(pedido["valor_total"])
    valor_itens = calcular_valor_itens(pedido["itens"])
    return {
        "id": pedido["id"],
        "cliente_id": pedido["cliente_id"],
        "data_pedido": converter_data(pedido["data_pedido"]),
        "status": pedido["status"],
        "valor_total": valor_total,
        "valor_itens": valor_itens,
        "divergente": divergente(valor_total, valor_itens),
    }


def tratar_itens(pedido_id, itens):
    """Gera as linhas de itens_pedido, numeradas a partir de 1."""
    return [
        {
            "pedido_id": pedido_id,
            "linha": numero,
            "produto_id": int(item["produto_id"]),
            "quantidade": int(item["quantidade"]),
            "preco_unitario": converter_valor(item["preco_unitario"]),
        }
        for numero, item in enumerate(itens, start=1)
    ]


def tratar_produto(produto):
    return {
        "produto_id": int(produto["produto_id"]),
        "nome": produto["nome"],
        "categoria": produto["categoria"],
        "preco_base": converter_valor(produto["preco_base"]),
    }


def transformar_dados(clientes, pedidos, produtos):
    """Aplica as transformacoes. Devolve (dados por tabela, contadores)."""
    pedidos_unicos, repetidos = remover_repetidos(pedidos)

    contadores = {
        "repetidos_descartados": repetidos,
        "emails_nulos": sum(1 for c in clientes if not c["email"]),
        "estados_padronizados": sum(1 for c in clientes if c["estado"] != c["estado"].strip().upper()),
        "datas_convertidas": sum(1 for p in pedidos_unicos if "/" in p["data_pedido"]),
        "valores_convertidos": sum(1 for p in pedidos_unicos if isinstance(p["valor_total"], str)),
    }

    pedidos_tratados = [tratar_pedido(p) for p in pedidos_unicos]
    itens_pedido = []
    for pedido in pedidos_unicos:
        itens_pedido.extend(tratar_itens(pedido["id"], pedido["itens"]))
    contadores["divergentes"] = sum(1 for p in pedidos_tratados if p["divergente"])

    dados = {
        "clientes": [tratar_cliente(c) for c in clientes],
        "produtos": [tratar_produto(p) for p in produtos],
        "pedidos": pedidos_tratados,
        "itens_pedido": itens_pedido,
    }
    return dados, contadores


def ler_json(caminho):
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def main():
    """Lê brutos/, transforma e salva um JSON para cada tabela."""
    arquivos_necessarios = (
        PASTA_BRUTOS / "clientes.json",
        PASTA_BRUTOS / "pedidos.json",
        PASTA_BRUTOS / "produtos.json",
    )

    for caminho in arquivos_necessarios:
        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo bruto não encontrado: {caminho}\n"
                "Execute a extração antes da transformação."
            )

    clientes_brutos = ler_json(arquivos_necessarios[0])
    pedidos_brutos = ler_json(arquivos_necessarios[1])
    produtos_brutos = ler_json(arquivos_necessarios[2])

    dados, contadores = transformar_dados(clientes_brutos, pedidos_brutos, produtos_brutos)

    PASTA_TRANSFORMADOS.mkdir(exist_ok=True)

    for nome_tabela, registros in dados.items():
        caminho_saida = PASTA_TRANSFORMADOS / f"{nome_tabela}.json"
        salvar_json(caminho_saida, registros)


    c = contadores
    print(f"transformacao: pedidos_unicos={len(dados['pedidos'])} repetidos_descartados={c['repetidos_descartados']}")
    print(f"transformacao: emails_nulos={c['emails_nulos']} estados_padronizados={c['estados_padronizados']} "
          f"datas_convertidas={c['datas_convertidas']} valores_convertidos={c['valores_convertidos']}")
    print(f"divergentes: {c['divergentes']} pedidos com valor_total diferente da soma dos itens")


if __name__ == "__main__":
    main()