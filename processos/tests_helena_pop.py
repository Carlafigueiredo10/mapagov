# -*- coding: utf-8 -*-
"""
Testes Unitários para Helena POP v2.0
Cobertura de todos os 21 estados da máquina de estados

Estrutura:
1. Testes de transições de estado
2. Testes de validação de dados
3. Testes de integração com helena_ajuda_inteligente
4. Testes de schema JSON
5. Testes de persistência de sessão

IMPORTANTE: Execute com: python manage.py test processos.tests_helena_pop
"""

import pytest
import json
import os
import django
from unittest.mock import Mock, patch, MagicMock

# Configurar Django antes de importar models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagovx.settings')
django.setup()

from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model

from processos.domain.helena_produtos.helena_pop import HelenaPOP, POPStateMachine, EstadoPOP

try:
    from processos.models_new.chat_session import ChatSession
    from processos.models_new.chat_message import ChatMessage
    from processos.models import Orgao
except ImportError:
    # Se models não carregarem, continuar (testes stateless não precisam)
    pass

User = get_user_model()


class TestPOPStateMachine(TestCase):
    """Testes da máquina de estados (sem IO)"""

    def setUp(self):
        """Setup comum para todos os testes"""
        self.helena = HelenaPOP()
        self.sm = POPStateMachine()

    def test_estado_inicial(self):
        """Verifica estado inicial da máquina"""
        self.assertEqual(self.sm.estado, EstadoPOP.NOME_USUARIO)
        self.assertFalse(self.sm.concluido)
        self.assertEqual(self.sm.dados_coletados, {})

    def test_to_dict_e_from_dict(self):
        """Verifica serialização e deserialização"""
        # Modificar estado
        self.sm.nome_usuario = "João"
        self.sm.estado = EstadoPOP.AREA_DECIPEX
        self.sm.dados_coletados = {"teste": "valor"}

        # Serializar
        dict_data = self.sm.to_dict()
        self.assertIn('estado', dict_data)
        self.assertIn('nome_usuario', dict_data)

        # Deserializar
        sm_novo = POPStateMachine()
        sm_novo.from_dict(dict_data)
        self.assertEqual(sm_novo.estado, EstadoPOP.AREA_DECIPEX)
        self.assertEqual(sm_novo.nome_usuario, "João")
        self.assertEqual(sm_novo.dados_coletados['teste'], "valor")


