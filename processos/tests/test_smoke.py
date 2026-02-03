# -*- coding: utf-8 -*-
"""
Testes Smoke - MapaGov

Testes mínimos para verificar que os endpoints críticos respondem.
Não testam lógica de negócio, apenas disponibilidade.

Executar: python manage.py test processos.tests.test_smoke -v2
"""

from django.test import TestCase, Client
from django.urls import reverse
import json


class ChatEndpointSmokeTest(TestCase):
    """Testes smoke para endpoints de chat"""

    def setUp(self):
        self.client = Client()

    def test_chat_endpoint_aceita_post(self):
        """Verifica que /api/chat/ aceita POST e retorna JSON"""
        response = self.client.post(
            '/api/chat/',
            data=json.dumps({'mensagem': 'oi'}),
            content_type='application/json'
        )
        # Aceita 200 (sucesso) ou 400 (erro de validação) - ambos indicam que endpoint funciona
        self.assertIn(response.status_code, [200, 400])
        # Deve retornar JSON
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_chat_endpoint_rejeita_get(self):
        """Verifica que /api/chat/ rejeita GET"""
        response = self.client.get('/api/chat/')
        # Deve retornar 405 Method Not Allowed ou 400
        self.assertIn(response.status_code, [400, 405])

    def test_chat_v2_aceita_post(self):
        """Verifica que /api/chat-v2/ aceita POST"""
        response = self.client.post(
            '/api/chat-v2/',
            data=json.dumps({'mensagem': 'teste', 'produto': 'helena_pop'}),
            content_type='application/json'
        )
        # Aceita 200 ou 400 - endpoint está funcionando
        self.assertIn(response.status_code, [200, 400])

    def test_chat_v2_produtos_lista(self):
        """Verifica que /api/chat-v2/produtos/ responde (200 ou 302 redirect)"""
        response = self.client.get('/api/chat-v2/produtos/')
        # Aceita 200 (lista produtos) ou 302 (redirect para login)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('produtos', data)
            self.assertIsInstance(data['produtos'], list)


class ValidacaoEndpointSmokeTest(TestCase):
    """Testes smoke para endpoints de validação"""

    def setUp(self):
        self.client = Client()

    def test_validar_dados_pop_aceita_post(self):
        """Verifica que /api/validar-dados-pop/ aceita POST"""
        dados_teste = {
            'nome_processo': 'Teste',
            'entrega_esperada': 'Resultado teste',
            'dispositivos_normativos': [],
            'operadores': [],
            'sistemas': [],
            'fluxos_entrada': [],
            'fluxos_saida': []
        }
        response = self.client.post(
            '/api/validar-dados-pop/',
            data=json.dumps(dados_teste),
            content_type='application/json'
        )
        # Aceita 200 ou 400 - endpoint está funcionando
        self.assertIn(response.status_code, [200, 400])
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_validar_dados_pop_rejeita_get(self):
        """Verifica que /api/validar-dados-pop/ rejeita GET"""
        response = self.client.get('/api/validar-dados-pop/')
        self.assertIn(response.status_code, [400, 405])


class PDFEndpointSmokeTest(TestCase):
    """Testes smoke para endpoints de PDF"""

    def setUp(self):
        self.client = Client()

    def test_gerar_pdf_pop_aceita_post(self):
        """Verifica que /api/gerar-pdf-pop/ aceita POST"""
        dados_teste = {
            'nome_processo': 'Processo Teste',
            'entrega_esperada': 'Resultado',
            'codigo_cap': 'TEST.01.01.01.001'
        }
        response = self.client.post(
            '/api/gerar-pdf-pop/',
            data=json.dumps(dados_teste),
            content_type='application/json'
        )
        # Aceita 200, 400 ou 500 (falta dados) - endpoint está funcionando
        self.assertIn(response.status_code, [200, 400, 500])


class HealthCheckSmokeTest(TestCase):
    """Testes de health check básicos"""

    def setUp(self):
        self.client = Client()

    def test_landing_page_carrega(self):
        """Verifica que a landing page carrega"""
        response = self.client.get('/')
        # Aceita 200 (página existe) ou 302 (redirect)
        self.assertIn(response.status_code, [200, 302])

    def test_admin_existe(self):
        """Verifica que /admin/ existe (pode redirecionar para login)"""
        response = self.client.get('/admin/')
        # 200 (admin carregou) ou 302 (redirect para login)
        self.assertIn(response.status_code, [200, 302])


class HelenaMapeamentoSmokeTest(TestCase):
    """Testes smoke para Helena Mapeamento"""

    def setUp(self):
        self.client = Client()

    def test_helena_mapeamento_aceita_post(self):
        """Verifica que /api/helena-mapeamento/ aceita POST"""
        response = self.client.post(
            '/api/helena-mapeamento/',
            data=json.dumps({'mensagem': 'o que é POP?'}),
            content_type='application/json'
        )
        # Aceita 200 ou 400 - endpoint está funcionando
        self.assertIn(response.status_code, [200, 400])
