"""
Testes para Bloco B Estruturado (v2)

Checklist de validacao:
1. Payload novo valida enums (inclui NAO_SEI)
2. Recursos: [] diferente de "nao respondeu"
3. Adaptador respeita NAO_SEI
4. Analises antigas abrem, editam e exportam sem erro
5. Motor continua funcionando com regras atuais
6. Relatorio mostra dados novos e faz fallback para antigos
"""
import os
import django

# Configurar Django antes de importar models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mapagov.settings")
django.setup()

import pytest
from processos.domain.helena_analise_riscos.contexto_schema import (
    validar_bloco_b_estruturado,
    tem_campos_estruturados,
)
from processos.domain.helena_analise_riscos.bloco_b_adapter import (
    adaptar_bloco_b,
    SinalMotor,
    SinalDependencia,
    mapear_para_bloco_3,
    mapear_para_bloco_1,
    mapear_para_bloco_4,
)
from processos.api.export_helpers import build_bloco_b_renderizado


class TestValidacaoEnums:
    """1. Payload novo valida enums (inclui NAO_SEI)"""

    def test_sla_nao_sei_valido(self):
        """NAO_SEI deve ser valor valido para SLA"""
        bloco_b = {"sla": "NAO_SEI"}
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "sla" not in erros

    def test_dependencia_nao_sei_valido(self):
        """NAO_SEI deve ser valor valido para dependencia"""
        bloco_b = {"dependencia": "NAO_SEI"}
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "dependencia" not in erros

    def test_incidentes_nao_sei_valido(self):
        """NAO_SEI deve ser valor valido para incidentes"""
        bloco_b = {"incidentes": "NAO_SEI"}
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "incidentes" not in erros

    def test_enum_invalido_gera_erro(self):
        """Enum invalido deve gerar erro"""
        bloco_b = {"sla": "TALVEZ"}  # Valor invalido
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "sla" in erros

    def test_recursos_invalido_gera_erro(self):
        """Recursos com valor invalido deve gerar erro"""
        bloco_b = {"recursos": ["PESSOAS", "FOGUETE"]}  # FOGUETE invalido
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "recursos" in erros


class TestRecursosVazioVsAusente:
    """2. Recursos: [] diferente de "nao respondeu" """

    def test_recursos_lista_vazia_valida(self):
        """Lista vazia [] = respondeu 'nenhum', nao e erro"""
        bloco_b = {"recursos": []}
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "recursos" not in erros

    def test_recursos_ausente_nao_e_erro(self):
        """Chave ausente = nao respondeu, nao e erro (campo opcional)"""
        bloco_b = {}
        erros = validar_bloco_b_estruturado(bloco_b)
        assert "recursos" not in erros

    def test_adapter_distingue_vazio_de_ausente(self):
        """Adapter deve distinguir [] de chave ausente"""
        # Recursos = [] -> respondeu "nenhum"
        bloco_b_vazio = {"recursos": []}
        sinais_vazio = adaptar_bloco_b(bloco_b_vazio)
        assert sinais_vazio.depende_ti == SinalMotor.NAO.value
        assert sinais_vazio.depende_pessoas == SinalMotor.NAO.value

        # Recursos ausente -> nao respondeu (None)
        bloco_b_ausente = {}
        sinais_ausente = adaptar_bloco_b(bloco_b_ausente)
        assert sinais_ausente.depende_ti is None
        assert sinais_ausente.depende_pessoas is None


class TestAdaptadorNaoSei:
    """3. Adaptador respeita NAO_SEI"""

    def test_sla_nao_sei_vira_desconhecido(self):
        """NAO_SEI nunca deve virar NAO - deve virar DESCONHECIDO"""
        bloco_b = {"sla": "NAO_SEI"}
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.tem_sla == SinalMotor.DESCONHECIDO.value
        assert sinais.tem_sla != SinalMotor.NAO.value

    def test_dependencia_nao_sei_vira_desconhecido(self):
        """Dependencia NAO_SEI deve virar DESCONHECIDO"""
        bloco_b = {"dependencia": "NAO_SEI"}
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.tipo_dependencia == SinalDependencia.DESCONHECIDO.value

    def test_incidentes_nao_sei_vira_desconhecido(self):
        """Incidentes NAO_SEI deve virar DESCONHECIDO"""
        bloco_b = {"incidentes": "NAO_SEI"}
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.tem_incidentes == SinalMotor.DESCONHECIDO.value

    def test_mapeamento_motor_nao_mapeia_desconhecido(self):
        """Motor NAO deve receber mapeamento quando adaptador retorna DESCONHECIDO"""
        bloco_b = {"sla": "NAO_SEI", "dependencia": "NAO_SEI"}
        sinais = adaptar_bloco_b(bloco_b)

        # Mapeamento para BLOCO_4 (prazos) - NAO deve mapear Q1
        respostas_b4 = mapear_para_bloco_4(sinais)
        assert "Q1" not in respostas_b4

        # Mapeamento para BLOCO_1 (terceiros) - NAO deve mapear Q1
        respostas_b1 = mapear_para_bloco_1(sinais)
        assert "Q1" not in respostas_b1


