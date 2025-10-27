"""
Testes Unitários para Helena POP v2.0

Cobertura:
- Inicialização e herança de BaseHelena
- State machine transitions
- Processamento de mensagens
- Validações
- Serialização/Deserialização
- Golden tests de payload
"""
import pytest
import json
from processos.domain.helena_produtos.helena_pop import (
    HelenaPOP, POPStateMachine, EstadoPOP
)
from processos.domain.base import BaseHelena


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def helena_pop():
    """Instância limpa de Helena POP"""
    return HelenaPOP()


@pytest.fixture
def estado_inicial():
    """Estado inicial limpo"""
    return HelenaPOP().inicializar_estado()


@pytest.fixture
def state_machine_boas_vindas():
    """State machine no estado BOAS_VINDAS"""
    return POPStateMachine()


@pytest.fixture
def state_machine_nome_usuario():
    """State machine no estado NOME_USUARIO"""
    sm = POPStateMachine()
    sm.estado = EstadoPOP.NOME_USUARIO
    return sm


@pytest.fixture
def state_machine_confirma_nome():
    """State machine no estado CONFIRMA_NOME com nome temporário"""
    sm = POPStateMachine()
    sm.estado = EstadoPOP.CONFIRMA_NOME
    sm.nome_temporario = "Roberto"
    return sm


# ============================================================================
# TESTES DE INICIALIZAÇÃO
# ============================================================================

class TestInicializacao:
    """Testes de inicialização e configuração"""

    def test_heranca_base_helena(self, helena_pop):
        """Helena POP deve herdar de BaseHelena"""
        assert isinstance(helena_pop, BaseHelena)

    def test_versao_correta(self, helena_pop):
        """Helena POP deve ter versão 2.0.0"""
        assert helena_pop.VERSION == "2.0.0"

    def test_produto_nome(self, helena_pop):
        """Helena POP deve ter nome correto"""
        assert helena_pop.PRODUTO_NOME == "Helena POP"

    def test_areas_decipex_existem(self, helena_pop):
        """AREAS_DECIPEX deve ter 8 áreas"""
        areas = helena_pop.AREAS_DECIPEX
        assert len(areas) == 8
        assert 1 in areas
        assert areas[1]['codigo'] == 'CGBEN'

    def test_sistemas_decipex_existem(self, helena_pop):
        """SISTEMAS_DECIPEX deve ter categorias"""
        sistemas = helena_pop.SISTEMAS_DECIPEX
        assert 'gestao_pessoal' in sistemas
        assert 'documentos' in sistemas
        assert 'SIAPE' in sistemas['gestao_pessoal']

    def test_operadores_decipex_existem(self, helena_pop):
        """OPERADORES_DECIPEX deve ter lista de operadores"""
        operadores = helena_pop.OPERADORES_DECIPEX
        assert len(operadores) > 0
        assert 'Técnico Especializado' in operadores


# ============================================================================
# TESTES DE ESTADO INICIAL
# ============================================================================

class TestEstadoInicial:
    """Testes de inicialização de estado"""

    def test_estado_inicial_dict(self, estado_inicial):
        """Estado inicial deve ser um dicionário"""
        assert isinstance(estado_inicial, dict)

    def test_estado_inicial_tem_estado(self, estado_inicial):
        """Estado inicial deve ter campo 'estado'"""
        assert 'estado' in estado_inicial
        assert estado_inicial['estado'] == EstadoPOP.BOAS_VINDAS.value

    def test_estado_inicial_tem_dados_coletados(self, estado_inicial):
        """Estado inicial deve ter dados_coletados vazio"""
        assert 'dados_coletados' in estado_inicial
        assert isinstance(estado_inicial['dados_coletados'], dict)

    def test_estado_inicial_nao_concluido(self, estado_inicial):
        """Estado inicial deve ter concluido=False"""
        assert 'concluido' in estado_inicial
        assert estado_inicial['concluido'] is False


# ============================================================================
# TESTES DE STATE MACHINE
# ============================================================================

