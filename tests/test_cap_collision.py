"""
Testes de colisão de CAP (codigo_processo).

Garante que:
1. UniqueConstraint impede duplicatas ativas
2. Retry no autosave incrementa CAP em colisão
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')

import django
django.setup()

from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from processos.models import POP


class TestUniqueCapConstraint(TestCase):
    """Testa que UniqueConstraint impede CAPs duplicados ativos."""

    def test_dois_pops_mesmo_cap_ativo_falha(self):
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='3.1.1.1.1',
            is_deleted=False,
            status='draft',
        )
        with self.assertRaises(IntegrityError):
            POP.objects.create(
                session_id='sess-2',
                codigo_processo='3.1.1.1.1',
                is_deleted=False,
                status='draft',
            )

    def test_cap_ativo_e_deletado_ok(self):
        """Um ativo e um soft-deleted com mesmo CAP devem coexistir."""
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='3.1.1.1.2',
            is_deleted=False,
            status='draft',
        )
        pop2 = POP.objects.create(
            session_id='sess-2',
            codigo_processo='3.1.1.1.2',
            is_deleted=True,
            status='draft',
        )
        self.assertTrue(pop2.pk)

    def test_dois_deletados_mesmo_cap_ok(self):
        """Dois soft-deleted com mesmo CAP devem coexistir."""
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='3.1.1.1.3',
            is_deleted=True,
            status='draft',
        )
        pop2 = POP.objects.create(
            session_id='sess-2',
            codigo_processo='3.1.1.1.3',
            is_deleted=True,
            status='draft',
        )
        self.assertTrue(pop2.pk)

    def test_caps_null_nao_colidem(self):
        """Dois POPs sem codigo_processo (null) devem coexistir."""
        p1 = POP.objects.create(session_id='s1', is_deleted=False, status='draft')
        p2 = POP.objects.create(session_id='s2', is_deleted=False, status='draft')
        self.assertTrue(p1.pk)
        self.assertTrue(p2.pk)

    def test_caps_vazios_nao_colidem(self):
        """Dois POPs com codigo_processo='' devem coexistir."""
        p1 = POP.objects.create(session_id='s1', codigo_processo='', is_deleted=False, status='draft')
        p2 = POP.objects.create(session_id='s2', codigo_processo='', is_deleted=False, status='draft')
        self.assertTrue(p1.pk)
        self.assertTrue(p2.pk)


class TestAutosaveRetry(TransactionTestCase):
    """Testa que o retry com transaction.atomic() incrementa o CAP em colisão."""

    def _save_with_retry(self, pop, max_tentativas=3):
        """Mesma lógica de retry da view autosave_pop."""
        for tentativa in range(max_tentativas):
            try:
                with transaction.atomic():
                    pop.save()
                return
            except IntegrityError:
                if pop.codigo_processo and tentativa < max_tentativas - 1:
                    cap = pop.codigo_processo
                    partes = cap.rsplit('.', 1)
                    if len(partes) == 2:
                        try:
                            novo_num = int(partes[1]) + 1
                            pop.codigo_processo = f"{partes[0]}.{novo_num}"
                        except ValueError:
                            pop.codigo_processo = f"{cap}-{tentativa + 2}"
                    else:
                        pop.codigo_processo = f"{cap}-{tentativa + 2}"
                else:
                    raise

    def test_save_com_retry_incrementa_cap(self):
        """Simula colisão: cria POP existente, tenta salvar outro com mesmo CAP."""
        POP.objects.create(
            session_id='sess-existing',
            codigo_processo='6.1.1.1.5',
            is_deleted=False,
            status='draft',
        )

        pop = POP(
            session_id='sess-new',
            codigo_processo='6.1.1.1.5',
            is_deleted=False,
            status='draft',
        )
        self._save_with_retry(pop)

        self.assertTrue(pop.pk)
        self.assertEqual(pop.codigo_processo, '6.1.1.1.6')

    def test_save_retry_dupla_colisao(self):
        """Colisão em 2 CAPs consecutivos, resolve na 3a tentativa."""
        POP.objects.create(session_id='s1', codigo_processo='6.1.1.1.5', is_deleted=False, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='6.1.1.1.6', is_deleted=False, status='draft')

        pop = POP(session_id='s3', codigo_processo='6.1.1.1.5', is_deleted=False, status='draft')
        self._save_with_retry(pop)

        self.assertTrue(pop.pk)
        self.assertEqual(pop.codigo_processo, '6.1.1.1.7')


if __name__ == '__main__':
    unittest.main()