class TestRetrocompatibilidade:
    """4. Analises antigas funcionam sem erro"""

    def test_bloco_b_antigo_valida(self):
        """Bloco B com campos antigos deve validar sem erro"""
        bloco_b_antigo = {
            "recursos_necessarios": "Pessoas e sistemas",
            "areas_atores_envolvidos": "CGTI",
            "frequencia_execucao": "CONTINUO",
            "prazos_slas": "30 dias",
            "dependencias_externas": "SIAPE",
            "historico_problemas": "Nao ha",
            "impacto_se_falhar": "Atraso no pagamento",
        }
        # Validacao de campos novos deve passar (campos ausentes nao sao erro)
        erros = validar_bloco_b_estruturado(bloco_b_antigo)
        assert len(erros) == 0

    def test_bloco_b_antigo_nao_tem_campos_estruturados(self):
        """Bloco B antigo deve ser detectado como sem campos estruturados"""
        bloco_b_antigo = {
            "recursos_necessarios": "Pessoas",
            "frequencia_execucao": "CONTINUO",
        }
        assert tem_campos_estruturados(bloco_b_antigo) is False

    def test_bloco_b_novo_tem_campos_estruturados(self):
        """Bloco B novo deve ser detectado como tendo campos estruturados"""
        bloco_b_novo = {
            "recursos": ["PESSOAS", "TI"],
            "frequencia": "CONTINUO",
        }
        assert tem_campos_estruturados(bloco_b_novo) is True

    def test_adapter_fallback_texto_antigo(self):
        """Adapter deve fazer fallback para texto antigo quando novo ausente"""
        bloco_b_antigo = {
            "recursos_necessarios": "sistema SIAPE, equipe de TI",
            "prazos_slas": "prazo legal de 30 dias",
            "dependencias_externas": "sistema externo SIAPE",
            "historico_problemas": "houve problema em 2023",
        }
        sinais = adaptar_bloco_b(bloco_b_antigo)

        # Fallback deve detectar palavras-chave
        assert sinais.depende_ti == SinalMotor.SIM.value  # "sistema"
        assert sinais.tem_sla == SinalMotor.SIM.value  # "prazo"
        assert sinais.tipo_dependencia == SinalDependencia.SISTEMAS.value  # "sistema"
        assert sinais.tem_incidentes == SinalMotor.SIM.value  # "problema"


class TestExportFallback:
    """6. Relatorio mostra dados novos e faz fallback para antigos"""

    def test_export_bloco_b_antigo(self):
        """Export deve renderizar campos antigos quando novos ausentes"""
        bloco_b_antigo = {
            "recursos_necessarios": "Pessoas e TI",
            "frequencia_execucao": "CONTINUO",
            "prazos_slas": "30 dias",
        }
        resultado = build_bloco_b_renderizado(bloco_b_antigo)

        assert resultado["tem_campos_estruturados"] is False
        assert len(resultado["campos"]) > 0

        # Deve ter campo de recursos do texto antigo
        labels = [c["label"] for c in resultado["campos"]]
        assert "Recursos necessarios" in labels

    def test_export_bloco_b_novo(self):
        """Export deve renderizar campos novos quando presentes"""
        bloco_b_novo = {
            "recursos": ["PESSOAS", "TI"],
            "frequencia": "CONTINUO",
            "sla": "SIM",
            "sla_detalhe": "30 dias",
        }
        resultado = build_bloco_b_renderizado(bloco_b_novo)

        assert resultado["tem_campos_estruturados"] is True

        # Deve ter campo estruturado
        campos_estruturados = [c for c in resultado["campos"] if c.get("tipo") == "estruturado"]
        assert len(campos_estruturados) > 0

    def test_export_bloco_b_misto(self):
        """Export deve mesclar campos novos e antigos corretamente"""
        bloco_b_misto = {
            # Campos novos
            "recursos": ["PESSOAS"],
            "sla": "NAO_SEI",
            # Campos antigos (fallback)
            "dependencias_externas": "SIAPE externo",
            "impacto_se_falhar": "Consequencia grave",
        }
        resultado = build_bloco_b_renderizado(bloco_b_misto)

        labels = [c["label"] for c in resultado["campos"]]
        # Deve ter campo novo (recursos)
        assert "Recursos necessarios" in labels
        # Deve ter campo antigo (dependencias - fallback)
        assert "Dependencias externas" in labels