class TestStateMachine:
    """Testes de POPStateMachine"""

    def test_criar_state_machine(self):
        """Deve criar state machine com estado inicial"""
        sm = POPStateMachine()
        assert sm.estado == EstadoPOP.BOAS_VINDAS
        assert sm.nome_usuario == ""
        assert sm.concluido is False

    def test_serializar_to_dict(self, state_machine_boas_vindas):
        """Deve serializar state machine para dict"""
        data = state_machine_boas_vindas.to_dict()
        assert isinstance(data, dict)
        assert data['estado'] == EstadoPOP.BOAS_VINDAS.value
        assert 'dados_coletados' in data

    def test_deserializar_from_dict(self):
        """Deve deserializar dict para state machine"""
        data = {
            'estado': EstadoPOP.NOME_USUARIO.value,
            'nome_usuario': 'João',
            'nome_temporario': '',
            'area_selecionada': None,
            'dados_coletados': {'nome_processo': 'Teste'},
            'concluido': False
        }
        sm = POPStateMachine.from_dict(data)
        assert sm.estado == EstadoPOP.NOME_USUARIO
        assert sm.nome_usuario == 'João'
        assert sm.dados_coletados['nome_processo'] == 'Teste'

    def test_roundtrip_serialization(self, state_machine_confirma_nome):
        """Serialização roundtrip deve preservar dados"""
        original = state_machine_confirma_nome
        data = original.to_dict()
        restored = POPStateMachine.from_dict(data)

        assert restored.estado == original.estado
        assert restored.nome_temporario == original.nome_temporario


# ============================================================================
# TESTES DE PROCESSAMENTO - BOAS VINDAS
# ============================================================================

class TestProcessamentoBoasVindas:
    """Testes de processamento no estado BOAS_VINDAS"""

    def test_processar_primeira_mensagem(self, helena_pop, estado_inicial):
        """Primeira mensagem deve responder com boas-vindas"""
        resultado = helena_pop.processar("Olá", estado_inicial)

        assert 'resposta' in resultado
        assert 'Helena' in resultado['resposta']
        assert 'novo_estado' in resultado
        assert resultado['novo_estado']['estado'] == EstadoPOP.NOME_USUARIO.value

    def test_progresso_inicial(self, helena_pop, estado_inicial):
        """Progresso deve ser calculado corretamente"""
        resultado = helena_pop.processar("Olá", estado_inicial)
        assert 'progresso' in resultado
        assert resultado['progresso'].startswith('2/')


# ============================================================================
# TESTES DE PROCESSAMENTO - NOME USUARIO
# ============================================================================

class TestProcessamentoNome:
    """Testes de processamento de nome do usuário"""

    def test_processar_nome_usuario(self, helena_pop):
        """Deve coletar nome e pedir confirmação"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.NOME_USUARIO
        session_data = sm.to_dict()

        resultado = helena_pop.processar("Roberto", session_data)

        assert 'resposta' in resultado
        assert 'Roberto' in resultado['resposta']
        assert 'novo_estado' in resultado
        assert resultado['novo_estado']['estado'] == EstadoPOP.CONFIRMA_NOME.value
        assert resultado['novo_estado']['nome_temporario'] == 'Roberto'

    def test_confirmar_nome_sim(self, helena_pop, state_machine_confirma_nome):
        """Confirmação positiva deve aceitar nome"""
        session_data = state_machine_confirma_nome.to_dict()

        resultado = helena_pop.processar("sim", session_data)

        assert resultado['novo_estado']['nome_usuario'] == 'Roberto'
        assert resultado['novo_estado']['estado'] == EstadoPOP.AREA_DECIPEX.value

    def test_confirmar_nome_nao(self, helena_pop, state_machine_confirma_nome):
        """Confirmação negativa deve pedir nome novamente"""
        session_data = state_machine_confirma_nome.to_dict()

        resultado = helena_pop.processar("não", session_data)

        assert resultado['novo_estado']['estado'] == EstadoPOP.NOME_USUARIO.value


# ============================================================================
# TESTES DE PROCESSAMENTO - ÁREA DECIPEX
# ============================================================================

class TestProcessamentoArea:
    """Testes de processamento de seleção de área"""

    def test_selecionar_area_valida(self, helena_pop):
        """Deve aceitar número de área válido"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.AREA_DECIPEX
        sm.nome_usuario = "Roberto"
        session_data = sm.to_dict()

        resultado = helena_pop.processar("1", session_data)

        assert resultado['novo_estado']['area_selecionada']['codigo'] == 'CGBEN'
        # Deve avançar para arquitetura ou nome_processo dependendo se CSV existe

    def test_selecionar_area_invalida(self, helena_pop):
        """Deve rejeitar número de área inválido"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.AREA_DECIPEX
        session_data = sm.to_dict()

        resultado = helena_pop.processar("99", session_data)

        assert 'inválido' in resultado['resposta'].lower()
        assert resultado['novo_estado']['estado'] == EstadoPOP.AREA_DECIPEX.value

    def test_selecionar_area_texto(self, helena_pop):
        """Deve rejeitar texto em vez de número"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.AREA_DECIPEX
        session_data = sm.to_dict()

        resultado = helena_pop.processar("CGBEN", session_data)

        assert 'número' in resultado['resposta'].lower()


