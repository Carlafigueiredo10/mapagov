"""
Testes unitários para parsers

Executar com: pytest processos/tests/test_parsers.py -v
"""
import pytest
import json
from helena_produtos.infra.parsers import parse_documentos, parse_fluxos, normalizar_texto


class TestNormalizarTexto:
    """Testes para normalização de texto"""

    def test_remover_acentos(self):
        assert normalizar_texto("São Paulo") == "sao paulo"
        assert normalizar_texto("Coordenação") == "coordenacao"

    def test_lowercase(self):
        assert normalizar_texto("SIAPE") == "siape"

    def test_strip(self):
        assert normalizar_texto("  teste  ") == "teste"

    def test_combinacao(self):
        assert normalizar_texto("  Não há   ") == "nao ha"


class TestParseDocumentos:
    """Testes para parse de documentos"""

    def test_json_estruturado(self):
        """Testa parsing de JSON estruturado"""
        json_str = json.dumps([
            {
                "tipo_documento": "Formulário",
                "tipo_uso": "Gerado",
                "obrigatorio": True,
                "descricao": "Requerimento de auxílio",
                "sistema": "SIGEPE"
            },
            {
                "tipo_documento": "Comprovante",
                "tipo_uso": "Recebido",
                "obrigatorio": False,
                "descricao": "Comprovante de residência",
                "sistema": None
            }
        ])

        resultado = parse_documentos(json_str)
        assert len(resultado) == 2
        assert resultado[0]["descricao"] == "Requerimento de auxílio"
        assert resultado[1]["tipo_documento"] == "Comprovante"

    def test_texto_livre(self):
        """Testa parsing de texto livre (fallback)"""
        resultado = parse_documentos("Requerimento assinado")
        assert len(resultado) == 1
        assert resultado[0]["descricao"] == "Requerimento assinado"

    def test_json_invalido_fallback(self):
        """Testa fallback quando JSON é malformado"""
        resultado = parse_documentos('[{"descricao": invalid}')
        assert len(resultado) == 1
        assert "descricao" in resultado[0]


class TestParseFluxos:
    """Testes para parse de fluxos"""

    def test_fluxos_saida_json(self):
        """Testa parsing de fluxos de saída estruturados"""
        json_str = json.dumps({
            "destinos_selecionados": [
                {"tipo": "CGBEN", "especificacao": "Setor de Análise"},
                {"tipo": "CGPAG", "especificacao": None}
            ],
            "outros_destinos": "Área externa não listada"
        })

        resultado = parse_fluxos(json_str)
        assert len(resultado) == 3
        assert resultado[0] == "CGBEN: Setor de Análise"
        assert resultado[1] == "CGPAG"
        assert resultado[2] == "Área externa não listada"

    def test_fluxos_entrada_json(self):
        """Testa parsing de fluxos de entrada estruturados"""
        json_str = json.dumps({
            "origens_selecionadas": [
                {"tipo": "COATE", "especificacao": "Atendimento presencial"}
            ],
            "outras_origens": "Demanda externa"
        })

        resultado = parse_fluxos(json_str)
        assert len(resultado) == 2
        assert resultado[0] == "COATE: Atendimento presencial"
        assert resultado[1] == "Demanda externa"

    def test_texto_livre_virgula(self):
        """Testa fallback com separação por vírgula"""
        resultado = parse_fluxos("CGBEN, CGPAG, COATE")
        assert len(resultado) == 3
        assert resultado[0] == "CGBEN"
        assert resultado[2] == "COATE"

    def test_texto_livre_linhas(self):
        """Testa fallback com separação por linha"""
        resultado = parse_fluxos("CGBEN\nCGPAG\nCOATE")
        assert len(resultado) == 3

    def test_texto_livre_simples(self):
        """Testa fallback com texto único"""
        resultado = parse_fluxos("Setor de Análise")
        assert len(resultado) == 1
        assert resultado[0] == "Setor de Análise"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
