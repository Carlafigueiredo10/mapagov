# -*- coding: utf-8 -*-
"""
DEPRECATED: Este arquivo está deprecated e será removido na v3.0

Use: from processos.domain.helena_planejamento_estrategico import HelenaPlanejamentoEstrategico

Este arquivo mantém compatibilidade reversa com código existente.
Toda a lógica foi refatorada para a estrutura modular em:
    processos/domain/helena_planejamento_estrategico/

Mudanças:
- Código organizado em módulos
- Agentes especializados por metodologia
- Melhor testabilidade e manutenção
"""
import warnings

# Importa da nova estrutura
from processos.domain.helena_planejamento_estrategico.pe_orchestrator import (
    HelenaPlanejamentoEstrategico
)
from processos.domain.helena_planejamento_estrategico.schemas import (
    EstadoPlanejamento,
    MODELOS_ESTRATEGICOS,
    PERGUNTAS_DIAGNOSTICO
)

# Aviso de deprecação
warnings.warn(
    "processos.domain.helena_produtos.helena_planejamento_estrategico está deprecated. "
    "Use processos.domain.helena_planejamento_estrategico ao invés disso. "
    "Este arquivo será removido na versão 3.0.0",
    DeprecationWarning,
    stacklevel=2
)

# Mantém exports para compatibilidade
__all__ = [
    'HelenaPlanejamentoEstrategico',
    'EstadoPlanejamento',
    'MODELOS_ESTRATEGICOS',
    'PERGUNTAS_DIAGNOSTICO'
]
