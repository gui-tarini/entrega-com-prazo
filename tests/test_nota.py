""" RF-001
Dado que um trabalho não possui data e hora limite
Quando o sistema tentar calcular a nota da entrega
Então deve rejeitar a operação e informar que o prazo é obrigatório
RF-002
Dado um trabalho com nota 10 e prazo em 20/11/2026 às 23:59
Quando o aluno entregar em 20/11/2026 às 23:59
Então a entrega deve ser aceita com nota final 10 e desconto de 0%
RF-003
Dado um trabalho com nota 10 e prazo em 20/11/2026 às 23:59
Quando o aluno entregar em 22/11/2026 às 00:00
Então a entrega deve ser aceita com desconto de 20% e nota final 8
RF-004
Dado um trabalho com nota 10 e prazo em 20/11/2026 às 23:59
Quando o aluno entregar em 25/11/2026 às 23:59
Então a entrega deve ser aceita com desconto máximo de 50%
E a nota final deve ser 5
RF-005
Dado um trabalho com prazo em 20/11/2026 às 23:59
Quando o aluno entregar em 25/11/2026 às 00:00
Então a entrega deve ser aceita, pois ainda não completou cinco dias

Dado o mesmo trabalho
Quando o aluno entregar em 26/11/2026 às 00:00
Então a entrega deve ser recusada por ultrapassar cinco dias
RF-006
Dado um trabalho com nota 10 e prazo original em 20/11/2026
E uma justificativa aprovada pela coordenação
E um novo prazo em 27/11/2026 às 23:59
Quando o aluno entregar em 26/11/2026 às 15:00
Então a entrega deve ser aceita sem desconto
E a nota final deve ser 10
RF-007
Dado que o prazo de um trabalho já terminou
E que existem dois alunos matriculados
Quando o professor reabrir a entrega apenas para o primeiro aluno
Então o primeiro aluno deve receber permissão para entregar
E o segundo aluno deve permanecer sem a permissão adicional
RF-008
Dado um aluno identificado no sistema
E um trabalho com nota 10 e prazo em 20/11/2026 às 23:59
Quando o aluno realizar a entrega em 21/11/2026 às 12:00
Então o sistema deve registrar a identificação do aluno
E a data e hora da entrega
E o desconto aplicado de 10%  """

from datetime import datetime

import pytest

from src.nota import calcular_nota_final


PRAZO = datetime(2026, 11, 20, 23, 59)


def test_rf001_prazo_obrigatorio():
    with pytest.raises(ValueError, match="prazo.*obrigatório"):
        calcular_nota_final(
            nota=10,
            prazo=None,
            entrega=datetime(2026, 11, 20, 23, 59),
            justificativa_aprovada=False,
            novo_prazo=None,
        )


def test_rf002_entrega_no_limite():
    resultado = calcular_nota_final(
        10, PRAZO, datetime(2026, 11, 20, 23, 59), False, None
    )

    assert resultado["aceita"] is True
    assert resultado["nota_final"] == 10
    assert resultado["desconto_percentual"] == 0


def test_rf003_desconto_de_um_dia_de_atraso():
    resultado = calcular_nota_final(
        10, PRAZO, datetime(2026, 11, 22, 0, 0), False, None
    )

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 20
    assert resultado["nota_final"] == 8


def test_rf004_desconto_maximo():
    resultado = calcular_nota_final(
        10, PRAZO, datetime(2026, 11, 25, 23, 59), False, None
    )

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 50
    assert resultado["nota_final"] == 5


def test_rf005_limite_de_cinco_dias():
    antes_do_limite = calcular_nota_final(
        10, PRAZO, datetime(2026, 11, 25, 0, 0), False, None
    )
    apos_o_limite = calcular_nota_final(
        10, PRAZO, datetime(2026, 11, 26, 0, 0), False, None
    )

    assert antes_do_limite["aceita"] is True
    assert apos_o_limite["aceita"] is False


def test_rf006_novo_prazo_com_justificativa_aprovada():
    novo_prazo = datetime(2026, 11, 27, 23, 59)

    resultado = calcular_nota_final(
        10,
        PRAZO,
        datetime(2026, 11, 26, 15, 0),
        True,
        novo_prazo,
    )

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 0
    assert resultado["nota_final"] == 10


def test_rf007_reabertura_para_aluno_especifico():
    primeiro = calcular_nota_final(
        10,
        PRAZO,
        datetime(2026, 11, 21, 12, 0),
        False,
        None,
        aluno_id="aluno-1",
        permissoes_reabertura={"aluno-1"},
    )
    segundo = calcular_nota_final(
        10,
        PRAZO,
        datetime(2026, 11, 21, 12, 0),
        False,
        None,
        aluno_id="aluno-2",
        permissoes_reabertura={"aluno-1"},
    )

    assert primeiro["pode_entregar"] is True
    assert segundo["pode_entregar"] is False


def test_rf008_registro_da_entrega():
    entrega = datetime(2026, 11, 21, 12, 0)

    resultado = calcular_nota_final(
        10,
        PRAZO,
        entrega,
        False,
        None,
        aluno_id="aluno-1",
    )

    assert resultado["aluno_id"] == "aluno-1"
    assert resultado["data_entrega"] == entrega
    assert resultado["desconto_percentual"] == 10
