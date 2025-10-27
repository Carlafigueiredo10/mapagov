"""
Testes unitários para EtapaStateMachine

Executar com: pytest processos/tests/test_state_machine.py -v
"""
import pytest
import json
from helena_produtos.domain.state_machine import EtapaStateMachine
from helena_produtos.domain.enums import EstadoEtapa


class TestEtapaLinear:
    """Testes para etapa linear (sem condicionais)"""

    def test_fluxo_completo_linear(self):
        """Testa fluxo completo de etapa linear"""
        sm = EtapaStateMachine(numero_etapa=1, operadores_disponiveis=["Técnico", "Coordenador"])

        # 1. Coletar descrição
        resultado = sm.processar("Analisar requerimento no SIGEPE")
        assert resultado["proximo"] == "OPERADOR"
        assert sm.estado == EstadoEtapa.OPERADOR
        assert sm.descricao == "Analisar requerimento no SIGEPE"

        # 2. Coletar operador
        resultado = sm.processar("Técnico Especializado")
        assert resultado["pergunta"] == "tem_condicionais?"
        assert sm.estado == EstadoEtapa.PERGUNTA_CONDICIONAL
        assert sm.operador == "Técnico Especializado"

        # 3. Responder que NÃO tem condicionais
        resultado = sm.processar("não")
        assert resultado["pergunta"] == "detalhes"
        assert sm.estado == EstadoEtapa.DETALHES
        assert sm.tem_condicionais == False

        # 4. Adicionar detalhes
        resultado = sm.processar("Acessar sistema SIGEPE")
        assert resultado["pergunta"] == "mais_detalhes"
        assert len(sm.detalhes) == 1
        assert "1.1" in sm.detalhes[0]

        resultado = sm.processar("Conferir documentação anexada")
        assert len(sm.detalhes) == 2
        assert "1.2" in sm.detalhes[1]

        # 5. Finalizar
        resultado = sm.processar("fim")
        assert resultado["status"] == "etapa_linear_finalizada"
        assert sm.completa()

        # 6. Validar objeto final
        etapa = sm.obter_dict()
        assert etapa["numero"] == "1"
        assert etapa["descricao"] == "Analisar requerimento no SIGEPE"
        assert etapa["operador"] == "Técnico Especializado"
        assert len(etapa["detalhes"]) == 2
        assert "tipo" not in etapa or etapa.get("tipo") != "condicional"


class TestEtapaCondicionalBinaria:
    """Testes para etapa condicional binária (2 cenários)"""

    def test_fluxo_completo_condicional_binaria(self):
        """Testa fluxo completo de etapa condicional binária"""
        sm = EtapaStateMachine(numero_etapa=2, operadores_disponiveis=["Coordenador"])

        # 1. Descrição
        sm.processar("Avaliar documentação do servidor")

        # 2. Operador
        sm.processar("Coordenador de Auxílios")

        # 3. TEM condicionais
        resultado = sm.processar("sim")
        assert resultado["pergunta"] == "tipo_condicional"
        assert sm.tem_condicionais == True

        # 4. Tipo binário
        resultado = sm.processar("binario")
        assert resultado["pergunta"] == "antes_decisao"
        assert sm.tipo_condicional == "binario"

        # 5. Antes da decisão
        resultado = sm.processar("Conferir se documentação está completa")
        assert resultado["pergunta"] == "cenarios_descricoes"
        assert sm.antes_decisao == "Conferir se documentação está completa"

        # 6. Cenários (JSON)
        cenarios_json = json.dumps({
            "cenarios": [
                {"descricao": "Documentação completa"},
                {"descricao": "Documentação incompleta"}
            ]
        })
        resultado = sm.processar(cenarios_json)
        assert resultado["pergunta"] == "subetapas"
        assert len(sm.cenarios) == 2
        assert sm.cenarios[0].descricao == "Documentação completa"
        assert sm.cenarios[0].numero == "2.1.1"

        # 7. Subetapas do primeiro cenário
        resultado = sm.processar("Aprovar pedido\nRegistrar no sistema\nNotificar servidor")
        assert resultado["pergunta"] == "subetapas"
        assert len(sm.cenarios[0].subetapas) == 3
        assert "2.1.1.1" in sm.cenarios[0].subetapas[0].numero

        # 8. Subetapas do segundo cenário
        resultado = sm.processar("Solicitar documentação faltante\nAguardar reenvio")
        assert resultado["status"] == "etapa_condicional_finalizada"
        assert len(sm.cenarios[1].subetapas) == 2
        assert sm.completa()

        # 9. Validar objeto final
        etapa = sm.obter_dict()
        assert etapa["tipo"] == "condicional"
        assert etapa["tipo_condicional"] == "binario"
        assert etapa["antes_decisao"]["numero"] == "2.1"
        assert len(etapa["cenarios"]) == 2
        assert len(etapa["cenarios"][0]["subetapas"]) == 3
        assert len(etapa["cenarios"][1]["subetapas"]) == 2