# ============================================================================
# TESTES DE PROCESSAMENTO - DADOS DO PROCESSO
# ============================================================================

class TestProcessamentoDados:
    """Testes de processamento de dados do processo"""

    def test_coletar_nome_processo(self, helena_pop):
        """Deve coletar nome do processo"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.NOME_PROCESSO
        session_data = sm.to_dict()

        resultado = helena_pop.processar("Conceder auxílio alimentação", session_data)

        assert resultado['novo_estado']['dados_coletados']['nome_processo'] == "Conceder auxílio alimentação"
        assert resultado['novo_estado']['estado'] == EstadoPOP.ENTREGA_ESPERADA.value

    def test_coletar_entrega_esperada(self, helena_pop):
        """Deve coletar entrega esperada"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.ENTREGA_ESPERADA
        sm.dados_coletados['nome_processo'] = "Processo teste"
        session_data = sm.to_dict()

        resultado = helena_pop.processar("Auxílio concedido", session_data)

        assert resultado['novo_estado']['dados_coletados']['entrega_esperada'] == "Auxílio concedido"
        assert resultado['novo_estado']['estado'] == EstadoPOP.DISPOSITIVOS_NORMATIVOS.value

    def test_coletar_normas_multiplas(self, helena_pop):
        """Deve coletar múltiplas normas separadas por vírgula"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS
        session_data = sm.to_dict()

        resultado = helena_pop.processar("Lei 8.112/90, IN 97/2022", session_data)

        normas = resultado['novo_estado']['dados_coletados']['dispositivos_normativos']
        assert len(normas) == 2
        assert "Lei 8.112/90" in normas
        assert "IN 97/2022" in normas


# ============================================================================
# TESTES DE VALIDAÇÃO
# ============================================================================

class TestValidacoes:
    """Testes de validação de entrada"""

    def test_validar_mensagem_vazia(self, helena_pop, estado_inicial):
        """Deve rejeitar mensagem vazia"""
        with pytest.raises(ValueError, match="não-vazia"):
            helena_pop.processar("", estado_inicial)

    def test_validar_mensagem_muito_longa(self, helena_pop, estado_inicial):
        """Deve rejeitar mensagem muito longa"""
        mensagem_longa = "a" * 10001
        with pytest.raises(ValueError, match="muito longa"):
            helena_pop.processar(mensagem_longa, estado_inicial)

    def test_validar_session_data_invalido(self, helena_pop):
        """Deve rejeitar session_data inválido"""
        with pytest.raises(ValueError, match="dicionário"):
            helena_pop.processar("teste", "não é dict")


# ============================================================================
# TESTES DE DELEGAÇÃO
# ============================================================================

class TestDelegacao:
    """Testes de delegação para Helena Etapas"""

    def test_sugerir_contexto_etapas(self, helena_pop):
        """Deve sugerir mudança para contexto etapas"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.DELEGACAO_ETAPAS
        sm.nome_usuario = "Roberto"
        sm.dados_coletados = {
            'nome_processo': 'Processo teste',
            'entrega_esperada': 'Resultado',
            'dispositivos_normativos': ['Lei 123'],
            'operadores': ['Técnico'],
            'sistemas': ['SIAPE'],
            'documentos': [],
            'fluxos_entrada': ['Dados'],
            'fluxos_saida': ['Resultado']
        }
        session_data = sm.to_dict()

        resultado = helena_pop.processar("ok", session_data)

        assert 'sugerir_contexto' in resultado
        assert resultado['sugerir_contexto'] == 'etapas'
        assert resultado['novo_estado']['concluido'] is True


# ============================================================================
# GOLDEN TESTS - PAYLOAD
# ============================================================================

