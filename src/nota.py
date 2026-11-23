import math
from collections.abc import Iterable


def calcular_nota_final(
    nota,
    prazo,
    entrega,
    justificativa_aprovada,
    novo_prazo,
    aluno_id=None,
    permissoes_reabertura: Iterable | None = None,
):
    """Calcula o resultado de uma entrega conforme o prazo e o atraso."""
    if prazo is None:
        raise ValueError("O prazo é obrigatório.")
    if entrega is None:
        raise ValueError("A data e hora da entrega são obrigatórias.")

    permissoes = set(permissoes_reabertura or ())
    reabertura_autorizada = aluno_id is not None and aluno_id in permissoes

    justificativa_valida = (
        justificativa_aprovada
        and novo_prazo is not None
        and entrega <= novo_prazo
    )

    if justificativa_valida:
        aceita = True
        desconto_percentual = 0
        pode_entregar = True
    elif reabertura_autorizada:
        aceita = True
        pode_entregar = True

        atraso = entrega - prazo
        if atraso.total_seconds() <= 0:
            dias_atrasados = 0
        else:
            dias_atrasados = math.ceil(atraso.total_seconds() / 86400)
        desconto_percentual = min(dias_atrasados * 10, 50)
    else:
        pode_entregar = entrega <= prazo
        if entrega <= prazo:
            aceita = True
            desconto_percentual = 0
        else:
            atraso = entrega - prazo
            dias_atrasados = math.ceil(atraso.total_seconds() / 86400)

            aceita = dias_atrasados <= 5
            if aceita:
                desconto_percentual = min(dias_atrasados * 10, 50)
            else:
                desconto_percentual = 0

    if aceita:
        nota_final = nota * (1 - desconto_percentual / 100)
        if isinstance(nota, int):
            nota_final = int(nota_final) if nota_final.is_integer() else nota_final
    else:
        nota_final = None

    return {
        "aceita": aceita,
        "pode_entregar": pode_entregar,
        "nota_final": nota_final,
        "desconto_percentual": desconto_percentual,
        "aluno_id": aluno_id,
        "data_entrega": entrega,
    }