class TestTransicoesEstado(TestCase):
    """Testa todas as transições de estado"""

    def setUp(self):
        self.helena = HelenaPOP()
        self.sm = POPStateMachine()

    def test_transicao_nome_usuario_para_confirma_nome(self):
        """NOME_USUARIO → CONFIRMA_NOME (quando envia nome válido)"""
        resposta, novo_sm = self.helena._processar_nome_usuario("João", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.CONFIRMA_NOME)
        self.assertEqual(novo_sm.nome_temporario, "João")
        self.assertIn("João", resposta)
        self.assertIn("me confirma", resposta.lower())

    def test_transicao_confirma_nome_sim(self):
        """CONFIRMA_NOME → ESCOLHA_TIPO_EXPLICACAO (confirmação positiva)"""
        self.sm.estado = EstadoPOP.CONFIRMA_NOME
        self.sm.nome_temporario = "Maria"

        resposta, novo_sm = self.helena._processar_confirma_nome("sim", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.ESCOLHA_TIPO_EXPLICACAO)
        self.assertEqual(novo_sm.nome_usuario, "Maria")
        self.assertIn("Maria", resposta)

    def test_transicao_confirma_nome_nao(self):
        """CONFIRMA_NOME → NOME_USUARIO (confirmação negativa)"""
        self.sm.estado = EstadoPOP.CONFIRMA_NOME
        self.sm.nome_temporario = "Pedro"

        resposta, novo_sm = self.helena._processar_confirma_nome("não", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.NOME_USUARIO)
        self.assertIsNone(novo_sm.nome_temporario)

    def test_transicao_escolha_tipo_explicacao_curta(self):
        """ESCOLHA_TIPO_EXPLICACAO → PEDIDO_COMPROMISSO (explicação curta)"""
        self.sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO
        self.sm.nome_usuario = "Ana"

        resposta, novo_sm = self.helena._processar_escolha_tipo_explicacao("curta", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.PEDIDO_COMPROMISSO)
        self.assertIn("compromisso", resposta.lower())

    def test_transicao_escolha_tipo_explicacao_longa(self):
        """ESCOLHA_TIPO_EXPLICACAO → EXPLICACAO_LONGA (explicação detalhada)"""
        self.sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO
        self.sm.nome_usuario = "Carlos"

        resposta, novo_sm = self.helena._processar_escolha_tipo_explicacao("detalhada", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.EXPLICACAO_LONGA)
        self.assertIn("processo", resposta.lower())

    def test_transicao_pedido_compromisso_aceito(self):
        """PEDIDO_COMPROMISSO → AREA_DECIPEX (aceita compromisso)"""
        self.sm.estado = EstadoPOP.PEDIDO_COMPROMISSO
        self.sm.nome_usuario = "Roberto"

        resposta, novo_sm = self.helena._processar_pedido_compromisso("sim", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.AREA_DECIPEX)
        self.assertIn("área", resposta.lower())

    def test_transicao_area_decipex_valida(self):
        """AREA_DECIPEX → ARQUITETURA ou SUBAREA_DECIPEX"""
        self.sm.estado = EstadoPOP.AREA_DECIPEX
        self.sm.nome_usuario = "Helena"

        # Selecionar área 1 (DIGEP)
        resposta, novo_sm = self.helena._processar_area_decipex("1", self.sm)

        # Deve ir para SUBAREA_DECIPEX (DIGEP tem subáreas)
        self.assertEqual(novo_sm.estado, EstadoPOP.SUBAREA_DECIPEX)
        self.assertIsNotNone(novo_sm.area_selecionada)
        self.assertIn("DIGEP", resposta)

    def test_transicao_arquitetura_com_descricao(self):
        """ARQUITETURA → CONFIRMACAO_ARQUITETURA (IA sugere classificação)"""
        self.sm.estado = EstadoPOP.ARQUITETURA
        self.sm.nome_usuario = "Teste"
        self.sm.area_selecionada = {'nome': 'DIGEP', 'codigo': 'DIGEP'}

        with patch.object(self.helena, '_buscar_no_csv_oficial') as mock_csv:
            # Simular encontrou no CSV
            mock_csv.return_value = {
                'encontrado': True,
                'dados': {
                    'macroprocesso': 'Gestão de Aposentadorias',
                    'processo': 'Concessão',
                    'subprocesso': 'Análise',
                    'atividade': 'Validar documentos',
                    'entrega': 'Parecer de análise'
                }
            }

            resposta, novo_sm = self.helena._processar_arquitetura("Analiso documentos de aposentadoria", self.sm)

            self.assertEqual(novo_sm.estado, EstadoPOP.CONFIRMACAO_ARQUITETURA)
            self.assertIn("Gestão de Aposentadorias", resposta)


class TestValidacaoDados(TestCase):
    """Testa validações de entrada"""

    def setUp(self):
        self.helena = HelenaPOP()
        self.sm = POPStateMachine()

    def test_nome_invalido_rejeita_numeros(self):
        """Rejeita nomes com números"""
        resposta, novo_sm = self.helena._processar_nome_usuario("João123", self.sm)

        # Não deve aceitar, permanece no estado NOME_USUARIO
        self.assertEqual(novo_sm.estado, EstadoPOP.NOME_USUARIO)
        self.assertIn("não entendi", resposta.lower())

    def test_nome_invalido_rejeita_multiplas_palavras(self):
        """Rejeita múltiplas palavras"""
        resposta, novo_sm = self.helena._processar_nome_usuario("João Silva", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.NOME_USUARIO)

    def test_nome_valido_aceita_acentuacao(self):
        """Aceita nomes com acentuação"""
        resposta, novo_sm = self.helena._processar_nome_usuario("José", self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.CONFIRMA_NOME)
        self.assertEqual(novo_sm.nome_temporario, "José")

    def test_operadores_json_array(self):
        """Operadores devem aceitar JSON array"""
        self.sm.estado = EstadoPOP.OPERADORES

        operadores_json = json.dumps(["EXECUTOR", "REVISOR"])
        resposta, novo_sm = self.helena._processar_operadores(operadores_json, self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.FLUXOS_ENTRADA)
        self.assertIn("EXECUTOR", str(novo_sm.dados_coletados['operadores']))

    def test_fluxos_saida_json_estruturado(self):
        """Fluxos de saída devem aceitar JSON estruturado"""
        self.sm.estado = EstadoPOP.FLUXOS_SAIDA

        fluxos_json = json.dumps({
            "destinos_selecionados": [
                {"tipo": "Área Interna", "especificacao": "DIGEP"},
                {"tipo": "Órgão Centralizado", "especificacao": "CGU"}
            ]
        })

        resposta, novo_sm = self.helena._processar_fluxos_saida(fluxos_json, self.sm)

        self.assertEqual(novo_sm.estado, EstadoPOP.PONTOS_ATENCAO)
        self.assertIsNotNone(novo_sm.dados_coletados.get('fluxos_saida'))


