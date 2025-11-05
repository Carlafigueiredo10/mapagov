"""
Helena POP v2.0 - Mapeamento de Processos Operacionais Padrão

Arquitetura Clean:
- Herda de BaseHelena (stateless)
- Estado gerenciado via session_data
- Sem dependências externas de domain_old/infra_old
- Máquina de estados para coleta de dados do processo
"""
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import logging
import pandas as pd
from datetime import datetime, timezone
from django.db import transaction
import hashlib

from processos.domain.base import BaseHelena
from processos.infra.parsers import parse_sistemas, parse_operadores, normalizar_texto
from processos.infra.pdf_generator import gerar_pop_pdf
from processos.models_new import ControleIndices, AtividadeSugerida, HistoricoAtividade

# Tentativa de importar BaseLegalSuggestorDECIPEx (opcional)
try:
    from processos.base_legal_decipex import BaseLegalSuggestorDECIPEx
    BASE_LEGAL_DISPONIVEL = True
except ImportError:
    BASE_LEGAL_DISPONIVEL = False

logger = logging.getLogger(__name__)

# LOG DE DIAGNOSTICO - Confirma que este arquivo esta sendo carregado
print("=" * 80)
print(">>> helena_pop.py FOI CARREGADO! (VERSAO CORRETA)")
print("=" * 80)


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPOP(str, Enum):
    """Estados da máquina de estados para coleta do POP"""
    # BOAS_VINDAS removido - começa direto em NOME_USUARIO (evita duplicação)
    NOME_USUARIO = "nome_usuario"
    CONFIRMA_NOME = "confirma_nome"
    ESCOLHA_TIPO_EXPLICACAO = "escolha_tipo_explicacao"  # 🆕 Escolher explicação curta ou longa
    EXPLICACAO_LONGA = "explicacao_longa"  # 🆕 Explicação detalhada do processo
    DUVIDAS_EXPLICACAO = "duvidas_explicacao"  # 🆕 Lidar com dúvidas sobre a explicação
    EXPLICACAO = "explicacao"
    PEDIDO_COMPROMISSO = "pedido_compromisso"  # 🆕 Pedido de compromisso antes de começar
    AREA_DECIPEX = "area_decipex"
    SUBAREA_DECIPEX = "subarea_decipex"  # 🆕 Seleção de subárea (ex: DIGEP-RO, DIGEP-RR, DIGEP-AP)
    ARQUITETURA = "arquitetura"
    CONFIRMACAO_ARQUITETURA = "confirmacao_arquitetura"  # 🎯 NOVO: confirmar arquitetura sugerida pela IA
    SELECAO_HIERARQUICA = "selecao_hierarquica"  # 🆕 FALLBACK: seleção manual via dropdowns hierárquicos
    NOME_PROCESSO = "nome_processo"
    ENTREGA_ESPERADA = "entrega_esperada"
    CONFIRMACAO_ENTREGA = "confirmacao_entrega"  # 🎯 NOVO: confirmar/editar entrega
    RECONHECIMENTO_ENTREGA = "reconhecimento_entrega"  # 🎯 Gamificação após entrega
    DISPOSITIVOS_NORMATIVOS = "dispositivos_normativos"
    TRANSICAO_ROADTRIP = "transicao_roadtrip"  # 🚗 Animação de transição entre normas e operadores
    OPERADORES = "operadores"
    SISTEMAS = "sistemas"
    FLUXOS = "fluxos"
    PONTOS_ATENCAO = "pontos_atencao"  # 🎯 Novo campo do OLD
    REVISAO_PRE_DELEGACAO = "revisao_pre_delegacao"  # 🎯 REVISÃO 2: após coletar tudo
    TRANSICAO_EPICA = "transicao_epica"  # 🎯 Transição motivacional antes das etapas
    SELECAO_EDICAO = "selecao_edicao"  # 🎯 Menu de edição granular
    DELEGACAO_ETAPAS = "delegacao_etapas"
    FINALIZADO = "finalizado"


# ============================================================================
# ARQUITETURA DECIPEX
# ============================================================================