class TestPayloadCompleto:
    """Teste de integracao com payload completo"""

    def test_payload_novo_completo(self):
        """Payload novo completo deve validar e adaptar corretamente"""
        bloco_b = {
            "recursos": ["PESSOAS", "TI", "ORCAMENTO"],
            "recursos_outros": "Sala de reuniao",
            "atores_envolvidos_texto": "CGTI, CGBEN",
            "frequencia": "CONTINUO",
            "sla": "SIM",
            "sla_detalhe": "Lei 8.112, 30 dias",
            "dependencia": "AMBOS",
            "dependencia_detalhe": "SIAPE, Fornecedor X",
            "incidentes": "SIM",
            "incidentes_detalhe": "Falha em 2023",
            "consequencia_texto": "Atraso no pagamento de servidores",
        }

        # Validacao
        erros = validar_bloco_b_estruturado(bloco_b)
        assert len(erros) == 0

        # Adaptador
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.depende_ti == SinalMotor.SIM.value
        assert sinais.depende_pessoas == SinalMotor.SIM.value
        assert sinais.tem_sla == SinalMotor.SIM.value
        assert sinais.tipo_dependencia == SinalDependencia.AMBOS.value
        assert sinais.tem_incidentes == SinalMotor.SIM.value

        # Export
        resultado = build_bloco_b_renderizado(bloco_b)
        assert resultado["tem_campos_estruturados"] is True
        assert len(resultado["campos"]) >= 7  # Todos os campos

    def test_payload_antigo_completo(self):
        """Payload antigo completo deve continuar funcionando"""
        bloco_b = {
            "recursos_necessarios": "Pessoas, sistemas, orcamento",
            "areas_atores_envolvidos": "CGTI, CGBEN, COADM",
            "frequencia_execucao": "CONTINUO",
            "prazos_slas": "Prazo legal de 30 dias conforme Lei 8.112",
            "dependencias_externas": "SIAPE, Banco do Brasil",
            "historico_problemas": "Houve atraso em dezembro/2023",
            "impacto_se_falhar": "Atraso no pagamento de 10.000 servidores",
        }

        # Validacao (campos novos ausentes = OK)
        erros = validar_bloco_b_estruturado(bloco_b)
        assert len(erros) == 0

        # Adaptador com fallback
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.depende_ti == SinalMotor.SIM.value  # detectou "sistema"
        assert sinais.tem_sla == SinalMotor.SIM.value  # detectou "prazo legal"
        assert sinais.tem_incidentes == SinalMotor.SIM.value  # detectou "atraso"

        # Export com fallback
        resultado = build_bloco_b_renderizado(bloco_b)
        assert resultado["tem_campos_estruturados"] is False
        assert len(resultado["campos"]) >= 7

    def test_payload_caso_nao_sei(self):
        """Payload com NAO_SEI em todos os campos aplicaveis"""
        bloco_b = {
            "recursos": [],  # Nenhum recurso
            "frequencia": "SOB_DEMANDA",
            "sla": "NAO_SEI",
            "dependencia": "NAO_SEI",
            "incidentes": "NAO_SEI",
        }

        # Validacao
        erros = validar_bloco_b_estruturado(bloco_b)
        assert len(erros) == 0

        # Adaptador - NAO_SEI vira DESCONHECIDO
        sinais = adaptar_bloco_b(bloco_b)
        assert sinais.tem_sla == SinalMotor.DESCONHECIDO.value
        assert sinais.tipo_dependencia == SinalDependencia.DESCONHECIDO.value
        assert sinais.tem_incidentes == SinalMotor.DESCONHECIDO.value

        # Mapeamentos NAO devem incluir Q1 quando DESCONHECIDO
        assert "Q1" not in mapear_para_bloco_4(sinais)
        assert "Q1" not in mapear_para_bloco_1(sinais)
