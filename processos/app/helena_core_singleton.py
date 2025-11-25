"""
Singleton do HelenaCore para evitar reinstanciação em cada request.

Responsabilidades:
- Fornece instância única do HelenaCore
- Registry de produtos (POP, Etapas, etc.)
- Sem dependências de Django/Redis (Core puro)

⚠️ IMPORTANTE - Comportamento em Produção:
-------------------------------------------------
Este singleton cria UMA instância POR PROCESSO Python.

Em produção com gunicorn/uwsgi multi-processo:
- Cada worker terá seu próprio HelenaCore
- Não há compartilhamento entre processos
- Isso é OK porque HelenaCore é stateless

O ESTADO da conversa fica na Django session (ou DB), não no Core.

Em desenvolvimento com auto-reload:
- O módulo pode ser recarregado → singleton recriado
- Isso é esperado e não causa problemas

Se precisar de singleton GLOBAL (todos os processos):
- Use Redis/Memcached
- Ou singleton por request (anti-pattern)
"""
from processos.app.helena_core import HelenaCore
from processos.domain.helena_mapeamento.helena_pop import HelenaPOP
from processos.domain.helena_mapeamento.helena_etapas import HelenaEtapas

# Instância global única
_core_instance = None


def get_helena_core():
    """
    Retorna instância singleton do HelenaCore.

    Registry de produtos:
    - 'pop': HelenaPOP (coleta metadados básicos)
    - 'etapas': HelenaEtapas (detalhamento operacional)

    Returns:
        HelenaCore: Instância única do orquestrador
    """
    global _core_instance

    if _core_instance is None:
        _core_instance = HelenaCore(registry={
            'pop': HelenaPOP,
            'etapas': HelenaEtapas,
        })

    return _core_instance
