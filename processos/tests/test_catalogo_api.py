"""
Testes para o catalogo de POPs: Areas, CRUD, Publish, Resolve, Stats.
Cobre Etapas 1-5 do plano.
"""

import uuid as uuid_lib

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from processos.models import Area, POP, PopVersion


# ============================================================================
# Helpers
# ============================================================================

_area_counter = 0

def create_area(**kwargs):
    global _area_counter
    _area_counter += 1
    defaults = {
        'codigo': f'TEST{_area_counter}',
        'nome': f'Area de Teste {_area_counter}',
        'nome_curto': f'Teste {_area_counter}',
        'slug': f'test{_area_counter}',
        'prefixo': f'T{_area_counter}',
        'ordem': 100 + _area_counter,
        'ativo': True,
    }
    defaults.update(kwargs)
    return Area.objects.create(**defaults)


def create_pop(area=None, **kwargs):
    defaults = {
        'session_id': f'sess-{uuid_lib.uuid4().hex[:8]}',
        'nome_processo': 'Concessao de aposentadoria',
        'codigo_processo': f'1.1.1.1.{POP.objects.count() + 1}',
        'status': 'draft',
        'area': area,
    }
    defaults.update(kwargs)
    return POP.objects.create(**defaults)


# ============================================================================
# Etapa 1: Area model + POP CRUD
# ============================================================================

class TestAreaModel(TestCase):
    def test_create_area(self):
        area = create_area()
        self.assertIn('TEST', area.codigo)
        self.assertIn('test', area.slug)

    def test_area_unique_codigo(self):
        area = create_area(codigo='UNICO1', slug='unico1')
        with self.assertRaises(Exception):
            Area.objects.create(codigo='UNICO1', slug='unico1-dup', nome='Dup', nome_curto='Dup', prefixo='X')

    def test_area_pai_subareas(self):
        pai = create_area(tem_subareas=True)
        filho = create_area(area_pai=pai)
        self.assertEqual(filho.area_pai, pai)
        self.assertIn(filho, pai.subareas.all())


class TestPOPWithArea(TestCase):
    def setUp(self):
        self.area = create_area()

    def test_create_pop_with_area(self):
        pop = create_pop(area=self.area)
        self.assertEqual(pop.area, self.area)
        self.assertEqual(pop.status, 'draft')

    def test_pop_status_choices(self):
        pop = create_pop(area=self.area, status='published')
        pop.refresh_from_db()
        self.assertEqual(pop.status, 'published')

    def test_pop_soft_delete(self):
        pop = create_pop(area=self.area)
        pop.is_deleted = True
        pop.save(update_fields=['is_deleted'])
        self.assertEqual(POP.objects.filter(is_deleted=False).count(), 0)


