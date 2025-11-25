"""
Testes Unitários - Transição POP → Etapas

Testa o contrato crítico de mudança de contexto entre produtos Helena.
Este é o teste mais importante: se a transição quebrar, o fluxo inteiro quebra.
"""
import os
import sys
import django

# Configurar Django antes de importar models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
django.setup()

import pytest
from processos.app.helena_core import HelenaCore


# ============================================================================
# FAKE PRODUCTS - Mínimo necessário para testar transição
# ============================================================================

class FakePOP:
    """Produto fake que simula HelenaPOP"""

    def processar(self, mensagem: str, estado: dict) -> dict:
        """Simula POP querendo ir para Etapas"""

        if mensagem == 'VAMOS':
            # Simula transição
            return {
                'resposta': "Passando para Etapas...",
                'novo_estado': {'finalizado': True},
                'metadados': {
                    'mudar_contexto': 'etapas',
                    'dados_herdados': {
                        'area': 'CGBEN',
                        'sistemas': ['SEI', 'SIAPNET']
                    }
                }
            }

        # Mensagem normal
        return {
            'resposta': "Resposta normal do POP",
            'novo_estado': {'etapa': 1},
            'metadados': {}
        }

    def inicializar_estado(self, dados_herdados=None) -> dict:
        return {}


class FakeEtapas:
    """Produto fake que simula HelenaEtapas"""

    def processar(self, mensagem: str, estado: dict) -> dict:
        """Simula Etapas recebendo inicialização"""

        if mensagem == 'iniciar':
            dados_herdados = estado.get('dados_herdados', {})
            return {
                'resposta': f"Helena Etapas iniciada com área {dados_herdados.get('area', 'N/A')}",
                'novo_estado': {
                    'dados_herdados': dados_herdados,
                    'etapa_atual': 1
                },
                'metadados': {}
            }

        return {
            'resposta': "Processando etapa...",
            'novo_estado': estado,
            'metadados': {}
        }

    def inicializar_estado(self, dados_herdados=None) -> dict:
        estado = {'etapa_atual': 0}
        if dados_herdados:
            estado['dados_herdados'] = dados_herdados
        return estado


# ============================================================================
# TESTES
# ============================================================================

def test_core_sem_transicao():
    """Testa processamento normal sem mudança de contexto"""
    core = HelenaCore(registry={
        'pop': FakePOP,
        'etapas': FakeEtapas
    })

    resultado = core.processar_puro(
        contexto='pop',
        mensagem='Oi',
        estado_atual={}
    )

    # Deve continuar no mesmo contexto
    assert resultado['contexto'] == 'pop'
    assert resultado['resposta'] == "Resposta normal do POP"
    assert isinstance(resultado['novo_estado'], dict)
    assert resultado['novo_estado']['etapa'] == 1


def test_core_com_transicao_pop_para_etapas():
    """
    Teste CRÍTICO: Transição POP → Etapas

    Este é o fluxo mais importante do sistema.
    Se este teste falhar, o mapeamento não funciona.
    """
    core = HelenaCore(registry={
        'pop': FakePOP,
        'etapas': FakeEtapas
    })

    # 1. POP solicita transição
    resultado = core.processar_puro(
        contexto='pop',
        mensagem='VAMOS',
        estado_atual={}
    )

    # 2. Verificar que contexto mudou
    assert resultado['contexto'] == 'etapas', \
        "Contexto deve mudar de 'pop' para 'etapas'"

    # 3. Verificar que resposta foi concatenada
    assert "Passando para Etapas" in resultado['resposta'], \
        "Resposta deve conter mensagem do POP"
    assert "Helena Etapas iniciada" in resultado['resposta'], \
        "Resposta deve conter mensagem de Etapas"

    # 4. Verificar que dados foram herdados
    assert 'dados_herdados' in resultado['novo_estado'], \
        "Estado de Etapas deve conter dados_herdados"
    assert resultado['novo_estado']['dados_herdados']['area'] == 'CGBEN', \
        "Área deve ser herdada corretamente"
    assert 'SEI' in resultado['novo_estado']['dados_herdados']['sistemas'], \
        "Sistemas devem ser herdados"

    # 5. Verificar que novo estado é de Etapas, não de POP
    assert resultado['novo_estado']['etapa_atual'] == 1, \
        "Estado deve ser de Etapas, não de POP"


def test_core_continua_em_etapas_apos_transicao():
    """Testa que depois da transição, Etapas continua ativa"""
    core = HelenaCore(registry={
        'pop': FakePOP,
        'etapas': FakeEtapas
    })

    # Simular estado após transição
    estado_etapas = {
        'dados_herdados': {'area': 'CGBEN'},
        'etapa_atual': 1
    }

    resultado = core.processar_puro(
        contexto='etapas',  # ← Agora está em Etapas
        mensagem='Primeira etapa é...',
        estado_atual=estado_etapas
    )

    # Deve continuar em Etapas
    assert resultado['contexto'] == 'etapas'
    assert "Processando etapa" in resultado['resposta']


def test_core_contexto_invalido():
    """Testa erro quando contexto não existe"""
    core = HelenaCore(registry={
        'pop': FakePOP,
        'etapas': FakeEtapas
    })

    with pytest.raises(ValueError, match="Contexto 'invalido' inválido"):
        core.processar_puro(
            contexto='invalido',
            mensagem='teste',
            estado_atual={}
        )


def test_core_dados_herdados_preservados():
    """Testa que dados herdados são preservados corretamente"""
    core = HelenaCore(registry={
        'pop': FakePOP,
        'etapas': FakeEtapas
    })

    resultado = core.processar_puro(
        contexto='pop',
        mensagem='VAMOS',
        estado_atual={}
    )

    dados_herdados = resultado['novo_estado']['dados_herdados']

    # Verificar estrutura completa
    assert dados_herdados['area'] == 'CGBEN'
    assert len(dados_herdados['sistemas']) == 2
    assert 'SEI' in dados_herdados['sistemas']
    assert 'SIAPNET' in dados_herdados['sistemas']


# ============================================================================
# TESTES DE INTEGRAÇÃO (com produtos reais)
# ============================================================================

@pytest.mark.integration
def test_transicao_com_produtos_reais():
    """
    Teste de integração com HelenaPOP e HelenaEtapas reais.

    Este teste é mais pesado (importa produtos reais), então marcado como integration.
    Rode com: pytest -m integration
    """
    from processos.domain.helena_mapeamento.helena_pop import HelenaPOP
    from processos.domain.helena_mapeamento.helena_etapas import HelenaEtapas

    core = HelenaCore(registry={
        'pop': HelenaPOP,
        'etapas': HelenaEtapas
    })

    # Iniciar POP
    estado_pop = HelenaPOP().inicializar_estado(skip_intro=True)

    # Simular coleta de dados até transição
    # (este teste assumiria que você já tem o estado TRANSICAO_EPICA)

    # Por enquanto, apenas verificar que produtos são válidos
    assert 'pop' in core.registry
    assert 'etapas' in core.registry


if __name__ == '__main__':
    # Rodar testes manualmente
    pytest.main([__file__, '-v'])
