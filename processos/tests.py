from django.test import TestCase, Client
from django.urls import reverse
from .models import POP, POPSnapshot
import json


class AutosavePOPTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.url = reverse('pop_autosave')

	def test_autosave_creates_snapshot_every_cycle(self):
		# Primeiro autosave cria POP (sem snapshot ainda porque sequence=1 mod 1 ==0 gera snapshot)
		payload1 = {
			'session_id': 'sess1',
			'nome_usuario': 'Tester',
			'nome_processo': 'Processo X',
			'autosave_every': 1,
			'etapas': ['Etapa 1']
		}
		resp1 = self.client.post(self.url, data=json.dumps(payload1), content_type='application/json')
		self.assertEqual(resp1.status_code, 200)
		data1 = resp1.json()
		self.assertTrue(data1['snapshot_created'])
		self.assertEqual(POPSnapshot.objects.count(), 1)

		pop_id = data1['pop']['id']

		# Segundo autosave gera segundo snapshot
		payload2 = {
			'id': pop_id,
			'autosave_every': 1,
			'etapas': ['Etapa 1','Etapa 2']
		}
		resp2 = self.client.post(self.url, data=json.dumps(payload2), content_type='application/json')
		self.assertEqual(resp2.status_code, 200)
		data2 = resp2.json()
		self.assertTrue(data2['snapshot_created'])
		self.assertEqual(POPSnapshot.objects.count(), 2)

		# Verifica integridade básica
		pop = POP.objects.get(id=pop_id)
		self.assertEqual(pop.autosave_sequence, 2)
		self.assertIn('Etapa 2', pop.etapas)


class VersionamentoPOPTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.url = reverse('pop_autosave')

	def _create_pop(self):
		resp = self.client.post(self.url, data=json.dumps({
			'session_id': 'v1',
			'nome_usuario': 'Tester',
			'nome_processo': 'Processo Versao',
			'autosave_every': 5
		}), content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		return resp.json()['pop']['id']

	def test_incrementa_versao_review_e_approved(self):
		pop_id = self._create_pop()
		# Padrão inicia em versao 1
		from .models import POP
		pop = POP.objects.get(id=pop_id)
		self.assertEqual(pop.versao, 1)

		# Mudar para review
		r1 = self.client.post(self.url, data=json.dumps({'id': pop_id, 'status': 'review'}), content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		pop.refresh_from_db()
		self.assertEqual(pop.status, 'review')
		self.assertEqual(pop.versao, 2)

		# Mudar para approved
		r2 = self.client.post(self.url, data=json.dumps({'id': pop_id, 'status': 'approved'}), content_type='application/json')
		self.assertEqual(r2.status_code, 200)
		pop.refresh_from_db()
		self.assertEqual(pop.status, 'approved')
		self.assertEqual(pop.versao, 3)


class DiffSnapshotsTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.autosave_url = reverse('pop_autosave')
		self.diff_url = reverse('pop_snapshot_diff')

	def test_diff_mostra_campo_modificado(self):
		# Criar POP e dois snapshots (autosave_every=1)
		r1 = self.client.post(self.autosave_url, data=json.dumps({
			'session_id': 'diffsess',
			'nome_usuario': 'Tester',
			'nome_processo': 'Proc Diff',
			'autosave_every': 1,
			'etapas': ['E1']
		}), content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		pop_id = r1.json()['pop']['id']
		snap_a_id = POPSnapshot.objects.first().id

		r2 = self.client.post(self.autosave_url, data=json.dumps({
			'id': pop_id,
			'autosave_every': 1,
			'etapas': ['E1','E2'],
			'pontos_atencao': 'Novo ponto'
		}), content_type='application/json')
		self.assertEqual(r2.status_code, 200)
		snap_b_id = POPSnapshot.objects.order_by('-id').first().id

		diff_resp = self.client.post(self.diff_url, data=json.dumps({
			'snapshot_a': snap_a_id,
			'snapshot_b': snap_b_id
		}), content_type='application/json')
		self.assertEqual(diff_resp.status_code, 200)
		diff_data = diff_resp.json()
		self.assertTrue(diff_data['success'])
		self.assertIn('etapas', diff_data['diff'])
		self.assertIn('pontos_atencao', diff_data['diff'])