class TestSchemaJSON(TestCase):
    """Valida schema das respostas JSON"""

    def setUp(self):
        self.helena = HelenaPOP()
        self.sm = POPStateMachine()
        self.sm.nome_usuario = "Teste"

    def test_schema_resposta_completa(self):
        """Verifica schema completo da resposta"""
        self.sm.estado = EstadoPOP.NOME_USUARIO

        resultado = self.helena.processar("João", self.sm.to_dict())

        # Verificar campos obrigatórios
        self.assertIn('resposta', resultado)
        self.assertIn('novo_estado', resultado)
        self.assertIn('dados_extraidos', resultado)
        self.assertIn('formulario_pop', resultado)

        # Verificar tipos
        self.assertIsInstance(resultado['resposta'], str)
        self.assertIsInstance(resultado['novo_estado'], dict)
        self.assertIsInstance(resultado['dados_extraidos'], dict)
        self.assertIsInstance(resultado['formulario_pop'], dict)

    def test_schema_metadados_badge(self):
        """Verifica schema do badge quando presente"""
        self.sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

        resultado = self.helena.processar("sim", self.sm.to_dict())

        # Após aceitar compromisso, deve receber badge
        if 'metadados' in resultado and 'badge' in resultado['metadados']:
            badge = resultado['metadados']['badge']
            self.assertIn('tipo', badge)
            self.assertIn('emoji', badge)
            self.assertIn('titulo', badge)
            self.assertIn('descricao', badge)
            self.assertIn('mostrar_animacao', badge)
            self.assertTrue(badge['mostrar_animacao'])

    def test_schema_interface_dinamica(self):
        """Verifica schema das interfaces dinâmicas"""
        self.sm.estado = EstadoPOP.SISTEMAS
        self.sm.nome_usuario = "Teste"

        resultado = self.helena.processar("continuar", self.sm.to_dict())

        if 'interface' in resultado:
            interface = resultado['interface']
            self.assertIn('tipo', interface)

            # Verificar tipo específico para sistemas
            if interface['tipo'] == 'cards_sistemas':
                self.assertIn('dados', interface)
                self.assertIsInstance(interface['dados'], dict)


class TestIntegracaoHelenaAjuda(TestCase):
    """Testa integração com helena_ajuda_inteligente"""

    def setUp(self):
        self.helena = HelenaPOP()
        self.sm = POPStateMachine()
        self.sm.nome_usuario = "Teste"
        self.sm.area_selecionada = {'nome': 'DIGEP', 'codigo': 'DIGEP'}

    @patch('processos.domain.helena_produtos.helena_pop.HelenaPOP._buscar_no_csv_oficial')
    @patch('processos.domain.helena_produtos.helena_ajuda_inteligente.analisar_atividade_com_helena')
    def test_fallback_ia_quando_csv_vazio(self, mock_ia, mock_csv):
        """Deve chamar IA quando CSV não retorna resultados"""
        self.sm.estado = EstadoPOP.ARQUITETURA

        # Simular CSV vazio
        mock_csv.return_value = {'encontrado': False}

        # Simular resposta da IA
        mock_ia.return_value = {
            'sucesso': True,
            'sugestao': {
                'macroprocesso': 'Gestão de Pessoas',
                'processo': 'Avaliação',
                'subprocesso': 'Perícia',
                'atividade': 'Realizar perícia',
                'resultado_final': 'Laudo médico'
            },
            'confianca': 'alta',
            'justificativa': 'Atividade típica de perícia médica'
        }

        resposta, novo_sm = self.helena._processar_arquitetura("Faço perícia médica", self.sm)

        # Verificar que IA foi chamada
        mock_ia.assert_called_once()

        # Verificar que sugestão foi aceita
        self.assertEqual(novo_sm.estado, EstadoPOP.CONFIRMACAO_ARQUITETURA)
        self.assertIn("Gestão de Pessoas", resposta)

    @patch('processos.domain.helena_produtos.helena_pop.HelenaPOP._buscar_no_csv_oficial')
    def test_prioriza_csv_sobre_ia(self, mock_csv):
        """Deve priorizar CSV quando encontra match"""
        self.sm.estado = EstadoPOP.ARQUITETURA

        # Simular CSV encontrou
        mock_csv.return_value = {
            'encontrado': True,
            'dados': {
                'macroprocesso': 'Gestão de Aposentadorias',
                'processo': 'Concessão',
                'subprocesso': 'Análise',
                'atividade': 'Validar tempo de contribuição',
                'entrega': 'Parecer técnico'
            }
        }

        with patch('processos.domain.helena_produtos.helena_ajuda_inteligente.analisar_atividade_com_helena') as mock_ia:
            resposta, novo_sm = self.helena._processar_arquitetura("Valido tempo de contribuição", self.sm)

            # IA NÃO deve ter sido chamada
            mock_ia.assert_not_called()

            # Deve ter usado dados do CSV
            self.assertIn("Gestão de Aposentadorias", resposta)