class TestGoldenPayloads:
    """Testes de payload para garantir compatibilidade com frontend"""

    def test_payload_formato_padrao(self, helena_pop, estado_inicial):
        """Payload deve ter formato esperado pelo frontend"""
        resultado = helena_pop.processar("Olá", estado_inicial)

        # Campos obrigatórios
        assert 'resposta' in resultado
        assert isinstance(resultado['resposta'], str)

        assert 'novo_estado' in resultado
        assert isinstance(resultado['novo_estado'], dict)

        # Campos opcionais
        if 'progresso' in resultado:
            assert isinstance(resultado['progresso'], str)

        if 'sugerir_contexto' in resultado:
            assert isinstance(resultado['sugerir_contexto'], str)

        if 'metadados' in resultado:
            assert isinstance(resultado['metadados'], dict)

    def test_payload_serializavel_json(self, helena_pop, estado_inicial):
        """Payload deve ser serializável para JSON"""
        resultado = helena_pop.processar("Olá", estado_inicial)

        # Não deve lançar exceção
        json_str = json.dumps(resultado)
        assert len(json_str) > 0

        # Deve poder deserializar
        parsed = json.loads(json_str)
        assert parsed['resposta'] == resultado['resposta']


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestFluxoCompleto:
    """Testes de fluxo completo de conversa"""

    def test_fluxo_linear_completo(self, helena_pop):
        """Deve completar fluxo linear básico"""
        # 1. Boas vindas
        estado = helena_pop.inicializar_estado()
        resultado = helena_pop.processar("Olá", estado)
        assert resultado['novo_estado']['estado'] == EstadoPOP.NOME_USUARIO.value

        # 2. Nome
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("Roberto", estado)
        assert resultado['novo_estado']['estado'] == EstadoPOP.CONFIRMA_NOME.value

        # 3. Confirmar nome
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("sim", estado)
        assert resultado['novo_estado']['estado'] == EstadoPOP.AREA_DECIPEX.value
        assert resultado['novo_estado']['nome_usuario'] == "Roberto"

    def test_fluxo_com_correcao_nome(self, helena_pop):
        """Deve permitir corrigir nome"""
        # 1. Boas vindas
        estado = helena_pop.inicializar_estado()
        resultado = helena_pop.processar("Olá", estado)

        # 2. Nome errado
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("Robeto", estado)

        # 3. Não confirmar
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("não", estado)
        assert resultado['novo_estado']['estado'] == EstadoPOP.NOME_USUARIO.value

        # 4. Nome correto
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("Roberto", estado)

        # 5. Confirmar
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("sim", estado)
        assert resultado['novo_estado']['nome_usuario'] == "Roberto"


# ============================================================================
# TESTES DE HELPERS
# ============================================================================

class TestHelpers:
    """Testes de métodos auxiliares"""

    def test_calcular_progresso(self, helena_pop):
        """Deve calcular progresso corretamente"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.NOME_USUARIO
        session_data = sm.to_dict()

        resultado = helena_pop.processar("teste", session_data)

        # Progresso deve existir e estar no formato X/Y
        assert 'progresso' in resultado
        assert '/' in resultado['progresso']

    def test_gerar_resumo(self, helena_pop):
        """Deve gerar resumo com dados coletados"""
        sm = POPStateMachine()
        sm.estado = EstadoPOP.FLUXOS
        sm.nome_usuario = "Roberto"
        sm.area_selecionada = {'nome': 'CGBEN', 'codigo': 'CGBEN'}
        sm.dados_coletados = {
            'nome_processo': 'Processo teste',
            'entrega_esperada': 'Resultado',
            'dispositivos_normativos': ['Lei 123'],
            'operadores': ['Técnico'],
            'sistemas': ['SIAPE'],
            'documentos': ['Processo SEI'],
            'fluxos_entrada': [],
            'fluxos_saida': []
        }
        session_data = sm.to_dict()

        # Coletar fluxos de entrada primeiro
        resultado = helena_pop.processar("Requerimento", session_data)

        # Agora coletar fluxos de saída - aqui deve mostrar resumo
        estado = resultado['novo_estado']
        resultado = helena_pop.processar("Decisão", estado)

        # Resumo deve aparecer na resposta
        assert 'RESUMO' in resultado['resposta'].upper()
        assert 'Processo teste' in resultado['resposta']
        assert resultado['novo_estado']['estado'] == EstadoPOP.DELEGACAO_ETAPAS.value
