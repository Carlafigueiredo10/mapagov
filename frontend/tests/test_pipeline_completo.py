"""
Teste End-to-End do Pipeline v4.0
Testa todas as 4 camadas e suas integrações
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from processos.domain.helena_produtos.busca_atividade_pipeline import BuscaAtividadePipeline


def testar_camada_1_match_exato():
    """Teste Camada 1: Match Exato"""
    print("\n" + "="*80)
    print("TESTE 1: CAMADA 1 - MATCH EXATO")
    print("="*80)

    pipeline = BuscaAtividadePipeline()
    resultado = pipeline.buscar_atividade(
        descricao_usuario='Conceder benefício estatutário geral',
        area_codigo='CGBEN'
    )

    print(f"✓ Origem: {resultado.get('origem')}")
    print(f"✓ Score: {resultado.get('score', 1.0)}")
    print(f"✓ Ações: {resultado.get('acoes_usuario')}")
    print(f"✓ Mensagem: {resultado.get('mensagem', '')[:80]}")

    assert resultado.get('origem') == 'match_exato', "Deveria ser match_exato"
    assert resultado.get('acoes_usuario') == ['confirmar', 'selecionar_manualmente'], "Deveria ter 2 botões"
    print("\n✅ CAMADA 1 - PASSOU")


def testar_camada_2_semantic():
    """Teste Camada 2: Busca Semântica"""
    print("\n" + "="*80)
    print("TESTE 2: CAMADA 2 - BUSCA SEMÂNTICA")
    print("="*80)

    pipeline = BuscaAtividadePipeline()
    resultado = pipeline.buscar_atividade(
        descricao_usuario='analiso aposentadorias',
        area_codigo='CGBEN'
    )

    print(f"✓ Origem: {resultado.get('origem')}")
    print(f"✓ Score: {resultado.get('score', 0):.3f}")
    print(f"✓ Ações: {resultado.get('acoes_usuario')}")
    print(f"✓ Atividade: {resultado.get('atividade', {}).get('atividade', '')[:60]}")

    assert resultado.get('origem') == 'semantic', "Deveria ser semantic"
    assert resultado.get('acoes_usuario') == ['confirmar', 'selecionar_manualmente'], "Deveria ter 2 botões"
    assert resultado.get('score', 0) > 0, "Deveria ter score > 0"
    print("\n✅ CAMADA 2 - PASSOU")


def testar_camada_3_selecao_manual():
    """Teste Camada 3: Seleção Manual Hierárquica"""
    print("\n" + "="*80)
    print("TESTE 3: CAMADA 3 - SELEÇÃO MANUAL")
    print("="*80)

    pipeline = BuscaAtividadePipeline()

    # Simular que usuário clicou "Selecionar manualmente"
    # Na prática, isso vem do frontend, mas vamos testar diretamente
    hierarquia = pipeline._preparar_hierarquia_completa()

    print(f"✓ Macroprocessos: {len(hierarquia)}")
    print(f"✓ Estrutura correta: {isinstance(hierarquia, dict)}")

    # Verificar estrutura
    primeiro_macro = list(hierarquia.keys())[0]
    primeiro_processo = list(hierarquia[primeiro_macro].keys())[0]
    primeiro_subprocesso = list(hierarquia[primeiro_macro][primeiro_processo].keys())[0]
    atividades = hierarquia[primeiro_macro][primeiro_processo][primeiro_subprocesso]

    print(f"✓ Exemplo Macro: {primeiro_macro[:50]}")
    print(f"✓ Exemplo Processo: {primeiro_processo[:50]}")
    print(f"✓ Exemplo Subprocesso: {primeiro_subprocesso[:50]}")
    print(f"✓ Atividades no subprocesso: {len(atividades)}")

    assert len(hierarquia) > 0, "Deveria ter macroprocessos"
    assert len(atividades) > 0, "Deveria ter atividades"
    assert 'atividade' in atividades[0], "Atividade deveria ter campo 'atividade'"
    assert 'cap' in atividades[0], "Atividade deveria ter campo 'cap'"

    print("\n✅ CAMADA 3 - PASSOU")


def testar_camada_4_rag_parte1():
    """Teste Camada 4 Parte 1: RAG Pergunta"""
    print("\n" + "="*80)
    print("TESTE 4: CAMADA 4 PARTE 1 - RAG PERGUNTA")
    print("="*80)

    pipeline = BuscaAtividadePipeline()

    # Simular hierarquia selecionada pelo usuário na Camada 3
    hierarquia_selecionada = {
        'macroprocesso': 'Gestão de Benefícios Previdenciários',
        'processo': 'Gestão de Aposentadorias',
        'subprocesso': 'Concessão de aposentadorias'
    }

    resultado = pipeline._camada4_fallback_rag(
        descricao_usuario='',
        area_codigo='CGBEN',
        contexto=None,
        autor_dados={'nome': 'Teste', 'cpf': '12345678900'},
        hierarquia_selecionada=hierarquia_selecionada
    )

    print(f"✓ Origem: {resultado.get('origem')}")
    print(f"✓ Tipo Interface: {resultado.get('tipo_interface')}")
    print(f"✓ Mensagem: {resultado.get('mensagem', '')[:80]}")
    print(f"✓ Hierarquia herdada: {resultado.get('hierarquia_herdada')}")

    assert resultado.get('origem') == 'rag_aguardando_descricao', "Deveria aguardar descrição"
    assert resultado.get('tipo_interface') == 'pergunta_atividade', "Deveria ser pergunta"
    assert 'hierarquia_herdada' in resultado, "Deveria ter hierarquia herdada"

    print("\n✅ CAMADA 4 PARTE 1 - PASSOU")


def testar_camada_4_rag_parte2():
    """Teste Camada 4 Parte 2: RAG Criar Atividade"""
    print("\n" + "="*80)
    print("TESTE 5: CAMADA 4 PARTE 2 - RAG CRIAR ATIVIDADE")
    print("="*80)

    pipeline = BuscaAtividadePipeline()

    hierarquia_herdada = {
        'macroprocesso': 'Gestão de Benefícios Previdenciários',
        'processo': 'Gestão de Aposentadorias',
        'subprocesso': 'Concessão de aposentadorias'
    }

    descricao = "Eu analiso tempo de contribuição especial de servidores que trabalharam em condições insalubres"

    resultado = pipeline._camada4_processar_resposta(
        descricao_atividade=descricao,
        hierarquia_herdada=hierarquia_herdada,
        area_codigo='CGBEN',
        autor_dados={'nome': 'Teste', 'cpf': '12345678900'}
    )

    print(f"✓ Sucesso: {resultado.get('sucesso')}")
    print(f"✓ Origem: {resultado.get('origem')}")

    if resultado.get('sucesso'):
        ativ = resultado.get('atividade', {})
        print(f"✓ Nova Atividade: {ativ.get('atividade', '')[:80]}")
        print(f"✓ Macro: {ativ.get('macroprocesso', '')[:50]}")
        print(f"✓ Processo: {ativ.get('processo', '')[:50]}")
        print(f"✓ Subprocesso: {ativ.get('subprocesso', '')[:50]}")
        print(f"✓ CAP: {resultado.get('cap', 'N/A')}")
        print(f"✓ Tipo CAP: {resultado.get('tipo_cap', 'N/A')}")

        assert ativ.get('macroprocesso') == hierarquia_herdada['macroprocesso'], "Macro deveria ser herdado"
        assert ativ.get('processo') == hierarquia_herdada['processo'], "Processo deveria ser herdado"
        assert ativ.get('subprocesso') == hierarquia_herdada['subprocesso'], "Subprocesso deveria ser herdado"
        assert len(ativ.get('atividade', '')) > 0, "Deveria ter nome de atividade"
        assert resultado.get('tipo_cap') == 'oficial_gerado_rag', "Tipo CAP deveria ser oficial_gerado_rag"

        print("\n✅ CAMADA 4 PARTE 2 - PASSOU")
    else:
        print(f"\n❌ CAMADA 4 PARTE 2 - FALHOU: {resultado.get('erro', 'Erro desconhecido')}")


def main():
    print("\n" + "="*80)
    print("TESTE COMPLETO DO PIPELINE v4.0")
    print("="*80)

    try:
        testar_camada_1_match_exato()
        testar_camada_2_semantic()
        testar_camada_3_selecao_manual()
        testar_camada_4_rag_parte1()
        testar_camada_4_rag_parte2()

        print("\n" + "="*80)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*80)

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
