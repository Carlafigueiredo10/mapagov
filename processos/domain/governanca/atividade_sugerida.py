"""
Persistência de Atividades Sugeridas

Responsabilidade única: salvar atividades sugeridas com rastreabilidade completa.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from processos.models_new import AtividadeSugerida, HistoricoAtividade

logger = logging.getLogger(__name__)


def salvar_atividade_sugerida(
    cap_provisorio: str,
    area_codigo: str,
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    entrega_esperada: str,
    autor_cpf: str,
    autor_nome: str,
    autor_area: str,
    descricao_original: str,
    score_similaridade: float,
    sugestoes_similares: List[Dict[str, Any]],
    scores_similares_todos: List[float],
    origem_fluxo: str,
    interacao_id: str
) -> AtividadeSugerida:
    """
    Salva uma nova atividade sugerida no banco de dados com rastreabilidade completa.

    Args:
        cap_provisorio: CAP provisório gerado
        area_codigo: Código da área (ex: 'CGBEN')
        macroprocesso: Nome do macroprocesso
        processo: Nome do processo
        subprocesso: Nome do subprocesso
        atividade: Descrição da atividade
        entrega_esperada: Entrega esperada da atividade
        autor_cpf: CPF do autor da sugestão
        autor_nome: Nome completo do autor
        autor_area: Área do autor
        descricao_original: Descrição original fornecida pelo usuário
        score_similaridade: Score máximo de similaridade encontrado
        sugestoes_similares: Lista de atividades similares (score >= threshold)
        scores_similares_todos: Lista completa de scores (para análise futura)
        origem_fluxo: 'match_exato', 'match_fuzzy', 'nova_atividade_ia', 'selecao_manual'
        interacao_id: ID da interação (chat_message_id)

    Returns:
        Instância de AtividadeSugerida criada
    """
    # Timestamp UTC atual
    agora_utc = datetime.now(timezone.utc)

    # Gerar hash único (anti-duplicata)
    hash_sugestao = AtividadeSugerida.gerar_hash_sugestao(
        macroprocesso, processo, subprocesso, atividade, autor_cpf, agora_utc
    )

    # Determinar confiança da IA
    if score_similaridade >= 0.90:
        confianca = 'alta'
    elif score_similaridade >= 0.75:
        confianca = 'media'
    else:
        confianca = 'baixa'

    # Criar registro
    atividade_obj = AtividadeSugerida.objects.create(
        cap_provisorio=cap_provisorio,
        cap_oficial=None,
        status='sugerida',
        area_codigo=area_codigo,
        macroprocesso=macroprocesso,
        processo=processo,
        subprocesso=subprocesso,
        atividade=atividade,
        entrega_esperada=entrega_esperada,
        autor_cpf=autor_cpf,
        autor_nome=autor_nome,
        autor_area=autor_area,
        data_sugestao_utc=agora_utc,
        descricao_original=descricao_original,
        hash_sugestao=hash_sugestao,
        score_similaridade=score_similaridade,
        sugestoes_similares=sugestoes_similares,
        scores_similares_todos=scores_similares_todos,
        confianca=confianca,
        origem_fluxo=origem_fluxo,
        interacao_id=interacao_id
    )

    # Registrar no histórico
    HistoricoAtividade.objects.create(
        atividade=atividade_obj,
        tipo_evento='criacao',
        usuario_cpf=autor_cpf,
        usuario_nome=autor_nome,
        comentario=f"Atividade sugerida via {origem_fluxo}"
    )

    logger.info(
        f"[GOVERNANÇA] Atividade sugerida salva: {cap_provisorio} | "
        f"Autor: {autor_nome} ({autor_cpf}) | Confiança: {confianca}"
    )

    return atividade_obj
