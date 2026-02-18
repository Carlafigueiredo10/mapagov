# -*- coding: utf-8 -*-
"""
===============================================================================
🧠 PIPELINE DE BUSCA EM 5 CAMADAS - Helena POP v4.0
===============================================================================

Objetivo:
    Implementar busca inteligente de atividades no catálogo oficial da DECIPEX,
    com 5 camadas de decisão automatizada e rastreabilidade completa.

Camadas:
    1. Match Exato/Fuzzy (helena_ajuda_inteligente.py)
    2. Busca Semântica (embeddings pré-computados + numpy)
    3. Curadoria Humana (Dropdown hierárquico)
    4. Fallback RAG (Helena Contextual)
    5. Geração CAP + Rastreabilidade

OTIMIZAÇÃO v4.0:
    - Embeddings pré-computados em arquivo .npy (não gera em runtime)
    - Busca por cosine com numpy (rápido, sem ChromaDB)
    - Lazy load com cache global por processo (não por request)
    - Fallback gracioso se arquivos não existirem

Autor: Claude Code Agent
Data: 2025-10-28
===============================================================================
"""

import logging
import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from processos.domain.governanca.normalize import normalize_area_prefix, normalize_numero_csv, resolve_prefixo_cap

logger = logging.getLogger(__name__)

# ==============================================================================
# CACHE GLOBAL (1x por worker, não por request)
# ==============================================================================
_CORPUS_CACHE = {
    'embeddings': None,      # np.ndarray (N, D)
    'meta': None,            # List[Dict]
    'fingerprint': None,     # Dict
    'model': None,           # SentenceTransformer (lazy)
    'loaded': False,
    'load_time_ms': 0
}


def precarregar_modelo_semantico():
    """
    Pré-carrega modelo SentenceTransformer e embeddings no startup do servidor.

    Chamada pelo AppConfig.ready() para eliminar cold-start na primeira busca.
    Idempotente: se já carregado, retorna imediatamente.
    """
    global _CORPUS_CACHE

    if _CORPUS_CACHE['model'] is not None and _CORPUS_CACHE['loaded']:
        logger.info("[STARTUP] Modelo semântico já carregado")
        return

    if os.getenv('HELENA_LITE_MODE', 'False').lower() in ('true', '1', 'yes'):
        logger.info("[STARTUP] HELENA_LITE_MODE ativo - pulando pré-carregamento")
        return

    logger.info("[STARTUP] Pré-carregando modelo semântico...")
    start_total = time.time()

    pipeline = BuscaAtividadePipeline()

    # Embeddings (.npy + meta)
    t0 = time.time()
    pipeline._carregar_embeddings_precomputados()
    t_embeddings = time.time() - t0

    # SentenceTransformer model
    t1 = time.time()
    pipeline._carregar_modelo_query()
    t_modelo = time.time() - t1

    elapsed = time.time() - start_total

    # RAM do processo atual
    try:
        import psutil
        mem_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        mem_info = f" | RAM: {mem_mb:.0f}MB"
    except ImportError:
        mem_info = ""

    logger.info(
        f"[STARTUP] Modelo semântico pré-carregado em {elapsed:.1f}s "
        f"(embeddings: {t_embeddings:.1f}s, modelo: {t_modelo:.1f}s{mem_info})"
    )


def _max_atividade_csv(caps_existentes):
    """Retorna o maior número de atividade (último segmento) nos CAPs do CSV."""
    max_csv = 0
    for cap in caps_existentes:
        partes = str(cap).split('.')
        if len(partes) >= 4:
            try:
                max_csv = max(max_csv, int(partes[-1]))
            except ValueError:
                continue
    return max_csv


def _max_atividade_db(prefixo):
    """Retorna o maior número de atividade no banco para o prefixo dado."""
    max_db = 0
    try:
        from processos.models import POP
        prefixo_busca = f"{prefixo}."
        caps_banco = POP.objects.filter(
            codigo_processo__startswith=prefixo_busca,
            is_deleted=False,
        ).values_list('codigo_processo', flat=True)
        for cap_db in caps_banco:
            try:
                max_db = max(max_db, int(str(cap_db).split('.')[-1]))
            except (ValueError, IndexError):
                continue
    except Exception as e:
        logger.warning(f"[PIPELINE] Falha ao consultar banco: {e}")
    return max_db


