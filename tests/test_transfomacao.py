from etl.transformacao import (
    calcular_valor_itens,
    converter_data,
    converter_valor,
    divergente,
    padronizar_estado,
    remover_repetidos,
    tratar_email,
)


def test_a1_email_vazio_vira_none():
    assert tratar_email("") is None
    assert tratar_email(None) is None


def test_a1_email_preenchido_permanece():
    assert tratar_email("ana@exemplo.com") == "ana@exemplo.com"


def test_a2_estado_minusculo_vira_maiusculo():
    assert padronizar_estado("rs") == "RS"


def test_a3_data_dd_mm_aaaa_vira_aaaa_mm_dd():
    assert converter_data("05/03/2026") == "2026-03-05"


def test_a3_data_ja_no_formato_permanece():
    assert converter_data("2026-03-05") == "2026-03-05"


def test_a4_valor_com_virgula_vira_numero():
    assert converter_valor("125,84") == 125.84


def test_a4_valor_numerico_permanece():
    assert converter_valor(94.34) == 94.34


def test_a5_repetido_e_descartado_mantendo_primeira_ocorrencia():
    pedidos = [
        {"id": 1, "status": "primeiro"},
        {"id": 2, "status": "unico"},
        {"id": 1, "status": "segundo"},
    ]
    unicos, descartados = remover_repetidos(pedidos)
    assert [p["id"] for p in unicos] == [1, 2]
    assert unicos[0]["status"] == "primeiro"
    assert descartados == 1


def test_a6_valores_iguais_nao_sao_divergentes():
    assert divergente(10.00, 10.00) is False


def test_a6_diferenca_de_um_centavo_nao_e_divergente():
    assert divergente(10.00, 10.01) is False


def test_a6_diferenca_maior_que_um_centavo_e_divergente():
    assert divergente(10.00, 12.00) is True


def test_calcular_valor_itens_soma_quantidade_vezes_preco():
    itens = [
        {"quantidade": 2, "preco_unitario": 3.50},
        {"quantidade": 1, "preco_unitario": 4.20},
    ]
    assert calcular_valor_itens(itens) == 11.20