#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples do Pipeline de Busca em 5 Camadas
"""

import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from processos.domain.helena_produtos.busca_atividade_pipeline import BuscaAtividadePipeline

def testar_pipeline():
    """Testa o pipeline com casos variados"""

    print("="*80)
    print("TESTE DO PIPELINE DE BUSCA EM 5 CAMADAS")
    print("="*80)

    # Inicializar pipeline
    pipeline = BuscaAtividadePipeline()

    # Casos de teste
    casos_teste = [
        # Caso 1: Termo exato (deve encontrar na Camada 1)
        {
            'descricao': 'Conceder benefício estatutário geral',
            'area_codigo': 'CGBEN',
            'esperado': 'match_exato'
        },
        # Caso 2: Termo similar (deve encontrar na Camada 1 ou 2)
        {
            'descricao': 'analiso aposentadorias',
            'area_codigo': 'CGBEN',
            'esperado': 'match_fuzzy ou semantic'
        },
        # Caso 3: Termo muito genérico (pode ir para Camada 4 ou 5)
        {
            'descricao': 'trabalho com pensões',
            'area_codigo': 'CGBEN',
            'esperado': 'semantic ou rag'
        },
        # Caso 4: Termo completamente novo (deve ir para Camada 5)
        {
            'descricao': 'desenvolvo sistemas de machine learning para previsão de demandas',
            'area_codigo': 'CGTIC',
            'esperado': 'nova'
        }
    ]

    resultados = []

    for i, caso in enumerate(casos_teste, 1):
        print(f"\n{'='*80}")
        print(f"CASO {i}: {caso['descricao']}")
        print(f"   Area: {caso['area_codigo']}")
        print(f"   Esperado: {caso['esperado']}")
        print(f"{'='*80}\n")

        try:
            resultado = pipeline.buscar_atividade(
                descricao_usuario=caso['descricao'],
                area_codigo=caso['area_codigo'],
                contexto=None,
                autor_dados={'nome': 'Teste', 'cpf': '00000000000'}
            )

            print(f"\n[OK] Resultado:")
            print(f"   Origem: {resultado.get('origem')}")
            print(f"   Score: {resultado.get('score', 0):.3f}")
            print(f"   Sucesso: {resultado.get('sucesso')}")

            if resultado.get('atividade'):
                ativ = resultado['atividade']
                print(f"\n   Atividade encontrada:")
                print(f"      Macro: {ativ.get('macroprocesso')}")
                print(f"      Processo: {ativ.get('processo')}")
                print(f"      Subprocesso: {ativ.get('subprocesso')}")
                print(f"      Atividade: {ativ.get('atividade')}")
                print(f"      CAP: {resultado.get('cap')}")

            if resultado.get('candidatos'):
                print(f"\n   Candidatos (dropdown): {len(resultado['candidatos'])}")
                for j, cand in enumerate(resultado['candidatos'][:3], 1):
                    print(f"      {j}. {cand['atividade']} (score: {cand['score']:.3f})")

            resultados.append({
                'caso': i,
                'descricao': caso['descricao'],
                'origem': resultado.get('origem'),
                'score': resultado.get('score', 0),
                'sucesso': resultado.get('sucesso')
            })

        except Exception as e:
            print(f"\n[ERRO] Erro no teste: {e}")
            import traceback
            traceback.print_exc()
            resultados.append({
                'caso': i,
                'descricao': caso['descricao'],
                'erro': str(e)
            })

    # Resumo
    print(f"\n\n{'='*80}")
    print("RESUMO DOS TESTES")
    print(f"{'='*80}\n")

    for res in resultados:
        status = "[OK]" if res.get('sucesso') else ("[WARN]" if res.get('origem') == 'dropdown_required' else "[ERRO]")
        print(f"{status} Caso {res['caso']}: {res.get('origem', 'ERRO')} (score: {res.get('score', 0):.3f})")

    print(f"\n{'='*80}")
    print("TESTE CONCLUIDO!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    testar_pipeline()
