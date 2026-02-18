"""
Testes para geração de CP (Código de Produto) — produtos não-POP.

Cobre:
1. resolve_prefixo_cp() — prefixo completo com subárea, fail-fast
2. gerar_cp() — formato correto, sequência incremental
3. atribuir_cp_se_necessario() — idempotência
4. ControleIndicesProduto — UniqueConstraint
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')

import django
django.setup()

from unittest.mock import patch, MagicMock
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase

from processos.domain.governanca.normalize import resolve_prefixo_cp
from processos.domain.governanca.cp_generator import (
    gerar_cp, atribuir_cp_se_necessario, PRODUTOS, _carregar_prefixos_area,
)
from processos.models_new import ControleIndicesProduto


# Mapa de áreas para testes (evita dependência de banco para funções puras)
AREAS_MAP_TESTE = {
    "CGBEN": "01",
    "CGPAG": "02",
    "COATE": "03",
    "CGGAF": "04",
    "DIGEP": "05",
    "DIGEP-RO": "05.01",
    "DIGEP-RR": "05.02",
    "DIGEP-AP": "05.03",
    "CGRIS": "06",
    "CGCAF": "07",
    "CGECO": "08",
    "COADM": "09",
    "COGES": "10",
    "CDGEP": "11",
}


# ── Testes unitários (funções puras) ──────────────────────────────────────────

class TestResolvePrefixoCp(unittest.TestCase):
    """Testa resolução de prefixo para CP."""

    def test_area_simples(self):
        self.assertEqual(resolve_prefixo_cp("COATE", AREAS_MAP_TESTE), "03")

    def test_area_dois_digitos(self):
        self.assertEqual(resolve_prefixo_cp("COGES", AREAS_MAP_TESTE), "10")

    def test_subarea_inclui_prefixo_completo(self):
        """CP inclui subárea (diferente do CAP)."""
        self.assertEqual(resolve_prefixo_cp("DIGEP-RO", AREAS_MAP_TESTE), "05.01")
        self.assertEqual(resolve_prefixo_cp("DIGEP-RR", AREAS_MAP_TESTE), "05.02")
        self.assertEqual(resolve_prefixo_cp("DIGEP-AP", AREAS_MAP_TESTE), "05.03")

    def test_area_desconhecida_raise_valueerror(self):
        with self.assertRaises(ValueError):
            resolve_prefixo_cp("XPTO", AREAS_MAP_TESTE)

    def test_area_vazia_raise_valueerror(self):
        with self.assertRaises(ValueError):
            resolve_prefixo_cp("", AREAS_MAP_TESTE)


class TestProdutosCatalogo(unittest.TestCase):
    """Verifica constantes do catálogo de produtos."""

    def test_analise_riscos_eh_01(self):
        self.assertEqual(PRODUTOS["analise_riscos"], "01")

    def test_planejamento_estrategico_eh_02(self):
        self.assertEqual(PRODUTOS["planejamento_estrategico"], "02")


# ── Testes com banco (TransactionTestCase) ────────────────────────────────────

class TestGerarCp(TransactionTestCase):
    """Testa geração de CP com lock transacional."""

    def _mock_prefixos(self):
        return AREAS_MAP_TESTE

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_formato_area_simples(self, mock_prefixos):
        """COATE, produto 01 → 03.01.001"""
        mock_prefixos.return_value = AREAS_MAP_TESTE
        cp = gerar_cp("COATE", "01")
        self.assertEqual(cp, "03.01.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_formato_subarea(self, mock_prefixos):
        """DIGEP-RO, produto 03 → 05.01.03.001"""
        mock_prefixos.return_value = AREAS_MAP_TESTE
        cp = gerar_cp("DIGEP-RO", "03")
        self.assertEqual(cp, "05.01.03.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_sequencia_incremental(self, mock_prefixos):
        """Chamadas consecutivas incrementam sequência."""
        mock_prefixos.return_value = AREAS_MAP_TESTE
        cp1 = gerar_cp("COATE", "01")
        cp2 = gerar_cp("COATE", "01")
        cp3 = gerar_cp("COATE", "01")
        self.assertEqual(cp1, "03.01.001")
        self.assertEqual(cp2, "03.01.002")
        self.assertEqual(cp3, "03.01.003")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_sequencias_independentes_por_produto(self, mock_prefixos):
        """Produtos diferentes na mesma área têm sequências independentes."""
        mock_prefixos.return_value = AREAS_MAP_TESTE
        cp_ar = gerar_cp("COATE", "01")
        cp_pe = gerar_cp("COATE", "02")
        self.assertEqual(cp_ar, "03.01.001")
        self.assertEqual(cp_pe, "03.02.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_sequencias_independentes_por_area(self, mock_prefixos):
        """Áreas diferentes com mesmo produto têm sequências independentes."""
        mock_prefixos.return_value = AREAS_MAP_TESTE
        cp1 = gerar_cp("COATE", "01")
        cp2 = gerar_cp("CGRIS", "01")
        self.assertEqual(cp1, "03.01.001")
        self.assertEqual(cp2, "06.01.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_area_desconhecida_raise_valueerror(self, mock_prefixos):
        mock_prefixos.return_value = AREAS_MAP_TESTE
        with self.assertRaises(ValueError):
            gerar_cp("XPTO", "01")


class TestControleIndicesProdutoConstraint(TransactionTestCase):
    """Testa UniqueConstraint em ControleIndicesProduto."""

    def test_unique_area_produto(self):
        """Não permite duplicata de (area_codigo, produto_codigo)."""
        ControleIndicesProduto.objects.create(
            area_codigo="COATE", produto_codigo="01", ultimo_indice=1
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ControleIndicesProduto.objects.create(
                    area_codigo="COATE", produto_codigo="01", ultimo_indice=2
                )

    def test_mesmo_area_produto_diferente_ok(self):
        """Mesma área com produto diferente é permitido."""
        ControleIndicesProduto.objects.create(
            area_codigo="COATE", produto_codigo="01", ultimo_indice=1
        )
        ControleIndicesProduto.objects.create(
            area_codigo="COATE", produto_codigo="02", ultimo_indice=1
        )
        self.assertEqual(
            ControleIndicesProduto.objects.filter(area_codigo="COATE").count(), 2
        )


class TestAtribuirCpSeNecessario(TransactionTestCase):
    """Testa padrão idempotente de atribuição de CP."""

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_atribui_cp_quando_nao_tem(self, mock_prefixos):
        """Objeto sem CP recebe um."""
        mock_prefixos.return_value = AREAS_MAP_TESTE

        from processos.models_analise_riscos import AnaliseRiscos
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(
            username='test_cp', defaults={'email': 'test@cp.com'}
        )
        ar = AnaliseRiscos.objects.create(
            orgao_id="orgao-teste",
            tipo_origem="manual",
            criado_por=user,
        )

        resultado = atribuir_cp_se_necessario(ar, "COATE")
        self.assertTrue(resultado)
        self.assertEqual(ar.codigo_cp, "03.01.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_idempotente_nao_duplica(self, mock_prefixos):
        """Segundo request não gera segundo CP."""
        mock_prefixos.return_value = AREAS_MAP_TESTE

        from processos.models_analise_riscos import AnaliseRiscos
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(
            username='test_cp2', defaults={'email': 'test2@cp.com'}
        )
        ar = AnaliseRiscos.objects.create(
            orgao_id="orgao-teste-2",
            tipo_origem="manual",
            criado_por=user,
        )

        resultado1 = atribuir_cp_se_necessario(ar, "COATE")
        resultado2 = atribuir_cp_se_necessario(ar, "COATE")

        self.assertTrue(resultado1)
        self.assertFalse(resultado2)  # Já tinha CP
        self.assertEqual(ar.codigo_cp, "03.01.001")

    @patch('processos.domain.governanca.cp_generator._carregar_prefixos_area')
    def test_area_desconhecida_nao_atribui(self, mock_prefixos):
        """Área desconhecida retorna False sem crash."""
        mock_prefixos.return_value = AREAS_MAP_TESTE

        from processos.models_analise_riscos import AnaliseRiscos
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(
            username='test_cp3', defaults={'email': 'test3@cp.com'}
        )
        ar = AnaliseRiscos.objects.create(
            orgao_id="orgao-teste-3",
            tipo_origem="manual",
            criado_por=user,
        )

        resultado = atribuir_cp_se_necessario(ar, "XPTO")
        self.assertFalse(resultado)
        self.assertIsNone(ar.codigo_cp)

    def test_area_vazia_nao_atribui(self):
        """Área vazia retorna False sem gerar CP."""
        from processos.models_analise_riscos import AnaliseRiscos
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(
            username='test_cp4', defaults={'email': 'test4@cp.com'}
        )
        ar = AnaliseRiscos.objects.create(
            orgao_id="orgao-teste-4",
            tipo_origem="manual",
            criado_por=user,
        )

        resultado = atribuir_cp_se_necessario(ar, "")
        self.assertFalse(resultado)


if __name__ == '__main__':
    unittest.main()
