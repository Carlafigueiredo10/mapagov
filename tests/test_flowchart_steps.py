"""
Testes de manipulação de etapas do fluxograma.

Cobre:
1. _build_labeled_steps (helper puro)
2. insert_after / edit / remove via FlowchartAgent._executar_comando
3. Integridade de IDs e decisões após mutação
4. Regeneração do Mermaid
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')

import django
django.setup()

from processos.domain.helena_fluxograma.agents.flowchart_agent import FlowchartAgent
from processos.views import _build_labeled_steps


def _make_ctx(n=3):
    """Cria contexto com n etapas lineares."""
    etapas = [{'id': i, 'texto': f'Texto etapa {i}'} for i in range(1, n + 1)]
    return {
        '_version': '3',
        'campo_atual_idx': 2,
        'etapas': etapas,
        'decisoes': [],
        'fluxograma_gerado': True,
        'nome_processo': 'Teste',
        'proximo_etapa_id': n + 1,
    }


class TestBuildLabeledSteps(unittest.TestCase):

    def test_vazio(self):
        self.assertEqual(_build_labeled_steps([]), [])

    def test_normal(self):
        etapas = [{'id': 5, 'texto': 'A'}, {'id': 2, 'texto': 'B'}]
        result = _build_labeled_steps(etapas)
        self.assertEqual(result[0], {'id': 5, 'label': 'Etapa 1', 'texto': 'A'})
        self.assertEqual(result[1], {'id': 2, 'label': 'Etapa 2', 'texto': 'B'})


class TestInsertAfter(unittest.TestCase):

    def test_insert_no_meio(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        result = agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 2, 'texto': 'Nova'},
            ctx,
        )
        self.assertNotIn('erro', result)
        ids = [e['id'] for e in ctx['etapas']]
        self.assertEqual(ids, [1, 2, 4, 3])
        self.assertEqual(ctx['proximo_etapa_id'], 5)

    def test_insert_preserva_ids_existentes(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        original = {e['id'] for e in ctx['etapas']}
        agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 1, 'texto': 'X'},
            ctx,
        )
        current = {e['id'] for e in ctx['etapas']}
        self.assertTrue(original.issubset(current))

    def test_insert_nao_altera_decisoes(self):
        ctx = _make_ctx(3)
        ctx['decisoes'] = [
            {'id': 1, 'apos_etapa_id': 2, 'condicao': 'OK?', 'sim_id': 3, 'nao_id': 1}
        ]
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 1, 'texto': 'X'},
            ctx,
        )
        d = ctx['decisoes'][0]
        self.assertEqual(d['sim_id'], 3)
        self.assertEqual(d['nao_id'], 1)
        self.assertEqual(d['apos_etapa_id'], 2)

    def test_labels_recalculam(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 1, 'texto': 'Meio'},
            ctx,
        )
        labels = [s['label'] for s in _build_labeled_steps(ctx['etapas'])]
        self.assertEqual(labels, ['Etapa 1', 'Etapa 2', 'Etapa 3', 'Etapa 4'])

    def test_insert_etapa_inexistente_erro(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        result = agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 99, 'texto': 'X'},
            ctx,
        )
        self.assertIn('erro', result)


class TestEditStep(unittest.TestCase):

    def test_edit_mantem_id_e_posicao(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        agent._executar_comando(
            {'tipo': 'editar_etapa', 'id': 2, 'texto': 'Modificada'},
            ctx,
        )
        ids = [e['id'] for e in ctx['etapas']]
        self.assertEqual(ids, [1, 2, 3])
        self.assertEqual(ctx['etapas'][1]['texto'], 'Modificada')


class TestRemoveStep(unittest.TestCase):

    def test_remove_bloqueado_por_decisao(self):
        ctx = _make_ctx(3)
        ctx['decisoes'] = [
            {'id': 1, 'apos_etapa_id': 1, 'condicao': 'OK?', 'sim_id': 2, 'nao_id': 3}
        ]
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        result = agent._executar_comando(
            {'tipo': 'remover_etapa', 'id': 2},
            ctx,
        )
        self.assertIn('erro', result)
        self.assertEqual(len(ctx['etapas']), 3)

    def test_remove_sem_referencia_ok(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        result = agent._executar_comando(
            {'tipo': 'remover_etapa', 'id': 2},
            ctx,
        )
        self.assertNotIn('erro', result)
        ids = [e['id'] for e in ctx['etapas']]
        self.assertEqual(ids, [1, 3])


class TestMermaidRegeneration(unittest.TestCase):

    def test_mermaid_atualiza_apos_insert(self):
        ctx = _make_ctx(3)
        agent = FlowchartAgent()
        agent._init_contexto(ctx)
        agent._executar_comando(
            {'tipo': 'inserir_etapa', 'apos_id': 2, 'texto': 'Nova etapa'},
            ctx,
        )
        mermaid = agent.gerar_mermaid(ctx)
        self.assertIn('e4', mermaid)
        self.assertIn('Nova etapa', mermaid)
        self.assertIn('e1', mermaid)
        self.assertIn('e3', mermaid)


if __name__ == '__main__':
    unittest.main()
