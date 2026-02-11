"""
Sugestor de Base Legal adaptado ao contexto DECIPEX
Versão 2.2 - Focado em Gestão de Pessoas, Benefícios e Governança
Sem normas de Licitações, Compras, TI ou Orçamento
"""

import csv
import os
import re
from functools import lru_cache
from typing import Dict, List, Any


class FormatadorUtils:
    """Utilitários para formatação de dados (subset local)"""

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Remove acentos e caracteres especiais"""
        import unicodedata
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        return texto.lower()


class BaseLegalSuggestorDECIPEx:
    """
    Sugestor de Base Legal para o contexto DECIPEX
    Foco: Benefícios, Gestão de Pessoas, Processos Administrativos, Governança
    """

    def __init__(self):
        """Inicializa sugestor com biblioteca focada no DECIPEX"""
        self.biblioteca = self._carregar_biblioteca()
        self.grupos_labels = {
            "beneficios": "🩺 Benefícios e Saúde do Servidor",
            "pessoas": "👥 Gestão de Pessoas e Conduta Funcional",
            "processos": "⚙️ Gestão Processual e Atendimento",
            "riscos": "🧾 Governança, Riscos e Controles Internos",
            "dados": "🔐 Proteção de Dados e Segurança da Informação",
            "transparencia": "🔍 Transparência e Acesso à Informação",
            "controle": "📋 Controle e Acumulação"
        }

    @lru_cache(maxsize=1)
    def _carregar_biblioteca(self) -> Dict[str, Any]:
        """Carrega normas do CSV em documentos_base/base_legal_decipex.csv (cached)"""
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'documentos_base',
            'base_legal_decipex.csv'
        )

        normas = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                normas.append({
                    'id': row['id'],
                    'nome_curto': row['nome_curto'],
                    'nome_completo': row['nome_completo'],
                    'artigos': row['artigos'],
                    'palavras_chave': row['palavras_chave'].split('|'),
                    'areas': row['areas'].split('|'),
                    'hierarquia': int(row['hierarquia']),
                    'grupo': row['grupo'],
                })

        return {"normas": normas}

    def _normalizar_keywords(self, texto: str) -> List[str]:
        """Normaliza e extrai keywords de um texto"""
        texto_limpo = FormatadorUtils.normalizar_texto(texto)
        texto_limpo = re.sub(r'[^a-z0-9\s]', ' ', texto_limpo)
        palavras = texto_limpo.split()
        palavras = [p for p in palavras if len(p) > 3]
        return list(set(palavras))

    def _calcular_score_norma(self, norma: Dict[str, Any], contexto_keywords: List[str], area_codigo: str) -> float:
        """Calcula score de relevância de uma norma"""
        score = 0.0

        # Match de keywords (peso 60)
        keywords_norma = norma.get('palavras_chave', [])
        matches = sum(1 for kw in contexto_keywords if any(kw in nkw for nkw in keywords_norma))

        if len(contexto_keywords) > 0:
            score += (matches / len(contexto_keywords)) * 60

        # Match de área (peso 20)
        areas_norma = norma.get('areas', [])
        if 'todas' in areas_norma or area_codigo in areas_norma:
            score += 20

        # Hierarquia (peso 20) - quanto menor a hierarquia, maior a prioridade
        hierarquia = norma.get('hierarquia', 5)
        score_hierarquia = ((6 - hierarquia) / 5) * 20
        score += score_hierarquia

        return min(score, 100.0)

    def sugerir_base_legal(self, contexto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sugere base legal baseada no contexto do processo

        Args:
            contexto: Dict com:
                - nome_processo: str
                - area_codigo: str
                - sistemas: List[str] (opcional)
                - objetivo: str (opcional)

        Returns:
            List[Dict] com top 3 sugestões:
                - nome_curto: str
                - nome_completo: str
                - artigos: str
                - confianca: float (0-100)
                - fonte: str ("biblioteca")
                - grupo: str ("beneficios", "pessoas", etc.)
                - label: str ("🩺 Benefícios e Saúde do Servidor", etc.)
        """
        try:
            # Extrair keywords do contexto
            texto_contexto = f"{contexto.get('nome_processo', '')} {contexto.get('objetivo', '')}"
            if contexto.get('sistemas'):
                texto_contexto += " " + " ".join(contexto.get('sistemas', []))

            keywords = self._normalizar_keywords(texto_contexto)
            area_codigo = contexto.get('area_codigo', '')

            # Calcular scores para todas as normas
            normas_com_score = []
            for norma in self.biblioteca['normas']:
                score = self._calcular_score_norma(norma, keywords, area_codigo)

                if score > 0:
                    normas_com_score.append({
                        'nome_curto': norma['nome_curto'],
                        'nome_completo': norma['nome_completo'],
                        'artigos': norma['artigos'],
                        'confianca': round(score, 2),
                        'fonte': 'biblioteca',
                        'grupo': norma['grupo'],
                        'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                    })

            # Ordenar por score decrescente
            normas_com_score.sort(key=lambda x: x['confianca'], reverse=True)

            # Retornar top 3 (ou fallback se vazio)
            if not normas_com_score:
                return [{
                    'nome_curto': 'Lei 9784/99',
                    'nome_completo': 'Lei nº 9.784, de 29 de janeiro de 1999',
                    'artigos': 'Todos',
                    'confianca': 50.0,
                    'fonte': 'biblioteca',
                    'grupo': 'processos',
                    'label': self.grupos_labels['processos']
                }]

            return normas_com_score[:3]

        except Exception as e:
            print(f"Erro ao sugerir base legal: {e}")
            return []

    def buscar_por_palavra_chave(self, termo: str) -> List[Dict[str, Any]]:
        """
        Busca normas por palavra-chave específica

        Args:
            termo: Termo a ser buscado

        Returns:
            Lista de normas que contêm a palavra-chave
        """
        termo_normalizado = FormatadorUtils.normalizar_texto(termo)
        resultados = []

        for norma in self.biblioteca['normas']:
            keywords_norma = norma.get('palavras_chave', [])

            if any(termo_normalizado in kw for kw in keywords_norma):
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'confianca': 100.0,
                    'fonte': 'biblioteca',
                    'grupo': norma['grupo'],
                    'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                })

        return resultados

    def obter_normas_por_area(self, area_codigo: str) -> List[Dict[str, Any]]:
        """
        Retorna todas as normas aplicáveis a uma área específica

        Args:
            area_codigo: Código da área (ex: "CGBEN", "CGPAG")

        Returns:
            Lista de normas da área, ordenadas por hierarquia
        """
        resultados = []

        for norma in self.biblioteca['normas']:
            areas_norma = norma.get('areas', [])

            if 'todas' in areas_norma or area_codigo in areas_norma:
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'hierarquia': norma['hierarquia'],
                    'grupo': norma['grupo'],
                    'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                })

        # Ordenar por hierarquia (Lei > Decreto > IN)
        resultados.sort(key=lambda x: x['hierarquia'])

        return resultados

    def obter_grupos_normas(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna normas agrupadas por categoria

        Returns:
            Dict com estrutura:
            {
                "beneficios": {
                    "label": "🩺 Benefícios e Saúde do Servidor",
                    "itens": [norma1, norma2, ...]
                },
                ...
            }
        """
        grupos = {}

        for norma in self.biblioteca['normas']:
            grupo = norma['grupo']

            if grupo not in grupos:
                grupos[grupo] = {
                    'label': self.grupos_labels.get(grupo, grupo),
                    'itens': []
                }

            grupos[grupo]['itens'].append({
                'nome_curto': norma['nome_curto'],
                'nome_completo': norma['nome_completo'],
                'artigos': norma['artigos'],
                'hierarquia': norma['hierarquia']
            })

        # Ordenar itens dentro de cada grupo por hierarquia
        for grupo in grupos.values():
            grupo['itens'].sort(key=lambda x: x['hierarquia'])

        return grupos
