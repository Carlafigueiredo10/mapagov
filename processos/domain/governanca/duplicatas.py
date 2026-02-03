"""
Detecção de Atividades Similares

Responsabilidade única: detectar duplicatas usando TF-IDF + Cosine Similarity.
"""

import logging
from typing import Dict, Any, List, Tuple

from processos.models_new import AtividadeSugerida

logger = logging.getLogger(__name__)


def detectar_atividades_similares(
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    threshold: float = 0.80
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Detecta atividades similares já sugeridas usando TF-IDF + Cosine Similarity.

    IMPORTANTE: Sempre retorna scores, mesmo se < threshold (para análise futura).

    Args:
        macroprocesso: Macroprocesso da atividade
        processo: Processo da atividade
        subprocesso: Subprocesso da atividade
        atividade: Descrição da atividade
        threshold: Limite de similaridade (padrão 0.80)

    Returns:
        Tupla (max_score, lista_similares)
        - max_score: Maior score encontrado (0.0 a 1.0)
        - lista_similares: Lista de dicts com CAP, descrição e score
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Buscar todas as atividades sugeridas da mesma área hierárquica
    atividades_existentes = AtividadeSugerida.objects.filter(
        macroprocesso=macroprocesso,
        processo=processo,
        subprocesso=subprocesso
    ).exclude(status='rejeitada')

    if not atividades_existentes.exists():
        logger.info(f"[GOVERNANÇA] Nenhuma atividade similar encontrada (nenhuma sugestão prévia nesta hierarquia)")
        return 0.0, []

    # Preparar textos para comparação
    texto_novo = atividade.lower().strip()
    textos_existentes = [a.atividade.lower().strip() for a in atividades_existentes]
    todos_textos = textos_existentes + [texto_novo]

    # TF-IDF + Cosine Similarity
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=1, max_df=0.95)
    tfidf_matrix = vectorizer.fit_transform(todos_textos)

    # Calcular similaridade do novo texto com todos os existentes
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    # Preparar resultados
    max_score = float(similarities.max()) if len(similarities) > 0 else 0.0

    lista_similares = []
    for idx, score in enumerate(similarities):
        if score >= threshold:
            ativ = atividades_existentes[idx]
            lista_similares.append({
                'cap': ativ.cap_provisorio,
                'atividade': ativ.atividade,
                'status': ativ.status,
                'score': float(score),
                'autor': ativ.autor_nome,
                'data': ativ.data_sugestao_utc.isoformat()
            })

    # Ordenar por score decrescente
    lista_similares.sort(key=lambda x: x['score'], reverse=True)

    logger.info(
        f"[GOVERNANÇA] Detecção de duplicatas: max_score={max_score:.3f}, "
        f"similares acima de {threshold}={len(lista_similares)}"
    )

    return max_score, lista_similares
