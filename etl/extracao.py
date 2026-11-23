import csv
import json
import os
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"
PAGE_SIZE = 50
CAMINHO_PRODUTOS = "insumos/dados/produtos.csv"
PASTA_BRUTOS = "brutos"


def buscar_pagina(rota, pagina):
    # Pede uma pagina da API. Devolve o JSON da resposta ou None se der erro.
    url = f"{BASE_URL}/{rota}?page={pagina}&page_size={PAGE_SIZE}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resposta:
            if resposta.status != 200:
                print(f"extracao: /{rota} pagina={pagina} respondeu status {resposta.status}")
                return None
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        print(f"extracao: /{rota} pagina={pagina} respondeu status {erro.code}")
    except OSError as erro:
        print(f"extracao: erro de conexao em /{rota} pagina={pagina}: {erro}")
    except ValueError:
        print(f"extracao: /{rota} pagina={pagina} devolveu um JSON invalido")
    return None


def extrair_rota(rota):
    # Percorre todas as paginas de uma rota. Devolve (registros, paginas) ou None.
    registros = []
    pagina = 1
    total_paginas = 1  
    total_itens = 0

    while pagina <= total_paginas:
        corpo = buscar_pagina(rota, pagina)
        if corpo is None:
            return None
        total_paginas = corpo["total_pages"]
        total_itens = corpo["total_items"]
        registros.extend(corpo["items"])
        pagina += 1

    if len(registros) != total_itens:
        print(f"extracao: /{rota} recebeu {len(registros)} registros, mas a API informou {total_itens}")
        return None
    return registros, total_paginas


def ler_produtos(caminho):
    # Le o CSV de produtos. Devolve uma lista de dicionarios ou None.
    try:
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))
    except FileNotFoundError:
        print(f"extracao: arquivo nao encontrado: {caminho}")
        return None


def salvar_bruto(nome, dados):
    # Grava os dados extraidos, sem alteracao, em brutos/<nome>.json.
    os.makedirs(PASTA_BRUTOS, exist_ok=True)
    caminho = os.path.join(PASTA_BRUTOS, f"{nome}.json")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=1)


def main():
    resultado_clientes = extrair_rota("clientes")
    resultado_pedidos = extrair_rota("pedidos")
    produtos = ler_produtos(CAMINHO_PRODUTOS)

    if resultado_clientes is None or resultado_pedidos is None or produtos is None:
        print("extracao: falhou, nada foi salvo")
        return 1

    clientes, paginas_clientes = resultado_clientes
    pedidos, paginas_pedidos = resultado_pedidos

    salvar_bruto("clientes", clientes)
    salvar_bruto("pedidos", pedidos)
    salvar_bruto("produtos", produtos)

    print(f"extracao: clientes paginas={paginas_clientes} registros={len(clientes)}")
    print(f"extracao: pedidos paginas={paginas_pedidos} registros_brutos={len(pedidos)}")
    print(f"extracao: produtos registros={len(produtos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())