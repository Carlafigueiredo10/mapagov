# -*- coding: utf-8 -*-
"""
===============================================================================
🧠 PIPELINE DE BUSCA EM 5 CAMADAS - Helena POP v3.0
===============================================================================

Objetivo:
    Implementar busca inteligente de atividades no catálogo oficial da DECIPEX,
    com 5 camadas de decisão automatizada e rastreabilidade completa.

Camadas:
    1. Match Exato/Fuzzy (helena_ajuda_inteligente.py)
    2. Busca Semântica (SentenceTransformer)
    3. Curadoria Humana (Dropdown Top-5)
    4. Fallback RAG (Helena Contextual)
    5. Geração CAP + Rastreabilidade

Autor: Claude Code Agent
Data: 2025-10-28
===============================================================================
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)


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
                prefixo_float = float(prefixo)
                if prefixo_float == int(prefixo_float):
                    # É inteiro: 6.0 -> "6"
                    self.areas_map[codigo] = str(int(prefixo_float))
                else:
                    # Tem decimal: 5.1 -> "5.1"
                    self.areas_map[codigo] = str(prefixo_float)

            logger.info(f"[PIPELINE] Mapa de áreas carregado: {len(self.areas_map)} áreas")
            logger.debug(f"[PIPELINE] Mapa de áreas: {self.areas_map}")
        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar áreas: {e}")
            self.areas_map = {}

    def _obter_prefixo_area(self, area_codigo: str) -> str:
        """
        Converte código da área (ex: CGRIS) para prefixo numérico (ex: 6).

        Args:
            area_codigo: Código da área (ex: CGRIS, CGBEN)

        Returns:
            Prefixo numérico como string (ex: "6", "1")
        """
        return self.areas_map.get(area_codigo, area_codigo)

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

    def _carregar_modelo_embeddings(self):
        """Carrega modelo SentenceTransformer (lazy loading)."""
        if self._modelo_carregado:
            return

        try:
            logger.info("[PIPELINE] Carregando modelo SentenceTransformer...")
            # Modelo multilingual otimizado para similaridade semântica
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

            # Pré-computar embeddings do corpus (cache)
            logger.info("[PIPELINE] Gerando embeddings do corpus...")
            corpus_textos = []
            for _, row in self.df_csv.iterrows():
                texto = f"{row['Macroprocesso']} {row['Processo']} {row['Subprocesso']} {row['Atividade']}"
                corpus_textos.append(texto)

            self.corpus_embeddings = self.model.encode(corpus_textos, convert_to_tensor=True)
            logger.info(f"[PIPELINE] Embeddings gerados: shape={self.corpus_embeddings.shape}")

            self._modelo_carregado = True
        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao carregar modelo: {e}")
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
            from processos.domain.helena_produtos.helena_ajuda_inteligente import classificar_e_gerar_cap

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
        Camada 2: Busca semântica com SentenceTransformer
        """
        # Carregar modelo se necessário
        self._carregar_modelo_embeddings()

        if self.model is None or self.corpus_embeddings is None:
            logger.error("[PIPELINE] Modelo não carregado - pulando Camada 2")
            return {'sucesso': False, 'score': 0.0}

        try:
            # Gerar embedding da consulta do usuário
            query_embedding = self.model.encode(descricao_usuario, convert_to_tensor=True)

            # Calcular similaridade cosine
            cos_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]

            # BOOST: Dar prioridade para atividades cujo macroprocesso pertence à área selecionada
            # Respeitar a escolha do usuário - buscar primeiro nas atividades típicas da área dele
            macros_da_area = self.area_macros_map.get(area_codigo, [])

            boosted_scores = cos_scores.clone()
            for idx, row in self.df_csv.iterrows():
                # Pegar o MACROPROCESSO no CSV (primeiro número do formato 7.2.1.1)
                numero_csv = str(row.get('Numero', '')).strip()
                parts = numero_csv.split('.')
                if len(parts) > 0:
                    macro_numero_csv = parts[0]

                    # Se o macroprocesso do CSV pertence aos macroprocessos típicos da área, dar boost
                    if macro_numero_csv in macros_da_area:
                        # Boost de 50% para atividades dos macroprocessos da área selecionada
                        boosted_scores[idx] = boosted_scores[idx] * 1.50

            # Encontrar melhor match (com boost aplicado)
            best_idx = int(torch.argmax(boosted_scores))
            best_score = float(cos_scores[best_idx])  # Score original (sem boost) para exibição

            # Recuperar linha do CSV
            row_match = self.df_csv.iloc[best_idx]

            # Log do resultado
            numero_csv_match = str(row_match['Numero']).strip()
            macro_match = numero_csv_match.split('.')[0] if '.' in numero_csv_match else numero_csv_match
            foi_boosted = (macro_match in macros_da_area)

            logger.info(f"[PIPELINE] Melhor match semântico: score={best_score:.3f} {'(BOOSTED - macroprocesso ' + macro_match + ' pertence à área ' + area_codigo + ')' if foi_boosted else ''}")
            logger.info(f"[PIPELINE]   Atividade: {row_match['Atividade']}")
            logger.info(f"[PIPELINE]   Área usuário: {area_codigo} | Macroprocesso da atividade: {macro_match} | Macroprocessos da área: {macros_da_area}")

            # Gerar CAP completo: prefixo_area_usuario + numero_csv
            # SEMPRE usa o prefixo da área selecionada pelo usuário
            # Ex: Usuário escolheu CGRIS (6) → CAP sempre 6.X.X.X.X
            prefixo_area = self._obter_prefixo_area(area_codigo)
            cap_completo = f"{prefixo_area}.{str(row_match['Numero']).strip()}"

            return {
                'sucesso': True,
                'origem': 'semantic',
                'score': best_score,
                'cap': cap_completo,
                'tipo_cap': 'oficial',
                'acao_permitida': 'concordar_ou_selecionar_manual',
                'pode_editar': False,
                'atividade': {
                    'macroprocesso': row_match['Macroprocesso'],
                    'processo': row_match['Processo'],
                    'subprocesso': row_match['Subprocesso'],
                    'atividade': row_match['Atividade']
                }
            }

        except Exception as e:
            logger.error(f"[PIPELINE] Erro na Camada 2: {e}")
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
                # CAP = prefixo_area + numero_csv
                cap_completo = f"{prefixo_area}.{str(row['Numero']).strip()}"
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

                # Gerar CAP: prefixo_area + numero_csv
                if prefixo_area:
                    cap = f"{prefixo_area}.{numero_csv}"
                else:
                    cap = numero_csv  # Sem área, usa só o número do CSV

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
            from processos.domain.helena_produtos.helena_ajuda_inteligente import analisar_atividade_com_helena

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

            # Gerar CAP sequencial dentro do subprocesso
            cap_novo = self._gerar_cap_sequencial(macro, processo, subprocesso)

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
            logger.error(f"[PIPELINE] Erro ao processar resposta Camada 4: {e}")
            import traceback
            traceback.print_exc()
            return {'sucesso': False, 'erro': str(e)}

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
            return f"{prefixo_area}.{numero}"

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

            # Gerar número sequencial provisório
            import random
            seq = random.randint(1000, 9999)

            return f"{prefixo_area}.{idx_macro}.XX.XX.{seq}"

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao gerar CAP provisório: {e}")
            return f"{area_codigo}.99.XX.XX.9999"

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

    def _gerar_cap_sequencial(self, macroprocesso: str, processo: str, subprocesso: str) -> str:
        """
        Gera CAP sequencial dentro de um subprocesso existente

        LÓGICA:
        1. Busca todos os CAPs do mesmo subprocesso
        2. Localiza o último CAP (ex: 1.2.3.4.109)
        3. Incrementa o índice final: 1.2.3.4.110

        IMPORTANTE: Mantém os 4 primeiros níveis (macro.processo.sub.xxx)
        e incrementa apenas o último índice.
        """
        try:
            # Filtrar atividades do mesmo subprocesso
            filtro = (
                (self.df_csv['Macroprocesso'] == macroprocesso) &
                (self.df_csv['Processo'] == processo) &
                (self.df_csv['Subprocesso'] == subprocesso)
            )

            atividades_subprocesso = self.df_csv[filtro]

            if atividades_subprocesso.empty:
                raise ValueError(f"Nenhuma atividade encontrada no subprocesso: {subprocesso}")

            # Extrair todos os CAPs do subprocesso
            caps_existentes = atividades_subprocesso['Numero'].tolist()

            logger.info(f"[PIPELINE] CAPs existentes no subprocesso '{subprocesso}': {len(caps_existentes)}")

            # Encontrar o último CAP (assume formato X.X.X.X.NNN)
            ultimo_cap = caps_existentes[0]  # Pegue o primeiro como base

            # Extrair partes do CAP (ex: "1.2.3.4.109" → ["1", "2", "3", "4", "109"])
            partes = str(ultimo_cap).split('.')

            if len(partes) < 5:
                raise ValueError(f"Formato de CAP inválido no CSV: {ultimo_cap}")

            # Manter os 4 primeiros níveis, incrementar o último
            prefixo = '.'.join(partes[:4])  # "1.2.3.4"

            # Buscar o maior índice final no subprocesso
            indices_finais = []
            for cap in caps_existentes:
                partes_cap = str(cap).split('.')
                if len(partes_cap) >= 5:
                    try:
                        indice_final = int(partes_cap[4])
                        indices_finais.append(indice_final)
                    except ValueError:
                        continue

            if not indices_finais:
                # Se não conseguir parsear nenhum, começar do 1
                novo_indice = 1
            else:
                novo_indice = max(indices_finais) + 1

            cap_novo = f"{prefixo}.{novo_indice}"

            logger.info(f"[PIPELINE] CAP sequencial gerado: {cap_novo}")
            logger.info(f"[PIPELINE] Último índice no subprocesso era: {max(indices_finais) if indices_finais else 'N/A'}")

            return cap_novo

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao gerar CAP sequencial: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: gerar CAP genérico
            return "1.99.99.99.999"

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
