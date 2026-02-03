"""
Smoke Tests para API de Analise de Riscos

Testa: criar, listar, detalhar, adicionar risco
"""
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from processos.models_analise_riscos import (
    AnaliseRiscos,
    RiscoIdentificado,
)
from processos.domain.helena_analise_riscos.enums import StatusAnalise


class AnaliseRiscosAPITestCase(TestCase):
    """Smoke tests para API de Analise de Riscos"""

    def setUp(self):
        """Setup para cada teste"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="teste_riscos",
            email="teste@riscos.com",
            password="teste123"
        )
        self.client.force_authenticate(user=self.user)
        self.orgao_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        self.origem_id = uuid.UUID("22222222-2222-2222-2222-222222222222")

    def test_criar_analise(self):
        """Teste: criar nova analise"""
        response = self.client.post(
            "/api/analise-riscos/criar/",
            {"tipo_origem": "POP", "origem_id": str(self.origem_id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("dados", response.json())
        self.assertIn("id", response.json()["dados"])

    def test_criar_analise_sem_origem(self):
        """Teste: criar analise sem origem_id deve falhar"""
        response = self.client.post(
            "/api/analise-riscos/criar/",
            {"tipo_origem": "POP"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("erro", response.json())
        self.assertEqual(response.json()["codigo"], "ORIGEM_OBRIGATORIA")

    def test_listar_analises(self):
        """Teste: listar analises"""
        # Criar analise primeiro
        AnaliseRiscos.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tipo_origem="POP",
            origem_id=self.origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=self.user,
        )

        response = self.client.get("/api/analise-riscos/listar/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("dados", response.json())
        self.assertIn("analises", response.json()["dados"])

    def test_detalhar_analise(self):
        """Teste: detalhar analise existente"""
        analise = AnaliseRiscos.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tipo_origem="POP",
            origem_id=self.origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=self.user,
        )

        response = self.client.get(f"/api/analise-riscos/{analise.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("dados", response.json())
        self.assertEqual(response.json()["dados"]["id"], str(analise.id))

    def test_detalhar_analise_nao_existe(self):
        """Teste: detalhar analise que nao existe"""
        fake_id = uuid.uuid4()
        response = self.client.get(f"/api/analise-riscos/{fake_id}/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["codigo"], "NAO_ENCONTRADA")

    def test_adicionar_risco(self):
        """Teste: adicionar risco a analise"""
        analise = AnaliseRiscos.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tipo_origem="POP",
            origem_id=self.origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=self.user,
        )

        response = self.client.post(
            f"/api/analise-riscos/{analise.id}/riscos/",
            {
                "titulo": "Risco de teste",
                "categoria": "OPERACIONAL",
                "probabilidade": 3,
                "impacto": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("dados", response.json())
        self.assertEqual(response.json()["dados"]["score_risco"], 12)
        self.assertEqual(response.json()["dados"]["nivel_risco"], "ALTO")

    def test_adicionar_risco_sem_titulo(self):
        """Teste: adicionar risco sem titulo deve falhar"""
        analise = AnaliseRiscos.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tipo_origem="POP",
            origem_id=self.origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=self.user,
        )

        response = self.client.post(
            f"/api/analise-riscos/{analise.id}/riscos/",
            {"categoria": "OPERACIONAL"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["codigo"], "TITULO_OBRIGATORIO")

    def test_analisar_risco_prob_impacto(self):
        """Teste: atualizar probabilidade e impacto de risco"""
        analise = AnaliseRiscos.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tipo_origem="POP",
            origem_id=self.origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=self.user,
        )
        risco = RiscoIdentificado.objects.create(
            orgao_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            analise=analise,
            titulo="Risco teste",
            categoria="OPERACIONAL",
            probabilidade=2,
            impacto=2,
        )

        response = self.client.patch(
            f"/api/analise-riscos/{analise.id}/riscos/{risco.id}/analise/",
            {"probabilidade": 5, "impacto": 5},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["dados"]["score_risco"], 25)
        self.assertEqual(response.json()["dados"]["nivel_risco"], "CRITICO")


class AnaliseRiscosAPIv2TestCase(TestCase):
    """Testes para API v2 de Analise de Riscos"""

    def setUp(self):
        """Setup para cada teste"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="teste_riscos_v2",
            email="teste_v2@riscos.com",
            password="teste123"
        )
        self.client.force_authenticate(user=self.user)
        self.orgao_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    def test_criar_v2_questionario_sucesso(self):
        """Teste: criar analise v2 com QUESTIONARIO + tipo_origem -> 201"""
        response = self.client.post(
            "/api/analise-riscos/v2/criar/",
            {"modo_entrada": "QUESTIONARIO", "tipo_origem": "PROJETO"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("dados", response.json())
        self.assertEqual(response.json()["dados"]["modo_entrada"], "QUESTIONARIO")
        self.assertEqual(response.json()["dados"]["tipo_origem"], "PROJETO")
        self.assertEqual(response.json()["dados"]["etapa_atual"], 0)

    def test_criar_v2_modo_id_sem_origem(self):
        """Teste: criar v2 com modo_entrada=ID sem origem_id -> 400"""
        response = self.client.post(
            "/api/analise-riscos/v2/criar/",
            {"modo_entrada": "ID", "tipo_origem": "PROCESSO"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["codigo"], "ORIGEM_ID_OBRIGATORIO")

    def test_criar_v2_modo_id_com_origem(self):
        """Teste: criar v2 com modo_entrada=ID com origem_id -> 201"""
        origem_id = uuid.uuid4()
        response = self.client.post(
            "/api/analise-riscos/v2/criar/",
            {"modo_entrada": "ID", "tipo_origem": "POP", "origem_id": str(origem_id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["dados"]["modo_entrada"], "ID")

    def test_salvar_contexto_gate_invalido(self):
        """Teste: salvar_contexto com contexto incompleto -> 400 com dados.faltando"""
        # Criar analise
        analise = AnaliseRiscos.objects.create(
            orgao_id=self.orgao_id,
            modo_entrada="QUESTIONARIO",
            tipo_origem="PROJETO",
            status="RASCUNHO",
            etapa_atual=0,
            criado_por=self.user,
        )

        # Tentar salvar contexto incompleto
        response = self.client.patch(
            f"/api/analise-riscos/{analise.id}/contexto/",
            {"contexto_estruturado": {"bloco_a": {}, "bloco_b": {}}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["codigo"], "CONTEXTO_INCOMPLETO")
        self.assertIn("dados", response.json())
        self.assertIn("faltando", response.json()["dados"])
        self.assertGreater(len(response.json()["dados"]["faltando"]), 0)

    def test_salvar_contexto_valido(self):
        """Teste: salvar_contexto com contexto completo -> 200"""
        analise = AnaliseRiscos.objects.create(
            orgao_id=self.orgao_id,
            modo_entrada="QUESTIONARIO",
            tipo_origem="PROJETO",
            status="RASCUNHO",
            etapa_atual=0,
            criado_por=self.user,
        )

        contexto_completo = {
            "bloco_a": {
                "nome_objeto": "Projeto de teste",
                "objetivo_finalidade": "Testar a API v2",
                "area_responsavel": "CGTI",
                "descricao_escopo": "Escopo de teste completo",
            },
            "bloco_b": {
                "recursos_necessarios": "Pessoas e sistemas",
                "areas_atores_envolvidos": "CGTI, DECIPEX",
                "frequencia_execucao": "CONTINUO",
                "prazos_slas": "30 dias",
                "dependencias_externas": "Nao ha",
                "historico_problemas": "Nao ha registro",
                "impacto_se_falhar": "Atraso no projeto",
            },
        }

        response = self.client.patch(
            f"/api/analise-riscos/{analise.id}/contexto/",
            {"contexto_estruturado": contexto_completo},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["dados"]["etapa_atual"], 1)

    def test_inferir_idempotente(self):
        """Teste: duas chamadas de inferir nao duplicam riscos"""
        # Limpar cache de rate limiting no inicio do teste
        from django.core.cache import cache
        cache.clear()

        # Criar analise com contexto e blocos
        analise = AnaliseRiscos.objects.create(
            orgao_id=self.orgao_id,
            modo_entrada="QUESTIONARIO",
            tipo_origem="PROJETO",
            status="RASCUNHO",
            etapa_atual=2,
            contexto_estruturado={
                "bloco_a": {"nome_objeto": "Teste", "objetivo_finalidade": "X", "area_responsavel": "Y", "descricao_escopo": "Z"},
                "bloco_b": {"recursos_necessarios": "A", "areas_atores_envolvidos": "B", "frequencia_execucao": "CONTINUO", "prazos_slas": "C", "dependencias_externas": "D", "historico_problemas": "E", "impacto_se_falhar": "F"},
            },
            respostas_blocos={
                "BLOCO_1": {"Q1": "ALTA", "Q2": "INFORMAL", "Q3": "CONTRATO_VIGENTE", "Q4": "CRITICA_PARA_RESULTADO_FINAL"},
            },
            criado_por=self.user,
        )

        # Contar riscos antes
        riscos_antes = RiscoIdentificado.objects.filter(analise=analise).count()
        self.assertEqual(riscos_antes, 0)

        # Primeira chamada
        response1 = self.client.post(f"/api/analise-riscos/{analise.id}/inferir/")
        self.assertEqual(response1.status_code, 200)
        riscos_criados_1 = response1.json()["dados"]["riscos_criados"]
        self.assertGreater(riscos_criados_1, 0)

        # Contar riscos apos primeira chamada
        riscos_apos_1 = RiscoIdentificado.objects.filter(analise=analise).count()
        self.assertEqual(riscos_apos_1, riscos_criados_1)

        # Limpar cache de rate limiting para permitir segunda chamada
        from django.core.cache import cache
        cache.clear()

        # Segunda chamada (idempotente)
        response2 = self.client.post(f"/api/analise-riscos/{analise.id}/inferir/")
        self.assertEqual(response2.status_code, 200)
        riscos_criados_2 = response2.json()["dados"]["riscos_criados"]

        # Segunda chamada nao deve criar novos riscos
        self.assertEqual(riscos_criados_2, 0)

        # Verificar que count no banco nao mudou
        riscos_apos_2 = RiscoIdentificado.objects.filter(analise=analise).count()
        self.assertEqual(riscos_apos_2, riscos_apos_1)