class ArquiteturaDecipex:
    """Carrega e consulta arquitetura de processos da DECIPEX"""

    def __init__(self, caminho_csv='documentos_base/Arquitetura_DECIPEX_mapeada.csv'):
        try:
            self.df = pd.read_csv(caminho_csv)
        except FileNotFoundError:
            logger.warning(f"Arquivo CSV não encontrado: {caminho_csv}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])

    def obter_macroprocessos_unicos(self) -> List[str]:
        return self.df['Macroprocesso'].unique().tolist()

    def obter_processos_por_macro(self, macro: str) -> List[str]:
        return self.df[self.df['Macroprocesso'] == macro]['Processo'].unique().tolist()

    def obter_subprocessos_por_processo(self, macro: str, processo: str) -> List[str]:
        filtro = (self.df['Macroprocesso'] == macro) & (self.df['Processo'] == processo)
        return self.df[filtro]['Subprocesso'].unique().tolist()

    def obter_atividades_por_subprocesso(self, macro: str, processo: str, subprocesso: str) -> List[str]:
        filtro = (
            (self.df['Macroprocesso'] == macro) &
            (self.df['Processo'] == processo) &
            (self.df['Subprocesso'] == subprocesso)
        )
        return self.df[filtro]['Atividade'].unique().tolist()


# ============================================================================
# FUNÇÕES DE GOVERNANÇA - Geração de CAP e Detecção de Duplicatas
# ============================================================================

def gerar_cap_provisorio_seguro(
    area_codigo: str,
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    hierarquia_df: pd.DataFrame
) -> str:
    """
    Gera CAP provisório com lock transacional para evitar race conditions.

    Formato: PREFIXO_AREA.IDX_MACRO.IDX_PROCESSO.IDX_SUB.IDX_ATIVIDADE

    Exemplo: 1.02.03.04.108
    - 1 = CGBEN
    - 02 = índice do macroprocesso
    - 03 = índice do processo
    - 04 = índice do subprocesso
    - 108 = próximo índice de atividade (107 + 1)

    Args:
        area_codigo: Código da área (ex: 'CGBEN')
        macroprocesso: Nome do macroprocesso
        processo: Nome do processo
        subprocesso: Nome do subprocesso
        atividade: Nome da atividade
        hierarquia_df: DataFrame com a arquitetura completa para indexação

    Returns:
        CAP provisório único (ex: '1.02.03.04.108')
    """
    # Mapeamento de códigos de área para prefixos
    PREFIXOS_AREA = {
        "CGBEN": "1", "CGPAG": "2", "COATE": "3", "CGGAF": "4",
        "DIGEP": "5", "DIGEP-RO": "5.1", "DIGEP-RR": "5.2", "DIGEP-AP": "5.3",
        "CGRIS": "6", "CGCAF": "7", "CGECO": "8"
    }

    prefixo_area = PREFIXOS_AREA.get(area_codigo, "0")

    # Buscar numeração diretamente do CSV (coluna 'Numero')
    try:
        filtro = (
            (hierarquia_df['Macroprocesso'] == macroprocesso) &
            (hierarquia_df['Processo'] == processo) &
            (hierarquia_df['Subprocesso'] == subprocesso) &
            (hierarquia_df['Atividade'] == atividade)
        )
        linha_encontrada = hierarquia_df[filtro]

        if not linha_encontrada.empty and 'Numero' in linha_encontrada.columns:
            # Ler número hierárquico do CSV (ex: "1.1.1.1")
            numero_csv = str(linha_encontrada.iloc[0]['Numero'])
            partes = numero_csv.split('.')

            if len(partes) >= 4:
                idx_macro = int(partes[0])
                idx_processo = int(partes[1])
                idx_subprocesso = int(partes[2])
                idx_atividade = int(partes[3])
            else:
                # Fallback: gerar dinamicamente
                raise ValueError("Formato de numeração inválido no CSV")
        else:
            # Fallback: gerar dinamicamente (nova atividade)
            raise ValueError("Atividade não encontrada no CSV")

    except (ValueError, IndexError, KeyError):
        # Fallback: gerar índices dinamicamente (para novas atividades)
        logger.warning(f"[GOVERNANÇA] Numeração não encontrada no CSV, gerando dinamicamente")

        # 1. Índice do macroprocesso
        macros_unicos = hierarquia_df['Macroprocesso'].unique().tolist()
        idx_macro = macros_unicos.index(macroprocesso) + 1 if macroprocesso in macros_unicos else len(macros_unicos) + 1

        # 2. Índice do processo dentro do macroprocesso
        processos_no_macro = hierarquia_df[hierarquia_df['Macroprocesso'] == macroprocesso]['Processo'].unique().tolist()
        idx_processo = processos_no_macro.index(processo) + 1 if processo in processos_no_macro else len(processos_no_macro) + 1

        # 3. Índice do subprocesso dentro do processo
        subs_no_processo = hierarquia_df[
            (hierarquia_df['Macroprocesso'] == macroprocesso) &
            (hierarquia_df['Processo'] == processo)
        ]['Subprocesso'].unique().tolist()
        idx_subprocesso = subs_no_processo.index(subprocesso) + 1 if subprocesso in subs_no_processo else len(subs_no_processo) + 1

        # 4. Índice da atividade - obter próximo com lock transacional
        with transaction.atomic():
            controle, created = ControleIndices.objects.select_for_update().get_or_create(
                area_codigo=area_codigo,
                defaults={'ultimo_indice': 107}
            )

            proximo_indice = controle.ultimo_indice + 1
            controle.ultimo_indice = proximo_indice
            controle.save()

            idx_atividade = proximo_indice

    # Montar CAP com zero-padding
    cap_provisorio = f"{prefixo_area}.{idx_macro:02d}.{idx_processo:02d}.{idx_subprocesso:02d}.{idx_atividade:03d}"

    logger.info(f"[GOVERNANÇA] CAP provisório gerado: {cap_provisorio} para área {area_codigo}")

    return cap_provisorio


def detectar_atividades_similares(
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    threshold: float = 0.80
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Detecta atividades similares já sugeridas usando TF-IDF + Cosine Similarity.

    IMPORTANTE: Sempre retorna scores, mesmo se < threshold (para análise futura).

    Args:
        macroprocesso: Macroprocesso da atividade
        processo: Processo da atividade
        subprocesso: Subprocesso da atividade
        atividade: Descrição da atividade
        threshold: Limite de similaridade (padrão 0.80)

    Returns:
        Tupla (max_score, lista_similares)
        - max_score: Maior score encontrado (0.0 a 1.0)
        - lista_similares: Lista de dicts com CAP, descrição e score
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Buscar todas as atividades sugeridas da mesma área hierárquica
    atividades_existentes = AtividadeSugerida.objects.filter(
        macroprocesso=macroprocesso,
        processo=processo,
        subprocesso=subprocesso
    ).exclude(status='rejeitada')

    if not atividades_existentes.exists():
        logger.info(f"[GOVERNANÇA] Nenhuma atividade similar encontrada (nenhuma sugestão prévia nesta hierarquia)")
        return 0.0, []

    # Preparar textos para comparação
    texto_novo = atividade.lower().strip()
    textos_existentes = [a.atividade.lower().strip() for a in atividades_existentes]
    todos_textos = textos_existentes + [texto_novo]

    # TF-IDF + Cosine Similarity
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=1, max_df=0.95)
    tfidf_matrix = vectorizer.fit_transform(todos_textos)

    # Calcular similaridade do novo texto com todos os existentes
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    # Preparar resultados
    max_score = float(similarities.max()) if len(similarities) > 0 else 0.0

    lista_similares = []
    for idx, score in enumerate(similarities):
        if score >= threshold:
            ativ = atividades_existentes[idx]
            lista_similares.append({
                'cap': ativ.cap_provisorio,
                'atividade': ativ.atividade,
                'status': ativ.status,
                'score': float(score),
                'autor': ativ.autor_nome,
                'data': ativ.data_sugestao_utc.isoformat()
            })

    # Ordenar por score decrescente
    lista_similares.sort(key=lambda x: x['score'], reverse=True)

    logger.info(
        f"[GOVERNANÇA] Detecção de duplicatas: max_score={max_score:.3f}, "
        f"similares acima de {threshold}={len(lista_similares)}"
    )

    return max_score, lista_similares


def salvar_atividade_sugerida(
    cap_provisorio: str,
    area_codigo: str,
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    entrega_esperada: str,
    autor_cpf: str,
    autor_nome: str,
    autor_area: str,
    descricao_original: str,
    score_similaridade: float,
    sugestoes_similares: List[Dict[str, Any]],
    scores_similares_todos: List[float],
    origem_fluxo: str,
    interacao_id: str
) -> AtividadeSugerida:
    """
    Salva uma nova atividade sugerida no banco de dados com rastreabilidade completa.

    Args:
        cap_provisorio: CAP provisório gerado
        area_codigo: Código da área (ex: 'CGBEN')
        macroprocesso: Nome do macroprocesso
        processo: Nome do processo
        subprocesso: Nome do subprocesso
        atividade: Descrição da atividade
        entrega_esperada: Entrega esperada da atividade
        autor_cpf: CPF do autor da sugestão
        autor_nome: Nome completo do autor
        autor_area: Área do autor
        descricao_original: Descrição original fornecida pelo usuário
        score_similaridade: Score máximo de similaridade encontrado
        sugestoes_similares: Lista de atividades similares (score >= threshold)
        scores_similares_todos: Lista completa de scores (para análise futura)
        origem_fluxo: 'match_exato', 'match_fuzzy', 'nova_atividade_ia', 'selecao_manual'
        interacao_id: ID da interação (chat_message_id)

    Returns:
        Instância de AtividadeSugerida criada
    """
    # Timestamp UTC atual
    agora_utc = datetime.now(timezone.utc)

    # Gerar hash único (anti-duplicata)
    hash_sugestao = AtividadeSugerida.gerar_hash_sugestao(
        macroprocesso, processo, subprocesso, atividade, autor_cpf, agora_utc
    )

    # Determinar confiança da IA
    if score_similaridade >= 0.90:
        confianca = 'alta'
    elif score_similaridade >= 0.75:
        confianca = 'media'
    else:
        confianca = 'baixa'

    # Criar registro
    atividade_obj = AtividadeSugerida.objects.create(
        cap_provisorio=cap_provisorio,
        cap_oficial=None,
        status='sugerida',
        area_codigo=area_codigo,
        macroprocesso=macroprocesso,
        processo=processo,
        subprocesso=subprocesso,
        atividade=atividade,
        entrega_esperada=entrega_esperada,
        autor_cpf=autor_cpf,
        autor_nome=autor_nome,
        autor_area=autor_area,
        data_sugestao_utc=agora_utc,
        descricao_original=descricao_original,
        hash_sugestao=hash_sugestao,
        score_similaridade=score_similaridade,
        sugestoes_similares=sugestoes_similares,
        scores_similares_todos=scores_similares_todos,
        confianca=confianca,
        origem_fluxo=origem_fluxo,
        interacao_id=interacao_id
    )

    # Registrar no histórico
    HistoricoAtividade.objects.create(
        atividade=atividade_obj,
        tipo_evento='criacao',
        usuario_cpf=autor_cpf,
        usuario_nome=autor_nome,
        comentario=f"Atividade sugerida via {origem_fluxo}"
    )

    logger.info(
        f"[GOVERNANÇA] Atividade sugerida salva: {cap_provisorio} | "
        f"Autor: {autor_nome} ({autor_cpf}) | Confiança: {confianca}"
    )

    return atividade_obj


def criar_versao_csv(
    csv_path: str = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv',
    versao_path: str = 'documentos_base/versoes/',
    changelog_path: str = 'documentos_base/CHANGELOG_ARQUITETURA.json'
) -> Tuple[str, str]:
    """
    Cria versão imutável do CSV com timestamp e hash SHA256.

    Formato: Arquitetura_DECIPEX_vYYYYMMDD_HHMMSS_NNN.csv

    Args:
        csv_path: Caminho do CSV atual
        versao_path: Diretório para armazenar versões
        changelog_path: Caminho do arquivo changelog JSON

    Returns:
        Tupla (caminho_versao, hash_sha256)
    """
    import os
    import shutil
    import json
    from pathlib import Path

    # Criar diretório de versões se não existir
    Path(versao_path).mkdir(parents=True, exist_ok=True)

    # Timestamp UTC
    agora_utc = datetime.now(timezone.utc)
    timestamp_str = agora_utc.strftime('%Y%m%d_%H%M%S')

    # Contar versões existentes para gerar número sequencial
    versoes_existentes = list(Path(versao_path).glob('Arquitetura_DECIPEX_v*.csv'))
    numero_versao = len(versoes_existentes) + 1

    # Nome da versão
    nome_versao = f"Arquitetura_DECIPEX_v{timestamp_str}_{numero_versao:03d}.csv"
    caminho_versao = os.path.join(versao_path, nome_versao)

    # Copiar CSV atual para versão
    shutil.copy2(csv_path, caminho_versao)

    # Calcular hash SHA256 do arquivo
    with open(caminho_versao, 'rb') as f:
        conteudo = f.read()
        hash_sha256 = hashlib.sha256(conteudo).hexdigest()

    # Atualizar changelog
    atualizar_changelog(
        changelog_path=changelog_path,
        versao_nome=nome_versao,
        hash_sha256=hash_sha256,
        timestamp_utc=agora_utc,
        motivo="Versão automática gerada pelo sistema"
    )

    logger.info(f"[GOVERNANÇA] Versão CSV criada: {nome_versao} | Hash: {hash_sha256[:8]}...")

    return caminho_versao, hash_sha256


def atualizar_changelog(
    changelog_path: str,
    versao_nome: str,
    hash_sha256: str,
    timestamp_utc: datetime,
    motivo: str = "",
    atividades_adicionadas: List[Dict[str, Any]] = None
) -> None:
    """
    Atualiza changelog com metadados da nova versão do CSV.

    Args:
        changelog_path: Caminho do arquivo changelog JSON
        versao_nome: Nome do arquivo de versão
        hash_sha256: Hash SHA256 do arquivo
        timestamp_utc: Timestamp da criação
        motivo: Motivo da criação da versão
        atividades_adicionadas: Lista de atividades adicionadas nesta versão
    """
    import json
    from pathlib import Path

    # Carregar changelog existente ou criar novo
    if Path(changelog_path).exists():
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = json.load(f)
    else:
        changelog = {
            "versoes": [],
            "metadados": {
                "criado_em": datetime.now(timezone.utc).isoformat(),
                "ultima_atualizacao": None
            }
        }

    # Adicionar nova entrada
    entrada = {
        "versao": versao_nome,
        "hash_sha256": hash_sha256,
        "timestamp_utc": timestamp_utc.isoformat(),
        "motivo": motivo,
        "atividades_adicionadas": atividades_adicionadas or [],
        "total_atividades": len(atividades_adicionadas) if atividades_adicionadas else 0
    }

    changelog["versoes"].append(entrada)
    changelog["metadados"]["ultima_atualizacao"] = datetime.now(timezone.utc).isoformat()

    # Salvar changelog atualizado
    with open(changelog_path, 'w', encoding='utf-8') as f:
        json.dump(changelog, f, indent=2, ensure_ascii=False)

    logger.info(f"[GOVERNANÇA] Changelog atualizado: {versao_nome}")


def injetar_atividade_no_csv(
    atividade: AtividadeSugerida,
    csv_path: str = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv'
) -> bool:
    """
    Injeta atividade validada no CSV oficial e cria versão com changelog.

    Fluxo:
    1. Criar versão do CSV atual (backup)
    2. Adicionar nova linha ao CSV
    3. Atualizar status da atividade para 'publicada'
    4. Registrar CAP oficial

    Args:
        atividade: Instância de AtividadeSugerida (status='validada')
        csv_path: Caminho do CSV oficial

    Returns:
        bool: True se injetado com sucesso, False caso contrário
    """
    import pandas as pd

    if atividade.status != 'validada':
        logger.error(f"[GOVERNANÇA] Atividade {atividade.cap_provisorio} não está validada (status={atividade.status})")
        return False

    try:
        # 1. Criar versão do CSV atual (backup)
        criar_versao_csv(csv_path=csv_path)

        # 2. Ler CSV atual
        df = pd.read_csv(csv_path)

        # 3. Criar nova linha
        nova_linha = pd.DataFrame([{
            'Aba': atividade.area_codigo,
            'Macroprocesso': atividade.macroprocesso,
            'Processo': atividade.processo,
            'Subprocesso': atividade.subprocesso,
            'Atividade': atividade.atividade,
            'Entrega Esperada': atividade.entrega_esperada,
            # Adicionar outras colunas se existirem no CSV
        }])

        # 4. Concatenar e salvar
        df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
        df_atualizado.to_csv(csv_path, index=False, encoding='utf-8')

        # 5. Atualizar status da atividade para 'publicada'
        atividade.status = 'publicada'
        atividade.cap_oficial = atividade.cap_provisorio  # CAP provisório vira oficial
        atividade.save()

        # 6. Registrar no histórico
        HistoricoAtividade.objects.create(
            atividade=atividade,
            tipo_evento='mesclagem',
            usuario_cpf='SISTEMA',
            usuario_nome='Sistema Automático',
            comentario=f"Atividade injetada no CSV oficial e publicada com CAP: {atividade.cap_oficial}"
        )

        # 7. Atualizar changelog com detalhes da atividade adicionada
        atualizar_changelog(
            changelog_path='documentos_base/CHANGELOG_ARQUITETURA.json',
            versao_nome=f"Arquitetura_DECIPEX_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
            hash_sha256="recalcular",  # TODO: Recalcular hash após injeção
            timestamp_utc=datetime.now(timezone.utc),
            motivo=f"Injeção de atividade validada: {atividade.cap_provisorio}",
            atividades_adicionadas=[{
                'cap': atividade.cap_oficial,
                'macroprocesso': atividade.macroprocesso,
                'processo': atividade.processo,
                'subprocesso': atividade.subprocesso,
                'atividade': atividade.atividade,
                'autor': atividade.autor_nome,
                'validador': atividade.validador_nome,
                'data_sugestao': atividade.data_sugestao_utc.isoformat(),
                'data_validacao': atividade.data_validacao_utc.isoformat() if atividade.data_validacao_utc else None
            }]
        )

        logger.info(f"[GOVERNANÇA] Atividade {atividade.cap_oficial} injetada no CSV com sucesso!")

        return True

    except Exception as e:
        logger.error(f"[GOVERNANÇA] Erro ao injetar atividade no CSV: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# STATE MACHINE - POPStateMachine
# ============================================================================

class POPStateMachine:
    """Máquina de estados para coletar dados do POP"""

    def __init__(self):
        self.estado = EstadoPOP.NOME_USUARIO  # ✅ FIX: começa direto em NOME_USUARIO
        self.nome_usuario = ""
        self.nome_temporario = ""
        self.area_selecionada = None
        self.subarea_selecionada = None  # 🆕 Para áreas com subáreas (ex: DIGEP)
        self.macro_selecionado = None
        self.processo_selecionado = None
        self.subprocesso_selecionado = None
        self.atividade_selecionada = None
        self.codigo_cap = None  # 🎯 CÓDIGO ÚNICO DO PROCESSO (CPF)
        self.dados_coletados = {
            'nome_processo': '',
            'entrega_esperada': '',
            'dispositivos_normativos': [],
            'operadores': [],
            'sistemas': [],
            'documentos': [],
            'fluxos_entrada': [],
            'fluxos_saida': []
        }
        self.concluido = False
        # Controle de delegação para Helena Mapeamento
        self.em_modo_duvidas = False
        self.contexto_duvidas = None
        self.estado_helena_mapeamento = None  # Estado interno do Helena Mapeamento

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'estado': self.estado.value,
            'nome_usuario': self.nome_usuario,
            'nome_temporario': self.nome_temporario,
            'area_selecionada': self.area_selecionada,
            'subarea_selecionada': self.subarea_selecionada,  # 🆕 Subáreas
            'macro_selecionado': self.macro_selecionado,
            'processo_selecionado': self.processo_selecionado,
            'subprocesso_selecionado': self.subprocesso_selecionado,
            'atividade_selecionada': self.atividade_selecionada,
            'codigo_cap': self.codigo_cap,  # 🎯 CAP ÚNICO
            'dados_coletados': self.dados_coletados,
            'concluido': self.concluido,
            'em_modo_duvidas': self.em_modo_duvidas,
            'contexto_duvidas': self.contexto_duvidas,
            'estado_helena_mapeamento': self.estado_helena_mapeamento
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'POPStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls()
        sm.estado = EstadoPOP(data.get('estado', EstadoPOP.NOME_USUARIO.value))  # ✅ FIX: default para NOME_USUARIO
        sm.nome_usuario = data.get('nome_usuario', '')
        sm.nome_temporario = data.get('nome_temporario', '')
        sm.area_selecionada = data.get('area_selecionada')
        sm.subarea_selecionada = data.get('subarea_selecionada')  # 🆕 Subáreas
        sm.macro_selecionado = data.get('macro_selecionado')
        sm.processo_selecionado = data.get('processo_selecionado')
        sm.subprocesso_selecionado = data.get('subprocesso_selecionado')
        sm.atividade_selecionada = data.get('atividade_selecionada')
        sm.codigo_cap = data.get('codigo_cap')  # 🎯 CAP ÚNICO
        sm.dados_coletados = data.get('dados_coletados', {
            'nome_processo': '',
            'entrega_esperada': '',
            'dispositivos_normativos': [],
            'operadores': [],
            'sistemas': [],
            'documentos': [],
            'fluxos_entrada': [],
            'fluxos_saida': []
        })
        sm.concluido = data.get('concluido', False)
        sm.em_modo_duvidas = data.get('em_modo_duvidas', False)
        sm.contexto_duvidas = data.get('contexto_duvidas')
        sm.estado_helena_mapeamento = data.get('estado_helena_mapeamento')
        return sm


# ============================================================================
# HELENA POP v2.0
# ============================================================================

class HelenaPOP(BaseHelena):
    """
    Helena POP v2.0 - Coleta de dados para mapeamento de processos

    Responsabilidades:
    - Guiar usuário através da coleta de dados do processo
    - Integrar com arquitetura DECIPEX
    - Sugerir base legal quando disponível
    - Preparar dados para delegação ao Helena Etapas
    """

    VERSION = "2.0.0"
    PRODUTO_NOME = "Helena POP"

    def __init__(self):
        super().__init__()

        # Carregar arquitetura DECIPEX
        self.arquitetura = ArquiteturaDecipex()

        # Integração base legal (opcional)
        if BASE_LEGAL_DISPONIVEL:
            try:
                self.suggestor_base_legal = BaseLegalSuggestorDECIPEx()
            except Exception as e:
                logger.warning(f"Não foi possível carregar BaseLegalSuggestorDECIPEx: {e}")
                self.suggestor_base_legal = None
        else:
            self.suggestor_base_legal = None

        # Memória anti-repetição de sugestões
        self._atividades_sugeridas = []
        self._codigos_sugeridos = set()
        self._normas_sugeridas = set()

    @property
    def AREAS_DECIPEX(self) -> Dict[int, Dict[str, str]]:
        """
        Áreas organizacionais carregadas do CSV.

        Carrega de: documentos_base/areas_organizacionais.csv
        Fallback: Dados hardcoded (segurança)
        """
        return self._carregar_areas_organizacionais()

    def _carregar_areas_organizacionais(self) -> Dict[int, Dict[str, str]]:
        """
        Carrega áreas do CSV com fallback hardcoded.

        Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
        Basta trocar o CSV ou usar variável de ambiente.
        """
        import os

        # Caminho do CSV (pode ser configurado via env var)
        # __file__ = processos/domain/helena_produtos/helena_pop.py
        # dirname 1x = processos/domain/helena_produtos/
        # dirname 2x = processos/domain/
        # dirname 3x = processos/
        # dirname 4x = raiz do projeto
        csv_path = os.environ.get(
            'AREAS_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'areas_organizacionais.csv'
            )
        )

        try:
            # 🔧 FIX: Forçar encoding UTF-8 para evitar problemas com caracteres especiais
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Filtrar apenas áreas ativas E que não sejam subáreas (area_pai vazio/NaN)
            # Subáreas serão carregadas dentro das áreas principais
            if 'area_pai' in df.columns:
                df_ativas = df[(df['ativo'] == True) & (df['area_pai'].isna())].sort_values('ordem')
            else:
                df_ativas = df[df['ativo'] == True].sort_values('ordem')

            # Converter para dicionário no formato esperado
            areas_dict = {}
            for idx, row in df_ativas.iterrows():
                # FIX: Tratar prefixo corretamente (remover .0 de inteiros, manter decimais)
                prefixo_float = float(row['prefixo'])
                if prefixo_float == int(prefixo_float):
                    # É inteiro: 6.0 -> "6"
                    prefixo_tratado = str(int(prefixo_float))
                else:
                    # Tem decimal: 5.1 -> "5.1"
                    prefixo_tratado = str(prefixo_float)

                area_info = {
                    "codigo": row['codigo'],
                    "sigla": row['codigo'],  # Frontend espera 'sigla'
                    "nome": row['nome_completo'],
                    "prefixo": prefixo_tratado
                }

                # Adicionar informações de subáreas se existirem
                if 'tem_subareas' in row and row['tem_subareas'] in [True, 'true', 'True']:
                    area_info['tem_subareas'] = True
                    # Buscar subáreas dessa área no DataFrame completo (não filtrado)
                    if 'area_pai' in df.columns:
                        subareas = df[(df['ativo'] == True) & (df['area_pai'] == row['codigo'])]
                    else:
                        subareas = pd.DataFrame()  # Vazio se não houver coluna area_pai
                    if not subareas.empty:
                        subareas_list = []
                        for _, sub in subareas.iterrows():
                            # FIX: Tratar prefixo das subáreas corretamente
                            sub_prefixo_float = float(sub['prefixo'])
                            if sub_prefixo_float == int(sub_prefixo_float):
                                sub_prefixo = str(int(sub_prefixo_float))
                            else:
                                sub_prefixo = str(sub_prefixo_float)

                            subareas_list.append({
                                'codigo': sub['codigo'],
                                'nome': sub['nome_curto'],
                                'nome_completo': sub['nome_completo'],
                                'prefixo': sub_prefixo
                            })
                        area_info['subareas'] = subareas_list
                else:
                    area_info['tem_subareas'] = False

                areas_dict[int(row['ordem'])] = area_info

            logger.info(f"[AREAS] Carregadas do CSV: {len(areas_dict)} areas ativas")
            # 🔍 DEBUG: Mostrar primeiras 3 áreas carregadas
            print(f"\n📊 [AREAS CSV] Carregadas {len(areas_dict)} áreas ativas:")
            for key in sorted(list(areas_dict.keys())[:3]):
                area = areas_dict[key]
                print(f"   {key}: {area['codigo']} - {area['nome'][:50]}")
            print()
            return areas_dict

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de áreas ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return {
                1: {"codigo": "CGBEN", "nome": "Coordenação Geral de Benefícios", "prefixo": "1"},
                2: {"codigo": "CGPAG", "nome": "Coordenação Geral de Pagamentos", "prefixo": "2"},
                3: {"codigo": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3"},
                4: {"codigo": "CGGAF", "nome": "Coordenação Geral de Gestão de Acervos Funcionais", "prefixo": "4"},
                5: {"codigo": "DIGEP", "nome": "Divisão de Pessoal dos Ex-Territórios", "prefixo": "5"},
                6: {"codigo": "CGRIS", "nome": "Coordenação Geral de Riscos e Controle", "prefixo": "6"},
                7: {"codigo": "CGCAF", "nome": "Coordenação Geral de Gestão de Complementação da Folha", "prefixo": "7"},
                8: {"codigo": "CGECO", "nome": "Coordenação Geral de Extinção e Convênio", "prefixo": "8"}
            }

    @property
    def DESCRICOES_AREAS(self) -> Dict[str, str]:
        """
        Descrições personalizadas de cada área (carregadas do CSV).

        Retorna: {codigo: descricao}
        Exemplo: {"CGBEN": "que cuida das concessões..."}
        """
        import os

        csv_path = os.environ.get(
            'AREAS_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'areas_organizacionais.csv'
            )
        )

        try:
            df = pd.read_csv(csv_path)
            df_ativas = df[df['ativo'] == True]

            # Converter para dicionário {codigo: descricao}
            descricoes = {}
            for idx, row in df_ativas.iterrows():
                descricoes[row['codigo']] = row['descricao']

            return descricoes

        except Exception as e:
            # FALLBACK: Dados hardcoded
            return {
                "CGBEN": "que cuida das concessões, manutenções e revisões de aposentadorias e pensões, garantindo direitos e segurança jurídica aos beneficiários.",
                "CGPAG": "responsável pela execução e controle da folha de pagamentos dos aposentados e pensionistas, garantindo que tudo ocorra com precisão e transparência.",
                "COATE": "que acolhe, orienta e soluciona as demandas dos cidadãos e servidores, garantindo um atendimento humano e eficiente.",
                "CGGAF": "que organiza, digitaliza e mantém o acervo funcional dos servidores, preservando a memória e o acesso seguro às informações.",
                "DIGEP": "que assegura os direitos dos servidores vinculados aos ex-territórios, conduzindo análises e gestões complexas com zelo e compromisso histórico.",
                "CGRIS": "que fortalece a governança, os controles internos e a integridade institucional, promovendo uma gestão pública mais segura e eficiente.",
                "CGCAF": "responsável pela gestão das complementações de aposentadorias e pensões, garantindo equilíbrio e correção dos pagamentos.",
                "CGECO": "que gerencia processos de encerramento de órgãos e acordos administrativos, preservando a continuidade institucional e a responsabilidade pública."
            }

    @property
    def SISTEMAS_DECIPEX(self) -> Dict[str, List[str]]:
        """
        Sistemas carregados do CSV organizados por categoria.

        Carrega de: documentos_base/sistemas.csv
        Fallback: Dados hardcoded (segurança)
        """
        return self._carregar_sistemas()

    def _carregar_sistemas(self) -> Dict[str, List[str]]:
        """
        Carrega sistemas do CSV com fallback hardcoded.

        Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
        Basta trocar o CSV ou usar variável de ambiente.
        """
        import os

        # Caminho do CSV (pode ser configurado via env var)
        csv_path = os.environ.get(
            'SISTEMAS_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'sistemas.csv'
            )
        )

        try:
            df = pd.read_csv(csv_path)

            # Filtrar apenas sistemas ativos
            df_ativos = df[df['ativo'] == True].sort_values('ordem')

            # Agrupar por categoria
            sistemas_dict = {}
            for categoria in df_ativos['categoria'].unique():
                sistemas_da_categoria = df_ativos[df_ativos['categoria'] == categoria]['nome'].tolist()
                sistemas_dict[categoria] = sistemas_da_categoria

            logger.info(f"[SISTEMAS] Carregados do CSV: {len(df_ativos)} sistemas em {len(sistemas_dict)} categorias")
            return sistemas_dict

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de sistemas ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return {
                "gestao_pessoal": ["SIAPE", "E-SIAPE", "SIGEPE", "SIGEP - AFD", "E-Pessoal TCU", "SIAPNET", "SIGAC"],
                "documentos": ["SEI", "DOINET", "DOU", "SOUGOV", "PETRVS"],
                "transparencia": ["Portal da Transparência", "CNIS", "Site CGU-PAD", "Sistema de Pesquisa Integrada do TCU", "Consulta CPF RFB"],
                "previdencia": ["SISTEMA COMPREV", "BG COMPREV"],
                "comunicacao": ["TEAMS", "OUTLOOK"],
                "outros": ["DW"]
            }

    @property
    def OPERADORES_DECIPEX(self) -> List[str]:
        """
        Operadores carregados do CSV.

        Carrega de: documentos_base/operadores.csv
        Fallback: Dados hardcoded (segurança)
        """
        return self._carregar_operadores()

    def _carregar_operadores(self) -> List[str]:
        """
        Carrega operadores do CSV com fallback hardcoded.

        Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
        Basta trocar o CSV ou usar variável de ambiente.
        """
        import os

        # Caminho do CSV (pode ser configurado via env var)
        csv_path = os.environ.get(
            'OPERADORES_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'operadores.csv'
            )
        )

        try:
            df = pd.read_csv(csv_path)

            # Filtrar apenas operadores ativos
            df_ativos = df[df['ativo'] == True].sort_values('ordem')

            # Converter para lista no formato esperado
            operadores_list = df_ativos['nome'].tolist()

            logger.info(f"[OPERADORES] Carregados do CSV: {len(operadores_list)} operadores ativos")
            return operadores_list

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de operadores ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return [
                "Técnico Especializado",
                "Coordenador-Geral",
                "Coordenador",
                "Apoio-gabinete",
                "Equipe técnica",
                "Outros (especificar)"
            ]

    def _carregar_orgaos_centralizados(self) -> List[Dict[str, str]]:
        """
        Carrega órgãos centralizados do CSV com fallback hardcoded.

        Carrega de: documentos_base/orgaos_centralizados.csv
        Fallback: Dados hardcoded (segurança)

        Returns:
            List[Dict]: Lista de dicionários com sigla, nome_completo, observacao
        """
        import os

        # Caminho do CSV
        csv_path = os.environ.get(
            'ORGAOS_CENTRALIZADOS_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'orgaos_centralizados.csv'
            )
        )

        try:
            # 🔧 FIX: Forçar encoding UTF-8 para evitar problemas com caracteres especiais
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Filtrar apenas órgãos ativos (mesma lógica de areas_organizacionais)
            if 'ativo' in df.columns:
                df_ativos = df[df['ativo'] == True]
            else:
                df_ativos = df  # Fallback: se não houver coluna ativo, pega todos

            # Converter para lista de dicionários
            orgaos_list = []
            for _, row in df_ativos.iterrows():
                orgaos_list.append({
                    'sigla': row['sigla'],
                    'nome_completo': row['nome_completo'],
                    'observacao': row.get('observacao', '')
                })

            logger.info(f"[ORGAOS] Centralizados carregados do CSV: {len(orgaos_list)} órgãos ativos")
            # 🔍 DEBUG: Mostrar primeiros 3 órgãos carregados
            print(f"\n📊 [ORGAOS CSV] Carregados {len(orgaos_list)} órgãos ativos:")
            for i, orgao in enumerate(orgaos_list[:3]):
                print(f"   {i+1}: {orgao['sigla']} - {orgao['nome_completo'][:50]}")
            print()
            return orgaos_list

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de órgãos centralizados ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return [
                {'sigla': 'MGI', 'nome_completo': 'Ministério da Gestão e da Inovação em Serviços Públicos', 'observacao': ''},
                {'sigla': 'MF', 'nome_completo': 'Ministério da Fazenda', 'observacao': ''},
                {'sigla': 'MPO', 'nome_completo': 'Ministério do Planejamento e Orçamento', 'observacao': ''},
                {'sigla': 'INSS', 'nome_completo': 'Instituto Nacional do Seguro Social', 'observacao': 'Médicos peritos'},
                {'sigla': 'RFB', 'nome_completo': 'Receita Federal do Brasil', 'observacao': ''},
            ]

    def _carregar_canais_atendimento(self) -> List[Dict[str, str]]:
        """
        Carrega canais de atendimento do CSV com fallback hardcoded.

        Carrega de: documentos_base/canais_atendimento.csv
        Fallback: Dados hardcoded (segurança)

        Returns:
            List[Dict]: Lista de dicionários com codigo, nome, descricao
        """
        import os

        # Caminho do CSV
        csv_path = os.environ.get(
            'CANAIS_ATENDIMENTO_CSV_PATH',
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'canais_atendimento.csv'
            )
        )

        try:
            # 🔧 FIX: Forçar encoding UTF-8 para evitar problemas com caracteres especiais
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Filtrar apenas canais ativos (mesma lógica de areas_organizacionais)
            if 'ativo' in df.columns:
                df_ativos = df[df['ativo'] == True]
            else:
                df_ativos = df  # Fallback: se não houver coluna ativo, pega todos

            # Converter para lista de dicionários
            canais_list = []
            for _, row in df_ativos.iterrows():
                canais_list.append({
                    'codigo': row['codigo'],
                    'nome': row['nome'],
                    'descricao': row.get('descricao', '')
                })

            logger.info(f"[CANAIS] Atendimento carregados do CSV: {len(canais_list)} canais ativos")
            # 🔍 DEBUG: Mostrar primeiros 3 canais carregados
            print(f"\n📊 [CANAIS CSV] Carregados {len(canais_list)} canais ativos:")
            for i, canal in enumerate(canais_list[:3]):
                print(f"   {i+1}: {canal['codigo']} - {canal['nome']}")
            print()
            return canais_list

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de canais de atendimento ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return [
                {'codigo': 'SOUGOV', 'nome': 'SouGov.br', 'descricao': 'Portal de serviços do governo federal'},
                {'codigo': 'CENTRAL_TEL', 'nome': 'Central de Atendimento Telefônico', 'descricao': 'Atendimento por telefone (call center)'},
                {'codigo': 'ATEND_PRES', 'nome': 'Atendimento Presencial', 'descricao': 'Atendimento em balcão/guichê'},
                {'codigo': 'PROTOCOLO_DIG', 'nome': 'Protocolo Digital', 'descricao': 'Sistema de protocolo eletrônico'},
                {'codigo': 'ENT_REPRES', 'nome': 'Entidade Representativa', 'descricao': 'Sindicatos e associações de classe'},
                {'codigo': 'EMAIL', 'nome': 'E-mail', 'descricao': 'Atendimento por correio eletrônico'},
            ]

    def _carregar_arquitetura_csv(self) -> Dict[str, Any]:
        """
        Carrega CSV com 107 atividades mapeadas e estrutura hierarquicamente.

        Returns:
            dict: Estrutura hierárquica {
                'macroprocessos': {
                    'Gestão de Benefícios Previdenciários': {
                        'processos': {
                            'Gestão de Aposentadorias': {
                                'subprocessos': {
                                    'Concessão de aposentadorias': {
                                        'atividades': ['Conceder benefício...', ...]
                                    }
                                }
                            }
                        }
                    }
                },
                'flat_list': [  # Lista plana para busca rápida
                    {
                        'macroprocesso': '...',
                        'processo': '...',
                        'subprocesso': '...',
                        'atividade': '...'
                    }
                ]
            }
        """
        import os

        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            'Arquitetura_DECIPEX_mapeada.csv'
        )

        try:
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Estrutura hierárquica
            hierarquia = {}
            lista_plana = []

            for _, row in df.iterrows():
                macro = row['Macroprocesso']
                processo = row['Processo']
                subprocesso = row['Subprocesso']
                atividade = row['Atividade']

                # Pular linhas vazias
                if pd.isna(macro) or pd.isna(atividade):
                    continue

                # Adicionar à lista plana
                lista_plana.append({
                    'macroprocesso': macro,
                    'processo': processo,
                    'subprocesso': subprocesso,
                    'atividade': atividade
                })

                # Construir hierarquia
                if macro not in hierarquia:
                    hierarquia[macro] = {'processos': {}}

                if processo not in hierarquia[macro]['processos']:
                    hierarquia[macro]['processos'][processo] = {'subprocessos': {}}

                if subprocesso not in hierarquia[macro]['processos'][processo]['subprocessos']:
                    hierarquia[macro]['processos'][processo]['subprocessos'][subprocesso] = {'atividades': []}

                hierarquia[macro]['processos'][processo]['subprocessos'][subprocesso]['atividades'].append(atividade)

            logger.info(f"[ATIVIDADES] CSV carregado: {len(lista_plana)} atividades em hierarquia")

            return {
                'macroprocessos': hierarquia,
                'flat_list': lista_plana
            }

        except Exception as e:
            logger.error(f"❌ Erro ao carregar CSV de arquitetura: {e}")
            return {'macroprocessos': {}, 'flat_list': []}

    def _preparar_dados_dropdown_hierarquico(self) -> Dict[str, Any]:
        """
        Prepara dados para interface de dropdown hierárquico (fallback quando IA falha).

        Returns:
            dict: Dados formatados para o frontend renderizar os dropdowns cascateados
        """
        estrutura = self._carregar_arquitetura_csv()

        # Formato para o frontend
        dados_dropdown = {
            'macroprocessos': list(estrutura['macroprocessos'].keys()),
            'hierarquia_completa': estrutura['macroprocessos']
        }

        return dados_dropdown

    def inicializar_estado(self, skip_intro: bool = False) -> dict:
        """
        Inicializa estado limpo para Helena POP

        Args:
            skip_intro: Se True, pula a introdução e vai direto para NOME_USUARIO
                       (usado quando frontend já mostrou mensagem de boas-vindas)

        Returns:
            dict: Estado inicial com POPStateMachine
        """
        sm = POPStateMachine()

        # Se frontend já mostrou introdução, pular para coleta de nome
        if skip_intro:
            sm.estado = EstadoPOP.NOME_USUARIO

        return sm.to_dict()

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuário de acordo com o estado atual

        Args:
            mensagem: Texto do usuário
            session_data: Estado atual da sessão

        Returns:
            dict: Resposta com novo estado
        """
        # Validações
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        # Carregar state machine
        sm = POPStateMachine.from_dict(session_data)

        # 🔍 DEBUG CRÍTICO: Log do estado NO INÍCIO do processamento
        logger.info(f"[PROCESSAR] ===== INÍCIO DO PROCESSAMENTO =====")
        logger.info(f"[PROCESSAR] Estado CARREGADO da sessão: {sm.estado}")
        logger.info(f"[PROCESSAR] Mensagem recebida (primeiros 100 chars): {mensagem[:100]}")
        logger.info(f"[PROCESSAR] ============================================")

        # 🎯 Inicializar variáveis que podem vir dos handlers
        metadados_arquitetura = None
        metadados_extra = None

        # Processar de acordo com o estado
        if sm.estado == EstadoPOP.NOME_USUARIO:
            resposta, novo_sm = self._processar_nome_usuario(mensagem, sm)

        elif sm.estado == EstadoPOP.CONFIRMA_NOME:
            resposta, novo_sm = self._processar_confirma_nome(mensagem, sm)

        elif sm.estado == EstadoPOP.ESCOLHA_TIPO_EXPLICACAO:
            resposta, novo_sm = self._processar_escolha_tipo_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO_LONGA:
            resposta, novo_sm = self._processar_explicacao_longa(mensagem, sm)

        elif sm.estado == EstadoPOP.DUVIDAS_EXPLICACAO:
            resposta, novo_sm = self._processar_duvidas_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO:
            resposta, novo_sm = self._processar_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            resposta, novo_sm = self._processar_pedido_compromisso(mensagem, sm)

        elif sm.estado == EstadoPOP.AREA_DECIPEX:
            resultado_area = self._processar_area_decipex(mensagem, sm)
            if len(resultado_area) == 3:
                resposta, novo_sm, metadados_extra = resultado_area
            else:
                resposta, novo_sm = resultado_area
                metadados_extra = None

        elif sm.estado == EstadoPOP.SUBAREA_DECIPEX:
            resultado_subarea = self._processar_subarea_decipex(mensagem, sm)
            if len(resultado_subarea) == 3:
                resposta, novo_sm, metadados_extra = resultado_subarea
            else:
                resposta, novo_sm = resultado_subarea
                metadados_extra = None

        elif sm.estado == EstadoPOP.ARQUITETURA:
            resultado_arq = self._processar_arquitetura(mensagem, sm)
            if len(resultado_arq) == 3:
                resposta, novo_sm, metadados_arquitetura = resultado_arq
            else:
                resposta, novo_sm = resultado_arq
                metadados_arquitetura = None

        elif sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            resultado_conf = self._processar_confirmacao_arquitetura(mensagem, sm)
            if len(resultado_conf) == 3:
                resposta, novo_sm, metadados_extra = resultado_conf
            else:
                resposta, novo_sm = resultado_conf
                metadados_extra = None

        elif sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            resposta, novo_sm = self._processar_selecao_hierarquica(mensagem, sm)

        elif sm.estado == EstadoPOP.NOME_PROCESSO:
            resposta, novo_sm = self._processar_nome_processo(mensagem, sm)

        elif sm.estado == EstadoPOP.ENTREGA_ESPERADA:
            resultado_entrega = self._processar_entrega_esperada(mensagem, sm)
            if len(resultado_entrega) == 3:
                resposta, novo_sm, metadados_extra = resultado_entrega
            else:
                resposta, novo_sm = resultado_entrega
                metadados_extra = None

        elif sm.estado == EstadoPOP.CONFIRMACAO_ENTREGA:
            resposta, novo_sm = self._processar_confirmacao_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            resposta, novo_sm = self._processar_reconhecimento_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            resposta, novo_sm = self._processar_dispositivos_normativos(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_ROADTRIP:
            resposta, novo_sm = self._processar_transicao_roadtrip(mensagem, sm)

        elif sm.estado == EstadoPOP.OPERADORES:
            logger.info(f"[PROCESSAR] Estado ANTES de chamar _processar_operadores: {sm.estado}")
            resposta, novo_sm = self._processar_operadores(mensagem, sm)
            logger.info(f"[PROCESSAR] Estado DEPOIS de _processar_operadores: {novo_sm.estado}")
            logger.info(f"[PROCESSAR] tipo_interface setado pelo handler: {novo_sm.tipo_interface}")

        elif sm.estado == EstadoPOP.SISTEMAS:
            resposta, novo_sm = self._processar_sistemas(mensagem, sm)

        elif sm.estado == EstadoPOP.FLUXOS:
            resposta, novo_sm = self._processar_fluxos(mensagem, sm)

        elif sm.estado == EstadoPOP.PONTOS_ATENCAO:
            resposta, novo_sm = self._processar_pontos_atencao(mensagem, sm)

        elif sm.estado == EstadoPOP.REVISAO_PRE_DELEGACAO:
            resposta, novo_sm = self._processar_revisao_pre_delegacao(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_EPICA:
            resultado_epica = self._processar_transicao_epica(mensagem, sm)
            if len(resultado_epica) == 3:
                resposta, novo_sm, metadados_extra = resultado_epica
            else:
                resposta, novo_sm = resultado_epica
                metadados_extra = None

        elif sm.estado == EstadoPOP.SELECAO_EDICAO:
            resposta, novo_sm = self._processar_selecao_edicao(mensagem, sm)

        elif sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            resultado_delegacao = self._processar_delegacao_etapas(mensagem, sm)
            if len(resultado_delegacao) == 3:
                resposta, novo_sm, metadados_extra = resultado_delegacao
            else:
                resposta, novo_sm = resultado_delegacao
                metadados_extra = None

        else:
            resposta = "Estado desconhecido. Vamos recomeçar?"
            novo_sm = POPStateMachine()

        # Calcular progresso
        progresso = self._calcular_progresso(novo_sm)
        progresso_detalhado = self.obter_progresso(novo_sm)

        # Verificar se deve sugerir mudança de contexto
        sugerir_contexto = None
        if novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS or novo_sm.concluido:
            sugerir_contexto = 'etapas'

        # 🎯 Inicializar variáveis de interface (serão preenchidas abaixo)
        tipo_interface = None
        dados_interface = None

        # Criar metadados_extra base (ou usar o que veio dos handlers)
        if not metadados_extra:
            metadados_extra = {}

        metadados_extra['progresso_detalhado'] = progresso_detalhado

        # Mesclar metadados_arquitetura se existir (vindo do pipeline)
        if metadados_arquitetura:
            metadados_extra.update(metadados_arquitetura)

            # ✅ FIX CRÍTICO: Extrair tipo_interface dos metadados do pipeline
            # O pipeline retorna: {'interface': {'tipo': 'sugestao_atividade', 'dados': {...}}}
            # Precisamos popular tipo_interface e dados_interface para o frontend
            if 'interface' in metadados_arquitetura:
                interface_info = metadados_arquitetura['interface']
                tipo_interface = interface_info.get('tipo')
                dados_interface = interface_info.get('dados', {})
                logger.debug(f"[FIX] Extraído do pipeline: tipo_interface={tipo_interface}")

        # Se metadados_extra contém interface (vindo de handlers como CONFIRMACAO_ARQUITETURA ou ENTREGA_ESPERADA)
        if metadados_extra and 'interface' in metadados_extra:
            interface_info = metadados_extra['interface']
            tipo_interface = interface_info.get('tipo')
            dados_interface = interface_info.get('dados', {})
            logger.debug(f"[FIX] Extraído de metadados_extra: tipo_interface={tipo_interface}")

        # Badge de conquista na transição épica
        if novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            metadados_extra['badge'] = {
                'tipo': 'fase_previa_completa',
                'emoji': '🏆',
                'titulo': 'Fase Prévia Concluída!',
                'descricao': 'Você mapeou toda a estrutura básica do processo',
                'mostrar_animacao': True
            }

        # Badge "Parceria confirmada!" ao aceitar compromisso
        if novo_sm.estado == EstadoPOP.AREA_DECIPEX and sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            metadados_extra['badge'] = {
                'tipo': 'parceria_confirmada',
                'emoji': '💬',
                'titulo': 'Parceria confirmada!',
                'descricao': 'Você e Helena agora são parceiros nessa jornada de mapeamento!',
                'mostrar_animacao': True
            }

        # 🎯 Definir interface dinâmica baseada no estado (se não foi definida pelo pipeline)
        # IMPORTANTE: Só definir se tipo_interface ainda estiver None (não foi definido pelo pipeline)
        if not tipo_interface and novo_sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            # Interface com badge de compromisso (estilo gamificação)
            tipo_interface = 'badge_compromisso'
            dados_interface = {
                'nome_compromisso': 'Compromisso de Cartógrafo(a)',
                'emoji': '🤝',
                'descricao': 'Você se comprometeu a registrar seu processo com cuidado e dedicação!'
            }

        elif novo_sm.estado == EstadoPOP.CONFIRMA_NOME:
            # Interface com 2 botões: Pode sim / Não, prefiro outro nome
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': 'Pode sim, Helena.',
                'botao_editar': 'Não, prefiro ser chamado de outro nome.',
                'valor_confirmar': 'sim',
                'valor_editar': 'não'
            }

        elif novo_sm.estado == EstadoPOP.ESCOLHA_TIPO_EXPLICACAO:
            # 🆕 Interface com 2 botões: Explicação detalhada / Explicação objetiva
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': '📘 Explicação detalhada',
                'botao_editar': '⚡ Explicação objetiva',
                'valor_confirmar': 'detalhada',
                'valor_editar': 'objetiva'
            }

        elif novo_sm.estado == EstadoPOP.EXPLICACAO_LONGA:
            # 🆕 Interface após explicação longa: Sim entendi / Não, tenho dúvidas
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': '🔹 Sim, vamos continuar!',
                'botao_editar': '🔹 Não, ainda tenho dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'não'
            }

        elif novo_sm.estado == EstadoPOP.AREA_DECIPEX:
            tipo_interface = 'areas'

            # 🔍 DEBUG: Ver o que tem em AREAS_DECIPEX
            print(f"\n🏢 [ESTADO AREA_DECIPEX] Construindo interface de áreas...")
            print(f"   self.AREAS_DECIPEX tem {len(self.AREAS_DECIPEX)} áreas")
            for num, info in list(self.AREAS_DECIPEX.items())[:3]:
                print(f"   {num}: {info}")

            dados_interface = {
                'opcoes_areas': {
                    str(num): {'codigo': info['codigo'], 'nome': info['nome']}
                    for num, info in self.AREAS_DECIPEX.items()
                }
            }

            print(f"   📦 opcoes_areas criado com {len(dados_interface['opcoes_areas'])} itens\n")

        elif novo_sm.estado == EstadoPOP.SUBAREA_DECIPEX:
            tipo_interface = 'subareas'
            dados_interface = {
                'area_pai': {
                    'codigo': novo_sm.area_selecionada['codigo'],
                    'nome': novo_sm.area_selecionada['nome']
                },
                'subareas': novo_sm.area_selecionada.get('subareas', [])
            }

        elif novo_sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            # 🆕 FALLBACK: Interface de dropdowns hierárquicos para seleção manual
            tipo_interface = 'arquitetura_hierarquica'
            dados_interface = self._preparar_dados_dropdown_hierarquico()

        elif not tipo_interface and novo_sm.estado == EstadoPOP.ARQUITETURA:
            # Interface de texto livre com botão de exemplos (se pipeline não retornou sugestão)
            tipo_interface = 'texto_com_exemplos'
            dados_interface = {
                'placeholder': 'Ex: Faço processo de pré aposentadoria, a pedido do servidor e envio para a área responsável pra análise.',
                'exemplos': [
                    "Analiso pensões. Fica pronto: o parecer aprovando ou negando, informo pro usuário.",
                    "Cadastro atos. Fica pronto: o ato no sistema, envio pro TCU.",
                    "Faço cálculos. Fica pronto: a planilha de valores vai pra AGU.",
                    "Faço pré-cadastro pra aposentadoria vai pra CGBEN."
                ]
            }

        elif novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            # Interface épica com botão pulsante e opção de pausa
            tipo_interface = 'transicao_epica'
            dados_interface = {
                'botao_principal': {
                    'texto': '🔍 COMEÇAR MINERAÇÃO DOS DETALHES',
                    'classe': 'botao-pulsante-centro',
                    'tamanho': 'grande',
                    'cor': '#4CAF50',
                    'animacao': 'pulse',
                    'valor_enviar': 'VAMOS'
                },
                'botao_secundario': {
                    'texto': 'Preciso de uma pausa',
                    'classe': 'link-discreto',
                    'posicao': 'abaixo',
                    'valor_enviar': 'PAUSA'
                },
                'mostrar_progresso': True,
                'progresso_texto': 'Identificação concluída!',
                'background_especial': True
            }

        elif novo_sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            # Gamificação após entrega esperada
            tipo_interface = 'caixinha_reconhecimento'
            dados_interface = {
                'nome_usuario': novo_sm.nome_usuario or 'você'
            }

        elif novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            # Interface de transição com troféu e auto-redirect
            tipo_interface = 'transicao'
            dados_interface = {
                'proximo_modulo': 'etapas',
                'mostrar_trofeu': True,
                'mensagem_trofeu': 'Primeira Fase Concluída!',
                'auto_redirect': True,
                'delay_ms': 2000
            }

        elif not tipo_interface and novo_sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            # Interface com 2 botões: Concordo / Editar manualmente
            # IMPORTANTE: Só definir se tipo_interface ainda não foi setado (ex: pelo pipeline RAG)
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': 'Concordo com a sugestão ✅',
                'botao_editar': 'Quero editar manualmente ✏️',
                'valor_confirmar': 'sim',
                'valor_editar': 'editar'
            }

        elif novo_sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            # Interface rica de normas com IA
            sugestoes = self._sugerir_base_legal_contextual(novo_sm)
            grupos_normas = {}
            if self.suggestor_base_legal:
                try:
                    grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
                except:
                    pass

            tipo_interface = 'normas'
            dados_interface = {
                'sugestoes': sugestoes,
                'grupos': grupos_normas,
                'campo_livre': True,
                'multipla_selecao': True,
                'texto_introducao': (
                    f"**1️⃣** Primeiro, pelo que eu entendi da sua atividade eu **sugeri normas pelo grau de aderência**. (Você concordar ou não, ok?)\n\n"
                    f"**2️⃣** Se vir que ainda faltam normas **você pode expandir e explorar a biblioteca completa de todas as normas** organizadas por categoria\n\n"
                    f"**3️⃣** Aqui minha forte recomendação: **Conversar com minha parceira do Sigepe Legis IA** (link abaixo). "
                    f"Ela pode te ajudar a buscar outras normas que talvez você nem saiba que existem, e aí é só copiar o trecho e colar aqui.\n\n"
                    f"**4️⃣** E lembrando que **você sempre pode adicionar norma manualmente** caso lembre de alguma norma que nem eu, nem a Legis encontramos."
                )
            }

        elif novo_sm.estado == EstadoPOP.TRANSICAO_ROADTRIP:
            logger.info(f"🚗🚗🚗 [PROXIMA_INTERFACE] ENTROU NO ELIF TRANSICAO_ROADTRIP!")

            # ✅ SEMPRE mostrar interface roadtrip junto com a mensagem (solução simplificada)
            tipo_interface = 'roadtrip'
            dados_interface = {}
            logger.info(f"🚗 [PROXIMA_INTERFACE] Definindo interface roadtrip! tipo={tipo_interface}")

        elif novo_sm.estado == EstadoPOP.OPERADORES:
            # Interface rica de operadores
            tipo_interface = 'operadores'
            dados_interface = {
                'opcoes': self.OPERADORES_DECIPEX,
                'campo_livre': True,
                'multipla_selecao': True
            }

        elif novo_sm.estado == EstadoPOP.SISTEMAS:
            # Interface rica de sistemas organizados
            tipo_interface = 'sistemas'
            dados_interface = {
                'sistemas_por_categoria': self.SISTEMAS_DECIPEX,
                'campo_livre': True,
                'multipla_selecao': True
            }

        # ✅ FIX: Verificar se o state machine tem tipo_interface setado
        # (usado por _processar_fluxos, etc.)
        # IMPORTANTE: SEMPRE dar prioridade ao tipo_interface definido pelo handler (sm.tipo_interface)
        # pois ele é mais específico e foi definido propositalmente pelo _processar_* correspondente
        logger.info(f"[PROCESSAR] Antes de ler sm.tipo_interface: tipo_interface={tipo_interface}, novo_sm.estado={novo_sm.estado}")
        if hasattr(novo_sm, 'tipo_interface') and novo_sm.tipo_interface:
            logger.info(f"[PROCESSAR] sm.tipo_interface EXISTE e é: {novo_sm.tipo_interface}")
            # 🔥 FIX CRÍTICO: SEMPRE dar prioridade ao sm.tipo_interface (removido o "not tipo_interface")
            tipo_interface = novo_sm.tipo_interface
            dados_interface = getattr(novo_sm, 'dados_interface', {})
            logger.info(f"[PROCESSAR] ✅ tipo_interface ATUALIZADO de sm para: {tipo_interface}")

        # 🎯 PREENCHIMENTO EM TEMPO REAL - Dados do formulário POP
        formulario_pop = self._preparar_dados_formulario(novo_sm)

        # ✅ FIX CRÍTICO: Frontend OLD lia "dados_extraidos", não "formulario_pop"
        # Enviar AMBOS para compatibilidade total
        dados_extraidos = formulario_pop.copy()

        # 🔒 INVARIANTE DE SEGURANÇA: Garantir resposta=None em modo interface
        # Evita regressões caso alguém esqueça de definir resposta=None em algum handler
        if tipo_interface and resposta == "":
            resposta = None

        # DEBUG: Log para verificar se dados estão sendo enviados
        def _short(r):
            """Helper para log: diferenciar None vs "" vs texto"""
            if r is None: return "<None>"
            if r == "": return "<vazia>"
            return r[:100]

        logger.info(f"[DEBUG] Dados preparados: CAP={formulario_pop.get('codigo_cap')}, Macro={formulario_pop.get('macroprocesso')}, Atividade={formulario_pop.get('atividade')}")
        logger.debug(f"[RETORNO FINAL] tipo_interface={tipo_interface}, dados_interface presente={dados_interface is not None}, resposta={_short(resposta)}")

        # 🔍 DEBUG CRÍTICO: Log completo antes de retornar
        logger.info(f"[PROCESSAR] ===== RETORNO FINAL =====")
        logger.info(f"[PROCESSAR] novo_sm.estado = {novo_sm.estado}")
        logger.info(f"[PROCESSAR] tipo_interface = {tipo_interface}")
        logger.info(f"[PROCESSAR] dados_interface tem {len(dados_interface) if dados_interface else 0} chaves")
        logger.info(f"[PROCESSAR] resposta = {_short(resposta)}")
        logger.info(f"[PROCESSAR] ===============================")

        resposta_final = self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_sm.to_dict(),
            progresso=progresso,
            sugerir_contexto=sugerir_contexto,
            metadados=metadados_extra,
            tipo_interface=tipo_interface,
            dados_interface=dados_interface,
            formulario_pop=formulario_pop,  # ✅ FASE 2: Novo nome
            dados_extraidos=dados_extraidos  # ✅ FIX: Compatibilidade com frontend OLD
        )

        # 🔍 DEBUG ULTRA CRÍTICO: Log do JSON EXATO que será enviado ao frontend
        logger.info(f"[PROCESSAR] 📤📤📤 RESPOSTA HTTP FINAL 📤📤📤")
        logger.info(f"[PROCESSAR] 📤 tipo_interface na resposta = {resposta_final.get('tipo_interface')}")
        logger.info(f"[PROCESSAR] 📤 interface na resposta = {resposta_final.get('interface')}")
        logger.info(f"[PROCESSAR] 📤 dados_interface.keys = {list(resposta_final.get('dados_interface', {}).keys())}")
        logger.info(f"[PROCESSAR] 📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤")

        return resposta_final

    # ========================================================================
    # PROCESSADORES DE ESTADO
    # ========================================================================

    def _processar_nome_usuario(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa coleta do nome do usuário (SOLUÇÃO DO OLD - sem duplicação)

        Detecta se mensagem é um nome candidato ou precisa pedir nome

        ✅ FIX DUPLICAÇÃO BOAS-VINDAS:
        - Frontend já mostra mensagem hardcoded
        - Backend apenas processa o nome, sem repetir introdução
        """
        import re

        msg_limpa = mensagem.strip()
        palavras = msg_limpa.split()

        # Saudações comuns
        saudacoes = ["oi", "olá", "ola", "hey", "e aí", "e ai", "oie"]
        confirmacoes = ["sim", "s", "não", "nao", "n"]

        # Verificar se é nome candidato
        apenas_uma_palavra = len(palavras) == 1
        palavra = palavras[0] if palavras else ""
        eh_saudacao = palavra.lower() in saudacoes
        tem_pontuacao_frase = bool(re.search(r"[!?.,]", msg_limpa)) or len(palavras) > 1
        eh_nome_candidato = (
            apenas_uma_palavra and
            len(palavra) >= 2 and
            palavra.isalpha() and
            not eh_saudacao and
            not tem_pontuacao_frase and
            palavra.lower() not in confirmacoes
        )

        if eh_nome_candidato:
            # É um nome válido - ir para confirmação
            sm.nome_temporario = palavra.capitalize()
            sm.estado = EstadoPOP.CONFIRMA_NOME
            resposta = (
                f"Olá, {sm.nome_temporario}! Prazer em te conhecer.\n\n"
                "Fico feliz que você tenha aceitado essa missão de documentar nossos processos.\n\n"
                f"**Antes de continuarmos, me confirma, posso te chamar de {sm.nome_temporario} mesmo?**"
            )
            return resposta, sm

        # ✅ FIX: Se mensagem não é nome válido, apenas pedir clarificação
        # NUNCA repetir boas-vindas completas (frontend já mostrou)
        resposta = "Desculpe, não entendi. Pode me dizer seu nome? (Digite apenas o primeiro nome)"
        return resposta, sm

    def _gerar_explicacao_longa_com_delay(self) -> str:
        """
        Gera mensagem de explicação longa com delays progressivos.

        Quebra a mensagem em 4 partes com delays de 1500ms entre elas:
        1. Introdução empática (imediata)
        2. Explicação do contexto (após 1500ms)
        3. Detalhamento das etapas (após 1500ms)
        4. Fechamento motivacional (após 1500ms)

        Returns:
            str: Mensagem com tags [DELAY:1500] para processamento no frontend
        """
        return (
            f"Opa, você quer mais detalhes? 😊[DELAY:1500]"
            f"Eu amei, porque adoro conversar![DELAY:1500]"
            f"Então vamos com calma, que eu te explico tudo direitinho.\n\n"
            f"Nesse chat, a gente vai mapear a sua atividade:\n\n"
            f"aquilo que você faz todos os dias (ou quase), a rotina real do seu trabalho.\n\n"
            f"A ideia é preencher juntos o formulário de Procedimento Operacional Padrão, o famoso POP, "
            f"que tá aí do lado 👉\n"
            f"Dá uma olhadinha! Nossa meta é deixar esse POP prontinho, claro e útil pra todo mundo que "
            f"trabalha com você. ✅[DELAY:1500]"
            f"\n\nEu vou te perguntar:\n"
            f"🧭 em qual área você atua,\n"
            f"🧩 te ajudar com a parte mais burocrática — macroprocesso, processo, subprocesso e atividade,\n"
            f"📘 e criar o \"CPF\" do seu processo (a gente chama de CAP, Código na Arquitetura do Processo).\n\n"
            f"Depois, vamos falar sobre os sistemas que você usa e as normas que regem sua atividade.\n"
            f"Nessa parte, vou até te apresentar minha amiga do Sigepe Legis IA — ela é especialista em achar "
            f"a norma certa no meio de tanta lei e portaria 🤖📜[DELAY:1500]"
            f"\n\nPor fim, vem a parte mais detalhada: você vai me contar passo a passo o que faz no dia a dia.\n\n"
            f"Pode parecer demorado, mas pensa assim: quanto melhor você mapear agora, menos retrabalho vai "
            f"ter depois — e o seu processo vai ficar claro, seguro e fácil de ensinar pra quem chegar novo. 💪\n\n"
            f"Tudo certo até aqui?"
        )

    def _processar_confirma_nome(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação do nome e vai direto para escolha de tipo de explicação"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['sim', 's', 'pode', 'ok', 'claro']):
            sm.nome_usuario = sm.nome_temporario
            sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO

            resposta = (
                f"Ótimo então, {sm.nome_usuario}. 😊\n\n"
                f"Antes de seguir, preciso te explicar rapidinho como tudo vai funcionar.\n\n"
                f"Você prefere:\n\n"
                f"🕐 **que eu fale de forma objetiva**, ou\n"
                f"💬 **uma explicação mais detalhada**\n\n"
                f"sobre o que vamos fazer daqui pra frente?"
            )
        else:
            sm.estado = EstadoPOP.NOME_USUARIO
            resposta = "Sem problemas! Como você prefere que eu te chame?"

        return resposta, sm

    def _processar_escolha_tipo_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa escolha entre explicação curta ou longa"""
        msg_lower = mensagem.lower().strip()

        # Explicação detalhada/longa
        if any(palavra in msg_lower for palavra in ['detalhada', 'longa', 'detalhes', 'completa']):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
            return resposta, sm

        # Explicação objetiva/curta (fluxo atual)
        elif any(palavra in msg_lower for palavra in ['objetiva', 'curta', 'rápida', 'rapida', 'resumida']):
            sm.estado = EstadoPOP.EXPLICACAO
            sm.tipo_interface = 'confirmacao_explicacao'
            sm.dados_interface = {
                'botoes': [
                    {'label': 'Sim', 'valor': 'sim', 'tipo': 'primary'},
                    {'label': 'Não, quero mais detalhes', 'valor': 'detalhes', 'tipo': 'secondary'}
                ]
            }
            resposta = (
                f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário "
                f"de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\n"
                f"Nossa meta é entregar esse POP prontinho. Vamos continuar?"
            )
            return resposta, sm

        # Não entendeu
        else:
            resposta = (
                f"Desculpe, não entendi. Por favor, escolha:\n\n"
                f"📘 **Explicação detalhada** - para entender tudo em detalhes\n"
                f"⚡ **Explicação objetiva** - para ir direto ao ponto"
            )
            return resposta, sm

    def _processar_explicacao_longa(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa resposta após explicação longa"""
        msg_lower = mensagem.lower().strip()

        # Entendeu tudo - vai para PEDIDO DE COMPROMISSO
        if any(palavra in msg_lower for palavra in ['sim', 's', 'entendi', 'ok', 'claro', 'beleza', 'tudo']):
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
            )
            return resposta, sm

        # Ainda tem dúvidas - ativar Helena Mapeamento internamente
        elif any(palavra in msg_lower for palavra in ['não', 'nao', 'n', 'duvida', 'dúvida']):
            sm.estado = EstadoPOP.DUVIDAS_EXPLICACAO
            # Flag para indicar que está em modo dúvidas (Helena Mapeamento ativo)
            sm.em_modo_duvidas = True
            sm.contexto_duvidas = "explicacao_pop"  # Contexto: está tirando dúvidas sobre explicação do POP

            resposta = (
                f"Sem problemas, {sm.nome_usuario}! 😊\n\n"
                f"Pode me fazer qualquer pergunta sobre o processo. "
                f"Estou aqui para te ajudar a entender melhor!"
            )
            return resposta, sm

        # Fallback
        else:
            resposta = (
                f"Por favor, me diga:\n"
                f"🔹 **Sim, vamos continuar!** - para continuar\n"
                f"🔹 **Não, ainda tenho dúvidas** - para eu te explicar melhor"
            )
            return resposta, sm

    def _processar_duvidas_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa dúvidas sobre a explicação delegando para Helena Mapeamento.

        Fluxo:
        1. Instancia Helena Mapeamento
        2. Delega mensagem para Helena Mapeamento
        3. Helena Mapeamento responde livremente com DOIS botões
        4. "Ok, já entendi" → vai para PEDIDO_COMPROMISSO
        5. "Tenho mais uma pergunta" → continua com Helena Mapeamento
        """
        msg_lower = mensagem.lower().strip()

        # 🔥 Tratar cliques nos botões da interface anterior
        if msg_lower in ['ok_entendi', 'ok', 'entendi', 'ja entendi', 'já entendi']:
            # Usuário clicou em "Ok, já entendi" → sair do modo dúvidas
            sm.em_modo_duvidas = False
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
            )

            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': 'Clique aqui pra fechar nosso acordo',
                'botao_editar': 'Tenho mais dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'duvidas'
            }
            return resposta, sm

        elif msg_lower in ['mais_pergunta', 'mais', 'pergunta', 'tenho mais']:
            # Usuário clicou em "Tenho mais uma pergunta" → solicitar a pergunta
            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = f"Claro, {sm.nome_usuario}! Pode fazer sua pergunta que vou te ajudar. 😊"
            return resposta, sm

        from processos.domain.helena_mapeamento.helena_mapeamento import HelenaMapeamento

        # Instanciar Helena Mapeamento se ainda não existe
        helena_map = HelenaMapeamento()

        # Inicializar estado de Helena Mapeamento se necessário
        if sm.estado_helena_mapeamento is None:
            sm.estado_helena_mapeamento = helena_map.inicializar_estado()
            # Contexto: usuário está tirando dúvidas sobre explicação do POP
            sm.estado_helena_mapeamento['contexto'] = sm.contexto_duvidas
            sm.estado_helena_mapeamento['nome_usuario'] = sm.nome_usuario

        # Delegar processamento para Helena Mapeamento
        resultado = helena_map.processar(mensagem, sm.estado_helena_mapeamento)

        # Atualizar estado de Helena Mapeamento
        sm.estado_helena_mapeamento = resultado['novo_estado']

        # 🔥 SEMPRE retornar interface de confirmação dupla após resposta da Helena Mapeamento
        resposta = resultado['resposta']

        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Ok, já entendi',
            'botao_editar': 'Tenho mais uma pergunta',
            'valor_confirmar': 'ok_entendi',
            'valor_editar': 'mais_pergunta'
        }

        return resposta, sm

    def _processar_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Confirma que está tudo claro e pronto para começar (modo curto)"""
        msg_lower = mensagem.lower().strip()

        # Limpar interface após resposta
        sm.tipo_interface = None
        sm.dados_interface = {}

        respostas_positivas = ['sim', 's', 'pode', 'ok', 'claro', 'vamos', 'yes', 'uhum', 'aham', 'beleza', 'entendi', 'bora', 'vamo', 'pronta', 'pronto']

        # Se escolheu "Sim" - vai para PEDIDO DE COMPROMISSO
        if msg_lower in respostas_positivas:
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
            )
        # Se escolheu "Não, quero mais detalhes" - vai para EXPLICACAO_LONGA
        elif 'detalhes' in msg_lower or 'detalhe' in msg_lower or ('não' in msg_lower or 'nao' in msg_lower):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
        else:
            resposta = f"Tudo bem! Só posso seguir quando você me disser 'sim', {sm.nome_usuario}. Quando quiser continuar, é só digitar."

        return resposta, sm

    def _processar_pedido_compromisso(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pedido de compromisso antes de começar o mapeamento

        Gamificação: Badge "Cartógrafo de Processos" ao aceitar o compromisso
        """
        msg_lower = mensagem.lower().strip()

        # 🔥 Tratar clique no botão "Tenho mais dúvidas"
        if msg_lower in ['duvidas', 'dúvidas', 'mais duvidas', 'mais dúvidas', 'tenho duvidas', 'tenho dúvidas']:
            # Voltar para modo dúvidas
            sm.em_modo_duvidas = True
            sm.estado = EstadoPOP.DUVIDAS_EXPLICACAO
            sm.contexto_duvidas = 'compromisso'

            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = f"Sem problemas, {sm.nome_usuario}! Pode fazer sua pergunta que vou te ajudar. 😊"
            return resposta, sm

        # Aceita qualquer resposta positiva (ambas opções levam para o mesmo lugar)
        respostas_positivas = ['sim', 'pode', 'conte', 'contigo', 'melhor', 'farei', 'ok', 'claro', 'vamos', 'junto']

        if any(palavra in msg_lower for palavra in respostas_positivas):
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"Uau! 🌟\n"
                f"**PARCERIA CONFIRMADA!** Tô super animada 😄\n\n"
                f"E agora oficialmente começamos nossa jornada de mapeamento.\n\n"
                f"Sei que dá trabalho, mas cada detalhe que você registrar hoje vai poupar horas (ou até dias!) "
                f"de dúvida no futuro. Pra você e pra sua equipe.\n\n"
                f"Esse é o tipo de esforço que vira legado dentro da DECIPEX. 🚀"
            )
            return resposta, sm
        else:
            # Se não entendeu, repete a pergunta
            resposta = (
                f"Desculpe, não entendi.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
            )
            return resposta, sm

    def _processar_area_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da área DECIPEX"""
        try:
            numero = int(mensagem.strip())
            if numero in self.AREAS_DECIPEX:
                sm.area_selecionada = self.AREAS_DECIPEX[numero]

                # Verificar se a área tem subáreas
                if sm.area_selecionada.get('tem_subareas', False):
                    sm.estado = EstadoPOP.SUBAREA_DECIPEX

                    # Buscar descrição personalizada da área
                    codigo_area = sm.area_selecionada['codigo']
                    descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                    resposta = (
                        f"Ótimo, {sm.nome_usuario}!\n"
                        f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}"
                    )

                else:
                    # Área sem subáreas, segue para arquitetura
                    sm.estado = EstadoPOP.ARQUITETURA

                    # Buscar descrição personalizada da área
                    codigo_area = sm.area_selecionada['codigo']
                    descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                    resposta = (
                        f"Ótimo, {sm.nome_usuario}!\n"
                        f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}\n\n"
                        f"✍️ Agora me conte: qual sua atividade principal e o que você entrega ao finalizar?\n\n"
                        f"Responda como se alguém te perguntasse \"você trabalha com o que?\"\n\n"
                        f"💡 Pode ser uma ou duas frases simples!"
                    )

                    # ✅ FLAG: Próxima resposta será descrição inicial de atividade (para quadro roxo no frontend)
                    metadados_extra = {
                        'aguardando_descricao_inicial': True
                    }

                    return resposta, sm, metadados_extra
            else:
                resposta = (
                    "Número inválido. Por favor, digite um número de 1 a 8 correspondente "
                    "a uma das áreas listadas acima."
                )
        except ValueError:
            resposta = (
                "Por favor, digite apenas o número da área (de 1 a 8)."
            )

        return resposta, sm

    def _processar_subarea_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da subárea (ex: DIGEP-RO, DIGEP-RR, DIGEP-AP)"""
        try:
            numero = int(mensagem.strip())
            subareas = sm.area_selecionada.get('subareas', [])

            if 1 <= numero <= len(subareas):
                sm.subarea_selecionada = subareas[numero - 1]
                sm.estado = EstadoPOP.ARQUITETURA

                resposta = (
                    f"Perfeito! Você trabalha na **{sm.subarea_selecionada['nome_completo']}**! 🌿\n\n"
                    f"✍️ Agora me conte: qual sua atividade principal e o que você entrega ao finalizar?\n\n"
                    f"Responda como se alguém te perguntasse \"você trabalha com o que?\"\n\n"
                    f"💡 Pode ser uma ou duas frases simples!"
                )

                # ✅ FLAG: Próxima resposta será descrição inicial de atividade (para quadro roxo no frontend)
                metadados_extra = {
                    'aguardando_descricao_inicial': True
                }

                return resposta, sm, metadados_extra
            else:
                resposta = (
                    f"Número inválido. Por favor, digite um número de 1 a {len(subareas)} correspondente "
                    "a uma das opções listadas acima."
                )
        except ValueError:
            resposta = (
                f"Por favor, digite apenas o número (1 a {len(sm.area_selecionada.get('subareas', []))})."
            )

        return resposta, sm

    def _processar_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa navegação na arquitetura DECIPEX usando sistema de busca em 4 camadas:

        CAMADA 1: Match Exato/Fuzzy no CSV
        CAMADA 2: Busca Semântica
        CAMADA 3: Seleção Manual Hierárquica
        CAMADA 4: RAG (criação de nova atividade)
        """
        import json

        # ================================================================
        # DETECTAR SE É RESPOSTA DE INTERFACE (JSON)
        # ================================================================
        try:
            dados_resposta = json.loads(mensagem)
            acao = dados_resposta.get('acao')

            # Se o usuário clicou "Não encontrei" na Camada 3
            if acao == 'nao_encontrei':
                logger.info("[HELENA POP] Usuário clicou 'Não encontrei' - acionando Camada 4 (RAG)")

                from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline

                # Preparar dados do autor
                area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
                autor_dados = {
                    'nome': sm.nome_usuario or "Usuário",
                    'cpf': "00000000000",
                    'area_codigo': area_codigo,
                    'area_nome': sm.area_selecionada['nome']
                }

                pipeline = BuscaAtividadePipeline()
                hierarquia_selecionada = dados_resposta.get('selecao')

                # Chamar Camada 4 com hierarquia selecionada
                resultado = pipeline._camada4_fallback_rag(
                    descricao_usuario='',  # Não usado nesta etapa
                    area_codigo=area_codigo,
                    contexto=None,
                    autor_dados=autor_dados,
                    hierarquia_selecionada=hierarquia_selecionada
                )

                # Retornar interface de pergunta
                if resultado.get('origem') == 'rag_aguardando_descricao':
                    # Salvar hierarquia herdada no estado para usar na próxima resposta
                    hierarquia_herdada = resultado.get('hierarquia_herdada')
                    sm.macro_selecionado = hierarquia_herdada.get('macroprocesso')
                    sm.processo_selecionado = hierarquia_herdada.get('processo')
                    sm.subprocesso_selecionado = hierarquia_herdada.get('subprocesso')

                    # Marcar que estamos aguardando descrição RAG
                    sm.dados_coletados['aguardando_descricao_rag'] = True

                    metadados_extra = {
                        'interface': {
                            'tipo': 'rag_pergunta_atividade',
                            'dados': {
                                'mensagem': resultado.get('mensagem'),
                                'hierarquia_herdada': hierarquia_herdada,
                                'instrucao': resultado.get('instrucao_frontend')
                            }
                        }
                    }
                    return "", sm, metadados_extra

            # Se o usuário enviou descrição na Camada 4
            elif acao == 'enviar_descricao':
                logger.info("[HELENA POP] Processando descrição da Camada 4 (RAG)")

                from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline

                descricao_atividade = dados_resposta.get('descricao')

                # Recuperar hierarquia herdada do estado (foi salva na etapa anterior)
                hierarquia_herdada = {
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado
                }

                # Preparar dados
                area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
                autor_dados = {
                    'nome': sm.nome_usuario or "Usuário",
                    'cpf': "00000000000",
                    'area_codigo': area_codigo,
                    'area_nome': sm.area_selecionada['nome']
                }

                pipeline = BuscaAtividadePipeline()

                # Processar resposta e criar atividade
                resultado = pipeline._camada4_processar_resposta(
                    descricao_atividade=descricao_atividade,
                    hierarquia_herdada=hierarquia_herdada,
                    area_codigo=area_codigo,
                    autor_dados=autor_dados
                )

                if resultado.get('sucesso'):
                    # Salvar dados no estado
                    ativ = resultado['atividade']
                    sm.macro_selecionado = ativ['macroprocesso']
                    sm.processo_selecionado = ativ['processo']
                    sm.subprocesso_selecionado = ativ['subprocesso']
                    sm.atividade_selecionada = ativ['atividade']
                    sm.codigo_cap = resultado.get('cap', 'PROVISORIO')
                    # NÃO mudar estado - permanecer em ARQUITETURA para permitir "prefiro_digitar"
                    # sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                    metadados_extra = {
                        'interface': {
                            'tipo': 'sugestao_atividade',
                            'dados': {
                                'atividade': ativ,
                                'cap': resultado.get('cap'),
                                'origem': 'rag_nova_atividade',
                                'score': 1.0,
                                'pode_editar': True,
                                'tipo_cap': 'oficial_gerado_rag',
                                'mensagem': resultado.get('mensagem', '')
                            }
                        }
                    }

                    return "", sm, metadados_extra
                else:
                    return "Desculpe, ocorreu um erro ao criar a atividade. Tente novamente.", sm

            # Se o usuário confirmou uma seleção da Camada 3
            elif acao == 'confirmar':
                selecao = dados_resposta.get('selecao')
                sm.macro_selecionado = selecao['macroprocesso']
                sm.processo_selecionado = selecao['processo']
                sm.subprocesso_selecionado = selecao['subprocesso']
                sm.atividade_selecionada = selecao['atividade']
                sm.codigo_cap = selecao.get('cap', 'A definir')
                sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                resposta = (
                    f"✅ Perfeito! Você selecionou:\n\n"
                    f"📋 **Macroprocesso:** {sm.macro_selecionado}\n"
                    f"📋 **Processo:** {sm.processo_selecionado}\n"
                    f"📋 **Subprocesso:** {sm.subprocesso_selecionado}\n"
                    f"📋 **Atividade:** {sm.atividade_selecionada}\n"
                    f"🔢 **Código CAP:** {sm.codigo_cap}\n\n"
                    f"Está correto?"
                )
                return resposta, sm

        except (json.JSONDecodeError, TypeError):
            # Não é JSON, é descrição normal do usuário
            pass

        # ================================================================
        # TRATAR AÇÃO "selecionar_manual" (botão da interface sugestao_atividade)
        # ================================================================
        if mensagem.strip().lower() in ['selecionar_manual', 'selecionar_manualmente']:
            logger.info("[HELENA POP] Usuário clicou 'Minha atividade não é essa, vou selecionar' - acionando Camada 3 (Dropdown)")

            from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline

            # Preparar pipeline
            area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
            pipeline = BuscaAtividadePipeline()

            # Chamar Camada 3: Seleção Manual Hierárquica (passando area_codigo para gerar CAP correto)
            hierarquia = pipeline._preparar_hierarquia_completa(area_codigo=area_codigo)

            if not hierarquia:
                logger.error("[HELENA POP] Erro ao carregar hierarquia para seleção manual")
                return "Desculpe, ocorreu um erro ao carregar as opções. Tente novamente.", sm

            # Retornar interface de seleção hierárquica
            metadados_extra = {
                'interface': {
                    'tipo': 'selecao_manual_hierarquica',
                    'dados': {
                        'hierarquia': hierarquia,
                        'acoes_usuario': ['confirmar', 'nao_encontrei'],
                        'mensagem': 'Por favor, selecione sua atividade navegando pela estrutura organizacional:',
                        'tipo_cap': 'oficial'
                    }
                }
            }

            resposta = None  # Modo interface: mensagem textual ausente por design
            return resposta, sm, metadados_extra

        # ================================================================
        # TRATAR "prefiro_digitar" (botão após RAG falhar)
        # ================================================================
        if mensagem.strip().lower() == 'prefiro_digitar':
            logger.info("[HELENA POP] Usuário rejeitou sugestão RAG - pedindo digitação manual final")

            nome = sm.nome_usuario or "você"

            # Retornar interface de texto livre para digitação final
            metadados_extra = {
                'interface': {
                    'tipo': 'texto_livre',
                    'dados': {
                        'placeholder': 'Ex: Analiso processos de aposentadoria e emito parecer final'
                    }
                }
            }

            resposta = (
                f"Sem problema, {nome}! Que pena que não consegui te ajudar 😢\n\n"
                f"Me diz então qual atividade, é bom que eu também aprendo!"
            )

            # Marcar que a próxima digitação deve ir direto pro POP sem buscar
            sm.dados_coletados['pular_busca'] = True

            return resposta, sm, metadados_extra

        # ================================================================
        # TRATAR "concordar" (botão "Você acertou, Helena!" da sugestão IA)
        # ================================================================
        msg_lower = mensagem.strip().lower()
        if msg_lower in ['concordar', 'confirmar', 'sim', 'concordo']:
            # Usuário confirmou a sugestão da IA (Camada 1 ou 2)
            # Ir direto para ENTREGA_ESPERADA (usuário já confirmou na interface de sugestão)
            logger.info(f"[HELENA POP] Usuário confirmou sugestão - pulando para ENTREGA_ESPERADA")

            # Sugerir entrega esperada usando Helena Ajuda Inteligente
            try:
                from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

                # Obter contexto da área
                if sm.subarea_selecionada:
                    area_nome = sm.subarea_selecionada.get('nome_completo', sm.subarea_selecionada.get('nome', ''))
                    area_codigo = sm.subarea_selecionada.get('codigo', '')
                elif sm.area_selecionada:
                    area_nome = sm.area_selecionada.get('nome', '')
                    area_codigo = sm.area_selecionada.get('codigo', '')
                else:
                    area_nome = 'DECIPEX'
                    area_codigo = 'DECIPEX'

                contexto = {
                    'area': area_nome,
                    'area_codigo': area_codigo,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada
                }

                # Chamar Helena Ajuda Inteligente para sugerir entrega
                descricao_original = sm.dados_coletados.get('descricao_original', sm.atividade_selecionada)
                resultado = analisar_atividade_com_helena(
                    descricao_usuario=descricao_original,
                    nivel_atual='resultado_final',  # Apenas sugerir entrega
                    contexto_ja_selecionado=contexto
                )

                sugestao_entrega = None
                if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                    sugestao_entrega = resultado['sugestao']['resultado_final']
                    sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                    logger.info(f"[ENTREGA] Sugestão da IA: {sugestao_entrega}")

            except Exception as e:
                logger.error(f"[ENTREGA] Erro ao sugerir entrega: {e}")
                sugestao_entrega = None

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:
                # Salvar sugestão temporariamente para uso posterior
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

                # Enviar interface com sugestão e botões
                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade. 📋"
                )
                return resposta, sm, metadados_extra
            else:
                # Se não conseguiu sugerir, pedir entrada manual
                metadados_extra = {
                    'interface': {
                        'tipo': 'texto_livre',
                        'dados': {
                            'placeholder': 'Ex: Processo analisado e parecer emitido'
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora me conta: **qual é o resultado final** dessa atividade?\n\n"
                    f"O que fica pronto quando você termina?"
                )
                return resposta, sm, metadados_extra

        descricao_usuario = mensagem.strip()

        # Validação: mínimo 10 caracteres (APENAS para descrições de atividade nova)
        if len(descricao_usuario) < 10:
            resposta = (
                "Por favor, descreva sua atividade com mais detalhes (mínimo 10 caracteres).\n\n"
                "Exemplo: 'Analiso requerimentos de auxílio saúde de aposentados'"
            )
            return resposta, sm

        # Obter dados do autor (para rastreabilidade)
        # Se há subárea selecionada, usar ela; senão, usar área principal
        if sm.subarea_selecionada:
            area_nome = sm.subarea_selecionada['nome_completo']
            area_codigo = sm.subarea_selecionada['codigo']
        else:
            area_nome = sm.area_selecionada['nome']
            area_codigo = sm.area_selecionada['codigo']

        autor_nome = sm.nome_usuario or "Usuário"
        autor_cpf = "00000000000"  # TODO: Obter CPF real do usuário autenticado

        logger.info(f"[GOVERNANÇA] Iniciando busca para: '{descricao_usuario}' | Autor: {autor_nome} | Área: {area_codigo}")

        print(f"[DEBUG] Área selecionada: {sm.area_selecionada}")
        print(f"[DEBUG] Subárea selecionada: {sm.subarea_selecionada}")
        print(f"[DEBUG] area_nome: {area_nome}")
        print(f"[DEBUG] area_codigo: {area_codigo}")

        # ============================================================================
        # VERIFICAR SE DEVE PULAR BUSCA (usuário rejeitou RAG e digitou manualmente)
        # ============================================================================
        if sm.dados_coletados.get('pular_busca'):
            logger.info("[HELENA POP] PULANDO BUSCA - Usuário digitou atividade final após rejeitar RAG")

            # Salvar atividade digitada (usando hierarquia já definida pelo RAG ou dropdown)
            sm.atividade_selecionada = descricao_usuario
            sm.dados_coletados['descricao_original'] = descricao_usuario

            # Gerar código CAP se ainda não tiver
            if not sm.codigo_cap or sm.codigo_cap == 'PROVISORIO':
                sm.codigo_cap = self._gerar_codigo_processo(sm)

            # Limpar flag
            sm.dados_coletados['pular_busca'] = False

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            # Sugerir entrega esperada usando Helena Ajuda Inteligente
            try:
                from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

                contexto = {
                    'area': area_nome,
                    'area_codigo': area_codigo,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada
                }

                resultado = analisar_atividade_com_helena(
                    descricao_usuario=descricao_usuario,
                    nivel_atual='resultado_final',
                    contexto_ja_selecionado=contexto
                )

                sugestao_entrega = None
                if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                    sugestao_entrega = resultado['sugestao']['resultado_final']
                    sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                    logger.info(f"[ENTREGA] Sugestão da IA: {sugestao_entrega}")

            except Exception as e:
                logger.error(f"[ENTREGA] Erro ao sugerir entrega: {e}")
                sugestao_entrega = None

            if sugestao_entrega:
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade. 📋"
                )
                return resposta, sm, metadados_extra
            else:
                metadados_extra = {
                    'interface': {
                        'tipo': 'texto_livre',
                        'dados': {
                            'placeholder': 'Ex: Processo analisado e parecer emitido'
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora me conta: **qual é o resultado final** dessa atividade?\n\n"
                    f"O que fica pronto quando você termina?"
                )
                return resposta, sm, metadados_extra

        # ============================================================================
        # DETECTAR SE ESTAMOS AGUARDANDO RESPOSTA DA CAMADA 4 RAG
        # ============================================================================
        if sm.dados_coletados.get('aguardando_descricao_rag', False):
            logger.info("[HELENA POP] Detectado: usuário respondeu à pergunta da Camada 4 RAG")
            logger.info(f"[HELENA POP] Descrição recebida: '{mensagem}'")

            from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline

            # Recuperar hierarquia herdada do estado (foi salva na etapa anterior)
            hierarquia_herdada = {
                'macroprocesso': sm.macro_selecionado,
                'processo': sm.processo_selecionado,
                'subprocesso': sm.subprocesso_selecionado
            }

            # Preparar dados
            area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
            autor_dados = {
                'nome': sm.nome_usuario or "Usuário",
                'cpf': "00000000000",
                'area_codigo': area_codigo,
                'area_nome': sm.area_selecionada['nome']
            }

            pipeline = BuscaAtividadePipeline()

            # Processar resposta e criar atividade
            resultado = pipeline._camada4_processar_resposta(
                descricao_atividade=mensagem,
                hierarquia_herdada=hierarquia_herdada,
                area_codigo=area_codigo,
                autor_dados=autor_dados
            )

            # Limpar flag
            sm.dados_coletados['aguardando_descricao_rag'] = False

            if resultado.get('sucesso'):
                # Salvar dados no estado
                ativ = resultado['atividade']
                sm.macro_selecionado = ativ['macroprocesso']
                sm.processo_selecionado = ativ['processo']
                sm.subprocesso_selecionado = ativ['subprocesso']
                sm.atividade_selecionada = ativ['atividade']
                sm.codigo_cap = resultado.get('cap', 'PROVISORIO')

                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_atividade',
                        'dados': {
                            'atividade': ativ,
                            'cap': resultado.get('cap'),
                            'origem': 'rag_nova_atividade',
                            'score': 1.0,
                            'pode_editar': True,
                            'tipo_cap': 'oficial_gerado_rag',
                            'mensagem': resultado.get('mensagem', '')
                        }
                    }
                }

                return "", sm, metadados_extra
            else:
                return "Desculpe, ocorreu um erro ao criar a atividade. Tente novamente.", sm

        # ============================================================================
        # NOVO PIPELINE DE BUSCA EM 5 CAMADAS (v3.0)
        # ============================================================================
        logger.info("="*80)
        logger.info("[PIPELINE] Usando NOVO PIPELINE de busca em 4 camadas (v4.0)")
        logger.info("="*80)

        try:
            from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline

            # Inicializar pipeline
            pipeline = BuscaAtividadePipeline()

            # Preparar dados do autor para rastreabilidade
            autor_dados = {
                'nome': autor_nome,
                'cpf': autor_cpf,
                'area_codigo': area_codigo,
                'area_nome': area_nome
            }

            # Executar pipeline
            resultado = pipeline.buscar_atividade(
                descricao_usuario=descricao_usuario,
                area_codigo=area_codigo,
                contexto=None,  # TODO: Adicionar contexto se necessário
                autor_dados=autor_dados
            )

            logger.info(f"[PIPELINE] Resultado: origem={resultado.get('origem')}, score={resultado.get('score', 0):.3f}")

            # ========================================================================
            # PROCESSAR RESULTADO DO PIPELINE
            # ========================================================================

            # CASO 1: Dropdown necessário (zona cinza: 0.70 <= score < 0.85)
            if resultado.get('origem') == 'dropdown_required':
                logger.info("[PIPELINE] Dropdown necessário - apresentando candidatos ao usuário")

                # TODO: Implementar interface de dropdown no frontend
                # Por enquanto, vamos aceitar o primeiro candidato automaticamente
                candidatos = resultado.get('candidatos', [])
                if candidatos:
                    melhor = candidatos[0]
                    sm.macro_selecionado = melhor['macroprocesso']
                    sm.processo_selecionado = melhor['processo']
                    sm.subprocesso_selecionado = melhor['subprocesso']
                    sm.atividade_selecionada = melhor['atividade']
                    sm.codigo_cap = melhor.get('numero', 'PROVISORIO')
                    sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                    resposta = (
                        f"Encontrei algumas opções similares. A que melhor se adequa é:\n\n"
                        f"📋 **Macroprocesso:** {melhor['macroprocesso']}\n"
                        f"📋 **Processo:** {melhor['processo']}\n"
                        f"📋 **Subprocesso:** {melhor['subprocesso']}\n"
                        f"📋 **Atividade:** {melhor['atividade']}\n"
                        f"🔢 **Código:** {melhor.get('numero', 'A definir')}\n\n"
                        f"*Similaridade: {melhor['score']*100:.1f}%*\n\n"
                        f"Está correto?"
                    )
                    return resposta, sm

            # CASO 2: Seleção manual hierárquica (Camada 3)
            if resultado.get('origem') == 'selecao_manual':
                logger.info("[HELENA POP] Enviando interface de seleção manual (dropdown 4 níveis)")

                metadados_extra = {
                    'interface': {
                        'tipo': 'selecao_manual_hierarquica',
                        'dados': {
                            'hierarquia': resultado.get('hierarquia', {}),
                            'acoes_usuario': resultado.get('acoes_usuario', ['confirmar', 'nao_encontrei']),
                            'mensagem': resultado.get('mensagem', ''),
                            'tipo_cap': resultado.get('tipo_cap', 'oficial')
                        }
                    }
                }

                resposta = None  # Modo interface: mensagem textual ausente por design
                return resposta, sm, metadados_extra

            # CASO 3: RAG aguardando descrição (Camada 4 - Parte 1)
            elif resultado.get('origem') == 'rag_aguardando_descricao':
                logger.info("[HELENA POP] RAG aguardando descrição do usuário")

                # Guardar hierarquia herdada no estado
                hierarquia = resultado.get('hierarquia_herdada', {})
                sm.macro_selecionado = hierarquia.get('macroprocesso')
                sm.processo_selecionado = hierarquia.get('processo')
                sm.subprocesso_selecionado = hierarquia.get('subprocesso')

                # Marcar que estamos aguardando descrição RAG
                sm.dados_coletados['aguardando_descricao_rag'] = True

                metadados_extra = {
                    'interface': {
                        'tipo': 'rag_pergunta_atividade',
                        'dados': {
                            'mensagem': resultado.get('mensagem', ''),
                            'hierarquia_herdada': hierarquia,
                            'instrucao': resultado.get('instrucao_frontend', '')
                        }
                    }
                }

                resposta = None  # Modo interface: mensagem textual ausente por design
                return resposta, sm, metadados_extra

            # CASO 4: Atividade encontrada via Camadas 1-2 (match/semantic)
            # Enviar interface visual com botões "Concordar" e "Selecionar manualmente"
            elif resultado.get('sucesso') and resultado.get('atividade'):
                ativ = resultado['atividade']
                origem = resultado.get('origem')

                # Para TODAS as origens que precisam de interface visual
                if origem in ['match_exato', 'match_fuzzy', 'semantic', 'rag_nova_atividade']:
                    logger.info(f"[HELENA POP] Enviando interface sugestao_atividade (origem: {origem})")

                    # Guardar dados no estado
                    sm.macro_selecionado = ativ['macroprocesso']
                    sm.processo_selecionado = ativ.get('processo', 'A definir')
                    sm.subprocesso_selecionado = ativ.get('subprocesso', 'A definir')
                    sm.atividade_selecionada = ativ['atividade']
                    sm.codigo_cap = resultado.get('cap', 'PROVISORIO')

                    # Preparar interface
                    metadados_extra = {
                        'interface': {
                            'tipo': 'sugestao_atividade',
                            'dados': {
                                'atividade': ativ,
                                'cap': resultado.get('cap'),
                                'origem': origem,
                                'score': resultado.get('score', 1.0),
                                'pode_editar': resultado.get('pode_editar', False),
                                'tipo_cap': resultado.get('tipo_cap', 'csv_oficial'),
                                'acoes_usuario': resultado.get('acoes_usuario', ['confirmar', 'selecionar_manualmente']),
                                'mensagem': resultado.get('mensagem', '')
                            }
                        }
                    }

                    resposta = None  # Modo interface: mensagem textual ausente por design
                    return resposta, sm, metadados_extra

                # Fallback para formato texto (não deveria chegar aqui)
                else:
                    sm.macro_selecionado = ativ['macroprocesso']
                    sm.processo_selecionado = ativ.get('processo', 'A definir')
                    sm.subprocesso_selecionado = ativ.get('subprocesso', 'A definir')
                    sm.atividade_selecionada = ativ['atividade']
                    sm.codigo_cap = resultado.get('cap', 'PROVISORIO')
                    sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                    origem_label = {
                        'match_exato': 'correspondência exata no catálogo oficial',
                        'match_fuzzy': 'correspondência fuzzy no catálogo oficial',
                        'semantic': 'busca semântica no catálogo',
                        'rag': 'análise contextual da Helena',
                        'rag_nova_atividade': 'nova atividade criada pela Helena',
                        'nova': 'nova atividade candidata'
                    }.get(origem, 'busca automática')

                    resposta = (
                        f"✅ Perfeito! Identifiquei sua atividade via **{origem_label}**:\n\n"
                        f"📋 **Macroprocesso:** {ativ['macroprocesso']}\n"
                        f"📋 **Processo:** {ativ.get('processo', 'A definir')}\n"
                        f"📋 **Subprocesso:** {ativ.get('subprocesso', 'A definir')}\n"
                        f"📋 **Atividade:** {ativ['atividade']}\n"
                        f"🔢 **CAP:** {resultado.get('cap', 'A definir')}\n\n"
                    )

                    if origem in ['nova', 'rag_nova_atividade']:
                        resposta += (
                            f"⚠️ **Atenção:** Esta é uma nova atividade que não está no catálogo oficial.\n"
                            f"Ela será marcada como **candidata** para revisão posterior.\n\n"
                        )
                    elif resultado.get('score', 0) < 1.0:
                        resposta += f"*Confiança: {resultado['score']*100:.1f}%*\n\n"

                    resposta += "Está correto?"

                    return resposta, sm

            # CASO 3: Erro no pipeline - fallback para método antigo
            logger.warning("[PIPELINE] Pipeline retornou erro - usando fallback")

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao executar pipeline: {e}")
            logger.info("[PIPELINE] Fallback para método antigo (sklearn)")

        # ============================================================================
        # FALLBACK: MÉTODO ANTIGO (sklearn/TF-IDF) - MANTIDO COMO SEGURANÇA
        # ============================================================================
        logger.info("="*80)
        logger.info("🧩 [helena_pop.py] FALLBACK - Método de busca por SIMILARIDADE VETORIAL (sklearn)")
        logger.info("="*80)
        logger.info(f"🔍 Termo recebido: '{descricao_usuario}'")
        logger.info(f"   - Length: {len(descricao_usuario)}")
        logger.info(f"   - Type: {type(descricao_usuario)}")
        logger.info(f"   - Área código: {area_codigo}")

        try:
            print("[DEBUG] Tentando importar sklearn...")
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            print("[DEBUG] sklearn importado com sucesso!")
            logger.info("✅ sklearn importado com sucesso")

            # Preparar textos do CSV
            print("[DEBUG] Carregando CSV da arquitetura...")
            logger.info("📂 Carregando CSV da arquitetura...")
            df_csv = self.arquitetura.df
            print(f"[DEBUG] CSV carregado! Linhas: {len(df_csv)}")
            logger.info(f"📊 CSV carregado! Total de linhas: {len(df_csv)}")
            logger.info(f"📋 Colunas do CSV: {df_csv.columns.tolist()}")
            logger.info(f"📝 Primeiras 3 linhas:\n{df_csv.head(3)}")

            if df_csv.empty:
                raise ValueError("CSV vazio")

            # Criar corpus de textos do CSV
            textos_csv = []
            for idx, row in df_csv.iterrows():
                texto_completo = f"{row['Macroprocesso']} {row['Processo']} {row['Subprocesso']} {row['Atividade']}"
                textos_csv.append(texto_completo.lower().strip())
                if idx < 3:
                    logger.info(f"   Corpus[{idx}]: '{texto_completo[:100]}...'")

            # Adicionar descrição do usuário
            todos_textos = textos_csv + [descricao_usuario.lower().strip()]
            logger.info(f"🧠 Número de entradas no corpus: {len(todos_textos)} (incluindo termo do usuário)")
            logger.info(f"🔍 Termo normalizado: '{descricao_usuario.lower().strip()}'")

            # TF-IDF + Cosine Similarity
            logger.info("🔢 Vetorizando corpus com TF-IDF...")
            vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=1, max_df=0.95)
            tfidf_matrix = vectorizer.fit_transform(todos_textos)
            logger.info(f"📊 Vetor de embeddings: shape={tfidf_matrix.shape}")

            # Calcular similaridade da descrição do usuário com todas as linhas do CSV
            logger.info("🎯 Calculando similaridade cosine...")
            similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

            # Encontrar match com maior score
            idx_melhor = similarities.argmax()
            score_melhor = float(similarities[idx_melhor])

            logger.info(f"[GOVERNANÇA] Melhor match no CSV: score={score_melhor:.3f} | idx={idx_melhor}")
            if idx_melhor < len(df_csv):
                row_match = df_csv.iloc[idx_melhor]
                logger.info(f"   Match encontrado:")
                logger.info(f"      Macro: {row_match['Macroprocesso']}")
                logger.info(f"      Processo: {row_match['Processo']}")
                logger.info(f"      Subprocesso: {row_match['Subprocesso']}")
                logger.info(f"      Atividade: {row_match['Atividade']}")
            logger.info("="*80)

            # ============================================================================
            # SE SCORE >= 0.85 → MATCH EXATO OU FUZZY (usar atividade do CSV)
            # ============================================================================
            if score_melhor >= 0.85:
                row_match = df_csv.iloc[idx_melhor]

                # Salvar no state machine
                sm.macro_selecionado = row_match['Macroprocesso']
                sm.processo_selecionado = row_match['Processo']
                sm.subprocesso_selecionado = row_match['Subprocesso']
                sm.atividade_selecionada = row_match['Atividade']
                sm.dados_coletados['macroprocesso'] = row_match['Macroprocesso']
                sm.dados_coletados['processo'] = row_match['Processo']
                sm.dados_coletados['subprocesso'] = row_match['Subprocesso']
                sm.dados_coletados['atividade'] = row_match['Atividade']
                sm.dados_coletados['nome_processo'] = row_match['Atividade']

                # Gerar CAP baseado no CSV
                if not sm.codigo_cap:
                    sm.codigo_cap = self._gerar_codigo_processo(sm)
                    logger.info(f"[GOVERNANÇA] CAP gerado (match CSV): {sm.codigo_cap}")

                # Tentar sugerir entrega esperada via IA
                try:
                    from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

                    contexto = {
                        'area': area_nome,
                        'area_codigo': area_codigo,
                        'macroprocesso': sm.macro_selecionado,
                        'processo': sm.processo_selecionado,
                        'subprocesso': sm.subprocesso_selecionado,
                        'atividade': sm.atividade_selecionada
                    }

                    resultado = analisar_atividade_com_helena(
                        descricao_usuario=descricao_usuario,
                        nivel_atual='resultado_final',
                        contexto_ja_selecionado=contexto
                    )

                    if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                        sm.dados_coletados['entrega_esperada'] = resultado['sugestao']['resultado_final']
                        logger.info(f"[GOVERNANÇA] Entrega sugerida: {resultado['sugestao']['resultado_final']}")

                except Exception as e:
                    logger.warning(f"[GOVERNANÇA] Não foi possível sugerir entrega: {e}")

                # Ir para confirmação
                sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                tipo_match = "exata" if score_melhor >= 0.95 else "similar"
                emoji = "🎯" if score_melhor >= 0.95 else "🤔"

                resposta = (
                    f"{emoji} Encontrei uma correspondência {tipo_match} no meu catálogo oficial (confiança: {score_melhor:.0%}):\n\n"
                    f"**Arquitetura:**\n"
                    f"**CAP (Código na Arquitetura de Processos):** {sm.codigo_cap}\n\n"
                    f"Baseada em:\n"
                    f"• Área: {area_nome}\n"
                    f"• Macroprocesso: {row_match['Macroprocesso']}\n"
                    f"• Processo: {row_match['Processo']}\n"
                    f"• Subprocesso: {row_match['Subprocesso']}\n"
                    f"• Atividade: {row_match['Atividade']}\n\n"
                )

                if sm.dados_coletados.get('entrega_esperada'):
                    resposta += f"**Entrega Final (sugestão):**\n• {sm.dados_coletados['entrega_esperada']}\n\n"

                resposta += (
                    f"✅ Esta atividade eu já **mapeei no meu catálogo oficial da DECIPEX**.\n\n"
                    f"Se você concordar, digite 'sim' para continuar.\n"
                    f"Se quiser ajustar algo, digite 'ajustar'."
                )

                logger.info(f"[GOVERNANÇA] Match encontrado no CSV (origem: match_fuzzy | score: {score_melhor:.3f})")

                return resposta, sm

        except ImportError as e:
            print(f"\n{'🔴'*40}")
            print(f"[ERRO] SKLEARN NÃO INSTALADO!")
            print(f"   Erro: {e}")
            print(f"   Solução: pip install scikit-learn")
            print(f"{'🔴'*40}\n")
            logger.error(f"[GOVERNANÇA] sklearn não instalado: {e}")
            # Ir direto para fallback (dropdowns)
            sm.estado = EstadoPOP.SELECAO_HIERARQUICA
            sm.dados_coletados['descricao_original'] = descricao_usuario
            resposta = (
                "⚠️ Sistema de busca temporariamente indisponível.\n\n"
                "Por favor, use os **dropdowns hierárquicos** abaixo para selecionar:\n"
                "📋 Macroprocesso → Processo → Subprocesso → Atividade"
            )
            return resposta, sm

        except Exception as e:
            print(f"\n{'🔴'*40}")
            print(f"[ERRO] EXCEÇÃO NA BUSCA NO CSV")
            print(f"   Erro: {e}")
            print(f"   Tipo: {type(e).__name__}")
            print(f"{'🔴'*40}\n")
            logger.error(f"[GOVERNANÇA] Erro na busca no CSV: {e}")
            import traceback
            traceback.print_exc()

        # ============================================================================
        # NÍVEL 2: SCORE < 0.85 → IA SUGERE NOVA ATIVIDADE
        # ============================================================================
        logger.info(f"[GOVERNANÇA] Score < 0.85, atividade NÃO encontrada no catálogo oficial. Sugerindo nova atividade...")

        try:
            from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

            contexto = {
                'area': area_nome,
                'area_codigo': area_codigo
            }

            # Chamar IA para sugerir arquitetura completa
            resultado = analisar_atividade_com_helena(
                descricao_usuario=descricao_usuario,
                nivel_atual='completo',
                contexto_ja_selecionado=contexto
            )

            if not resultado.get('sucesso'):
                raise ValueError("IA não conseguiu sugerir arquitetura")

            sugestao = resultado['sugestao']

            # Validar sugestão
            campos_obrigatorios = ['macroprocesso', 'processo', 'subprocesso', 'atividade', 'resultado_final']
            if not all(campo in sugestao for campo in campos_obrigatorios):
                raise ValueError("Sugestão incompleta da IA")

            # Detectar atividades similares já sugeridas (anti-duplicata)
            max_score, lista_similares = detectar_atividades_similares(
                macroprocesso=sugestao['macroprocesso'],
                processo=sugestao['processo'],
                subprocesso=sugestao['subprocesso'],
                atividade=sugestao['atividade'],
                threshold=0.80
            )

            # Gerar CAP provisório com lock transacional
            cap_provisorio = gerar_cap_provisorio_seguro(
                area_codigo=area_codigo,
                macroprocesso=sugestao['macroprocesso'],
                processo=sugestao['processo'],
                subprocesso=sugestao['subprocesso'],
                atividade=sugestao['atividade'],
                hierarquia_df=self.arquitetura.df
            )

            # Salvar atividade sugerida no banco com rastreabilidade completa
            atividade_obj = salvar_atividade_sugerida(
                cap_provisorio=cap_provisorio,
                area_codigo=area_codigo,
                macroprocesso=sugestao['macroprocesso'],
                processo=sugestao['processo'],
                subprocesso=sugestao['subprocesso'],
                atividade=sugestao['atividade'],
                entrega_esperada=sugestao['resultado_final'],
                autor_cpf=autor_cpf,
                autor_nome=autor_nome,
                autor_area=area_codigo,
                descricao_original=descricao_usuario,
                score_similaridade=max_score,
                sugestoes_similares=lista_similares,
                scores_similares_todos=[max_score],  # TODO: Salvar todos os scores
                origem_fluxo='nova_atividade_ia',
                interacao_id=f"chat_{sm.nome_usuario}_{area_codigo}"  # TODO: Usar ID real da mensagem
            )

            # Salvar no state machine
            sm.macro_selecionado = sugestao['macroprocesso']
            sm.processo_selecionado = sugestao['processo']
            sm.subprocesso_selecionado = sugestao['subprocesso']
            sm.atividade_selecionada = sugestao['atividade']
            sm.dados_coletados['macroprocesso'] = sugestao['macroprocesso']
            sm.dados_coletados['processo'] = sugestao['processo']
            sm.dados_coletados['subprocesso'] = sugestao['subprocesso']
            sm.dados_coletados['atividade'] = sugestao['atividade']
            sm.dados_coletados['nome_processo'] = sugestao['atividade']
            sm.dados_coletados['entrega_esperada'] = sugestao['resultado_final']
            sm.codigo_cap = cap_provisorio

            # Ir para confirmação
            sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

            # Montar resposta com AVISO CLARO
            resposta = (
                f"⚠️ **NOVA ATIVIDADE SUGERIDA** ⚠️\n\n"
                f"Esta atividade **NÃO encontrei** nas 107 atividades que já mapeei no meu catálogo oficial da DECIPEX.\n\n"
                f"Por isso, sugeri uma **nova arquitetura** baseada na sua descrição:\n\n"
                f"**Arquitetura Sugerida:**\n"
                f"**CAP Provisório (Código na Arquitetura de Processos):** {cap_provisorio}\n\n"
                f"• Área: {area_nome}\n"
                f"• Macroprocesso: {sugestao['macroprocesso']}\n"
                f"• Processo: {sugestao['processo']}\n"
                f"• Subprocesso: {sugestao['subprocesso']}\n"
                f"• Atividade: {sugestao['atividade']}\n\n"
                f"**Entrega Final (minha sugestão):**\n"
                f"• {sugestao['resultado_final']}\n\n"
            )

            # Se houver atividades similares, alertar
            if lista_similares:
                resposta += (
                    f"⚠️ **ATENÇÃO:** Encontrei {len(lista_similares)} atividade(s) similar(es) já sugerida(s) por outros usuários:\n"
                )
                for sim in lista_similares[:3]:  # Mostrar top 3
                    resposta += f"  • {sim['cap']}: {sim['atividade'][:60]}... (similaridade: {sim['score']:.0%})\n"
                resposta += "\n"

            resposta += (
                f"📋 Vou enviar esta sugestão para **validação do gestor** antes de ela se tornar oficial.\n\n"
                f"💡 **Alternativa:** Se você preferir, digite 'dropdowns' para selecionar manualmente entre as 107 atividades que já mapeei.\n\n"
                f"Se concordar com a minha sugestão, digite 'sim' para continuar.\n"
                f"Se quiser ajustar algo, digite 'ajustar'."
            )

            logger.info(f"[GOVERNANÇA] Nova atividade sugerida: {cap_provisorio} (confiança: {atividade_obj.confianca})")

            return resposta, sm

        except Exception as e:
            print(f"\n{'🔴'*40}")
            print(f"[ERRO] EXCEÇÃO AO SUGERIR NOVA ATIVIDADE")
            print(f"   Erro: {e}")
            print(f"   Tipo: {type(e).__name__}")
            print(f"{'🔴'*40}\n")
            logger.error(f"[GOVERNANÇA] Erro ao sugerir nova atividade: {e}")
            import traceback
            traceback.print_exc()
            # Não deixar o servidor travar - ir para fallback
            sm.estado = EstadoPOP.SELECAO_HIERARQUICA
            sm.dados_coletados['descricao_original'] = descricao_usuario
            resposta = (
                "⚠️ Não consegui processar sua descrição automaticamente.\n\n"
                "Sem problemas! Use os **dropdowns hierárquicos** abaixo:\n"
                "📋 Macroprocesso → Processo → Subprocesso → Atividade"
            )
            return resposta, sm

        # ============================================================================
        # FALLBACK: SELEÇÃO MANUAL VIA DROPDOWNS HIERÁRQUICOS
        # ============================================================================
        sm.estado = EstadoPOP.SELECAO_HIERARQUICA
        sm.dados_coletados['descricao_original'] = descricao_usuario

        resposta = (
            "Entendi! Não consegui mapear automaticamente sua descrição.\n\n"
            "Sem problemas! Abaixo você encontrará os **dropdowns hierárquicos** com todas as "
            "**107 atividades mapeadas** da DECIPEX organizadas por:\n\n"
            "📋 Macroprocesso → Processo → Subprocesso → Atividade\n\n"
            "É só ir selecionando cada nível que os próximos aparecem automaticamente. "
            "Encontre onde seu trabalho se encaixa! 🎯"
        )

        logger.info(f"[GOVERNANÇA] Fallback para seleção manual (dropdowns)")

        return resposta, sm

    def _processar_confirmacao_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        PASSO 2: Processa confirmação da arquitetura sugerida pela IA

        Mostra 2 botões:
        - Concordo com a sugestão ✅
        - Quero editar manualmente ✏️
        """
        msg_lower = mensagem.lower().strip()

        # Se confirmar → ir para ENTREGA ESPERADA com sugestão da IA
        if any(palavra in msg_lower for palavra in ['sim', 'concordo', 'confirmar', 'correto', 'ok', 'certo']):
            # 🐛 DEBUG: Verificar se dados da arquitetura estão salvos
            logger.info(f"[DEBUG] CONFIRMACAO ARQUITETURA:")
            logger.info(f"  - CAP: {sm.codigo_cap}")
            logger.info(f"  - Macro: {sm.macro_selecionado}")
            logger.info(f"  - Processo: {sm.processo_selecionado}")
            logger.info(f"  - Subprocesso: {sm.subprocesso_selecionado}")
            logger.info(f"  - Atividade: {sm.atividade_selecionada}")
            logger.info(f"  - dados_coletados: {sm.dados_coletados}")

            # Sugerir entrega esperada usando Helena Ajuda Inteligente
            try:
                from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

                # Obter contexto da área
                if sm.subarea_selecionada:
                    area_nome = sm.subarea_selecionada.get('nome_completo', sm.subarea_selecionada.get('nome', ''))
                    area_codigo = sm.subarea_selecionada.get('codigo', '')
                elif sm.area_selecionada:
                    area_nome = sm.area_selecionada.get('nome', '')
                    area_codigo = sm.area_selecionada.get('codigo', '')
                else:
                    area_nome = 'DECIPEX'
                    area_codigo = 'DECIPEX'

                contexto = {
                    'area': area_nome,
                    'area_codigo': area_codigo,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada
                }

                # Chamar Helena Ajuda Inteligente para sugerir entrega
                descricao_original = sm.dados_coletados.get('descricao_original', sm.atividade_selecionada)
                resultado = analisar_atividade_com_helena(
                    descricao_usuario=descricao_original,
                    nivel_atual='resultado_final',  # Apenas sugerir entrega
                    contexto_ja_selecionado=contexto
                )

                sugestao_entrega = None
                if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                    sugestao_entrega = resultado['sugestao']['resultado_final']
                    sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                    logger.info(f"[ENTREGA] Sugestão da IA: {sugestao_entrega}")

            except Exception as e:
                logger.error(f"[ENTREGA] Erro ao sugerir entrega: {e}")
                sugestao_entrega = None

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:
                # Salvar sugestão temporariamente para uso posterior
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

                # Enviar interface com sugestão e botões
                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }
                resposta = None  # Modo interface
                return resposta, sm, metadados_extra
            else:
                resposta = (
                    f"Perfeito! Agora me conta: qual é a **entrega esperada** dessa atividade?\n\n"
                    f"Exemplo: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
                )
                return resposta, sm

        # Se quiser editar → voltar para ENTREGA ESPERADA (arquitetura já está definida)
        elif any(palavra in msg_lower for palavra in ['editar', 'ajustar', 'mudar', 'alterar', 'manual']):
            # ✅ FIX: Não perguntar nome do processo novamente, só editar entrega
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA
            resposta = (
                "Sem problemas! A arquitetura está confirmada.\n\n"
                "Agora, qual é a entrega esperada desta atividade?\n\n"
                "Ex: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
            )
            return resposta, sm

        # Se não entendeu → reperguntar
        else:
            resposta = (
                "Desculpe, não entendi sua resposta.\n\n"
                "Por favor, escolha uma das opções:\n"
                "• Digite 'sim' ou clique em 'Concordo' se a classificação está correta\n"
                "• Digite 'editar' ou clique em 'Quero editar' se deseja ajustar manualmente"
            )
            return resposta, sm

    def _processar_selecao_hierarquica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        🆕 Processa seleção manual via dropdowns hierárquicos (fallback quando IA falha).

        Espera JSON com: {"macro": "...", "processo": "...", "subprocesso": "...", "atividade": "..."}
        """
        import json

        try:
            # Parse da seleção vinda do frontend
            selecao = json.loads(mensagem)

            # Validar campos obrigatórios
            campos_obrigatorios = ['macroprocesso', 'processo', 'subprocesso', 'atividade']
            if not all(campo in selecao for campo in campos_obrigatorios):
                raise ValueError("Seleção incompleta")

            # Salvar no state machine
            sm.macro_selecionado = selecao['macroprocesso']
            sm.processo_selecionado = selecao['processo']
            sm.subprocesso_selecionado = selecao['subprocesso']
            sm.atividade_selecionada = selecao['atividade']

            # Salvar em dados_coletados
            sm.dados_coletados['macroprocesso'] = selecao['macroprocesso']
            sm.dados_coletados['processo'] = selecao['processo']
            sm.dados_coletados['subprocesso'] = selecao['subprocesso']
            sm.dados_coletados['atividade'] = selecao['atividade']
            sm.dados_coletados['nome_processo'] = selecao['atividade']

            # Gerar código CAP baseado na arquitetura selecionada
            if not sm.codigo_cap:
                sm.codigo_cap = self._gerar_codigo_processo(sm)
                logger.info(f"[CAP] Codigo gerado (selecao manual): {sm.codigo_cap}")

            # 🎯 SUGERIR ENTREGA ESPERADA usando IA baseado na seleção + descrição original
            descricao_original = sm.dados_coletados.get('descricao_original', '')

            try:
                from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

                # Obter nome e código da área (considerando subárea se existir)
                if sm.subarea_selecionada:
                    area_nome = sm.subarea_selecionada.get('nome_completo', sm.subarea_selecionada.get('nome', ''))
                    area_codigo = sm.subarea_selecionada.get('codigo', '')
                elif sm.area_selecionada:
                    area_nome = sm.area_selecionada.get('nome', '')
                    area_codigo = sm.area_selecionada.get('codigo', '')
                else:
                    area_nome = 'DECIPEX'
                    area_codigo = 'DECIPEX'

                contexto = {
                    'area': area_nome,
                    'area_codigo': area_codigo,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada
                }

                # Tentar sugerir entrega esperada
                resultado = analisar_atividade_com_helena(
                    descricao_usuario=descricao_original or sm.atividade_selecionada,
                    nivel_atual='resultado_final',  # Apenas sugerir entrega
                    contexto_ja_selecionado=contexto
                )

                sugestao_entrega = None
                if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                    sugestao_entrega = resultado['sugestao']['resultado_final']
                    logger.info(f"[IA] Sugestao de entrega esperada: {sugestao_entrega}")

            except Exception as e:
                logger.warning(f"Não foi possível sugerir entrega esperada com IA: {e}")
                sugestao_entrega = None

            # Ir direto para ENTREGA_ESPERADA (pular confirmação de arquitetura)
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:
                # Se a IA conseguiu sugerir, mostrar sugestão
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade.\n\n"
                    f"Baseado na atividade **'{sm.atividade_selecionada}'**, sugiro:\n\n"
                    f"**Entrega esperada:** {sugestao_entrega}\n\n"
                    f"Essa sugestão está adequada? Digite 'sim' para confirmar ou escreva a entrega correta."
                )
            else:
                # Se não conseguiu sugerir, perguntar diretamente
                resposta = (
                    f"Perfeito! Agora me diga:\n\n"
                    f"Qual é a **entrega esperada** da atividade **'{sm.atividade_selecionada}'**?\n\n"
                    f"Exemplo: 'Demanda de controle respondida', 'Solicitação analisada e decidida', 'Relatório elaborado'"
                )

            return resposta, sm

        except json.JSONDecodeError:
            # Se não for JSON, pode ser resposta textual do usuário
            resposta = (
                "Por favor, selecione a arquitetura usando os dropdowns acima. "
                "É só ir escolhendo: Macroprocesso → Processo → Subprocesso → Atividade 📋"
            )
            return resposta, sm

        except Exception as e:
            logger.error(f"Erro ao processar seleção hierárquica: {e}")
            resposta = (
                "Desculpe, houve um erro ao processar sua seleção. "
                "Por favor, tente novamente selecionando os campos dos dropdowns."
            )
            return resposta, sm

    def _processar_nome_processo(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta do nome do processo"""
        sm.dados_coletados['nome_processo'] = mensagem.strip()
        sm.estado = EstadoPOP.ENTREGA_ESPERADA

        resposta = (
            f"Perfeito! Vamos mapear: '{sm.dados_coletados['nome_processo']}'\n\n"
            "Agora me diga: qual é o resultado final desta atividade?\n\n"
            "Ex: 'Auxílio concedido', 'Requerimento analisado e decidido', 'Cadastro atualizado'"
        )
        return resposta, sm

    def _processar_entrega_esperada(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta da entrega esperada e mostra confirmação com botões"""
        msg_lower = mensagem.lower().strip()

        # Se o usuário clicou "Concordo com a sugestão"
        if msg_lower == 'concordar':
            # Pegar a sugestão que foi enviada pela interface
            entrega_sugerida = sm.dados_coletados.get('entrega_sugerida_temp', mensagem.strip())
            sm.dados_coletados['entrega_esperada'] = entrega_sugerida
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA
        # Se o usuário clicou "Quero editar manualmente"
        elif msg_lower == 'editar_manual':
            sm.estado = EstadoPOP.ENTREGA_ESPERADA
            resposta = (
                "Sem problemas! Qual é a **entrega esperada** dessa atividade?\n\n"
                "Exemplo: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
            )
            return resposta, sm
        # Se o usuário digitou uma entrega manualmente
        else:
            sm.dados_coletados['entrega_esperada'] = mensagem.strip()
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA

        # Gerar código CAP antecipadamente
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Mostrar resumo completo com BOTÕES CONFIRMAR/EDITAR
        nome = sm.nome_usuario or "você"

        # Obter nome e código da área (considerando subárea se existir)
        if sm.subarea_selecionada:
            area_display = f"{sm.subarea_selecionada.get('nome_completo', '')} ({sm.subarea_selecionada.get('codigo', '')})"
        elif sm.area_selecionada:
            area_display = f"{sm.area_selecionada.get('nome', '')} ({sm.area_selecionada.get('codigo', '')})"
        else:
            area_display = "DECIPEX"

        # Pegar a entrega que foi salva (não a mensagem raw que pode ser "concordar")
        entrega_final = sm.dados_coletados.get('entrega_esperada', mensagem.strip())

        resposta = (
            f"## 📋 **RESUMO DA ARQUITETURA E ENTREGA**\n\n"
            f"**Código CAP (CPF do Processo):** {sm.codigo_cap}\n\n"
            f"**Área:** {area_display}\n\n"
            f"**Arquitetura:**\n"
            f"• Macroprocesso: {sm.macro_selecionado}\n"
            f"• Processo: {sm.processo_selecionado}\n"
            f"• Subprocesso: {sm.subprocesso_selecionado}\n"
            f"• Atividade: {sm.atividade_selecionada}\n\n"
            f"**Entrega Final:**\n"
            f"• {entrega_final}\n\n"
            f"**Está correto, {nome}?**"
        )

        # Interface com botões Confirmar/Editar
        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Confirmar ✅',
            'botao_editar': 'Editar ✏️',
            'valor_confirmar': 'CONFIRMAR',
            'valor_editar': 'EDITAR'
        }

        return resposta, sm

    def _processar_confirmacao_entrega(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação ou edição da entrega"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['edit', 'corrigir', 'alterar', 'mudar']):
            # Volta para entrega_esperada
            sm.estado = EstadoPOP.ENTREGA_ESPERADA
            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = (
                "Ok! Vamos corrigir a entrega esperada.\n\n"
                "Qual é a **entrega final** (resultado) desta atividade?\n\n"
                "Ex: 'Auxílio concedido', 'Processo arquivado', 'Reposição ao Erário Efetuada'"
            )
            return resposta, sm

        # Confirmar - IR DIRETO PARA SISTEMAS (nova ordem)
        sm.estado = EstadoPOP.SISTEMAS
        sm.tipo_interface = 'sistemas'
        sm.dados_interface = {
            'sistemas_por_categoria': self.SISTEMAS_DECIPEX,
            'campo_livre': True,
            'multipla_selecao': True
        }

        nome = sm.nome_usuario or "você"

        resposta = (
            f"Perfeito, {nome}! Entrega confirmada.\n\n"
            f"Agora me diga: quais sistemas você utiliza nesta atividade?"
        )

        return resposta, sm

    def _processar_reconhecimento_entrega(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa clique na caixinha de reconhecimento e avança para FLUXOS"""
        sm.estado = EstadoPOP.FLUXOS
        logger.info(f"[RECONHECIMENTO] Mudou estado para FLUXOS (pergunta aberta)")

        # ✅ SIMPLIFICADO: Pergunta aberta em vez de interface complexa
        sm.tipo_interface = "texto_livre"
        sm.dados_interface = {
            "placeholder": (
                "Ex.: Cidadão via SEI, Outras áreas da DECIPEX, Órgãos externos, "
                "Sistemas automáticos, Email, Telefone..."
            )
        }

        nome = sm.nome_usuario or "você"
        resposta = (
            f"Agora me diga: **de onde vem o processo** que você executa?\n\n"
            f"Pode ser de outras áreas, de cidadãos, de sistemas, de órgãos externos...\n\n"
            f"💡 Descreva livremente!"
        )

        logger.info(f"[RECONHECIMENTO] Retornando interface texto_livre para fluxos_entrada")
        return resposta, sm

    def _processar_dispositivos_normativos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de dispositivos normativos e vai para reconhecimento"""
        # Separar por vírgula ou quebra de linha (ou aceitar JSON de seleção)
        try:
            import json as json_lib
            dados = json_lib.loads(mensagem)
            if isinstance(dados, list):
                normas = dados
            else:
                normas = [mensagem.strip()]
        except:
            normas = [n.strip() for n in mensagem.replace('\n', ',').split(',') if n.strip()]

        sm.dados_coletados['dispositivos_normativos'] = normas

        # 🎯 Mudar estado para TRANSICAO_ROADTRIP
        sm.estado = EstadoPOP.TRANSICAO_ROADTRIP

        # 🔥 FIX: Limpar tipo_interface antigo (evita fallback para interface de normas)
        sm.tipo_interface = None
        sm.dados_interface = None

        logger.info(f"🚗 [ROADTRIP] Estado mudado para TRANSICAO_ROADTRIP. Interface será mostrada junto com a mensagem.")

        nome = sm.nome_usuario or "você"
        resposta = (
            f"👏 Perfeito, {nome}!\n\n"
            f"As normas são como as placas da estrada: mostram a direção certa pra sua atividade seguir segura e consistente. 🚦"
        )

        # ✅ Interface roadtrip será adicionada automaticamente no bloco de PROXIMA_INTERFACE
        # Não precisa de auto_continue!
        return resposta, sm

    def _processar_transicao_roadtrip(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa estado de transição roadtrip.

        Qualquer clique/mensagem avança para OPERADORES.
        """
        nome = sm.nome_usuario or "você"

        # 🎯 Avançar para operadores
        sm.estado = EstadoPOP.OPERADORES

        logger.info(f"👥 [ROADTRIP→OPERADORES] Clique no carro detectado! Indo para estado OPERADORES!")

        resposta = (
            f"Agora que você já está ligado na sinalização, vamos falar sobre os motoristas dessa jornada: "
            f"as pessoas que fazem essa atividade acontecer no dia a dia.\n\n"
            f"Por favor, **selecione abaixo quem executa diretamente, quem revisa, quem apoia… "
            f"e também quem prepara o terreno antes que o processo chegue até você.**\n\n"
            f"💡 Ei!!! Você faz parte!\n"
            f"Lembre de se incluir também!\n\n"
            f"As opções estão logo abaixo, mas se eu esqueci alguém pode digitar."
        )

        return resposta, sm

    def _processar_operadores(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de operadores com fuzzy matching"""
        logger.info(f"[OPERADORES] Processando mensagem: {mensagem[:100]}")

        # Aceitar JSON (de interface) ou texto
        try:
            import json as json_lib
            dados = json_lib.loads(mensagem)
            if isinstance(dados, list):
                operadores = dados
                logger.info(f"[OPERADORES] Parsed JSON com sucesso: {operadores}")
            else:
                raise ValueError("Não é lista JSON, fazer parsing manual")
        except Exception as e:
            # FUZZY PARSING de operadores
            logger.info(f"[OPERADORES] Caindo no fuzzy parsing (erro JSON: {e})")
            operadores = parse_operadores(mensagem, self.OPERADORES_DECIPEX)
            logger.info(f"[OPERADORES] Fuzzy parsing result: {operadores}")

        sm.dados_coletados['operadores'] = operadores

        # 🎯 GAMIFICAÇÃO: Ir para RECONHECIMENTO_ENTREGA antes de FLUXOS
        sm.estado = EstadoPOP.RECONHECIMENTO_ENTREGA
        logger.info(f"[OPERADORES] Salvou {len(operadores)} operadores, mudou estado para RECONHECIMENTO_ENTREGA (gamificação)")

        # ✅ Interface será definida automaticamente (caixinha_reconhecimento)
        # O carregamento de fluxos_entrada será feito em _processar_reconhecimento_entrega
        sm.tipo_interface = None  # Deixar None para usar interface padrão do estado
        sm.dados_interface = {}

        nome = sm.nome_usuario or "você"
        resposta = (
            f"🎉 **Eba! Você mapeou todos os operadores!**\n\n"
            f"Isso é um marco importante: agora temos clareza sobre **quem faz** essa atividade.\n\n"
            f"Continue assim! Cada passo que você dá fortalece a cultura de excelência na DECIPEX. 💪"
        )

        logger.info(f"[OPERADORES] Retornando RECONHECIMENTO_ENTREGA com caixinha")
        return resposta, sm

    def _processar_sistemas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa sistemas utilizados"""
        import json as json_lib

        # Parse: espera JSON array ["SIAPE", "SEI"] ou texto "nenhum"
        if mensagem.strip().lower() in ['nenhum', 'nao sei', 'não sei']:
            sistemas = []
        else:
            try:
                sistemas = json_lib.loads(mensagem)
                if not isinstance(sistemas, list):
                    sistemas = []
            except:
                sistemas = []

        # Salvar e avançar para DISPOSITIVOS_NORMATIVOS
        sm.dados_coletados['sistemas'] = sistemas
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        # Buscar sugestões de normas
        sugestoes = self._sugerir_base_legal_contextual(sm)
        grupos_normas = {}
        if self.suggestor_base_legal:
            try:
                grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
            except:
                pass

        # Interface de normas
        sm.tipo_interface = 'normas'
        sm.dados_interface = {
            'sugestoes': sugestoes,
            'grupos': grupos_normas,
            'campo_livre': True,
            'multipla_selecao': True,
            'texto_introducao': (
                f"Registrei {len(sistemas)} sistema(s).\n\n"
                f"Agora vamos falar sobre as normas legais e guias que orientam essa atividade."
            )
        }

        nome = sm.nome_usuario or "você"
        resposta = (
            f"Agora vamos falar sobre as normas legais, normativos e guias que orientam essa atividade. ⚖️\n\n"
            f"Como nós temos MUITAS normas 😅, eu separei em 4 formas de organização pra {nome}.\n\n"
            f"Aqui abaixo, eu já separei as principais normas que levantei, da seguinte forma:"
        )

        return resposta, sm

    def _processar_fluxos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de fluxos (entrada e saída)"""
        msg_lower = mensagem.lower().strip()

        # Se ainda não coletou fluxos de entrada
        if not sm.dados_coletados.get('fluxos_entrada'):
            if msg_lower in ['nenhum', 'nao', 'não', 'nao_sei']:
                sm.dados_coletados['fluxos_entrada'] = []
            else:
                # Aceitar JSON estruturado (da InterfaceFluxosEntrada) ou texto simples
                try:
                    import json as json_lib
                    dados_json = json_lib.loads(mensagem)
                    if isinstance(dados_json, dict):
                        # Formato novo: JSON com origens_selecionadas e outras_origens
                        fluxos = []
                        for origem in dados_json.get('origens_selecionadas', []):
                            if isinstance(origem, dict):
                                tipo = origem.get('tipo', '')
                                espec = origem.get('especificacao', '')
                                area = origem.get('area_decipex', '')

                                # Montar descrição completa
                                if espec:
                                    fluxos.append(f"{tipo}: {espec}")
                                else:
                                    fluxos.append(tipo)
                            else:
                                fluxos.append(str(origem))

                        if dados_json.get('outras_origens'):
                            fluxos.append(dados_json['outras_origens'])

                        sm.dados_coletados['fluxos_entrada'] = fluxos
                    else:
                        # JSON mas não é dict, usar como lista
                        fluxos = dados_json if isinstance(dados_json, list) else [mensagem]
                        sm.dados_coletados['fluxos_entrada'] = fluxos
                except:
                    # Formato antigo: texto separado por |
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split('|') if f.strip()]
                    sm.dados_coletados['fluxos_entrada'] = fluxos

            # ✅ SIMPLIFICADO: Interface texto_livre para fluxos de SAÍDA
            sm.tipo_interface = 'texto_livre'
            sm.dados_interface = {
                'placeholder': (
                    "Ex.: Cidadão via SEI, Outras áreas da DECIPEX, Órgãos externos, "
                    "Sistemas automáticos, Email, Telefone..."
                )
            }

            resposta = (
                f"Perfeito! Registrei {len(sm.dados_coletados['fluxos_entrada'])} origem(ns) de entrada. ✅\n\n"
                f"Agora me diga: **para onde vai o resultado** dessa atividade?\n\n"
                f"Pode ser para outras áreas, para cidadãos, para sistemas, para órgãos externos...\n\n"
                f"💡 Descreva livremente!"
            )
        else:
            # Coletar fluxos de saída
            if msg_lower in ['nenhum', 'nao', 'não', 'nao_sei']:
                sm.dados_coletados['fluxos_saida'] = []
            else:
                # Aceitar JSON estruturado ou texto simples
                try:
                    import json as json_lib
                    dados_json = json_lib.loads(mensagem)
                    if isinstance(dados_json, dict):
                        # Formato novo: JSON com destinos_selecionados e outros_destinos
                        fluxos = []
                        for destino in dados_json.get('destinos_selecionados', []):
                            if isinstance(destino, dict):
                                label = destino.get('tipo', '')
                                espec = destino.get('especificacao', '')
                                if espec:
                                    fluxos.append(f"{label} ({espec})")
                                else:
                                    fluxos.append(label)
                            else:
                                fluxos.append(str(destino))

                        if dados_json.get('outros_destinos'):
                            fluxos.append(dados_json['outros_destinos'])
                    else:
                        # JSON mas não é dict, usar como lista
                        fluxos = dados_json if isinstance(dados_json, list) else [mensagem]
                except:
                    # Formato antigo: texto separado por vírgulas
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]

                sm.dados_coletados['fluxos_saida'] = fluxos

            # 🎯 NOVO FLUXO: Ir para TRANSICAO_EPICA após fluxos_saida
            sm.estado = EstadoPOP.TRANSICAO_EPICA
            logger.info(f"[FLUXOS] Salvou fluxos_saida, mudou estado para TRANSICAO_EPICA")

            # ✅ Limpar interface (será definida automaticamente para transicao_epica)
            sm.tipo_interface = None
            sm.dados_interface = {}

            nome = sm.nome_usuario or "você"

            resposta = (
                f"🎉 **Maravilha, {nome}!**\n\n"
                f"Você mapeou as origens e destinos dessa atividade. "
                f"Agora sabemos de onde vem e para onde vai o processo!\n\n"
                f"Isso é fundamental para entender o fluxo completo. 🌊"
            )

        return resposta, sm

    def _processar_pontos_atencao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pontos de atenção (ÚLTIMA PERGUNTA DO FLUXO)

        Após coletar, finaliza o mapeamento
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

        # Aceitar respostas negativas
        if msg_lower in ['não', 'nao', 'nenhum', 'não há', 'nao ha', 'não tem', 'nao tem', 'sem pontos', 'pular', 'skip']:
            sm.dados_coletados['pontos_atencao'] = "Não há pontos especiais de atenção."
        else:
            sm.dados_coletados['pontos_atencao'] = mensagem.strip()

        # 🎯 FINALIZAR: Agora PONTOS_ATENCAO é a última pergunta
        sm.concluido = True
        sm.estado = EstadoPOP.FINALIZADO
        logger.info(f"[PONTOS_ATENCAO] Finalizou mapeamento POP (última pergunta)")

        # Gerar código CAP se ainda não foi gerado
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Gerar resumo completo
        resumo = self._gerar_resumo_pop(sm)

        resposta = (
            f"🎉 **PARABÉNS, {nome}!**\n\n"
            f"Você concluiu o mapeamento da sua atividade! 🏆\n\n"
            f"{resumo}\n\n"
            f"Todos os dados foram salvos e você pode:\n"
            f"• Gerar o documento POP completo\n"
            f"• Criar fluxograma visual\n"
            f"• Exportar para outros formatos\n\n"
            f"Obrigada pela dedicação! 💛"
        )

        # Limpar interface
        sm.tipo_interface = None
        sm.dados_interface = {}

        return resposta, sm

    def _processar_revisao_pre_delegacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        REVISÃO 2 - Pré-delegação

        Permite editar 9 campos ou seguir para etapas
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

        # Se confirmar/seguir → TRANSICAO_EPICA
        if any(palavra in msg_lower for palavra in ['seguir', 'tudo certo', 'confirmar', 'ok', 'continuar', 'sim', 'vamos']):
            sm.estado = EstadoPOP.TRANSICAO_EPICA
            sm.tipo_interface = None
            sm.dados_interface = {}

            progresso = self.obter_progresso(sm)
            percentual = progresso['percentual']

            resposta = (
                f"## 🎯 **AGORA ENTRAMOS NO CORAÇÃO DO PROCESSO**\n\n"
                f"A próxima fase é a **mais importante e detalhada**: vamos mapear **CADA ETAPA** da sua atividade!\n\n"
                f"Para cada etapa, vou perguntar:\n"
                f"📝 O que você faz\n"
                f"👤 Quem executa\n"
                f"📚 Qual norma fundamenta\n"
                f"💻 Qual sistema utiliza\n"
                f"📄 Quais documentos usa/gera\n\n"
                f"**⏱️ Tempo estimado:** 15-20 minutos\n\n"
                f"**💡 Dica importante:**\n"
                f"Esta é a parte mais demorada, então que tal:\n"
                f"☕ Pegar um café ou água\n"
                f"🚶 Dar uma esticada nas pernas\n"
                f"🚽 Ir ao banheiro se precisar\n"
                f"📋 Ter em mãos exemplos reais do processo\n\n"
                f"Quando estiver pronto e confortável, digite **'VAMOS'** para começarmos! 🚀\n"
                f"Ou digite **'PAUSA'** se preferir continuar depois."
            )

            return resposta, sm

        # Se editar → SELECAO_EDICAO com 9 campos
        elif any(palavra in msg_lower for palavra in ['editar', 'edit', 'alterar', 'corrigir', 'mudar', 'arrumar']):
            sm.estado = EstadoPOP.SELECAO_EDICAO
            sm.tipo_interface = 'selecao_edicao'
            sm._voltou_de_revisao = True  # Flag para saber que veio da revisão

            # 9 CAMPOS EDITÁVEIS (CAP é imutável)
            campos_editaveis = {
                "1": {"campo": "entrega_esperada", "label": "Entrega Esperada"},
                "2": {"campo": "sistemas", "label": "Sistemas Utilizados"},
                "3": {"campo": "dispositivos_normativos", "label": "Dispositivos Normativos"},
                "4": {"campo": "operadores", "label": "Operadores"},
                "5": {"campo": "fluxos_entrada", "label": "Fluxos de Entrada"},
                "6": {"campo": "etapas", "label": "Tarefas/Etapas (será editado depois)"},
                "7": {"campo": "fluxos_saida", "label": "Fluxos de Saída"},
                "8": {"campo": "documentos", "label": "Documentos"},
                "9": {"campo": "pontos_atencao", "label": "Pontos de Atenção"}
            }

            sm.dados_interface = {
                'campos_editaveis': campos_editaveis
            }

            resumo = self._gerar_resumo_pop(sm)

            resposta = (
                f"## 🔧 **EDIÇÃO DE CAMPOS**\n\n"
                f"{resumo}\n\n"
                f"**Qual campo você gostaria de editar, {nome}?**\n\n"
                f"1️⃣ Entrega Esperada\n"
                f"2️⃣ Sistemas Utilizados\n"
                f"3️⃣ Dispositivos Normativos\n"
                f"4️⃣ Operadores\n"
                f"5️⃣ Fluxos de Entrada\n"
                f"6️⃣ Tarefas/Etapas (será editado depois no Helena Etapas)\n"
                f"7️⃣ Fluxos de Saída\n"
                f"8️⃣ Documentos\n"
                f"9️⃣ Pontos de Atenção\n\n"
                f"Digite o **número** do campo ou **'cancelar'** para voltar."
            )

            return resposta, sm

        else:
            # Não entendeu - repetir pergunta
            resposta = (
                f"Não entendi, {nome}.\n\n"
                f"Digite **'tudo certo'** para seguir ou **'editar'** para alterar algum campo."
            )
            return resposta, sm

    def _processar_transicao_epica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Estado de transição épica - Celebra conquistas e prepara para etapas detalhadas

        Inclui:
        - Troféu/badge de conquista animado
        - Mensagem motivacional humanizada
        - Dicas práticas de preparação (café, banheiro, etc.)
        - Estimativa de tempo realista
        - Opção de pausa com salvamento automático
        - Interface dinâmica com botões pulsantes
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario

        # Palavras que indicam continuidade (incluindo clique no botão)
        continuar_palavras = ['ok', 'continuar', 'sim', 'vamos', 'próximo', 'seguir', 'bora', 'vai',
                             'começar', 'pode ser', 'partiu', 'lets go', 'vamos começar']

        # Palavras que indicam pausa
        pausa_palavras = ['pausa', 'pausar', 'esperar', 'depois', 'mais tarde', 'aguardar', 'não', 'nao']

        if any(palavra in msg_lower for palavra in pausa_palavras):
            # Usuário quer pausar - mensagem humanizada com resumo
            resposta = (
                f"Sem problema, {nome}! 😊\n\n"
                "Entendo perfeitamente. Mapear processos requer concentração e tempo.\n\n"
                "**✅ Seus dados foram salvos** e você pode continuar quando quiser.\n\n"
                "📌 **Para retomar:** É só dizer 'continuar mapeamento'\n\n"
                "**Dicas para o mapeamento de etapas:**\n"
                "📝 Tenha exemplos reais do processo em mãos\n"
                "📋 Pense em todas as decisões e caminhos alternativos\n"
                "⏱️ Reserve 20-30 minutos sem interrupções\n"
                "☕ Esteja confortável e descansado\n\n"
                "Até breve! Estarei aqui quando você voltar. 👋"
            )
            # Não muda o estado, fica esperando
            return resposta, sm

        elif any(palavra in msg_lower for palavra in continuar_palavras):
            # 🎯 DELEGAR DIRETAMENTE: Mudar contexto para Helena Etapas sem passar por DELEGACAO_ETAPAS
            sm.concluido = True
            sm.estado = EstadoPOP.FINALIZADO
            logger.info(f"[TRANSICAO_EPICA] POP concluído, delegando diretamente para Helena Etapas")

            resposta = (
                f"🏆 **PRIMEIRA FASE CONCLUÍDA!** 🏆\n\n"
                f"{nome}, você está indo muito bem!\n\n"
                f"Agora vou te passar para a **Helena especializada em etapas** que vai te guiar no detalhamento operacional.\n\n"
                f"🔍 **Começando a mineração dos detalhes de cada etapa...** 🎯\n\n"
                f"Ela vai te fazer as perguntas necessárias para mapear tudo com precisão!"
            )

            # ✅ Sinalizar mudança de contexto para 'etapas'
            metadados_extra = {
                'mudar_contexto': 'etapas',
                'dados_herdados': {
                    'area': sm.area_selecionada,
                    'subarea': sm.subarea_selecionada,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada,
                    'codigo_cap': sm.codigo_cap,
                    'dados_coletados': sm.dados_coletados
                }
            }

            return resposta, sm, metadados_extra

        else:
            # Primeira visita ou mensagem não reconhecida - mostrar transição épica COMPLETA
            progresso = self.obter_progresso(sm)
            percentual = progresso['percentual']

            resposta = (
                f"## 🎯 **AGORA ENTRAMOS NO CORAÇÃO DO PROCESSO**\n\n"
                f"A próxima fase é a **mais importante e detalhada**: vamos mapear **CADA ETAPA** da sua atividade!\n\n"
                f"Para cada etapa, vou perguntar:\n"
                f"📝 O que você faz\n"
                f"👤 Quem executa\n"
                f"📚 Qual norma fundamenta\n"
                f"💻 Qual sistema utiliza\n"
                f"📄 Quais documentos usa/gera\n\n"
                f"**⏱️ Tempo estimado:** 15-20 minutos\n\n"
                f"**💡 Dica importante:**\n"
                f"Esta é a parte mais demorada, então que tal:\n"
                f"☕ Pegar um café ou água\n"
                f"🚶 Dar uma esticada nas pernas\n"
                f"🚽 Ir ao banheiro se precisar\n"
                f"📋 Ter em mãos exemplos reais do processo\n\n"
                f"Quando estiver pronto e confortável, digite **'VAMOS'** para começarmos! 🚀\n"
                f"Ou digite **'PAUSA'** se preferir continuar depois."
            )

            return resposta, sm

    def _processar_selecao_edicao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Sistema de Edição Granular - permite editar qualquer campo coletado

        Menu interativo com todas as opções editáveis numeradas.
        Usuário seleciona número e volta ao estado correspondente.
        """
        msg_lower = mensagem.lower().strip()

        # Verificar se é cancelamento
        if any(palavra in msg_lower for palavra in ['cancelar', 'voltar', 'sair', 'não']):
            # Verificar se veio da revisão
            if hasattr(sm, '_voltou_de_revisao') and sm._voltou_de_revisao:
                sm._voltou_de_revisao = False
                sm.estado = EstadoPOP.REVISAO_PRE_DELEGACAO
                return "Ok, voltando para revisão! Digite 'tudo certo' para seguir ou 'editar' para alterar outro campo.", sm
            else:
                sm.estado = EstadoPOP.TRANSICAO_EPICA
                return "Ok, voltando ao fluxo principal! Digite 'VAMOS' quando estiver pronto.", sm

        # Mapear opções de edição para estados
        opcoes_edicao = {
            '1': ('Nome do Processo', EstadoPOP.NOME_PROCESSO),
            '2': ('Entrega Esperada', EstadoPOP.ENTREGA_ESPERADA),
            '3': ('Dispositivos Normativos', EstadoPOP.DISPOSITIVOS_NORMATIVOS),
            '4': ('Operadores', EstadoPOP.OPERADORES),
            '5': ('Sistemas', EstadoPOP.SISTEMAS),
            '6': ('Fluxos Entrada/Saída', EstadoPOP.FLUXOS),
        }

        # Se primeira visita, mostrar menu
        if not hasattr(sm, '_primeira_edicao') or sm._primeira_edicao:
            sm._primeira_edicao = False

            resumo = self._gerar_resumo_pop(sm)

            resposta = (
                f"## 🔧 **EDIÇÃO GRANULAR DE CAMPOS**\n\n"
                f"{resumo}\n\n"
                f"**Qual campo deseja editar?**\n\n"
                f"1️⃣ Nome do Processo\n"
                f"2️⃣ Entrega Esperada\n"
                f"3️⃣ Dispositivos Normativos\n"
                f"4️⃣ Operadores\n"
                f"5️⃣ Sistemas\n"
                f"6️⃣ Documentos de Entrada\n"
                f"7️⃣ Documentos de Saída\n"
                f"8️⃣ Fluxos Entrada/Saída\n\n"
                f"Digite o **número** do campo que deseja editar, ou **'CANCELAR'** para voltar."
            )

            sm.tipo_interface = 'selecao_numero'
            sm.dados_interface = {
                'titulo': 'Selecione o campo para editar',
                'opcoes': list(opcoes_edicao.keys()),
                'labels': [v[0] for v in opcoes_edicao.values()]
            }

            return resposta, sm

        # Processar seleção
        escolha = mensagem.strip()

        if escolha in opcoes_edicao:
            campo_nome, novo_estado = opcoes_edicao[escolha]
            sm.estado = novo_estado

            resposta = f"✏️ Editando **{campo_nome}**...\n\nPor favor, forneça o novo valor:"
            return resposta, sm
        else:
            resposta = (
                "❌ Opção inválida!\n\n"
                "Por favor, digite um número de **1 a 8** ou **'CANCELAR'**."
            )
            return resposta, sm

    def _processar_delegacao_etapas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa delegação para Helena Etapas - MUDA CONTEXTO PARA ETAPAS"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['ok', 'continuar', 'sim', 'vamos', 'próximo']):
            # 🎯 DELEGAR: Mudar contexto para Helena Etapas
            sm.concluido = True
            sm.estado = EstadoPOP.FINALIZADO
            logger.info(f"[DELEGACAO_ETAPAS] POP concluído, delegando para Helena Etapas")

            nome = sm.nome_usuario or "você"
            resposta = (
                f"🎉 **Perfeito, {nome}!**\n\n"
                f"Os dados iniciais do processo foram coletados com sucesso.\n\n"
                f"Agora vou transferir você para o Helena Etapas para detalharmos cada etapa operacional.\n\n"
                f"**Iniciando Helena Etapas...** 🚀"
            )

            # ✅ Sinalizar mudança de contexto para 'etapas'
            metadados_extra = {
                'mudar_contexto': 'etapas',
                'dados_herdados': {
                    'area': sm.area_selecionada,
                    'subarea': sm.subarea_selecionada,
                    'macroprocesso': sm.macro_selecionado,
                    'processo': sm.processo_selecionado,
                    'subprocesso': sm.subprocesso_selecionado,
                    'atividade': sm.atividade_selecionada,
                    'codigo_cap': sm.codigo_cap,
                    'dados_coletados': sm.dados_coletados
                }
            }

            return resposta, sm, metadados_extra
        else:
            resposta = (
                "Não entendi. Digite 'ok' ou 'continuar' para prosseguir."
            )

        return resposta, sm

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _sugerir_base_legal_contextual(self, sm: POPStateMachine) -> list:
        """Sugere base legal baseada no contexto coletado (IA completa)"""
        try:
            if not self.suggestor_base_legal:
                return []

            # Montar contexto rico
            area_info = sm.area_selecionada or {}
            contexto = {
                "nome_processo": sm.dados_coletados.get("nome_processo", ""),
                "area_codigo": area_info.get("codigo", ""),
                "area_nome": area_info.get("nome", ""),
                "sistemas": sm.dados_coletados.get("sistemas", []),
                "objetivo": sm.dados_coletados.get("entrega_esperada", ""),
                "macroprocesso": sm.macro_selecionado or "",
                "processo": sm.processo_selecionado or "",
                "subprocesso": sm.subprocesso_selecionado or "",
                "atividade": sm.atividade_selecionada or ""
            }

            # Chamar BaseLegalSuggestorDECIPEx com contexto completo
            sugestoes = self.suggestor_base_legal.sugerir_base_legal(contexto)

            # Filtrar sugestões já usadas (anti-repetição)
            sugestoes_novas = []
            for sug in sugestoes:
                norma_id = sug.get('norma', '') if isinstance(sug, dict) else str(sug)
                if norma_id not in self._normas_sugeridas:
                    sugestoes_novas.append(sug)
                    self._normas_sugeridas.add(norma_id)

            # Retornar top 5 sugestões novas
            return sugestoes_novas[:5] if sugestoes_novas else []

        except Exception as e:
            logger.error(f"Erro ao sugerir base legal contextual: {e}")
            return []

    def _gerar_codigo_processo(self, sm: POPStateMachine) -> str:
        """Gera código CAP (Código na Arquitetura de Processos) automaticamente

        Formato: PREFIXO.MACRO.PROCESSO.SUBPROCESSO.ATIVIDADE
        Exemplo: 1.2.3.4.5 (CGBEN.2.3.4.5)

        Valida duplicatas e incrementa sufixos se necessário
        """
        area_info = sm.area_selecionada
        if not area_info:
            return "X.X.X.X.X"

        prefixo = area_info.get("prefixo", "X")

        try:
            # Tentar buscar código no CSV primeiro
            logger.info(f"[CAP] Buscando no CSV:")
            logger.info(f"  Macro: '{sm.macro_selecionado}'")
            logger.info(f"  Processo: '{sm.processo_selecionado}'")
            logger.info(f"  Subprocesso: '{sm.subprocesso_selecionado}'")
            logger.info(f"  Atividade: '{sm.atividade_selecionada}'")

            filtro = (
                (self.arquitetura.df['Macroprocesso'] == sm.macro_selecionado) &
                (self.arquitetura.df['Processo'] == sm.processo_selecionado) &
                (self.arquitetura.df['Subprocesso'] == sm.subprocesso_selecionado) &
                (self.arquitetura.df['Atividade'] == sm.atividade_selecionada)
            )
            linha = self.arquitetura.df[filtro]

            if 'Codigo' in self.arquitetura.df.columns and not linha.empty:
                codigo_csv = linha['Codigo'].iloc[0]
                logger.info(f"[CAP] Encontrado no CSV: {codigo_csv}")
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
            elif 'codigo' in self.arquitetura.df.columns and not linha.empty:
                codigo_csv = linha['codigo'].iloc[0]
                logger.info(f"[CAP] Encontrado no CSV: {codigo_csv}")
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
            else:
                logger.warning(f"⚠️ [CAP] NÃO encontrado no CSV com match exato. Gerando por índice.")
        except Exception as e:
            logger.error(f"❌ [CAP] Erro ao buscar no CSV: {e}")
            pass

        # Gerar código baseado em numeração do CSV (coluna 'Numero')
        try:
            # Tentar buscar numeração da coluna 'Numero' do CSV
            filtro = (
                (self.arquitetura.df['Macroprocesso'] == sm.macro_selecionado) &
                (self.arquitetura.df['Processo'] == sm.processo_selecionado) &
                (self.arquitetura.df['Subprocesso'] == sm.subprocesso_selecionado) &
                (self.arquitetura.df['Atividade'] == sm.atividade_selecionada)
            )
            linha_encontrada = self.arquitetura.df[filtro]

            if not linha_encontrada.empty and 'Numero' in linha_encontrada.columns:
                # Ler número hierárquico do CSV (ex: "1.1.1.1")
                numero_csv = str(linha_encontrada.iloc[0]['Numero'])
                partes = numero_csv.split('.')

                if len(partes) >= 4:
                    idx_macro = int(partes[0])
                    idx_processo = int(partes[1])
                    idx_subprocesso = int(partes[2])
                    idx_atividade = int(partes[3])
                else:
                    raise ValueError("Formato de numeração inválido no CSV")
            else:
                raise ValueError("Numeração não encontrada no CSV")

            codigo_base = f"{prefixo}.{idx_macro}.{idx_processo}.{idx_subprocesso}.{idx_atividade}"

        except (ValueError, IndexError, KeyError) as e:
            # Fallback: gerar índices dinamicamente
            logger.warning(f"[CAP] Numeração não encontrada no CSV, gerando dinamicamente: {e}")

            macros = self.arquitetura.obter_macroprocessos_unicos()
            idx_macro = macros.index(sm.macro_selecionado) + 1 if sm.macro_selecionado in macros else 1

            processos = self.arquitetura.obter_processos_por_macro(sm.macro_selecionado)
            idx_processo = processos.index(sm.processo_selecionado) + 1 if sm.processo_selecionado in processos else 1

            subprocessos = self.arquitetura.obter_subprocessos_por_processo(sm.macro_selecionado, sm.processo_selecionado)
            idx_subprocesso = subprocessos.index(sm.subprocesso_selecionado) + 1 if sm.subprocesso_selecionado in subprocessos else 1

            atividades = self.arquitetura.obter_atividades_por_subprocesso(sm.macro_selecionado, sm.processo_selecionado, sm.subprocesso_selecionado)
            idx_atividade = atividades.index(sm.atividade_selecionada) + 1 if sm.atividade_selecionada in atividades else 1

            codigo_base = f"{prefixo}.{idx_macro}.{idx_processo}.{idx_subprocesso}.{idx_atividade}"

            # Validar duplicatas e incrementar sufixo se necessário
            codigo_final = codigo_base
            sufixo = 1
            while self._codigo_existe_no_banco(codigo_final):
                codigo_final = f"{codigo_base}-{sufixo}"
                sufixo += 1
                if sufixo > 50:  # Limite de segurança
                    break

            logger.info(f"CAP gerado: {codigo_final}")
            return codigo_final
        except Exception as e:
            logger.error(f"Erro ao gerar CAP: {e}")
            return f"{prefixo}.1.1.1.1"

    def _codigo_existe_no_banco(self, codigo: str) -> bool:
        """Verifica se código CAP já existe no banco de dados"""
        try:
            from processos.models import POP
            return POP.objects.filter(
                codigo_processo=codigo,
                is_deleted=False
            ).exists()
        except:
            # Se houver erro na consulta, não bloquear a geração
            return False

    def _calcular_progresso(self, sm: POPStateMachine) -> str:
        """
        Calcula progresso da coleta baseado em campos preenchidos (não estados).
        Retorna formato "X/13" onde 13 é o total de campos principais.
        """
        total_campos = 13  # Total de campos principais no POP
        campos_preenchidos = 0

        # Nome usuário
        if sm.nome_usuario:
            campos_preenchidos += 1

        # Área DECIPEX
        if sm.dados_coletados.get('area_decipex'):
            campos_preenchidos += 1

        # Arquitetura (macro/processo/subprocesso/atividade)
        if sm.dados_coletados.get('macroprocesso'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('processo'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('subprocesso'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('atividade'):
            campos_preenchidos += 1

        # Nome do processo
        if sm.dados_coletados.get('nome_processo'):
            campos_preenchidos += 1

        # Entrega esperada
        if sm.dados_coletados.get('entrega_esperada'):
            campos_preenchidos += 1

        # Dispositivos normativos
        if sm.dados_coletados.get('dispositivos_normativos'):
            campos_preenchidos += 1

        # Operadores
        if sm.dados_coletados.get('operadores'):
            campos_preenchidos += 1

        # Sistemas
        if sm.dados_coletados.get('sistemas'):
            campos_preenchidos += 1

        # Documentos (entrada/saída)
        if sm.dados_coletados.get('documentos_entrada') or sm.dados_coletados.get('documentos_saida'):
            campos_preenchidos += 1

        # Fluxos (entrada/saída)
        if sm.dados_coletados.get('fluxos_entrada') or sm.dados_coletados.get('fluxos_saida'):
            campos_preenchidos += 1

        return f"{campos_preenchidos}/{total_campos}"

    def obter_progresso(self, sm: POPStateMachine) -> dict:
        """
        Retorna detalhes completos do progresso atual.

        Returns:
            dict: {
                "campos_preenchidos": int,
                "total_campos": int,
                "percentual": int (0-100),
                "estado_atual": str,
                "campos_faltantes": list[str],
                "completo": bool
            }
        """
        total_campos = 13
        campos_preenchidos = 0
        campos_faltantes = []

        # Mapear campos e verificar preenchimento
        campos_map = {
            'nome_usuario': ('Nome do usuário', sm.nome_usuario),
            'area_decipex': ('Área DECIPEX', sm.dados_coletados.get('area_decipex')),
            'macroprocesso': ('Macroprocesso', sm.dados_coletados.get('macroprocesso')),
            'processo': ('Processo', sm.dados_coletados.get('processo')),
            'subprocesso': ('Subprocesso', sm.dados_coletados.get('subprocesso')),
            'atividade': ('Atividade', sm.dados_coletados.get('atividade')),
            'nome_processo': ('Nome do processo', sm.dados_coletados.get('nome_processo')),
            'entrega_esperada': ('Entrega esperada', sm.dados_coletados.get('entrega_esperada')),
            'dispositivos_normativos': ('Dispositivos normativos', sm.dados_coletados.get('dispositivos_normativos')),
            'operadores': ('Operadores', sm.dados_coletados.get('operadores')),
            'sistemas': ('Sistemas', sm.dados_coletados.get('sistemas')),
            'documentos': ('Documentos', sm.dados_coletados.get('documentos_entrada') or sm.dados_coletados.get('documentos_saida')),
            'fluxos': ('Fluxos', sm.dados_coletados.get('fluxos_entrada') or sm.dados_coletados.get('fluxos_saida')),
        }

        for campo_id, (campo_nome, valor) in campos_map.items():
            if valor:
                campos_preenchidos += 1
            else:
                campos_faltantes.append(campo_nome)

        percentual = int((campos_preenchidos / total_campos) * 100)

        return {
            "campos_preenchidos": campos_preenchidos,
            "total_campos": total_campos,
            "percentual": percentual,
            "estado_atual": sm.estado.value,
            "campos_faltantes": campos_faltantes,
            "completo": sm.estado == EstadoPOP.DELEGACAO_ETAPAS or percentual == 100
        }

    def _preparar_dados_formulario(self, sm: POPStateMachine) -> dict:
        """
        Prepara dados do POP para o FormularioPOP.tsx (PREENCHIMENTO EM TEMPO REAL)

        Este método retorna SEMPRE os dados coletados até o momento, permitindo
        que o frontend mostre o formulário sendo preenchido em tempo real.

        Returns:
            dict: Dados formatados para o FormularioPOP.tsx
        """
        dados = sm.dados_coletados
        area_info = sm.area_selecionada or {}

        # Gerar código CAP se ainda não foi gerado
        codigo_cap = sm.codigo_cap if sm.codigo_cap else "Aguardando..."

        return {
            # Identificação
            "codigo_cap": codigo_cap,
            "codigo_processo": codigo_cap,  # ✅ Alias para frontend
            "area": {
                "nome": area_info.get("nome", ""),
                "codigo": area_info.get("codigo", "")
            },
            "macroprocesso": sm.macro_selecionado or "",
            "processo": sm.processo_selecionado or "",
            "processo_especifico": sm.processo_selecionado or "",  # ✅ Alias para frontend
            "subprocesso": sm.subprocesso_selecionado or "",
            "atividade": sm.atividade_selecionada or "",

            # Dados coletados
            "nome_processo": dados.get("nome_processo", "") or sm.atividade_selecionada or "",  # ✅ Fallback para atividade
            "entrega_esperada": dados.get("entrega_esperada", ""),
            "dispositivos_normativos": dados.get("dispositivos_normativos", []),
            "operadores": '; '.join(dados.get("operadores", [])) if isinstance(dados.get("operadores", []), list) else dados.get("operadores", ""),
            "sistemas": dados.get("sistemas", []),
            "documentos": dados.get("documentos", []),
            "fluxos_entrada": dados.get("fluxos_entrada", []),
            "fluxos_saida": dados.get("fluxos_saida", []),
            "pontos_atencao": dados.get("pontos_atencao", ""),

            # Metadados
            "nome_usuario": sm.nome_usuario or "",
            "versao": "1.0",
            "data_criacao": "",  # Frontend preenche

            # Estado do preenchimento
            "campo_atual": self._obter_campo_atual(sm.estado),
            "percentual_conclusao": self._calcular_progresso(sm)
        }

    def _obter_campo_atual(self, estado: EstadoPOP) -> str:
        """Retorna qual campo está sendo preenchido no momento"""
        mapa_campos = {
            EstadoPOP.NOME_USUARIO: "nome_usuario",
            EstadoPOP.AREA_DECIPEX: "area",
            EstadoPOP.ARQUITETURA: "arquitetura",
            EstadoPOP.NOME_PROCESSO: "nome_processo",
            EstadoPOP.ENTREGA_ESPERADA: "entrega_esperada",
            EstadoPOP.DISPOSITIVOS_NORMATIVOS: "dispositivos_normativos",
            EstadoPOP.OPERADORES: "operadores",
            EstadoPOP.SISTEMAS: "sistemas",
            EstadoPOP.FLUXOS: "fluxos",
            EstadoPOP.PONTOS_ATENCAO: "pontos_atencao",
        }
        return mapa_campos.get(estado, "")

    def _gerar_resumo_pop(self, sm: POPStateMachine) -> str:
        """Gera resumo completo dos dados coletados (FORMULÁRIO POP COMPLETO)"""
        dados = sm.dados_coletados

        # Gerar código CAP se ainda não foi gerado
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        resumo = "**📋 RESUMO DO PROCESSO (POP)**\n\n"

        # 1. IDENTIFICAÇÃO
        resumo += f"**🔖 Código CAP:** {sm.codigo_cap}\n"
        resumo += f"**📍 Área:** {sm.area_selecionada['nome']} ({sm.area_selecionada['codigo']})\n"
        resumo += f"**📂 Macroprocesso:** {sm.macro_selecionado}\n"
        resumo += f"**📁 Processo:** {sm.processo_selecionado}\n"
        resumo += f"**📄 Subprocesso:** {sm.subprocesso_selecionado}\n"
        resumo += f"**⚙️ Atividade:** {sm.atividade_selecionada}\n\n"

        # 2. ENTREGA ESPERADA
        resumo += f"**🎯 Entrega Esperada:** {dados['entrega_esperada']}\n\n"

        # 3. SISTEMAS
        resumo += f"**💻 Sistemas:** {', '.join(dados['sistemas'])}\n\n"

        # 4. NORMAS
        resumo += f"**📚 Normas:** {', '.join(dados['dispositivos_normativos'])}\n\n"

        # 5. OPERADORES
        resumo += f"**👥 Operadores:** {', '.join(dados['operadores'])}\n\n"

        # 6. ENTRADA (De quais áreas recebe insumos)
        if dados.get('fluxos_entrada'):
            resumo += f"**📥 Entrada:** {', '.join(dados['fluxos_entrada'])}\n\n"

        # 7. SAÍDA (Para quais áreas entrega resultados)
        if dados.get('fluxos_saida'):
            resumo += f"**📤 Saída:** {', '.join(dados['fluxos_saida'])}\n\n"

        # 8. DOCUMENTOS
        if dados.get('documentos'):
            resumo += f"**📄 Documentos:** {', '.join(dados['documentos'])}\n\n"

        resumo += "**✅ Etapas:** Serão coletadas por Helena Etapas\n"
        resumo += "**⚠️ Pontos de Atenção:** Serão coletados após as etapas\n"

        return resumo

    def receber_dados(self, dados_etapas: dict) -> dict:
        """
        Recebe dados de volta do Helena Etapas (quando concluir)

        Args:
            dados_etapas: Etapas coletadas pelo Helena Etapas

        Returns:
            dict: Dados consolidados do processo completo
        """
        logger.info("Helena POP recebendo dados consolidados do Helena Etapas")

        # TODO: Consolidar dados do POP + Etapas
        # TODO: Gerar documento final
        # TODO: Oferecer próximos passos (fluxograma, riscos, etc.)

        return {
            'sucesso': True,
            'mensagem': 'Processo mapeado com sucesso!',
            'dados_consolidados': dados_etapas
        }
