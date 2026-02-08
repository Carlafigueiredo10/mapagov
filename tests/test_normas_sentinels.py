"""
Testes de regressao: sentinels de normas em _processar_dispositivos_normativos.

Garante que inputs vazios/sentinels nunca viram dado falso persistido.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')

import django
django.setup()

from processos.domain.helena_mapeamento.helena_pop import HelenaPOP, POPStateMachine, EstadoPOP


class TestNormasSentinels(unittest.TestCase):
    """Testa que sentinels resultam em lista vazia de normas."""

    def _processar(self, mensagem: str) -> list:
        """Helper: processa mensagem no estado DISPOSITIVOS_NORMATIVOS e retorna normas salvas."""
        helena = HelenaPOP()
        sm = POPStateMachine()
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS
        sm.nome_usuario = "Teste"
        helena._processar_dispositivos_normativos(mensagem, sm)
        return sm.dados_coletados.get('dispositivos_normativos', None)

    def test_nenhuma_retorna_lista_vazia(self):
        self.assertEqual(self._processar("nenhuma"), [])

    def test_nao_sei_retorna_lista_vazia(self):
        self.assertEqual(self._processar("nao sei"), [])

    def test_nao_sei_acentuado_retorna_lista_vazia(self):
        self.assertEqual(self._processar("não sei"), [])

    def test_string_vazia_retorna_lista_vazia(self):
        self.assertEqual(self._processar(""), [])

    def test_sem_normas_retorna_lista_vazia(self):
        self.assertEqual(self._processar("sem normas"), [])

    def test_lista_json_com_sentinel_filtra(self):
        """Input ["Lei X", "nao sei"] deve resultar em ["Lei X"]."""
        import json
        entrada = json.dumps(["Lei X", "nao sei"])
        resultado = self._processar(entrada)
        self.assertEqual(resultado, ["Lei X"])

    def test_norma_valida_persiste(self):
        resultado = self._processar("Art. 34 da IN SGP 97/2022")
        self.assertEqual(resultado, ["Art. 34 da IN SGP 97/2022"])

    def test_multiplas_normas_persistem(self):
        resultado = self._processar("Decreto 9991/2019, IN 21/2021")
        self.assertEqual(len(resultado), 2)
        self.assertIn("Decreto 9991/2019", resultado)
        self.assertIn("IN 21/2021", resultado)

    def test_pdf_com_normas_vazias(self):
        """PDF nao deve crashar com dispositivos_normativos=[]."""
        from processos.export.pop_adapter import preparar_pop_para_pdf
        dados = preparar_pop_para_pdf({
            "nome_processo": "Teste sem normas",
            "dispositivos_normativos": [],
        })
        # Deve ter sido normalizado para string de fallback ou mantido como lista vazia
        disp = dados.get('dispositivos_normativos')
        self.assertIsNotNone(disp)


if __name__ == '__main__':
    unittest.main()
