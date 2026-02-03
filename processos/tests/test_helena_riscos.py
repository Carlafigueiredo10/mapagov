"""
Testes para Helena Riscos

Testa: fluxo conversacional, transicoes de etapa, inferencia de categoria
"""
from django.test import TestCase

from processos.domain.helena_analise_riscos import HelenaRiscos


class HelenaRiscosTestCase(TestCase):
    """Testes para Helena Riscos"""

    def setUp(self):
        """Setup para cada teste"""
        self.helena = HelenaRiscos()

    def test_inicializar_estado(self):
        """Teste: estado inicial correto"""
        estado = self.helena.inicializar_estado()

        self.assertEqual(estado["etapa_atual"], 1)
        self.assertIsNone(estado["analise_id"])
        self.assertEqual(estado["questoes_respondidas"], {})
        self.assertIsNone(estado["area_decipex"])
        self.assertEqual(estado["riscos_identificados"], [])
        self.assertEqual(estado["historico"], [])
        self.assertEqual(estado["contador_mensagens"], 0)

    def test_etapa1_mensagem_inicial(self):
        """Teste: etapa 1 mostra areas DECIPEX"""
        estado = self.helena.inicializar_estado()
        resultado = self.helena.processar("ola", estado)

        self.assertIn("DECIPEX", resultado["resposta"])
        self.assertEqual(resultado["novo_estado"]["etapa_atual"], 1)

    def test_etapa1_selecionar_area(self):
        """Teste: selecionar area avanca para etapa 2"""
        estado = self.helena.inicializar_estado()
        resultado = self.helena.processar("CGBEN", estado)

        self.assertEqual(resultado["novo_estado"]["area_decipex"], "CGBEN")
        self.assertEqual(resultado["novo_estado"]["etapa_atual"], 2)

    def test_etapa2_adicionar_risco(self):
        """Teste: adicionar risco na etapa 2"""
        estado = self.helena.inicializar_estado()
        estado["etapa_atual"] = 2
        estado["area_decipex"] = "CGBEN"

        resultado = self.helena.processar(
            "Falha no sistema de pagamentos pode atrasar beneficios",
            estado
        )

        self.assertEqual(len(resultado["novo_estado"]["riscos_identificados"]), 1)
        self.assertIn("risco", resultado["resposta"].lower())

    def test_inferir_categoria_financeiro(self):
        """Teste: inferir categoria FINANCEIRO"""
        categoria = self.helena._inferir_categoria(
            "Risco de estouro do orcamento previsto"
        )
        self.assertEqual(categoria, "FINANCEIRO")

    def test_inferir_categoria_legal(self):
        """Teste: inferir categoria LEGAL"""
        categoria = self.helena._inferir_categoria(
            "Descumprimento da norma de compliance"
        )
        self.assertEqual(categoria, "LEGAL")

    def test_inferir_categoria_tecnologico(self):
        """Teste: inferir categoria TECNOLOGICO"""
        categoria = self.helena._inferir_categoria(
            "Falha no sistema de TI pode causar indisponibilidade"
        )
        self.assertEqual(categoria, "TECNOLOGICO")

    def test_inferir_categoria_default_operacional(self):
        """Teste: categoria default e OPERACIONAL"""
        categoria = self.helena._inferir_categoria(
            "Atraso na entrega do relatorio"
        )
        self.assertEqual(categoria, "OPERACIONAL")

    def test_etapa3_analisar_risco(self):
        """Teste: analisar risco com probabilidade e impacto"""
        estado = self.helena.inicializar_estado()
        estado["etapa_atual"] = 3
        estado["riscos_identificados"] = [{
            "titulo": "Risco teste",
            "categoria": "OPERACIONAL",
            "descricao": "Descricao teste",
            "probabilidade": None,
            "impacto": None,
        }]

        resultado = self.helena.processar("3 4", estado)

        risco = resultado["novo_estado"]["riscos_identificados"][0]
        self.assertEqual(risco["probabilidade"], 3)
        self.assertEqual(risco["impacto"], 4)
        self.assertEqual(risco["score"], 12)
        self.assertEqual(risco["nivel"], "ALTO")

    def test_get_etapas(self):
        """Teste: get_etapas retorna 6 etapas"""
        etapas = self.helena.get_etapas()
        self.assertEqual(len(etapas), 6)
        self.assertIn(1, etapas)
        self.assertIn(6, etapas)

    def test_get_categorias(self):
        """Teste: get_categorias retorna todas categorias"""
        categorias = self.helena.get_categorias()
        self.assertIn("OPERACIONAL", categorias)
        self.assertIn("IMPACTO_DESIGUAL", categorias)

    def test_get_estrategias(self):
        """Teste: get_estrategias retorna todas estrategias"""
        estrategias = self.helena.get_estrategias()
        self.assertIn("MITIGAR", estrategias)
        self.assertIn("COMPARTILHAR", estrategias)

    def test_version_e_nome(self):
        """Teste: version e nome corretos"""
        self.assertEqual(self.helena.VERSION, "1.0.0")
        self.assertEqual(self.helena.PRODUTO_NOME, "Helena Riscos")

    def test_historico_atualizado(self):
        """Teste: historico e atualizado apos processamento"""
        estado = self.helena.inicializar_estado()
        resultado = self.helena.processar("ola", estado)

        historico = resultado["novo_estado"]["historico"]
        self.assertEqual(len(historico), 2)  # user + assistant
        self.assertEqual(historico[0]["role"], "user")
        self.assertEqual(historico[1]["role"], "assistant")

    def test_mensagem_vazia_levanta_erro(self):
        """Teste: mensagem vazia deve levantar ValueError"""
        estado = self.helena.inicializar_estado()
        with self.assertRaises(ValueError):
            self.helena.processar("", estado)

    def test_mensagem_apenas_espacos_levanta_erro(self):
        """Teste: mensagem apenas espacos deve levantar ValueError"""
        estado = self.helena.inicializar_estado()
        with self.assertRaises(ValueError):
            self.helena.processar("   ", estado)

    def test_etapa_invalida_retorna_erro(self):
        """Teste: etapa invalida retorna mensagem de erro"""
        estado = self.helena.inicializar_estado()
        estado["etapa_atual"] = 99

        resultado = self.helena.processar("teste", estado)
        self.assertIn("Erro", resultado["resposta"])

    def test_detectar_comando_navegacao(self):
        """Teste: detecta comandos de navegacao"""
        self.assertTrue(self.helena._detectar_comando_navegacao("avancar"))
        self.assertTrue(self.helena._detectar_comando_navegacao("quero continuar"))
        self.assertTrue(self.helena._detectar_comando_navegacao("finalizar agora"))
        self.assertFalse(self.helena._detectar_comando_navegacao("adicionar risco"))

    def test_etapa2_nao_avanca_sem_riscos(self):
        """Teste: etapa 2 nao avanca sem riscos identificados"""
        estado = self.helena.inicializar_estado()
        estado["etapa_atual"] = 2
        estado["area_decipex"] = "CGBEN"

        resultado = self.helena.processar("avancar", estado)

        self.assertEqual(resultado["novo_estado"]["etapa_atual"], 2)
        self.assertIn("nao identificou", resultado["resposta"].lower())