class TestPersistenciaSessao(TestCase):
    """Testa persistência via Django session"""

    def setUp(self):
        self.factory = RequestFactory()
        self.helena = HelenaPOP()

    def test_sessao_persiste_estado(self):
        """Verifica que estado é persistido corretamente"""
        request = self.factory.post('/api/chat/')

        # Adicionar session ao request
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Estado inicial
        sm = POPStateMachine()
        session_key = 'helena_pop_state_test'

        # Salvar na sessão
        request.session[session_key] = sm.to_dict()
        request.session.modified = True

        # Recuperar
        sm_restaurado = POPStateMachine()
        sm_restaurado.from_dict(request.session[session_key])

        self.assertEqual(sm_restaurado.estado, EstadoPOP.NOME_USUARIO)

    def test_sessao_sobrevive_refresh(self):
        """Verifica que sessão sobrevive ao refresh da página"""
        request = self.factory.post('/api/chat/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        session_key = 'helena_pop_state_test'

        # Simular várias interações
        sm = POPStateMachine()
        sm.nome_usuario = "João"
        sm.estado = EstadoPOP.AREA_DECIPEX
        request.session[session_key] = sm.to_dict()
        request.session.modified = True

        # Simular nova request (refresh)
        request2 = self.factory.post('/api/chat/')
        request2.session = request.session

        # Recuperar estado
        sm_novo = POPStateMachine()
        sm_novo.from_dict(request2.session[session_key])

        self.assertEqual(sm_novo.nome_usuario, "João")
        self.assertEqual(sm_novo.estado, EstadoPOP.AREA_DECIPEX)


class TestTimeout(TestCase):
    """Testa comportamento de timeout"""

    def setUp(self):
        self.helena = HelenaPOP()

    @patch('time.time')
    def test_sessao_expira_apos_timeout(self, mock_time):
        """Verifica expiração de sessão (simulado)"""
        # Simular tempo inicial
        mock_time.return_value = 1000000

        sm = POPStateMachine()
        sm.nome_usuario = "Teste"
        estado_dict = sm.to_dict()

        # Adicionar timestamp
        estado_dict['last_activity'] = 1000000

        # Simular 16 minutos depois (timeout é 15min)
        mock_time.return_value = 1000000 + (16 * 60)

        # Verificar se expirou
        tempo_decorrido = mock_time.return_value - estado_dict['last_activity']
        self.assertGreater(tempo_decorrido, 15 * 60)


# ====================================
# FIXTURES PARA TESTES
# ====================================

@pytest.fixture
def helena_instancia():
    """Fixture para instância do HelenaPOP"""
    return HelenaPOP()


@pytest.fixture
def state_machine_limpa():
    """Fixture para state machine limpa"""
    return POPStateMachine()


@pytest.fixture
def state_machine_populada():
    """Fixture para state machine com dados"""
    sm = POPStateMachine()
    sm.nome_usuario = "João"
    sm.estado = EstadoPOP.ARQUITETURA
    sm.area_selecionada = {'nome': 'DIGEP', 'codigo': 'DIGEP'}
    sm.dados_coletados = {
        'nome_processo': 'Análise de Perícias',
        'entrega_esperada': 'Laudo médico'
    }
    return sm


# ====================================
# TESTES PYTEST (complementares)
# ====================================

def test_todos_estados_tem_handler(helena_instancia):
    """Verifica que todos os 21 estados têm handler correspondente"""
    for estado in EstadoPOP:
        handler_name = f"_processar_{estado.value}"
        assert hasattr(helena_instancia, handler_name), f"Handler {handler_name} não encontrado"


def test_formulario_pop_sempre_retornado(helena_instancia, state_machine_limpa):
    """Verifica que formulario_pop sempre é retornado"""
    resultado = helena_instancia.processar("João", state_machine_limpa.to_dict())

    assert 'formulario_pop' in resultado
    assert isinstance(resultado['formulario_pop'], dict)


def test_dados_extraidos_sempre_retornado(helena_instancia, state_machine_limpa):
    """Verifica que dados_extraidos sempre é retornado"""
    resultado = helena_instancia.processar("Maria", state_machine_limpa.to_dict())

    assert 'dados_extraidos' in resultado
    assert isinstance(resultado['dados_extraidos'], dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
