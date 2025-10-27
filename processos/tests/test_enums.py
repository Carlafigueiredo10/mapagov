"""
Testes unitários para enums e classificadores

Executar com: pytest processos/tests/test_enums.py -v
"""
import pytest
from helena_produtos.domain.enums import RespostaSN, EstadoConversacao, EstadoEtapa, TipoInterface


class TestRespostaSN:
    """Testes para classificador de respostas Sim/Não"""

    def test_respostas_positivas(self):
        """Testa todas as variações de 'sim'"""
        positivas = ["sim", "s", "SIM", "Sim", "ok", "OK", "yes", "claro",
                     "vamos", "bora", "uhum", "aham", "pode", "pronto"]

        for resposta in positivas:
            assert RespostaSN.classificar(resposta) == RespostaSN.SIM, f"Falhou: {resposta}"

    def test_respostas_negativas(self):
        """Testa todas as variações de 'não'"""
        negativas = ["não", "nao", "NÃO", "NAO", "Não", "n", "N", "no", "jamais"]

        for resposta in negativas:
            assert RespostaSN.classificar(resposta) == RespostaSN.NAO, f"Falhou: {resposta}"

    def test_respostas_ambiguas(self):
        """Testa respostas que não são sim nem não"""
        ambiguas = ["talvez", "sei lá", "depois", "agora não", ""]

        for resposta in ambiguas:
            assert RespostaSN.classificar(resposta) is None, f"Falhou: {resposta}"

    def test_normalizacao_acentos(self):
        """Testa remoção de acentos na normalização"""
        assert RespostaSN.classificar("não") == RespostaSN.NAO
        assert RespostaSN.classificar("nao") == RespostaSN.NAO

    def test_espacos(self):
        """Testa tratamento de espaços"""
        assert RespostaSN.classificar("  sim  ") == RespostaSN.SIM
        assert RespostaSN.classificar("não ") == RespostaSN.NAO


class TestEnumsExistencia:
    """Testes básicos de existência dos enums"""

    def test_estado_conversacao_completo(self):
        """Verifica se todos os estados essenciais existem"""
        assert EstadoConversacao.NOME
        assert EstadoConversacao.AREA
        assert EstadoConversacao.ETAPAS
        assert EstadoConversacao.REVISAO

    def test_estado_etapa_completo(self):
        """Verifica se todos os estados de etapa existem"""
        assert EstadoEtapa.DESCRICAO
        assert EstadoEtapa.OPERADOR
        assert EstadoEtapa.PERGUNTA_CONDICIONAL
        assert EstadoEtapa.FINALIZADA

    def test_tipo_interface_principais(self):
        """Verifica se tipos principais de interface existem"""
        assert TipoInterface.TEXTO.value == "texto"
        assert TipoInterface.AREAS.value == "areas"
        assert TipoInterface.OPERADORES_ETAPA.value == "operadores_etapa"
        assert TipoInterface.REVISAO.value == "revisao"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