class BuscaAtividadePipeline:
    """
    Pipeline de busca em 5 camadas para atividades da DECIPEX.
    """

    def __init__(self, csv_path: str = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv'):
        """
        Inicializa o pipeline de busca.

        Args:
            csv_path: Caminho do CSV com a arquitetura oficial
        """
        self.csv_path = csv_path
        self.df_csv = None
        self.model = None
        self.corpus_embeddings = None
        self.areas_map = {}  # Mapa: codigo -> prefixo (ex: CGRIS -> 6)
        self.area_macros_map = {}  # Mapa: area_codigo -> lista de números de macroprocessos (ex: CGRIS -> [7])

        # Carregar CSV
        self._carregar_csv()

        # Carregar mapa de áreas
        self._carregar_areas()

        # Carregar mapa macroprocesso -> área
        self._carregar_mapeamento_macroprocesso()

        # Carregar modelo de embeddings (lazy loading)
        self._modelo_carregado = False

    def _carregar_csv(self):
        """Carrega CSV da arquitetura oficial."""
        try:
            self.df_csv = pd.read_csv(self.csv_path)
            self.df_csv = self.df_csv.fillna('')
            logger.info(f"[PIPELINE] CSV carregado: {len(self.df_csv)} atividades")
        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar CSV: {e}")
            self.df_csv = pd.DataFrame()

    def _carregar_areas(self):
        """Carrega mapa de áreas: codigo -> prefixo numérico."""
        try:
            df_areas = pd.read_csv('documentos_base/areas_organizacionais.csv')
            # Criar dicionário: CGRIS -> "6", CGBEN -> "1", DIGEP-RO -> "5.1", etc
            # Remover .0 apenas se for inteiro (6.0 -> 6, mas manter 5.1 -> 5.1)
            self.areas_map = {}
            for codigo, prefixo in zip(df_areas['codigo'], df_areas['prefixo']):
                self.areas_map[codigo] = normalize_area_prefix(str(prefixo))

            logger.info(f"[PIPELINE] Mapa de áreas carregado: {len(self.areas_map)} áreas")
            logger.debug(f"[PIPELINE] Mapa de áreas: {self.areas_map}")
        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar áreas: {e}")
            self.areas_map = {}

    def _obter_prefixo_area(self, area_codigo: str) -> str:
        """
        Converte código da área para prefixo SNI de 2 dígitos para composição de CAP.

        Subáreas (ex: DIGEP-RO=05.01) retornam o prefixo da área pai (05),
        porque CAP nunca embute subárea.

        Args:
            area_codigo: Código da área (ex: CGRIS, DIGEP-RO)

        Returns:
            Prefixo SNI 2 dígitos (ex: "01", "05")
        """
        return resolve_prefixo_cap(area_codigo, self.areas_map)

    def _carregar_mapeamento_macroprocesso(self):
        """
        Carrega mapeamento: area_codigo -> lista de números de macroprocessos.
        Ex: CGRIS -> [7], CGBEN -> [1, 2]

        Permite dar boost para atividades cujo macroprocesso (primeiro número do CSV)
        corresponde aos macroprocessos típicos da área selecionada.
        """
        try:
            # Carregar CSV de mapeamento
            df_mapeamento = pd.read_csv('documentos_base/mapeamento_macroprocesso_area.csv')

            # Criar dicionário: area_codigo -> lista de números de macroprocessos
            # Ex: CGRIS -> [7], CGBEN -> [1, 2]
            area_macros_map = {}
            for _, row in df_mapeamento.iterrows():
                area_codigo = row['area_codigo']
                macro_numero = str(row['macroprocesso_numero'])

                if area_codigo not in area_macros_map:
                    area_macros_map[area_codigo] = []
                area_macros_map[area_codigo].append(macro_numero)

            self.area_macros_map = area_macros_map
            logger.info(f"[PIPELINE] Mapeamento área->macroprocessos carregado: {len(area_macros_map)} áreas")
            logger.debug(f"[PIPELINE] Mapeamento: {area_macros_map}")

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar mapeamento macroprocesso: {e}")
            self.area_macros_map = {}

    def _carregar_embeddings_precomputados(self) -> bool:
        """
        Carrega embeddings pré-computados de arquivo (lazy load com cache global).

        OTIMIZAÇÃO v4.0:
        - Carrega 1x por worker (não por request)
        - Usa cache global _CORPUS_CACHE
        - Fallback gracioso se arquivos não existirem

        Returns:
            True se carregou com sucesso, False caso contrário
        """
        global _CORPUS_CACHE

        # Já carregado neste worker?
        if _CORPUS_CACHE['loaded']:
            return True

        # Paths dos arquivos
        base_path = 'documentos_base'
        embeddings_path = os.path.join(base_path, 'corpus_embeddings.npy')
        meta_path = os.path.join(base_path, 'corpus_meta.json')
        fingerprint_path = os.path.join(base_path, 'corpus_fingerprint.json')

        # Verificar se arquivos existem
        if not os.path.exists(embeddings_path) or not os.path.exists(meta_path):
            logger.warning("[PIPELINE] Arquivos de embeddings não encontrados. Busca semântica desabilitada.")
            logger.warning(f"[PIPELINE] Esperado: {embeddings_path}, {meta_path}")
            logger.warning("[PIPELINE] Execute: python scripts/gerar_embeddings_corpus.py")
            return False

        try:
            start_time = time.time()

            # Carregar embeddings (numpy)
            logger.info(f"[PIPELINE] Carregando embeddings: {embeddings_path}")
            _CORPUS_CACHE['embeddings'] = np.load(embeddings_path)

            # Carregar metadados
            logger.info(f"[PIPELINE] Carregando metadados: {meta_path}")
            with open(meta_path, 'r', encoding='utf-8') as f:
                _CORPUS_CACHE['meta'] = json.load(f)

            # Carregar fingerprint (opcional)
            if os.path.exists(fingerprint_path):
                with open(fingerprint_path, 'r', encoding='utf-8') as f:
                    _CORPUS_CACHE['fingerprint'] = json.load(f)

            # Validar alinhamento
            n_embeddings = _CORPUS_CACHE['embeddings'].shape[0]
            n_meta = len(_CORPUS_CACHE['meta'])
            if n_embeddings != n_meta:
                logger.error(f"[PIPELINE] ERRO: embeddings ({n_embeddings}) != meta ({n_meta})")
                return False

            load_time = (time.time() - start_time) * 1000
            _CORPUS_CACHE['loaded'] = True
            _CORPUS_CACHE['load_time_ms'] = load_time

            logger.info(f"[PIPELINE] ✅ Embeddings carregados em {load_time:.0f}ms")
            logger.info(f"[PIPELINE]    Shape: {_CORPUS_CACHE['embeddings'].shape}")
            logger.info(f"[PIPELINE]    Atividades: {n_meta}")

            return True

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar embeddings: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _carregar_modelo_query(self) -> bool:
        """
        Carrega modelo SentenceTransformer para gerar embedding da query.

        NOTA: Só carrega quando realmente precisar (lazy load).
        O modelo é usado apenas para a query do usuário, não para o corpus.
        """
        global _CORPUS_CACHE

        if _CORPUS_CACHE['model'] is not None:
            return True

        try:
            logger.info("[PIPELINE] Carregando modelo SentenceTransformer para query...")
            from sentence_transformers import SentenceTransformer
            _CORPUS_CACHE['model'] = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("[PIPELINE] ✅ Modelo carregado")
            return True
        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar modelo: {e}")
            return False

    def _carregar_modelo_embeddings(self):
        """DEPRECATED: Mantido para compatibilidade. Usa _carregar_embeddings_precomputados()."""
        if self._modelo_carregado:
            return

        # Tentar carregar pré-computados primeiro
        if self._carregar_embeddings_precomputados():
            self._modelo_carregado = True
            # Referências locais para compatibilidade
            self.corpus_embeddings = _CORPUS_CACHE['embeddings']
            self.model = _CORPUS_CACHE.get('model')
            return

        # Fallback: gerar em runtime (LENTO - só para dev)
        logger.warning("[PIPELINE] FALLBACK: Gerando embeddings em runtime (LENTO!)")
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            corpus_textos = []
            for _, row in self.df_csv.iterrows():
                texto = f"{row['Macroprocesso']} {row['Processo']} {row['Subprocesso']} {row['Atividade']}"
                corpus_textos.append(texto)

            self.corpus_embeddings = self.model.encode(corpus_textos, convert_to_tensor=True)
            logger.info(f"[PIPELINE] Embeddings gerados (fallback): shape={self.corpus_embeddings.shape}")
            self._modelo_carregado = True
        except Exception as e:
            logger.error(f"[PIPELINE] Erro no fallback: {e}")
            self.model = None

    def buscar_atividade(
        self,
        descricao_usuario: str,
        area_codigo: str,
        contexto: Optional[Dict] = None,
        autor_dados: Optional[Dict] = None
    ) -> Dict:
        """
        Pipeline completo de busca em 5 camadas.

        Args:
            descricao_usuario: Descrição da atividade pelo usuário
            area_codigo: Código da área (ex: 'CGBEN')
            contexto: Contexto adicional (opcional)
            autor_dados: Dados do autor para rastreabilidade

        Returns:
            {
                'sucesso': True,
                'origem': 'match_exato' | 'match_fuzzy' | 'semantic' | 'manual' | 'rag' | 'nova',
                'score': 0.95,
                'cap': '1.2.3.4.5',
                'atividade': {...},
                'candidatos': [...],  # Se precisar dropdown
                'rastreabilidade': {...}
            }
        """
        logger.info("="*80)
        logger.info("[PIPELINE] Iniciando busca em 5 camadas")
        logger.info("="*80)
        logger.info(f"[PIPELINE] Termo: '{descricao_usuario}'")
        logger.info(f"[PIPELINE] Área: {area_codigo}")

        # ========================================================================
        # CAMADA 1: MATCH EXATO / FUZZY
        # ========================================================================
        logger.info("[PIPELINE] >>> CAMADA 1: Match Exato/Fuzzy")
        resultado_camada1 = self._camada1_match_deterministico(descricao_usuario, area_codigo, contexto, autor_dados)

        if resultado_camada1['sucesso'] and resultado_camada1.get('encontrado'):
            logger.info(f"[PIPELINE] [OK] CAMADA 1 encontrou atividade (origem: {resultado_camada1['origem']})")
            # Adicionar botões: Confirmar / Selecionar manualmente
            resultado_camada1['acoes_usuario'] = ['confirmar', 'selecionar_manualmente']
            resultado_camada1['mensagem'] = 'Encontrei esta atividade no sistema. Deseja confirmar ou selecionar manualmente?'
            return resultado_camada1

        # ========================================================================
        # CAMADA 2: BUSCA SEMÂNTICA (SentenceTransformer)
        # ========================================================================
        logger.info("[PIPELINE] >>> CAMADA 2: Busca Semântica (SentenceTransformer)")
        resultado_camada2 = self._camada2_busca_semantica(descricao_usuario, area_codigo)

        if resultado_camada2['sucesso'] and resultado_camada2['score'] > 0:
            logger.info(f"[PIPELINE] [OK] CAMADA 2 encontrou atividade (score: {resultado_camada2['score']:.3f})")
            # Adicionar botões: Confirmar / Selecionar manualmente
            resultado_camada2['acoes_usuario'] = ['confirmar', 'selecionar_manualmente']
            resultado_camada2['mensagem'] = f"Encontrei esta atividade com {resultado_camada2['score']*100:.1f}% de similaridade. Deseja confirmar ou selecionar manualmente?"
            # CAP já vem correto da _camada2_busca_semantica (linha 292)
            resultado_camada2['rastreabilidade'] = self._gerar_rastreabilidade(
                descricao_usuario, resultado_camada2, autor_dados
            )
            return resultado_camada2

        # ========================================================================
        # CAMADA 3: SELEÇÃO MANUAL HIERÁRQUICA (4 níveis)
        # ========================================================================
        logger.info("[PIPELINE] >>> CAMADA 3: Seleção Manual Hierárquica")
        logger.info("[PIPELINE] Preparando hierarquia completa do CSV (Macro > Processo > Subprocesso > Atividade)")

        # Preparar hierarquia completa de 4 níveis
        hierarquia = self._preparar_hierarquia_completa()

        return {
            'sucesso': True,
            'origem': 'selecao_manual',
            'tipo_interface': 'dropdown_hierarquico',
            'tipo_cap': 'oficial',
            'hierarquia': hierarquia,
            'acoes_usuario': ['confirmar', 'nao_encontrei'],
            'mensagem': 'Por favor, selecione sua atividade navegando pela estrutura organizacional:'
        }

    # ========================================================================
    # IMPLEMENTAÇÃO DAS CAMADAS
    # ========================================================================

    def _camada1_match_deterministico(
        self,
        descricao_usuario: str,
        area_codigo: str,
        contexto: Optional[Dict],
        autor_dados: Optional[Dict]
    ) -> Dict:
        """
        Camada 1: Match exato e fuzzy usando helena_ajuda_inteligente.py
        """
        try:
            from processos.domain.helena_mapeamento.helena_ajuda_inteligente import classificar_e_gerar_cap

            resultado = classificar_e_gerar_cap(
                descricao_usuario=descricao_usuario,
                area_codigo=area_codigo,
                contexto=contexto,
                autor_dados=autor_dados
            )

            # Verificar se resultado é um dicionário
            if not isinstance(resultado, dict):
                logger.error(f"[PIPELINE] classificar_e_gerar_cap retornou {type(resultado)} ao invés de dict")
                return {'sucesso': False, 'encontrado': False}

            if resultado.get('sucesso') and resultado.get('origem_fluxo') in ['match_exato', 'match_fuzzy']:
                return {
                    'sucesso': True,
                    'encontrado': True,
                    'origem': resultado['origem_fluxo'],
                    'score': 1.0 if resultado['origem_fluxo'] == 'match_exato' else 0.90,
                    'cap': resultado['cap'],
                    'tipo_cap': 'oficial',
                    'acao_permitida': 'concordar_ou_selecionar_manual',
                    'pode_editar': False,
                    'atividade': {
                        'macroprocesso': resultado['macroprocesso'],
                        'processo': resultado['processo'],
                        'subprocesso': resultado['subprocesso'],
                        'atividade': resultado['atividade']
                    },
                    'rastreabilidade': self._gerar_rastreabilidade(descricao_usuario, resultado, autor_dados)
                }

            return {'sucesso': True, 'encontrado': False}

        except Exception as e:
            logger.warning(f"[PIPELINE] Erro na Camada 1: {e}")
            import traceback
            traceback.print_exc()
            return {'sucesso': False, 'encontrado': False}

    def _camada2_busca_semantica(self, descricao_usuario: str, area_codigo: str) -> Dict:
        """
        Camada 2: Busca semântica com embeddings pré-computados + numpy

        OTIMIZAÇÃO v4.0:
        - Verifica HELENA_LITE_MODE (pula se ativo)
        - Usa embeddings de arquivo .npy (não gera em runtime)
        - Cosine similarity com numpy (rápido)
        - Fallback gracioso se arquivos não existirem
        """
        global _CORPUS_CACHE

        start_time = time.time()

        # ========================================================================
        # CHECK 1: HELENA_LITE_MODE
        # ========================================================================
        if os.getenv('HELENA_LITE_MODE', 'False').lower() in ('true', '1', 'yes'):
            logger.info("[PIPELINE] LITE MODE ativo - pulando Camada 2 (busca semântica)")
            return {'sucesso': False, 'score': 0.0}

        # ========================================================================
        # CHECK 2: Carregar embeddings pré-computados
        # ========================================================================
        if not self._carregar_embeddings_precomputados():
            logger.warning("[PIPELINE] Embeddings não disponíveis - pulando Camada 2")
            return {'sucesso': False, 'score': 0.0}

        # ========================================================================
        # CHECK 3: Carregar modelo para query
        # ========================================================================
        if not self._carregar_modelo_query():
            logger.warning("[PIPELINE] Modelo não disponível - pulando Camada 2")
            return {'sucesso': False, 'score': 0.0}

        try:
            # Gerar embedding da query (normalizado)
            query_embedding = _CORPUS_CACHE['model'].encode(
                descricao_usuario,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

            # Cosine similarity com numpy (vetores já normalizados = dot product)
            corpus_embeddings = _CORPUS_CACHE['embeddings']
            cos_scores = np.dot(corpus_embeddings, query_embedding)

            # BOOST: priorizar atividades da área do usuário
            macros_da_area = self.area_macros_map.get(area_codigo, [])
            boosted_scores = cos_scores.copy()

            corpus_meta = _CORPUS_CACHE['meta']
            for idx, meta in enumerate(corpus_meta):
                numero_csv = meta.get('numero', '')
                parts = numero_csv.split('.')
                if len(parts) > 0 and parts[0] in macros_da_area:
                    boosted_scores[idx] *= 1.50  # Boost 50%

            # Melhor match
            best_idx = int(np.argmax(boosted_scores))
            best_score = float(cos_scores[best_idx])  # Score original
            best_meta = corpus_meta[best_idx]

            # Log métricas
            elapsed_ms = (time.time() - start_time) * 1000
            macro_match = best_meta['numero'].split('.')[0] if '.' in best_meta['numero'] else best_meta['numero']
            foi_boosted = macro_match in macros_da_area

            logger.info(f"[PIPELINE] Camada 2 concluída em {elapsed_ms:.0f}ms")
            logger.info(f"[PIPELINE] Melhor match: score={best_score:.3f} {'(BOOSTED)' if foi_boosted else ''}")
            logger.info(f"[PIPELINE]   Atividade: {best_meta['atividade']}")

            # Gerar CAP (SNI: AA.MM.PP.SS.III)
            prefixo_area = self._obter_prefixo_area(area_codigo)
            cap_completo = f"{prefixo_area}.{normalize_numero_csv(best_meta['numero'])}"

            return {
                'sucesso': True,
                'origem': 'semantic',
                'score': best_score,
                'cap': cap_completo,
                'tipo_cap': 'oficial',
                'acao_permitida': 'concordar_ou_selecionar_manual',
                'pode_editar': False,
                'atividade': {
                    'macroprocesso': best_meta['macroprocesso'],
                    'processo': best_meta['processo'],
                    'subprocesso': best_meta['subprocesso'],
                    'atividade': best_meta['atividade']
                },
                'metricas': {
                    'tempo_ms': elapsed_ms,
                    'corpus_size': len(corpus_meta),
                    'cache_hit': _CORPUS_CACHE['loaded']
                }
            }

        except Exception as e:
            logger.error(f"[PIPELINE] Erro na Camada 2: {e}")
            import traceback
            traceback.print_exc()
            return {'sucesso': False, 'score': 0.0}

    def _preparar_candidatos_dropdown(self, descricao_usuario: str, area_codigo: str, top_k: int = 5) -> List[Dict]:
        """
        Prepara top-K candidatos para dropdown (Camada 3)
        """
        if self.model is None or self.corpus_embeddings is None:
            return []

        try:
            query_embedding = self.model.encode(descricao_usuario, convert_to_tensor=True)
            cos_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]

            # Top-K scores
            top_results = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))

            # Obter prefixo da área selecionada
            prefixo_area = self._obter_prefixo_area(area_codigo)

            candidatos = []
            for score, idx in zip(top_results[0], top_results[1]):
                row = self.df_csv.iloc[int(idx)]
                # CAP = prefixo_area + numero_csv (SNI padded)
                cap_completo = f"{prefixo_area}.{normalize_numero_csv(str(row['Numero']).strip())}"
                candidatos.append({
                    'score': float(score),
                    'cap': cap_completo,
                    'tipo_cap': 'oficial',
                    'macroprocesso': row['Macroprocesso'],
                    'processo': row['Processo'],
                    'subprocesso': row['Subprocesso'],
                    'atividade': row['Atividade']
                })

            logger.info(f"[PIPELINE] Top-{len(candidatos)} candidatos preparados para dropdown")
            return candidatos

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao preparar candidatos: {e}")
            return []

    def _preparar_hierarquia_completa(self, area_codigo: str = None) -> Dict:
        """
        Prepara hierarquia completa de 4 níveis do CSV para dropdown em cascata

        Args:
            area_codigo: Código da área selecionada (ex: CGBEN, CGRIS) para gerar CAP correto

        Retorna estrutura:
        {
            'Gestão de Benefícios Previdenciários': {
                'Gestão de Aposentadorias': {
                    'Concessão de aposentadorias': [
                        {'atividade': 'Conceder benefício...', 'cap': '1.1.1.1'},
                        ...
                    ]
                }
            }
        }
        """
        try:
            hierarquia = {}

            # Obter prefixo da área se fornecido
            prefixo_area = None
            if area_codigo:
                prefixo_area = self._obter_prefixo_area(area_codigo)

            for _, row in self.df_csv.iterrows():
                macro = row['Macroprocesso']
                processo = row['Processo']
                subprocesso = row['Subprocesso']
                atividade = row['Atividade']
                numero_csv = str(row['Numero']).strip()

                # Gerar CAP: prefixo_area + numero_csv (SNI padded)
                numero_norm = normalize_numero_csv(numero_csv)
                if prefixo_area:
                    cap = f"{prefixo_area}.{numero_norm}"
                else:
                    cap = numero_norm

                # Criar estrutura aninhada
                if macro not in hierarquia:
                    hierarquia[macro] = {}

                if processo not in hierarquia[macro]:
                    hierarquia[macro][processo] = {}

                if subprocesso not in hierarquia[macro][processo]:
                    hierarquia[macro][processo][subprocesso] = []

                # Adicionar atividade
                hierarquia[macro][processo][subprocesso].append({
                    'atividade': atividade,
                    'cap': cap
                })

            logger.info(f"[PIPELINE] Hierarquia preparada: {len(hierarquia)} macroprocessos")
            return hierarquia

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao preparar hierarquia: {e}")
            return {}

    def _camada4_fallback_rag(
        self,
        descricao_usuario: str,
        area_codigo: str,
        contexto: Optional[Dict],
        autor_dados: Optional[Dict] = None,
        hierarquia_selecionada: Optional[Dict] = None
    ) -> Dict:
        """
        Camada 4: RAG com hierarquia pré-selecionada (última instância)

        NOVA REGRA v4.0:
        - É chamada quando usuário clica "Não encontrei minha atividade" na Camada 3
        - HERDA a hierarquia (Macro/Processo/Subprocesso) selecionada na Camada 3
        - Cria APENAS a nova ATIVIDADE dentro dessa hierarquia
        - Helena pergunta: "Vi que você não encontrou. Me conta, uma última vez, o que você faz?"
        - CAP é gerado sequencialmente dentro do subprocesso selecionado

        IMPORTANTE: Esta camada SEMPRE resolve (nunca falha)
        """
        try:
            logger.info("[PIPELINE] >>> CAMADA 4: RAG (Criação de nova atividade)")

            # Verificar se temos hierarquia selecionada da Camada 3
            if not hierarquia_selecionada:
                logger.error("[PIPELINE] [ERRO CRÍTICO] Camada 4 chamada sem hierarquia selecionada!")
                return {
                    'sucesso': False,
                    'erro': 'Hierarquia não foi selecionada na Camada 3'
                }

            macro = hierarquia_selecionada.get('macroprocesso')
            processo = hierarquia_selecionada.get('processo')
            subprocesso = hierarquia_selecionada.get('subprocesso')

            logger.info(f"[PIPELINE] Hierarquia herdada da Camada 3:")
            logger.info(f"[PIPELINE]   Macro: {macro}")
            logger.info(f"[PIPELINE]   Processo: {processo}")
            logger.info(f"[PIPELINE]   Subprocesso: {subprocesso}")

            # Validar que hierarquia existe no CSV
            if not self._validar_hierarquia_existe(macro, processo, subprocesso):
                logger.error(f"[PIPELINE] Hierarquia inválida: {macro} > {processo} > {subprocesso}")
                return {
                    'sucesso': False,
                    'erro': 'Hierarquia selecionada não existe no CSV'
                }

            # Helena pergunta ao usuário
            mensagem_helena = "Vi que você não encontrou sua atividade. Me conta, uma última vez, o que você faz?"

            logger.info("[PIPELINE] Aguardando usuário descrever sua atividade...")

            # Retornar interface de pergunta para o usuário
            return {
                'sucesso': True,
                'origem': 'rag_aguardando_descricao',
                'tipo_interface': 'pergunta_atividade',
                'hierarquia_herdada': {
                    'macroprocesso': macro,
                    'processo': processo,
                    'subprocesso': subprocesso
                },
                'mensagem': mensagem_helena,
                'instrucao_frontend': 'Mostrar campo de texto para usuário descrever sua atividade'
            }

        except Exception as e:
            logger.error(f"[PIPELINE] Erro na Camada 4 (RAG): {e}")
            import traceback
            traceback.print_exc()
            return {'sucesso': False, 'encontrado': False}

    def _camada4_processar_resposta(
        self,
        descricao_atividade: str,
        hierarquia_herdada: Dict,
        area_codigo: str,
        autor_dados: Optional[Dict] = None
    ) -> Dict:
        """
        Processa a resposta do usuário na Camada 4 e cria a nova atividade

        Esta função é chamada APÓS o usuário responder a pergunta da Helena.
        Recebe a descrição da atividade e a hierarquia herdada da Camada 3.
        """
        try:
            from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

            macro = hierarquia_herdada['macroprocesso']
            processo = hierarquia_herdada['processo']
            subprocesso = hierarquia_herdada['subprocesso']

            logger.info(f"[PIPELINE] Processando descrição do usuário: '{descricao_atividade}'")
            logger.info(f"[PIPELINE] Dentro da hierarquia: {macro} > {processo} > {subprocesso}")

            # Chamar RAG apenas para sugerir o nome da atividade
            resultado_ia = analisar_atividade_com_helena(
                descricao_usuario=descricao_atividade,
                nivel_atual='apenas_atividade',
                contexto_ja_selecionado={
                    'macroprocesso': macro,
                    'processo': processo,
                    'subprocesso': subprocesso
                }
            )

            if not resultado_ia.get('sucesso'):
                logger.error("[PIPELINE] RAG falhou ao sugerir atividade")
                return {'sucesso': False, 'erro': 'Falha ao processar descrição'}

            atividade_sugerida = resultado_ia['sugestao'].get('atividade', descricao_atividade)

            # Gerar CAP sequencial dentro do subprocesso (incluindo área)
            cap_novo = self._gerar_cap_sequencial(area_codigo, macro, processo, subprocesso)

            logger.info(f"[PIPELINE] [RAG] Nova atividade criada!")
            logger.info(f"[PIPELINE] [RAG] Atividade: {atividade_sugerida}")
            logger.info(f"[PIPELINE] [RAG] CAP gerado: {cap_novo}")
            logger.info(f"[PIPELINE] [RAG] Dentro de: {macro} > {processo} > {subprocesso}")

            return {
                'sucesso': True,
                'encontrado': True,
                'origem': 'rag_nova_atividade',
                'cap': cap_novo,
                'tipo_cap': 'oficial_gerado_rag',
                'acao_permitida': 'revisar_e_aprovar',
                'pode_editar': True,
                'atividade': {
                    'macroprocesso': macro,
                    'processo': processo,
                    'subprocesso': subprocesso,
                    'atividade': atividade_sugerida
                },
                'hierarquia_herdada': hierarquia_herdada,
                'mensagem': f'Criei a nova atividade "{atividade_sugerida}" dentro de "{subprocesso}". Por favor, revise e aprove.'
            }

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao processar resposta Camada 4: {e}", exc_info=True)
            return {'sucesso': False, 'erro': 'Erro ao processar classificacao. Tente novamente.'}

    def _camada5_nova_atividade(
        self,
        descricao_usuario: str,
        area_codigo: str,
        contexto: Optional[Dict],
        autor_dados: Optional[Dict]
    ) -> Dict:
        """
        Camada 5: Cria nova atividade candidata e atribui a um dos 12 macroprocessos
        """
        logger.info("[PIPELINE] Criando nova atividade candidata...")

        # Classificar em um dos 12 macroprocessos existentes
        macroprocesso_atribuido = self._classificar_macroprocesso(descricao_usuario)

        logger.info(f"[PIPELINE] Macroprocesso atribuído: {macroprocesso_atribuido}")

        # Gerar CAP provisório
        cap_provisorio = self._gerar_cap_provisorio(macroprocesso_atribuido, area_codigo)

        return {
            'sucesso': True,
            'origem': 'nova',
            'score': 0.0,
            'cap': cap_provisorio,
            'atividade': {
                'macroprocesso': macroprocesso_atribuido,
                'processo': 'A definir',
                'subprocesso': 'A definir',
                'atividade': descricao_usuario
            },
            'rastreabilidade': {
                'termo_consulta': descricao_usuario,
                'timestamp': datetime.now().isoformat(),
                'origem': 'nova',
                'score': 0.0,
                'autor': autor_dados,
                'macroprocesso_atribuido': macroprocesso_atribuido
            }
        }

    def _classificar_macroprocesso(self, descricao_usuario: str) -> str:
        """
        Classifica a atividade em um dos 12 macroprocessos oficiais usando embeddings
        """
        if self.df_csv.empty:
            return "Gestão de Benefícios Previdenciários"  # Fallback

        try:
            # Carregar modelo se necessário
            self._carregar_modelo_embeddings()

            if self.model is None:
                return "Gestão de Benefícios Previdenciários"  # Fallback

            # Lista de macroprocessos únicos
            macros_unicos = self.df_csv['Macroprocesso'].unique().tolist()
            macros_unicos = [m for m in macros_unicos if m and str(m).strip()]

            if not macros_unicos:
                return "Gestão de Benefícios Previdenciários"  # Fallback

            logger.info(f"[PIPELINE] Classificando entre {len(macros_unicos)} macroprocessos")

            # Gerar embeddings dos macroprocessos
            macro_embeddings = self.model.encode(macros_unicos, convert_to_tensor=True)
            query_embedding = self.model.encode(descricao_usuario, convert_to_tensor=True)

            # Calcular similaridade
            scores = util.pytorch_cos_sim(query_embedding, macro_embeddings)[0]
            best_idx = int(torch.argmax(scores))
            best_score = float(scores[best_idx])

            macroprocesso_escolhido = macros_unicos[best_idx]

            logger.info(f"[PIPELINE] Macroprocesso escolhido: {macroprocesso_escolhido} (score: {best_score:.3f})")

            return macroprocesso_escolhido

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao classificar macroprocesso: {e}")
            return "Gestão de Benefícios Previdenciários"  # Fallback

    def _gerar_cap(self, atividade: Dict, area_codigo: str) -> str:
        """
        Gera CAP oficial baseado na atividade encontrada no CSV.

        Args:
            atividade: Dict com dados da atividade
            area_codigo: Código da área (ex: CGRIS) - será convertido para prefixo numérico

        Returns:
            CAP completo no formato: prefixo_area.numero (ex: 6.7.2.1.1)
        """
        prefixo_area = self._obter_prefixo_area(area_codigo)
        numero = atividade.get('numero', '')
        if numero:
            return f"{prefixo_area}.{normalize_numero_csv(numero)}"

        # Fallback: gerar provisório
        return self._gerar_cap_provisorio(atividade.get('macroprocesso', ''), area_codigo)

    def _gerar_cap_provisorio(self, macroprocesso: str, area_codigo: str) -> str:
        """
        Gera CAP provisório para novas atividades.

        Args:
            macroprocesso: Nome do macroprocesso
            area_codigo: Código da área (ex: CGRIS) - será convertido para prefixo numérico

        Returns:
            CAP provisório no formato: prefixo_area.macro.XX.XX.seq (ex: 6.7.XX.XX.1234)
        """
        # Buscar índice do macroprocesso
        try:
            prefixo_area = self._obter_prefixo_area(area_codigo)

            macros = self.df_csv['Macroprocesso'].unique().tolist()
            if macroprocesso in macros:
                idx_macro = macros.index(macroprocesso) + 1
            else:
                idx_macro = 99  # Provisório

            # Gerar número sequencial provisório (formato SNI)
            import random
            seq = random.randint(1, 9)

            return f"{prefixo_area}.{idx_macro:02d}.XX.XX.{seq:03d}"

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao gerar CAP provisório: {e}")
            return f"{area_codigo}.99.XX.XX.1"

    def _validar_hierarquia_existe(self, macroprocesso: str, processo: str, subprocesso: str) -> bool:
        """
        Valida se a hierarquia (Macro > Processo > Subprocesso) existe no CSV oficial

        REGRA: Camada 4 (RAG) NÃO pode criar novos níveis hierárquicos,
        apenas novas atividades dentro da hierarquia existente.
        """
        try:
            # Filtrar linhas que correspondem à hierarquia completa
            filtro = (
                (self.df_csv['Macroprocesso'] == macroprocesso) &
                (self.df_csv['Processo'] == processo) &
                (self.df_csv['Subprocesso'] == subprocesso)
            )

            exists = not self.df_csv[filtro].empty

            if exists:
                logger.info(f"[PIPELINE] Hierarquia validada: {macroprocesso} > {processo} > {subprocesso}")
            else:
                logger.warning(f"[PIPELINE] Hierarquia NÃO existe no CSV: {macroprocesso} > {processo} > {subprocesso}")

            return exists

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao validar hierarquia: {e}")
            return False

    def _gerar_cap_sequencial(self, area_codigo: str, macroprocesso: str, processo: str, subprocesso: str) -> str:
        """
        Gera CAP sequencial dentro de um subprocesso existente

        LÓGICA:
        1. Busca todos os CAPs do mesmo subprocesso E mesma área
        2. Localiza o último CAP (ex: 5.1.2.3.109 para CGBEN)
        3. Incrementa o índice final: 5.1.2.3.110

        FORMATO CORRETO: Área.Macro.Processo.Subprocesso.Atividade
        Exemplo: 5.1.2.3.110 = CGBEN / Gestão Governança / ... / atividade 110

        IMPORTANTE: Mantém os 4 primeiros níveis (área.macro.processo.sub)
        e incrementa apenas o último índice.
        """
        try:
            # 🎯 Obter prefixo da área usando o método que já trata floats corretamente
            # IMPORTANTE: prefixo pode ser "5" (área) ou "5.3" (subárea)
            # FIX: Usar _obter_prefixo_area() em vez de ler direto do CSV
            # para evitar bug de pandas ler "1" como 1.0 e virar "1.0" em CAPs
            try:
                prefixo_area = self._obter_prefixo_area(area_codigo)
                logger.info(f"[PIPELINE] Prefixo da área {area_codigo}: {prefixo_area}")
            except Exception as e:
                logger.error(f"[PIPELINE] Erro ao buscar prefixo da área: {e}")
                import traceback
                traceback.print_exc()
                # Fallback: usar 99 como área desconhecida
                prefixo_area = "99"

            # Filtrar atividades do mesmo subprocesso
            filtro = (
                (self.df_csv['Macroprocesso'] == macroprocesso) &
                (self.df_csv['Processo'] == processo) &
                (self.df_csv['Subprocesso'] == subprocesso)
            )

            atividades_subprocesso = self.df_csv[filtro]

            if atividades_subprocesso.empty:
                logger.warning(f"[PIPELINE] Nenhuma atividade encontrada no subprocesso: {subprocesso}")
                # Se não encontrou atividades, começar do índice 1
                return f"{prefixo_area}.01.01.01.001"

            # Extrair todos os CAPs do subprocesso
            caps_existentes = atividades_subprocesso['Numero'].tolist()

            logger.info(f"[PIPELINE] CAPs existentes no subprocesso '{subprocesso}': {len(caps_existentes)}")

            # Pegar o primeiro CAP como base para extrair a estrutura
            # IMPORTANTE: O CAP no CSV NÃO inclui o prefixo da área!
            # Exemplo CSV: "08.01.01.001" (MM.PP.SS.III — já normalizado)
            # CAP final: "05.08.01.01.001" (AA.MM.PP.SS.III)
            ultimo_cap = caps_existentes[0]

            # Extrair partes do Numero CSV (ex: "08.01.01.001" → ["08", "01", "01", "001"])
            partes = str(ultimo_cap).split('.')

            if len(partes) < 4:
                logger.warning(f"[PIPELINE] Formato de CAP inválido no CSV: {ultimo_cap}")
                return f"{prefixo_area}.01.01.01.001"

            # O CAP no CSV tem formato: Macro.Processo.Subprocesso.Atividade
            # Precisamos adicionar o prefixo da área no início
            macro = f"{int(partes[0]):02d}"
            processo = f"{int(partes[1]):02d}"
            subprocesso = f"{int(partes[2]):02d}"
            # partes[3] é a atividade, que vamos ignorar e calcular o próximo número

            estrutura_processo = f"{macro}.{processo}.{subprocesso}"
            prefixo = f"{prefixo_area}.{estrutura_processo}"

            logger.info(f"[PIPELINE] Prefixo área: {prefixo_area}")
            logger.info(f"[PIPELINE] Estrutura processo: {estrutura_processo} (Macro={macro}, Proc={processo}, Sub={subprocesso})")
            logger.info(f"[PIPELINE] CAP base do CSV (sem área): {ultimo_cap}")

            max_csv = _max_atividade_csv(caps_existentes)
            max_db = _max_atividade_db(prefixo)
            logger.info(f"[PIPELINE] Max atividade - CSV: {max_csv}, DB: {max_db}")

            # --- Candidato = max(csv, db) + 1, validar disponibilidade ---
            candidato = max(max_csv, max_db) + 1
            logger.info(f"[PIPELINE] max_csv={max_csv}, max_db={max_db}, candidato={candidato}")

            try:
                from processos.models import POP
                for _ in range(50):
                    cap_candidato = f"{prefixo}.{candidato}"
                    if not POP.objects.filter(codigo_processo=cap_candidato, is_deleted=False).exists():
                        break
                    candidato += 1
            except Exception:
                pass  # Se banco indisponível, usa o candidato calculado

            cap_novo = f"{prefixo}.{candidato}"

            logger.info(f"[PIPELINE] CAP sequencial gerado: {cap_novo}")
            logger.info(f"[PIPELINE] Composicao: [{prefixo_area}] + [{macro}.{processo}.{subprocesso}] + [{candidato}]")

            return cap_novo

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao gerar CAP sequencial: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: gerar CAP genérico com área 99
            return "99.99.99.99.001"

    def _gerar_rastreabilidade(
        self,
        descricao_usuario: str,
        resultado: Dict,
        autor_dados: Optional[Dict]
    ) -> Dict:
        """
        Gera metadados de rastreabilidade
        """
        # resultado pode vir de classificar_e_gerar_cap (flat: 'atividade' é string)
        # ou de outras camadas (nested: 'atividade' é dict)
        atividade_nome = resultado.get('atividade')
        if isinstance(atividade_nome, dict):
            atividade_nome = atividade_nome.get('atividade')

        return {
            'termo_consulta': descricao_usuario,
            'timestamp': datetime.now().isoformat(),
            'origem': resultado.get('origem', 'unknown'),
            'score': resultado.get('score', 0.0),
            'autor': autor_dados,
            'cap_gerado': resultado.get('cap'),
            'atividade_encontrada': atividade_nome
        }