# ============================================================================
# Etapa 1: API CRUD
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestAreaAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_list_areas(self):
        resp = self.client.get('/api/areas/')
        self.assertEqual(resp.status_code, 200)
        # 10 top-level do CSV + 1 de teste = 11
        self.assertGreaterEqual(len(resp.data), 10)
        codigos = [a['codigo'] for a in resp.data]
        self.assertIn(self.area.codigo, codigos)

    def test_area_pop_count(self):
        create_pop(area=self.area, status='published')
        create_pop(area=self.area, status='draft')
        resp = self.client.get(f'/api/areas/{self.area.slug}/')
        self.assertEqual(resp.data['pop_count'], 1)  # so published conta

    def test_retrieve_area_by_slug(self):
        resp = self.client.get(f'/api/areas/{self.area.slug}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['codigo'], self.area.codigo)

    def test_area_subareas_in_response(self):
        """Usa areas DIGEP ja criadas pela data migration."""
        resp = self.client.get('/api/areas/digep/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['subareas']), 3)  # RO, RR, AP


@override_settings(ROOT_URLCONF='mapagov.urls')
class TestPOPAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_list_pops(self):
        create_pop(area=self.area)
        resp = self.client.get('/api/pops/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_list_pops_filter_by_area(self):
        create_pop(area=self.area)
        area2 = create_area()
        create_pop(area=area2, codigo_processo='99.1.1.1.1')
        resp = self.client.get(f'/api/pops/?area={self.area.slug}')
        self.assertEqual(len(resp.data), 1)

    def test_list_pops_filter_by_status(self):
        create_pop(area=self.area, status='published')
        create_pop(area=self.area, status='draft')
        resp = self.client.get('/api/pops/?status=published')
        self.assertEqual(len(resp.data), 1)

    def test_retrieve_pop_by_uuid(self):
        pop = create_pop(area=self.area)
        resp = self.client.get(f'/api/pops/{pop.uuid}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['nome_processo'], 'Concessao de aposentadoria')

    def test_patch_pop(self):
        pop = create_pop(area=self.area)
        resp = self.client.patch(
            f'/api/pops/{pop.uuid}/',
            {'nome_processo': 'Titulo atualizado'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        pop.refresh_from_db()
        self.assertEqual(pop.nome_processo, 'Titulo atualizado')

    def test_delete_pop_soft(self):
        pop = create_pop(area=self.area)
        resp = self.client.delete(f'/api/pops/{pop.uuid}/')
        self.assertEqual(resp.status_code, 204)
        pop.refresh_from_db()
        self.assertTrue(pop.is_deleted)


# ============================================================================
# Etapa 2: Catalogo por area
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestCatalogoPorArea(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_area_pops_default_published(self):
        create_pop(area=self.area, status='published', codigo_processo='1.1.1.1.1')
        create_pop(area=self.area, status='draft', codigo_processo='1.1.1.1.2')
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_area_pops_include_subareas(self):
        """Usa DIGEP da data migration; cria POP em sub-area DIGEP-RO."""
        digep_ro = Area.objects.get(codigo='DIGEP-RO')
        create_pop(area=digep_ro, status='published', codigo_processo='5.1.1.1.99')
        resp = self.client.get('/api/areas/digep/pops/')
        self.assertEqual(len(resp.data), 1)  # POP do filho aparece via pai

    def test_detalhe_por_area_codigo(self):
        pop = create_pop(area=self.area, status='published', codigo_processo='1.1.1.1.1')
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.1/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['uuid'], str(pop.uuid))

    def test_detalhe_area_codigo_404(self):
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/99.99.99/')
        self.assertEqual(resp.status_code, 404)


# ============================================================================
# Etapa 3: Publish / Archive / Versions
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestPublishWorkflow(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_publish_creates_version(self):
        pop = create_pop(area=self.area)
        resp = self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['success'])
        self.assertEqual(resp.data['versao'], 2)  # versao default=1, incrementa para 2

        pop.refresh_from_db()
        self.assertEqual(pop.status, 'published')
        self.assertEqual(pop.versao, 2)

        version = PopVersion.objects.get(pop=pop, versao=2)
        self.assertTrue(version.is_current)
        self.assertIn('nome_processo', version.payload)

    def test_publish_twice_increments(self):
        pop = create_pop(area=self.area)
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        # Editar e publicar novamente
        pop.refresh_from_db()
        pop.status = 'draft'
        pop.save(update_fields=['status'])
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        pop.refresh_from_db()
        self.assertEqual(pop.versao, 3)
        self.assertEqual(PopVersion.objects.filter(pop=pop).count(), 2)
        # Apenas v3 e current
        self.assertFalse(PopVersion.objects.get(pop=pop, versao=2).is_current)
        self.assertTrue(PopVersion.objects.get(pop=pop, versao=3).is_current)

    def test_publish_rejects_without_nome(self):
        pop = create_pop(area=self.area, nome_processo='')
        resp = self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('nome_processo', resp.data['error'])

    def test_publish_rejects_archived(self):
        pop = create_pop(area=self.area, status='archived')
        resp = self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        self.assertEqual(resp.status_code, 400)

    def test_archive(self):
        pop = create_pop(area=self.area, status='published')
        resp = self.client.post(f'/api/pops/{pop.uuid}/archive/', format='json')
        self.assertEqual(resp.status_code, 200)
        pop.refresh_from_db()
        self.assertEqual(pop.status, 'archived')

    def test_versions_list(self):
        pop = create_pop(area=self.area)
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        resp = self.client.get(f'/api/pops/{pop.uuid}/versions/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['versao'], 2)


# ============================================================================
# Etapa 4: Resolve CAP
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestResolveCAP(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_resolve_by_area_codigo(self):
        pop = create_pop(area=self.area, codigo_processo='1.1.1.1.1')
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')

        resp = self.client.get(f'/api/pops/resolve/?area={self.area.slug}&codigo=1.1.1.1.1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['published'])
        self.assertEqual(resp.data['cap'], '1.1.1.1.1')
        self.assertIn('dados', resp.data)

    def test_resolve_by_cap(self):
        pop = create_pop(area=self.area, codigo_processo='1.1.1.1.2')
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')

        resp = self.client.get('/api/pops/resolve/?cap=1.1.1.1.2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['published'])

    def test_resolve_specific_version(self):
        pop = create_pop(area=self.area, codigo_processo='1.1.1.1.3')
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        # Publicar v3
        pop.refresh_from_db()
        pop.status = 'draft'
        pop.save(update_fields=['status'])
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')

        resp = self.client.get('/api/pops/resolve/?cap=1.1.1.1.3&v=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['versao'], 2)

    def test_resolve_unpublished_fallback(self):
        pop = create_pop(area=self.area, codigo_processo='1.1.1.1.4')
        resp = self.client.get('/api/pops/resolve/?cap=1.1.1.1.4')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data['published'])

    def test_resolve_404(self):
        resp = self.client.get('/api/pops/resolve/?cap=99.99.99')
        self.assertEqual(resp.status_code, 404)

    def test_resolve_version_404(self):
        pop = create_pop(area=self.area, codigo_processo='1.1.1.1.5')
        resp = self.client.get('/api/pops/resolve/?cap=1.1.1.1.5&v=99')
        self.assertEqual(resp.status_code, 404)


# ============================================================================
# Etapa 5: Stats
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestStats(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_stats_global(self):
        create_pop(area=self.area, status='published', codigo_processo='1.1.1.1.1')
        create_pop(area=self.area, status='draft', codigo_processo='1.1.1.1.2')

        resp = self.client.get('/api/stats/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['totais']['pops'], 2)
        self.assertEqual(resp.data['totais']['publicados'], 1)
        self.assertEqual(resp.data['totais']['rascunhos'], 1)

    def test_stats_area(self):
        create_pop(area=self.area, status='published', codigo_processo='1.1.1.1.1')

        resp = self.client.get(f'/api/stats/areas/{self.area.slug}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['area']['codigo'], self.area.codigo)
        self.assertEqual(resp.data['totais']['pops'], 1)

    def test_stats_area_404(self):
        resp = self.client.get('/api/stats/areas/inexistente/')
        self.assertEqual(resp.status_code, 404)


# ============================================================================
# Data migration: Areas populadas
# ============================================================================

class TestDataMigration(TestCase):
    def test_areas_from_csv_exist(self):
        """Verifica que a data migration populou areas do CSV."""
        self.assertTrue(Area.objects.filter(codigo='CGBEN').exists())
        self.assertTrue(Area.objects.filter(codigo='CGRIS').exists())
        self.assertTrue(Area.objects.filter(codigo='DIGEP').exists())
        self.assertTrue(Area.objects.filter(codigo='DIGEP-RO').exists())

    def test_areas_parent_linked(self):
        digep_ro = Area.objects.get(codigo='DIGEP-RO')
        self.assertEqual(digep_ro.area_pai.codigo, 'DIGEP')

    def test_total_areas(self):
        self.assertEqual(Area.objects.count(), 13)

    def test_slugs_correct(self):
        cgben = Area.objects.get(codigo='CGBEN')
        self.assertEqual(cgben.slug, 'cgben')
        digep_ro = Area.objects.get(codigo='DIGEP-RO')
        self.assertEqual(digep_ro.slug, 'digep-ro')


# ============================================================================
# Etapa 2.5: PDF sob demanda version-aware
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestCatalogoPDF(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_pdf_pop_corrente(self):
        """Gera PDF a partir do POP corrente (sem versao publicada)."""
        pop = create_pop(
            area=self.area,
            nome_processo='Processo para PDF',
            codigo_processo='1.1.1.1.1',
        )
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.1/pdf/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertIn('.pdf', resp['Content-Disposition'])

    def test_pdf_usa_versao_publicada(self):
        """Sem ?v, usa PopVersion is_current=True se existir."""
        pop = create_pop(
            area=self.area,
            nome_processo='Processo Publicado',
            codigo_processo='1.1.1.1.2',
        )
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        pop.refresh_from_db()
        self.assertEqual(pop.status, 'published')

        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.2/pdf/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        # Filename inclui v2 (publish incrementa de 1 para 2)
        self.assertIn('v2', resp['Content-Disposition'])

    def test_pdf_versao_especifica(self):
        """?v=2 retorna PDF baseado no payload da versao 2."""
        pop = create_pop(
            area=self.area,
            nome_processo='Processo Versionado',
            codigo_processo='1.1.1.1.3',
        )
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')
        # Publicar v3
        pop.refresh_from_db()
        pop.status = 'draft'
        pop.save(update_fields=['status'])
        self.client.post(f'/api/pops/{pop.uuid}/publish/', format='json')

        # Pedir v2 explicitamente
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.3/pdf/?v=2')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('v2', resp['Content-Disposition'])

    def test_pdf_versao_inexistente_404(self):
        pop = create_pop(
            area=self.area,
            nome_processo='Processo',
            codigo_processo='1.1.1.1.4',
        )
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.4/pdf/?v=99')
        self.assertEqual(resp.status_code, 404)

    def test_pdf_pop_inexistente_404(self):
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/99.99.99/pdf/')
        self.assertEqual(resp.status_code, 404)

    def test_pdf_area_inexistente_404(self):
        resp = self.client.get('/api/areas/inexistente/pops/1.1.1.1.1/pdf/')
        self.assertEqual(resp.status_code, 404)

    def test_pdf_sem_nome_400(self):
        """POP sem nome_processo retorna 400."""
        pop = create_pop(
            area=self.area,
            nome_processo='',
            codigo_processo='1.1.1.1.5',
        )
        resp = self.client.get(f'/api/areas/{self.area.slug}/pops/1.1.1.1.5/pdf/')
        self.assertEqual(resp.status_code, 400)


# ============================================================================
# Etapa 6: Busca full-text
# ============================================================================

@override_settings(ROOT_URLCONF='mapagov.urls')
class TestSearchPOPs(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area = create_area()

    def test_search_by_nome(self):
        create_pop(area=self.area, nome_processo='Concessao de aposentadoria', status='published')
        resp = self.client.get('/api/pops/search/?q=aposentadoria')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['nome_processo'], 'Concessao de aposentadoria')

    def test_search_by_codigo(self):
        create_pop(area=self.area, nome_processo='Processo X', codigo_processo='7.1.1.1.5', status='published')
        resp = self.client.get('/api/pops/search/?q=7.1.1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_search_filter_area(self):
        area2 = create_area()
        create_pop(area=self.area, nome_processo='Licenca especial', status='published')
        create_pop(area=area2, nome_processo='Licenca comum', status='published')
        resp = self.client.get(f'/api/pops/search/?q=licenca&area={self.area.slug}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_search_filter_status(self):
        create_pop(area=self.area, nome_processo='Progressao funcional', status='published')
        create_pop(area=self.area, nome_processo='Progressao salarial', status='draft')
        resp = self.client.get('/api/pops/search/?q=progressao&status=draft')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['status'], 'draft')

    def test_search_default_published(self):
        create_pop(area=self.area, nome_processo='Ferias servidor', status='published')
        create_pop(area=self.area, nome_processo='Ferias estagiario', status='draft')
        resp = self.client.get('/api/pops/search/?q=ferias')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)  # so published

    def test_search_min_chars_400(self):
        resp = self.client.get('/api/pops/search/?q=ab')
        self.assertEqual(resp.status_code, 400)

    def test_search_empty_q_400(self):
        resp = self.client.get('/api/pops/search/?q=')
        self.assertEqual(resp.status_code, 400)

    def test_search_no_results(self):
        resp = self.client.get('/api/pops/search/?q=inexistente')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_search_limit(self):
        for i in range(5):
            create_pop(area=self.area, nome_processo=f'Processo tipo X num {i}', status='published', codigo_processo=f'1.1.1.1.{i}')
        resp = self.client.get('/api/pops/search/?q=processo&limit=3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)

    def test_search_excludes_deleted(self):
        pop = create_pop(area=self.area, nome_processo='Deletado teste busca', status='published')
        pop.is_deleted = True
        pop.save(update_fields=['is_deleted'])
        resp = self.client.get('/api/pops/search/?q=deletado')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)
