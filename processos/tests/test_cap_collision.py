"""
Testes de colisão de CAP (codigo_processo).

Garante que:
1. _max_atividade_csv e _max_atividade_db retornam o maior segmento correto
2. UniqueConstraint impede duplicatas ativas
3. Retry no autosave incrementa CAP em colisão
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
from processos.domain.helena_mapeamento.busca_atividade_pipeline import (
    _max_atividade_csv,
    _max_atividade_db,
)


# ── Testes unitários do gerador (funções puras) ─────────────────────────────

class TestMaxAtividadeCSV(unittest.TestCase):
    """Testa parsing de max atividade a partir de lista de CAPs do CSV."""

    def test_csv_normal(self):
        caps = ['08.01.01.01', '08.01.01.02', '08.01.01.03']
        self.assertEqual(_max_atividade_csv(caps), 3)

    def test_csv_com_gaps(self):
        caps = ['01.01.01.01', '01.01.01.05', '01.01.01.03']
        self.assertEqual(_max_atividade_csv(caps), 5)

    def test_csv_vazio(self):
        self.assertEqual(_max_atividade_csv([]), 0)

    def test_csv_com_lixo(self):
        """Strings não-numéricas no último segmento são ignoradas."""
        caps = ['08.01.01.abc', '08.01.01.02', 'invalido']
        self.assertEqual(_max_atividade_csv(caps), 2)

    def test_csv_formato_curto_ignorado(self):
        """CAPs com menos de 4 segmentos são ignorados."""
        caps = ['01.01', '08.01.01.04']
        self.assertEqual(_max_atividade_csv(caps), 4)

    def test_csv_somente_lixo_retorna_zero(self):
        caps = ['abc', 'x.y.z.w', '']
        self.assertEqual(_max_atividade_csv(caps), 0)


class TestMaxAtividadeDB(TestCase):
    """Testa consulta de max atividade no banco."""

    def test_db_vazio_retorna_zero(self):
        """Sem POPs no banco, max_db deve ser 0 (CSV prevalece)."""
        self.assertEqual(_max_atividade_db('03.07.01.01'), 0)

    def test_db_com_pops(self):
        """DB com POPs existentes retorna o maior segmento."""
        POP.objects.create(session_id='s1', codigo_processo='03.07.01.01.002', is_deleted=False, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='03.07.01.01.005', is_deleted=False, status='draft')
        POP.objects.create(session_id='s3', codigo_processo='03.07.01.01.003', is_deleted=False, status='draft')
        self.assertEqual(_max_atividade_db('03.07.01.01'), 5)

    def test_db_maior_que_csv(self):
        """Cenário: CSV tem max=3, DB tem max=7 → gerador deve usar 7."""
        POP.objects.create(session_id='s1', codigo_processo='03.07.01.01.007', is_deleted=False, status='draft')
        csv_max = _max_atividade_csv(['07.01.01.01', '07.01.01.02', '07.01.01.03'])
        db_max = _max_atividade_db('03.07.01.01')
        candidato = max(csv_max, db_max) + 1
        self.assertEqual(csv_max, 3)
        self.assertEqual(db_max, 7)
        self.assertEqual(candidato, 8)

    def test_db_com_lixo_no_sufixo(self):
        """POPs com sufixo não-numérico são ignorados sem quebrar."""
        POP.objects.create(session_id='s1', codigo_processo='03.07.01.01.abc', is_deleted=False, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='03.07.01.01.004', is_deleted=False, status='draft')
        POP.objects.create(session_id='s3', codigo_processo='03.07.01.01.', is_deleted=False, status='draft')
        self.assertEqual(_max_atividade_db('03.07.01.01'), 4)

    def test_db_ignora_soft_deleted(self):
        """POPs soft-deleted não devem contar."""
        POP.objects.create(session_id='s1', codigo_processo='03.07.01.01.009', is_deleted=True, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='03.07.01.01.003', is_deleted=False, status='draft')
        self.assertEqual(_max_atividade_db('03.07.01.01'), 3)

    def test_db_ignora_outro_prefixo(self):
        """POPs de outro prefixo não interferem."""
        POP.objects.create(session_id='s1', codigo_processo='06.01.01.01.009', is_deleted=False, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='03.07.01.01.002', is_deleted=False, status='draft')
        self.assertEqual(_max_atividade_db('03.07.01.01'), 2)


# ── Testes de UniqueConstraint ───────────────────────────────────────────────

class TestUniqueCapConstraint(TestCase):
    """Testa que UniqueConstraint impede CAPs duplicados ativos."""

    def test_dois_pops_mesmo_cap_ativo_falha(self):
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='03.01.01.01.001',
            is_deleted=False,
            status='draft',
        )
        with self.assertRaises(IntegrityError):
            POP.objects.create(
                session_id='sess-2',
                codigo_processo='03.01.01.01.001',
                is_deleted=False,
                status='draft',
            )

    def test_cap_ativo_e_deletado_ok(self):
        """Um ativo e um soft-deleted com mesmo CAP devem coexistir."""
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='03.01.01.01.002',
            is_deleted=False,
            status='draft',
        )
        pop2 = POP.objects.create(
            session_id='sess-2',
            codigo_processo='03.01.01.01.002',
            is_deleted=True,
            status='draft',
        )
        self.assertTrue(pop2.pk)

    def test_dois_deletados_mesmo_cap_ok(self):
        """Dois soft-deleted com mesmo CAP devem coexistir."""
        POP.objects.create(
            session_id='sess-1',
            codigo_processo='03.01.01.01.003',
            is_deleted=True,
            status='draft',
        )
        pop2 = POP.objects.create(
            session_id='sess-2',
            codigo_processo='03.01.01.01.003',
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


# ── Testes de retry no autosave ──────────────────────────────────────────────

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
            codigo_processo='06.01.01.01.005',
            is_deleted=False,
            status='draft',
        )

        pop = POP(
            session_id='sess-new',
            codigo_processo='06.01.01.01.005',
            is_deleted=False,
            status='draft',
        )
        self._save_with_retry(pop)

        self.assertTrue(pop.pk)
        self.assertEqual(pop.codigo_processo, '06.01.01.01.6')

    def test_save_retry_dupla_colisao(self):
        """Colisão em 2 CAPs consecutivos, resolve na 3a tentativa."""
        POP.objects.create(session_id='s1', codigo_processo='06.01.01.01.005', is_deleted=False, status='draft')
        POP.objects.create(session_id='s2', codigo_processo='06.01.01.01.6', is_deleted=False, status='draft')

        pop = POP(session_id='s3', codigo_processo='06.01.01.01.005', is_deleted=False, status='draft')
        self._save_with_retry(pop)

        self.assertTrue(pop.pk)
        self.assertEqual(pop.codigo_processo, '06.01.01.01.7')


if __name__ == '__main__':
    unittest.main()
