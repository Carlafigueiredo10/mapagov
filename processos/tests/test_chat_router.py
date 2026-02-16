# -*- coding: utf-8 -*-
"""
Testes do roteador de contexto (HelenaCore)

Testa:
- Detecção de mudança de contexto por palavras-chave
- Mudança explícita de contexto (mudar_contexto)
- Validações de contexto inválido
- Registry vazio

Executar: python manage.py test processos.tests.test_chat_router -v2
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase

from processos.app.helena_core import HelenaCore
from processos.domain.base import BaseHelena


class FakeProduto(BaseHelena):
    """Produto fake para testes sem dependência de IA."""

    VERSION = "0.0.1"
    PRODUTO_NOME = "Fake"

    def processar(self, mensagem, session_data):
        return {
            'resposta': f"fake: {mensagem}",
            'novo_estado': session_data,
            'metadados': {},
        }

    def inicializar_estado(self, **kwargs):
        return {'etapa_atual': 0}


class TestDetectarMudancaContexto(TestCase):
    """Testa _detectar_mudanca_contexto do HelenaCore."""

    def setUp(self):
        self.registry = {
            'pop': FakeProduto(),
            'etapas': FakeProduto(),
            'mapeamento': FakeProduto(),
        }
        self.core = HelenaCore(registry=self.registry)
        self.session = MagicMock()
        self.session.contexto_atual = 'pop'

    def test_sem_mudanca_mensagem_normal(self):
        """Mensagem comum não deve mudar contexto."""
        resultado = self.core._detectar_mudanca_contexto("Olá, bom dia", self.session)
        self.assertIsNone(resultado)

    def test_mudar_para_detecta_contexto(self):
        """'mudar para etapas' deve detectar contexto 'etapas'."""
        resultado = self.core._detectar_mudanca_contexto("mudar para etapas", self.session)
        self.assertEqual(resultado, 'etapas')

    def test_trocar_para_detecta_contexto(self):
        """'trocar para mapeamento' deve detectar contexto 'mapeamento'."""
        resultado = self.core._detectar_mudanca_contexto("trocar para mapeamento", self.session)
        self.assertEqual(resultado, 'mapeamento')

    def test_contexto_inexistente_nao_detecta(self):
        """'mudar para xyz' não deve detectar (contexto não existe)."""
        resultado = self.core._detectar_mudanca_contexto("mudar para xyz", self.session)
        self.assertIsNone(resultado)

    def test_case_insensitive(self):
        """Deve funcionar independente de maiúsculas/minúsculas."""
        resultado = self.core._detectar_mudanca_contexto("MUDAR PARA POP", self.session)
        self.assertEqual(resultado, 'pop')

    def test_produto_sugere_mudanca(self):
        """Se produto atual sugere mudança, usar sugestão."""
        produto_mock = MagicMock(spec=BaseHelena)
        produto_mock.detectar_intencao_mudanca_contexto.return_value = 'mapeamento'
        self.core.registry['pop'] = produto_mock

        resultado = self.core._detectar_mudanca_contexto("quero mapear", self.session)
        self.assertEqual(resultado, 'mapeamento')

    def test_produto_sugere_contexto_invalido_ignora(self):
        """Se produto sugere contexto fora do registry, ignora."""
        produto_mock = MagicMock(spec=BaseHelena)
        produto_mock.detectar_intencao_mudanca_contexto.return_value = 'inexistente'
        self.core.registry['pop'] = produto_mock

        resultado = self.core._detectar_mudanca_contexto("algo", self.session)
        self.assertIsNone(resultado)


class TestMudarContexto(TestCase):
    """Testa mudar_contexto (mudança explícita via API)."""

    def setUp(self):
        self.registry = {
            'pop': FakeProduto(),
            'etapas': FakeProduto(),
        }
        self.core = HelenaCore(registry=self.registry)

    @patch.object(HelenaCore, '_detectar_mudanca_contexto', return_value=None)
    def test_mudar_para_contexto_valido(self, _mock):
        """Mudança para contexto válido deve retornar sucesso."""
        session_mock = MagicMock()
        session_mock.contexto_atual = 'pop'
        self.core.session_manager = MagicMock()
        self.core.session_manager.get_or_create_session.return_value = session_mock

        resultado = self.core.mudar_contexto(
            session_id='test-session',
            novo_contexto='etapas',
            user=MagicMock()
        )

        self.assertEqual(resultado['contexto_atual'], 'etapas')
        self.assertEqual(resultado['contexto_anterior'], 'pop')

    def test_mudar_para_contexto_invalido_lanca_erro(self):
        """Mudança para contexto inválido deve lançar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.core.mudar_contexto(
                session_id='test-session',
                novo_contexto='inexistente',
                user=MagicMock()
            )
        self.assertIn('inexistente', str(ctx.exception))
        self.assertIn('Disponíveis', str(ctx.exception))


class TestRegistryValidacao(TestCase):
    """Testa validações do registry."""

    def test_registry_vazio_lanca_erro(self):
        """Registry vazio deve lançar ValueError."""
        with self.assertRaises(ValueError):
            HelenaCore(registry={})

    def test_registry_com_produto_funciona(self):
        """Registry com pelo menos 1 produto deve funcionar."""
        core = HelenaCore(registry={'pop': FakeProduto()})
        self.assertIn('pop', core.registry)

    def test_listar_produtos(self):
        """listar_produtos deve retornar nome e versão de cada produto."""
        core = HelenaCore(registry={
            'pop': FakeProduto(),
            'etapas': FakeProduto(),
        })
        produtos = core.listar_produtos()
        self.assertEqual(len(produtos), 2)
        self.assertIn('pop', produtos)
        self.assertEqual(produtos['pop']['nome'], 'Fake')
        self.assertEqual(produtos['pop']['versao'], '0.0.1')