class TestEtapaCondicionalMultipla:
    """Testes para etapa condicional múltipla (3+ cenários)"""

    def test_fluxo_completo_condicional_multipla(self):
        """Testa fluxo completo de etapa condicional com múltiplos cenários"""
        sm = EtapaStateMachine(numero_etapa=3, operadores_disponiveis=["Técnico"])

        # Fluxo até cenários
        sm.processar("Classificar tipo de requerimento")
        sm.processar("Técnico Especializado")
        sm.processar("sim")  # tem condicionais
        sm.processar("multiplos")  # tipo
        sm.processar("Analisar natureza do pedido")

        # Cenários (3 opções)
        cenarios_json = json.dumps({
            "cenarios": [
                {"descricao": "Aposentadoria"},
                {"descricao": "Pensão"},
                {"descricao": "Auxílio"}
            ]
        })
        sm.processar(cenarios_json)
        assert len(sm.cenarios) == 3

        # Subetapas de cada cenário
        sm.processar("Verificar tempo de contribuição")
        sm.processar("Consultar dependentes habilitados")
        sm.processar("Conferir documentação médica")

        assert sm.completa()
        etapa = sm.obter_dict()
        assert etapa["tipo_condicional"] == "multiplos"
        assert len(etapa["cenarios"]) == 3


class TestValidacoes:
    """Testes de validações e edge cases"""

    def test_resposta_invalida_condicional(self):
        """Testa resposta inválida ao perguntar sobre condicionais"""
        sm = EtapaStateMachine(1, ["Técnico"])
        sm.processar("Etapa teste")
        sm.processar("Técnico")

        # Resposta ambígua → deve tratar como "não tem condicionais"
        resultado = sm.processar("talvez")
        assert resultado["pergunta"] == "detalhes"
        assert sm.tem_condicionais == False

    def test_subetapas_vazias(self):
        """Testa cenário sem subetapas (usuário digitou 'pular')"""
        sm = EtapaStateMachine(1, ["Técnico"])
        sm.processar("Etapa teste")
        sm.processar("Técnico")
        sm.processar("sim")
        sm.processar("binario")
        sm.processar("Verificar algo")

        cenarios_json = json.dumps({
            "cenarios": [
                {"descricao": "Cenário A"},
                {"descricao": "Cenário B"}
            ]
        })
        sm.processar(cenarios_json)

        # Pular subetapas do primeiro cenário
        sm.processar("pular")
        assert len(sm.cenarios[0].subetapas) == 0

        # Adicionar no segundo
        sm.processar("Fazer algo")
        assert len(sm.cenarios[1].subetapas) == 1
        assert sm.completa()

    def test_json_invalido_cenarios(self):
        """Testa JSON malformado na entrada de cenários"""
        sm = EtapaStateMachine(1, ["Técnico"])
        sm.processar("Etapa")
        sm.processar("Técnico")
        sm.processar("sim")
        sm.processar("binario")
        sm.processar("Antes")

        resultado = sm.processar("isso não é json")
        assert "erro" in resultado
        assert not sm.completa()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
