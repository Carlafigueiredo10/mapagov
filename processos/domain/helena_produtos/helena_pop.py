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
    AREA_DECIPEX = "area_decipex"
    ARQUITETURA = "arquitetura"
    CONFIRMACAO_ARQUITETURA = "confirmacao_arquitetura"  # 🎯 NOVO: confirmar arquitetura sugerida pela IA
    SELECAO_HIERARQUICA = "selecao_hierarquica"  # 🆕 FALLBACK: seleção manual via dropdowns hierárquicos
    NOME_PROCESSO = "nome_processo"
    ENTREGA_ESPERADA = "entrega_esperada"
    CONFIRMACAO_ENTREGA = "confirmacao_entrega"  # 🎯 NOVO: confirmar/editar entrega
    RECONHECIMENTO_ENTREGA = "reconhecimento_entrega"  # 🎯 Gamificação após entrega
    DISPOSITIVOS_NORMATIVOS = "dispositivos_normativos"
    OPERADORES = "operadores"
    SISTEMAS = "sistemas"
    DOCUMENTOS = "documentos"
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
        "DIGEP": "5", "CGRIS": "6", "CGCAF": "7", "CGECO": "8"
    }

    prefixo_area = PREFIXOS_AREA.get(area_codigo, "0")

    # Obter índices hierárquicos do CSV
    # 1. Índice do macroprocesso
    macros_unicos = hierarquia_df['Macroprocesso'].unique().tolist()
    try:
        idx_macro = macros_unicos.index(macroprocesso) + 1
    except ValueError:
        idx_macro = len(macros_unicos) + 1

    # 2. Índice do processo dentro do macroprocesso
    processos_no_macro = hierarquia_df[
        hierarquia_df['Macroprocesso'] == macroprocesso
    ]['Processo'].unique().tolist()
    try:
        idx_processo = processos_no_macro.index(processo) + 1
    except ValueError:
        idx_processo = len(processos_no_macro) + 1

    # 3. Índice do subprocesso dentro do processo
    subs_no_processo = hierarquia_df[
        (hierarquia_df['Macroprocesso'] == macroprocesso) &
        (hierarquia_df['Processo'] == processo)
    ]['Subprocesso'].unique().tolist()
    try:
        idx_subprocesso = subs_no_processo.index(subprocesso) + 1
    except ValueError:
        idx_subprocesso = len(subs_no_processo) + 1

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

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'estado': self.estado.value,
            'nome_usuario': self.nome_usuario,
            'nome_temporario': self.nome_temporario,
            'area_selecionada': self.area_selecionada,
            'macro_selecionado': self.macro_selecionado,
            'processo_selecionado': self.processo_selecionado,
            'subprocesso_selecionado': self.subprocesso_selecionado,
            'atividade_selecionada': self.atividade_selecionada,
            'codigo_cap': self.codigo_cap,  # 🎯 CAP ÚNICO
            'dados_coletados': self.dados_coletados,
            'concluido': self.concluido
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'POPStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls()
        sm.estado = EstadoPOP(data.get('estado', EstadoPOP.NOME_USUARIO.value))  # ✅ FIX: default para NOME_USUARIO
        sm.nome_usuario = data.get('nome_usuario', '')
        sm.nome_temporario = data.get('nome_temporario', '')
        sm.area_selecionada = data.get('area_selecionada')
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
            df = pd.read_csv(csv_path)

            # Filtrar apenas áreas ativas
            df_ativas = df[df['ativo'] == True].sort_values('ordem')

            # Converter para dicionário no formato esperado
            areas_dict = {}
            for idx, row in df_ativas.iterrows():
                areas_dict[int(row['ordem'])] = {
                    "codigo": row['codigo'],
                    "nome": row['nome_completo'],
                    "prefixo": str(row['prefixo'])
                }

            logger.info(f"✅ Áreas carregadas do CSV: {len(areas_dict)} áreas ativas")
            return areas_dict

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de áreas ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return {
                1: {"codigo": "CGBEN", "nome": "Coordenação Geral de Benefícios", "prefixo": "1"},
                2: {"codigo": "CGPAG", "nome": "Coordenação Geral de Pagamentos", "prefixo": "2"},
                3: {"codigo": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3"},
                4: {"codigo": "CGGAF", "nome": "Coordenação Geral de Gestão de Acervos Funcionais", "prefixo": "4"},
                5: {"codigo": "DIGEP", "nome": "Diretoria de Pessoal dos Ex-Territórios", "prefixo": "5"},
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

            logger.info(f"✅ Sistemas carregados do CSV: {len(df_ativos)} sistemas em {len(sistemas_dict)} categorias")
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

            logger.info(f"✅ Operadores carregados do CSV: {len(operadores_list)} operadores ativos")
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
            df = pd.read_csv(csv_path)

            # Converter para lista de dicionários
            orgaos_list = []
            for _, row in df.iterrows():
                orgaos_list.append({
                    'sigla': row['sigla'],
                    'nome_completo': row['nome_completo'],
                    'observacao': row.get('observacao', '')
                })

            logger.info(f"✅ Órgãos centralizados carregados do CSV: {len(orgaos_list)} órgãos")
            return orgaos_list

        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV de órgãos centralizados ({e}). Usando fallback hardcoded.")

            # FALLBACK: Dados hardcoded (segurança)
            return [
                {'sigla': 'MGI', 'nome_completo': 'Ministério da Gestão e da Inovação em Serviços Públicos', 'observacao': ''},
                {'sigla': 'MF', 'nome_completo': 'Ministério da Fazenda', 'observacao': ''},
                {'sigla': 'MPO', 'nome_completo': 'Ministério do Planejamento e Orçamento', 'observacao': ''},
                {'sigla': 'CGU', 'nome_completo': 'Controladoria-Geral da União', 'observacao': ''},
                {'sigla': 'TCU', 'nome_completo': 'Tribunal de Contas da União', 'observacao': ''},
                {'sigla': 'INSS', 'nome_completo': 'Instituto Nacional do Seguro Social', 'observacao': 'Médicos peritos'},
                {'sigla': 'RFB', 'nome_completo': 'Receita Federal do Brasil', 'observacao': ''},
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

            logger.info(f"✅ CSV carregado: {len(lista_plana)} atividades em hierarquia")

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

        elif sm.estado == EstadoPOP.AREA_DECIPEX:
            resposta, novo_sm = self._processar_area_decipex(mensagem, sm)

        elif sm.estado == EstadoPOP.ARQUITETURA:
            resposta, novo_sm = self._processar_arquitetura(mensagem, sm)

        elif sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            resposta, novo_sm = self._processar_confirmacao_arquitetura(mensagem, sm)

        elif sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            resposta, novo_sm = self._processar_selecao_hierarquica(mensagem, sm)

        elif sm.estado == EstadoPOP.NOME_PROCESSO:
            resposta, novo_sm = self._processar_nome_processo(mensagem, sm)

        elif sm.estado == EstadoPOP.ENTREGA_ESPERADA:
            resposta, novo_sm = self._processar_entrega_esperada(mensagem, sm)

        elif sm.estado == EstadoPOP.CONFIRMACAO_ENTREGA:
            resposta, novo_sm = self._processar_confirmacao_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            resposta, novo_sm = self._processar_reconhecimento_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            resposta, novo_sm = self._processar_dispositivos_normativos(mensagem, sm)

        elif sm.estado == EstadoPOP.OPERADORES:
            resposta, novo_sm = self._processar_operadores(mensagem, sm)

        elif sm.estado == EstadoPOP.SISTEMAS:
            resposta, novo_sm = self._processar_sistemas(mensagem, sm)

        elif sm.estado == EstadoPOP.DOCUMENTOS:
            resposta, novo_sm = self._processar_documentos(mensagem, sm)

        elif sm.estado == EstadoPOP.FLUXOS:
            resposta, novo_sm = self._processar_fluxos(mensagem, sm)

        elif sm.estado == EstadoPOP.PONTOS_ATENCAO:
            resposta, novo_sm = self._processar_pontos_atencao(mensagem, sm)

        elif sm.estado == EstadoPOP.REVISAO_PRE_DELEGACAO:
            resposta, novo_sm = self._processar_revisao_pre_delegacao(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_EPICA:
            resposta, novo_sm = self._processar_transicao_epica(mensagem, sm)

        elif sm.estado == EstadoPOP.SELECAO_EDICAO:
            resposta, novo_sm = self._processar_selecao_edicao(mensagem, sm)

        elif sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            resposta, novo_sm = self._processar_delegacao_etapas(mensagem, sm)

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

        # Adicionar badge de conquista se chegou na transição épica
        metadados_extra = {
            'progresso_detalhado': progresso_detalhado
        }

        # Badge de conquista na transição épica
        if novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            metadados_extra['badge'] = {
                'tipo': 'fase_previa_completa',
                'emoji': '🏆',
                'titulo': 'Fase Prévia Concluída!',
                'descricao': 'Você mapeou toda a estrutura básica do processo',
                'mostrar_animacao': True
            }

        # 🎯 Definir interface dinâmica baseada no estado
        tipo_interface = None
        dados_interface = None

        if novo_sm.estado == EstadoPOP.CONFIRMA_NOME:
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
                'botao_confirmar': '🔹 Sim, entendi tudo!',
                'botao_editar': '🔹 Não, ainda tenho dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'não'
            }

        elif novo_sm.estado == EstadoPOP.AREA_DECIPEX:
            tipo_interface = 'areas'
            dados_interface = {
                'opcoes_areas': {
                    str(num): {'codigo': info['codigo'], 'nome': info['nome']}
                    for num, info in self.AREAS_DECIPEX.items()
                }
            }

        elif novo_sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            # 🆕 FALLBACK: Interface de dropdowns hierárquicos para seleção manual
            tipo_interface = 'arquitetura_hierarquica'
            dados_interface = self._preparar_dados_dropdown_hierarquico()

        elif novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            # Interface épica com botão pulsante e opção de pausa
            tipo_interface = 'transicao_epica'
            dados_interface = {
                'botao_principal': {
                    'texto': '🚀 VAMOS COMEÇAR!',
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

        elif novo_sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            # Interface com 2 botões: Concordo / Editar manualmente
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
                'multipla_selecao': True
            }

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
        # (usado por _processar_documentos, _processar_fluxos, etc.)
        if hasattr(novo_sm, 'tipo_interface') and novo_sm.tipo_interface:
            tipo_interface = novo_sm.tipo_interface
            dados_interface = getattr(novo_sm, 'dados_interface', {})

        # 🎯 PREENCHIMENTO EM TEMPO REAL - Dados do formulário POP
        formulario_pop = self._preparar_dados_formulario(novo_sm)

        # ✅ FIX CRÍTICO: Frontend OLD lia "dados_extraidos", não "formulario_pop"
        # Enviar AMBOS para compatibilidade total
        dados_extraidos = formulario_pop.copy()

        # 🐛 DEBUG: Log para verificar se dados estão sendo enviados
        logger.info(f"📋 [DEBUG] Dados preparados: CAP={formulario_pop.get('codigo_cap')}, Macro={formulario_pop.get('macroprocesso')}, Atividade={formulario_pop.get('atividade')}")

        return self.criar_resposta(
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
                f"Antes de continuarmos, me confirma, posso te chamar de {sm.nome_temporario} mesmo?"
            )
            return resposta, sm

        # ✅ FIX: Se mensagem não é nome válido, apenas pedir clarificação
        # NUNCA repetir boas-vindas completas (frontend já mostrou)
        resposta = "Desculpe, não entendi. Pode me dizer seu nome? (Digite apenas o primeiro nome)"
        return resposta, sm

    def _processar_confirma_nome(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação do nome e vai direto para escolha de tipo de explicação"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['sim', 's', 'pode', 'ok', 'claro']):
            sm.nome_usuario = sm.nome_temporario
            sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO

            resposta = (
                f"Ótimo então, {sm.nome_usuario}. 😊\n\n"
                f"Antes de seguir, preciso te explicar rapidinho como tudo vai funcionar.\n\n"
                f"Você prefere que eu fale de forma objetiva 🕐 ou com uma explicação mais detalhada "
                f"sobre o que vamos fazer daqui pra frente? 💬"
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
            resposta = (
                f"Oi, {sm.nome_usuario}! 👋\n\n"
                f"Vi que você escolheu a explicação detalhada — então vamos com calma que eu te explico tudo.\n\n"
                f"Nesse chat, nós vamos mapear a sua atividade: aquilo que você faz todos os dias (ou quase), "
                f"a rotina real do seu trabalho.\n"
                f"A intenção é preencher esse formulário de Procedimento Operacional Padrão — o famoso POP — "
                f"que está aí do lado.\n"
                f"Tá vendo? 👀 Aproveita pra conhecer, porque nossa meta é entregar esse POP prontinho! ✅\n\n"
                f"Eu vou te perguntar:\n"
                f"🧭 em qual área você atua,\n"
                f"🧩 te ajudar com a parte mais burocrática — macroprocesso, processo, subprocesso e atividade,\n"
                f"📘 e criar o \"CPF\" do seu processo (a gente chama de CAP, código na arquitetura do processo).\n\n"
                f"Depois, vamos falar sobre os sistemas que você usa e as normas que regem sua atividade.\n"
                f"Nessa parte, vou até te apresentar minha amiga do Sigepe Legis IA — ela é ótima pra encontrar "
                f"as normas certas quando a gente se perde no meio de tantas! 🤖📜\n\n"
                f"Por fim, vem a parte mais detalhada: você vai me contar passo a passo o que faz no dia a dia.\n"
                f"Pode parecer demorado, mas pensa assim: quanto melhor você mapear agora, menos retrabalho vai "
                f"ter depois — e o seu processo vai ficar claro, seguro e fácil de ensinar pra quem chegar novo. 💪\n\n"
                f"Tudo certo até aqui?"
            )
            return resposta, sm

        # Explicação objetiva/curta (fluxo atual)
        elif any(palavra in msg_lower for palavra in ['objetiva', 'curta', 'rápida', 'rapida', 'resumida']):
            sm.estado = EstadoPOP.EXPLICACAO
            resposta = (
                f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário "
                f"de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\n"
                f"Nossa meta é entregar esse POP prontinho. Vamos continuar? (digite sim que seguimos em frente)"
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

        # Entendeu tudo - vai DIRETO para seleção de área
        if any(palavra in msg_lower for palavra in ['sim', 's', 'entendi', 'ok', 'claro', 'beleza', 'tudo']):
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"Mas olha, {sm.nome_usuario}, antes de seguir quero te tranquilizar sobre esse processo.\n"
                f"É normal ainda ter dúvidas — faz parte da construção.\n\n"
                f"Essa missão aqui é em dupla, e você pode contar comigo a qualquer momento pra te ajudar.\n\n"
                f"Agora sim, vamos começar? 🚀\n\n"
                f"Me conta: em qual área do DECIPEX você executa sua atividade?"
            )
            return resposta, sm

        # Ainda tem dúvidas
        elif any(palavra in msg_lower for palavra in ['não', 'nao', 'n', 'duvida', 'dúvida']):
            sm.estado = EstadoPOP.DUVIDAS_EXPLICACAO
            resposta = (
                f"Sem problemas, {sm.nome_usuario}! 😊\n\n"
                f"Me diga: qual parte você quer que eu explique melhor?\n\n"
                f"Pode perguntar à vontade sobre:\n"
                f"• O que é o formulário POP\n"
                f"• Para que serve o código CAP\n"
                f"• Como funciona o mapeamento de etapas\n"
                f"• Qualquer outra dúvida!"
            )
            return resposta, sm

        # Fallback
        else:
            resposta = (
                f"Por favor, me diga:\n"
                f"🔹 **Sim, entendi tudo!** - para continuar\n"
                f"🔹 **Não, ainda tenho dúvidas** - para eu te explicar melhor"
            )
            return resposta, sm

    def _processar_duvidas_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa dúvidas sobre a explicação"""
        msg_lower = mensagem.lower().strip()

        # Entendeu agora - vai DIRETO para seleção de área
        if any(palavra in msg_lower for palavra in ['entendi', 'ok', 'obrigad', 'valeu', 'claro', 'agora sim']):
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"Que bom que ficou claro, {sm.nome_usuario}! 😊\n\n"
                f"Mas olha, antes de seguir quero te tranquilizar sobre esse processo.\n"
                f"É normal ainda ter dúvidas — faz parte da construção.\n\n"
                f"Essa missão aqui é em dupla, e você pode contar comigo a qualquer momento pra te ajudar.\n\n"
                f"Agora sim, vamos começar? 🚀\n\n"
                f"Me conta: em qual área do DECIPEX você executa sua atividade?"
            )
            return resposta, sm

        # Ainda tem dúvidas - usar Helena Mapeamento (modo explicativo)
        else:
            # Aqui poderia chamar Helena Ajuda Inteligente em modo explicativo
            # Por enquanto, vamos dar uma resposta genérica e permitir continuar perguntando

            # Respostas contextuais baseadas em palavras-chave
            if 'pop' in msg_lower or 'formulário' in msg_lower or 'formulario' in msg_lower:
                resposta = (
                    f"O POP (Procedimento Operacional Padrão) é como um manual do seu trabalho! 📖\n\n"
                    f"Ele documenta tudo que você faz: desde os sistemas que usa, as normas que segue, "
                    f"até o passo a passo de cada etapa. É tipo uma receita de bolo, só que do seu processo de trabalho.\n\n"
                    f"Isso ajuda quando:\n"
                    f"• Chega alguém novo na equipe\n"
                    f"• Você precisa explicar o que faz\n"
                    f"• Quer melhorar alguma etapa\n\n"
                    f"Entendeu melhor agora? (Digite 'entendi' ou me faça outra pergunta)"
                )
            elif 'cap' in msg_lower or 'código' in msg_lower or 'codigo' in msg_lower:
                resposta = (
                    f"O CAP é o \"CPF\" do seu processo! 🆔\n\n"
                    f"É um código único que identifica exatamente o que você faz dentro da DECIPEX.\n"
                    f"Tipo: 2.1.3.5 = Área CGPAG → Macroprocesso → Processo → Subprocesso → Atividade\n\n"
                    f"Com ele, fica fácil encontrar, organizar e gerenciar todos os processos da diretoria.\n\n"
                    f"Ficou mais claro? (Digite 'entendi' ou me faça outra pergunta)"
                )
            elif 'etapa' in msg_lower or 'passo' in msg_lower or 'mapea' in msg_lower:
                resposta = (
                    f"O mapeamento de etapas é quando você me conta o passo a passo do seu dia a dia! 👣\n\n"
                    f"Por exemplo, se você analisa pedidos:\n"
                    f"1. Recebo o pedido no sistema\n"
                    f"2. Verifico se está completo\n"
                    f"3. Analiso os documentos\n"
                    f"4. Emito parecer\n\n"
                    f"Para cada etapa, vamos detalhar: quem faz, quanto tempo leva, que sistemas usa, etc.\n\n"
                    f"Entendeu? (Digite 'entendi' ou me faça outra pergunta)"
                )
            else:
                # Resposta genérica
                resposta = (
                    f"Entendo sua dúvida! Vou tentar explicar de outra forma:\n\n"
                    f"O que vamos fazer aqui é basicamente:\n"
                    f"1️⃣ Identificar qual área você trabalha\n"
                    f"2️⃣ Classificar sua atividade (isso gera o código CAP)\n"
                    f"3️⃣ Listar sistemas e normas que você usa\n"
                    f"4️⃣ Detalhar o passo a passo do seu trabalho\n\n"
                    f"No final, tudo isso vira um documento (POP) que fica guardado e pode ser consultado.\n\n"
                    f"Ficou mais claro? (Digite 'entendi' ou me faça uma pergunta mais específica)"
                )

            return resposta, sm

    def _processar_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Confirma que está tudo claro e pronto para começar (modo curto)"""
        msg_lower = mensagem.lower().strip()

        respostas_positivas = ['sim', 's', 'pode', 'ok', 'claro', 'vamos', 'yes', 'uhum', 'aham', 'beleza', 'entendi', 'bora', 'vamo', 'pronta', 'pronto']

        if msg_lower in respostas_positivas:
            # Vai DIRETO para seleção de área
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"Mas olha, {sm.nome_usuario}, antes de seguir quero te tranquilizar sobre esse processo.\n"
                f"É normal ainda ter dúvidas — faz parte da construção.\n\n"
                f"Essa missão aqui é em dupla, e você pode contar comigo a qualquer momento pra te ajudar.\n\n"
                f"Agora sim, vamos começar? 🚀\n\n"
                f"Me conta: em qual área do DECIPEX você executa sua atividade?"
            )
        else:
            resposta = f"Tudo bem! Só posso seguir quando você me disser 'sim', {sm.nome_usuario}. Quando quiser continuar, é só digitar."

        return resposta, sm

    def _processar_area_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da área DECIPEX"""
        try:
            numero = int(mensagem.strip())
            if numero in self.AREAS_DECIPEX:
                sm.area_selecionada = self.AREAS_DECIPEX[numero]
                sm.estado = EstadoPOP.ARQUITETURA

                # Buscar descrição personalizada da área
                codigo_area = sm.area_selecionada['codigo']
                descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                resposta = (
                    f"Ótimo, {sm.nome_usuario}! 🌿\n"
                    f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}\n\n"
                    "Agora vamos definir juntos o **macroprocesso, processo, subprocesso, atividade e entrega final** da sua rotina.\n\n"
                    "✍️ Pra isso, me conte em uma frase o que você faz por aqui — pode ser algo simples, tipo:\n"
                    "• 'Analiso pensões'\n"
                    "• 'Faço reposição ao erário'\n"
                    "• 'Cadastro atos de aposentadoria'"
                )
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

    def _processar_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa navegação na arquitetura DECIPEX usando sistema de busca em 3 níveis:

        PRIORIDADE 1: Busca exata no CSV das 107 atividades mapeadas
        PRIORIDADE 2: Busca fuzzy no CSV (score > 0.85)
        PRIORIDADE 3: IA sugere NOVA atividade (com aviso claro e detecção de duplicatas)

        FALLBACK: Seleção manual via dropdowns hierárquicos
        """
        descricao_usuario = mensagem.strip()

        # Validação: mínimo 10 caracteres
        if len(descricao_usuario) < 10:
            resposta = (
                "Por favor, descreva sua atividade com mais detalhes (mínimo 10 caracteres).\n\n"
                "Exemplo: 'Analiso requerimentos de auxílio saúde de aposentados'"
            )
            return resposta, sm

        # Obter dados do autor (para rastreabilidade)
        area_nome = sm.area_selecionada['nome']
        area_codigo = sm.area_selecionada['codigo']
        autor_nome = sm.nome_usuario or "Usuário"
        autor_cpf = "00000000000"  # TODO: Obter CPF real do usuário autenticado

        logger.info(f"[GOVERNANÇA] Iniciando busca para: '{descricao_usuario}' | Autor: {autor_nome} | Área: {area_codigo}")

        # ============================================================================
        # NÍVEL 1: BUSCA EXATA NO CSV (107 atividades mapeadas)
        # ============================================================================
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # Preparar textos do CSV
            df_csv = self.arquitetura.df
            if df_csv.empty:
                raise ValueError("CSV vazio")

            # Criar corpus de textos do CSV
            textos_csv = []
            for idx, row in df_csv.iterrows():
                texto_completo = f"{row['Macroprocesso']} {row['Processo']} {row['Subprocesso']} {row['Atividade']}"
                textos_csv.append(texto_completo.lower().strip())

            # Adicionar descrição do usuário
            todos_textos = textos_csv + [descricao_usuario.lower().strip()]

            # TF-IDF + Cosine Similarity
            vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=1, max_df=0.95)
            tfidf_matrix = vectorizer.fit_transform(todos_textos)

            # Calcular similaridade da descrição do usuário com todas as linhas do CSV
            similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

            # Encontrar match com maior score
            idx_melhor = similarities.argmax()
            score_melhor = float(similarities[idx_melhor])

            logger.info(f"[GOVERNANÇA] Melhor match no CSV: score={score_melhor:.3f} | idx={idx_melhor}")

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
                    from processos.domain.helena_produtos.helena_ajuda_inteligente import analisar_atividade_com_helena

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

        except Exception as e:
            logger.error(f"[GOVERNANÇA] Erro na busca no CSV: {e}")
            import traceback
            traceback.print_exc()

        # ============================================================================
        # NÍVEL 2: SCORE < 0.85 → IA SUGERE NOVA ATIVIDADE
        # ============================================================================
        logger.info(f"[GOVERNANÇA] Score < 0.85, atividade NÃO encontrada no catálogo oficial. Sugerindo nova atividade...")

        try:
            from processos.domain.helena_produtos.helena_ajuda_inteligente import analisar_atividade_com_helena

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
            logger.error(f"[GOVERNANÇA] Erro ao sugerir nova atividade: {e}")
            import traceback
            traceback.print_exc()

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

        # Se confirmar → ir para mensagem introdutória de normas (PASSO 3)
        if any(palavra in msg_lower for palavra in ['sim', 'concordo', 'confirmar', 'correto', 'ok', 'certo']):
            # 🐛 DEBUG: Verificar se dados da arquitetura estão salvos
            logger.info(f"🎯 [DEBUG] CONFIRMAÇÃO ARQUITETURA:")
            logger.info(f"  - CAP: {sm.codigo_cap}")
            logger.info(f"  - Macro: {sm.macro_selecionado}")
            logger.info(f"  - Processo: {sm.processo_selecionado}")
            logger.info(f"  - Subprocesso: {sm.subprocesso_selecionado}")
            logger.info(f"  - Atividade: {sm.atividade_selecionada}")
            logger.info(f"  - dados_coletados: {sm.dados_coletados}")

            sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

            # PASSO 3: Mensagem introdutória antes da interface de normas
            resposta = (
                "Agora vamos falar sobre as normas legais, normativos e guias que orientam essa atividade. ⚖️\n\n"
                "Aqui abaixo, eu já separei as principais normas que acho que têm relação com a sua entrega final: "
                "minhas sugestões em roxo. Mas, logo à frente dessas sugestões, você também vai encontrar o quadro "
                "completo com todas as normas disponíveis. Tô aprendendo ainda, então posso errar.\n\n"
                "E se quiser ir além, logo abaixo tem a opção de conversar com a minha parceira do Sigepe Legis IA "
                "(somos quase uma gangue 🤭). SUPER RECOMENDO. Ela pode te ajudar a buscar outras normas e aí é só "
                "copiar o trecho e colar aqui.\n\n"
                "Ah! E se você lembrar de alguma norma de cabeça, pode simplesmente digitar manualmente também. 💡"
            )

            return resposta, sm

        # Se quiser editar → voltar para coleta manual (nome processo)
        elif any(palavra in msg_lower for palavra in ['editar', 'ajustar', 'mudar', 'alterar', 'manual']):
            sm.estado = EstadoPOP.NOME_PROCESSO
            resposta = (
                "Sem problemas! Vamos fazer manualmente.\n\n"
                "Qual é o nome completo da atividade que você quer mapear?\n\n"
                "Ex: 'Conceder ressarcimento a aposentado civil', 'Análise de requerimento de auxílio alimentação'"
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
                logger.info(f"✅ Código CAP gerado (seleção manual): {sm.codigo_cap}")

            # 🎯 SUGERIR ENTREGA ESPERADA usando IA baseado na seleção + descrição original
            descricao_original = sm.dados_coletados.get('descricao_original', '')

            try:
                from processos.domain.helena_produtos.helena_ajuda_inteligente import analisar_atividade_com_helena

                contexto = {
                    'area': sm.area_selecionada['nome'],
                    'area_codigo': sm.area_selecionada['codigo'],
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
                    logger.info(f"✅ IA sugeriu entrega esperada: {sugestao_entrega}")

            except Exception as e:
                logger.warning(f"Não foi possível sugerir entrega esperada com IA: {e}")
                sugestao_entrega = None

            # Ir para confirmação da arquitetura (mesmo fluxo da IA)
            sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

            resposta = (
                f"✅ Perfeito! Você selecionou:\n\n"
                f"**Arquitetura:**\n"
                f"**CAP (Código na Arquitetura de Processos):** {sm.codigo_cap}\n\n"
                f"Baseada em:\n"
                f"• Área: {sm.area_selecionada.get('nome', 'N/A')}\n"
                f"• Macroprocesso: {sm.macro_selecionado}\n"
                f"• Processo: {sm.processo_selecionado}\n"
                f"• Subprocesso: {sm.subprocesso_selecionado}\n"
                f"• Atividade: {sm.atividade_selecionada}\n\n"
            )

            if sugestao_entrega:
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                resposta += (
                    f"**Entrega Final (sugestão da IA):**\n"
                    f"• {sugestao_entrega}\n\n"
                )

            resposta += "Se concordar, digite 'sim' para continuar.\nSe quiser ajustar algo, digite 'ajustar'."

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
        sm.dados_coletados['entrega_esperada'] = mensagem.strip()
        sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA

        # Gerar código CAP antecipadamente
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Mostrar resumo completo com BOTÕES CONFIRMAR/EDITAR
        nome = sm.nome_usuario or "você"

        resposta = (
            f"## 📋 **RESUMO DA ARQUITETURA E ENTREGA**\n\n"
            f"**Código CAP (CPF do Processo):** {sm.codigo_cap}\n\n"
            f"**Área:** {sm.area_selecionada['nome']} ({sm.area_selecionada['codigo']})\n\n"
            f"**Arquitetura:**\n"
            f"• Macroprocesso: {sm.macro_selecionado}\n"
            f"• Processo: {sm.processo_selecionado}\n"
            f"• Subprocesso: {sm.subprocesso_selecionado}\n"
            f"• Atividade: {sm.atividade_selecionada}\n\n"
            f"**Entrega Final:**\n"
            f"• {mensagem.strip()}\n\n"
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

        # Confirmar - avançar para gamificação
        sm.estado = EstadoPOP.RECONHECIMENTO_ENTREGA
        sm.tipo_interface = None
        sm.dados_interface = {}

        # Mensagem de reconhecimento épica
        resultado_resumido = sm.dados_coletados['entrega_esperada']
        resultado_resumido = resultado_resumido[:80] if len(resultado_resumido) <= 80 else resultado_resumido[:77] + "..."
        nome = sm.nome_usuario or "você"

        resposta = (
            f"✅ **Terminamos essa fase!**\n\n"
            f"Chegamos à entrega final: \"{resultado_resumido}\"\n\n"
            f"**Parabéns, {nome}!** 👏\n\n"
            f"O seu trabalho ajuda a tornar o serviço público mais eficiente e confiável, "
            f"e isso faz toda diferença para a sociedade.\n\n"
            f"Clique na caixinha abaixo para continuar:"
        )

        return resposta, sm

    def _processar_reconhecimento_entrega(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa clique na caixinha de reconhecimento e avança para normas"""
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        # Buscar sugestões de normas
        sugestoes = self._sugerir_base_legal_contextual(sm)

        resposta = (
            f"Agora, quais são as principais normas que regulam esta atividade?\n\n"
            f"💡 **Seleção inteligente disponível abaixo!**"
        )

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

        nome = sm.nome_usuario or "você"
        qtd_normas = len(normas)

        # Ir direto para OPERADORES (unificando as 2 mensagens)
        sm.estado = EstadoPOP.OPERADORES

        resposta = (
            f"✅ Perfeito! Registrei {qtd_normas} norma(s).\n\n"
            f"Terminamos uma parte essencial do trabalho, {nome}.\n\n"
            f"As normas são como placas na estrada — elas mostram o caminho certo "
            f"para sua atividade seguir com segurança e consistência. 🚦\n\n"
            f"Agora, vamos falar sobre os motoristas dessa jornada: "
            f"as pessoas que fazem essa atividade acontecer no dia a dia.\n\n"
            f"👥 Quem são os responsáveis?\n\n"
            f"Por favor, selecione abaixo quem executa diretamente, quem revisa, quem apoia… "
            f"e também quem prepara o terreno antes que o processo chegue até você.\n\n"
            f"💡 Lembre de se incluir também!\n\n"
            f"As opções estão logo abaixo, mas se eu esqueci alguém pode digitar."
        )

        return resposta, sm

    def _processar_operadores(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de operadores com fuzzy matching"""
        # Aceitar JSON (de interface) ou texto
        try:
            import json as json_lib
            dados = json_lib.loads(mensagem)
            if isinstance(dados, list):
                operadores = dados
            else:
                raise ValueError("Não é lista JSON, fazer parsing manual")
        except:
            # FUZZY PARSING de operadores
            operadores = parse_operadores(mensagem, self.OPERADORES_DECIPEX)

        sm.dados_coletados['operadores'] = operadores
        sm.estado = EstadoPOP.SISTEMAS

        resposta = (
            f"Registrei {len(operadores)} operador(es).\n\n"
            "Agora, indique os sistemas utilizados na execução desta atividade.\n\n"
            "Você pode selecionar os sistemas na lista abaixo ou digitar manualmente caso não os encontre."
        )
        return resposta, sm

    def _processar_sistemas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de sistemas com fuzzy matching"""
        # Aceitar JSON ou fazer fuzzy parsing
        try:
            import json as json_lib
            dados = json_lib.loads(mensagem)
            if isinstance(dados, list):
                sistemas = dados
            else:
                raise ValueError("Não é lista JSON")
        except:
            # FUZZY PARSING de sistemas
            sistemas = parse_sistemas(mensagem, self.SISTEMAS_DECIPEX)

        sm.dados_coletados['sistemas'] = sistemas
        sm.estado = EstadoPOP.DOCUMENTOS

        nome = sm.nome_usuario or "você"

        # Ativar interface de badge (troféu + confete)
        sm.tipo_interface = 'badge_sistemas'
        sm.dados_interface = {
            'nome_badge': 'Cartógrafo(a) de Processos – Nível 1'
        }

        # MENSAGEM 1: Reconhecimento + Presente
        resposta = (
            f"Uau, {nome}! Você acabou de registrar partes super importantes dessa atividade — "
            f"já temos o CAP do processo, sistemas, normas e operadores. Isso é um baita avanço!\n\n"
            f"Essas informações são o coração das integrações da DECIPEX. "
            f"Agora essa base está totalmente mapeada.\n\n"
            f"🏆 Como reconhecimento, deixei um pequeno presente pra você — "
            f"um símbolo do quanto seu trabalho ajuda a tornar o serviço público mais eficiente e inteligente. 💛"
        )
        return resposta, sm

    def _processar_documentos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa lista estruturada de documentos com formulário interativo.

        Aceita JSON estruturado do DocumentosForm.tsx:
        {
          "documentos": [
            {
              "tipo": "Formulário de Requerimento",
              "origem": "gerado",
              "detalhes": "Campos: nome, CPF, tipo de auxílio"
            },
            {
              "tipo": "Tela de sistema SEI",
              "origem": "recebido",
              "detalhes": "Comprovante de tramitação"
            }
          ]
        }

        Frontend usa DocumentosForm.tsx com:
        - 3 campos: tipo, origem (gerado/recebido), detalhes
        - Botões: "✅ Confirmar e adicionar outro" / "🚪 Encerrar lista"
        - Numeração automática para Helena Etapas consumir
        - Animações sutis de feedback
        """
        msg_lower = mensagem.lower().strip()

        # Se vem do badge (botão "Continuar") OU é primeira vez, ativar interface de formulário
        if msg_lower == 'continuar' or not hasattr(sm, '_enviou_interface_docs'):
            sm._enviou_interface_docs = True
            sm.tipo_interface = 'documentos_form'

            # Carregar tipos de documentos do CSV
            import csv
            from pathlib import Path

            tipos_documentos = []
            csv_path = Path(__file__).parent.parent.parent.parent / 'documentos_base' / 'tipos_documentos.csv'

            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('ativo', '').lower() == 'true':
                            tipos_documentos.append({
                                'tipo': row['tipo'],
                                'ordem': int(row['ordem']),
                                'hint': row.get('hint_detalhamento', ''),
                                'descricao': row.get('descricao', '')
                            })

                # Ordenar por ordem
                tipos_documentos.sort(key=lambda x: x['ordem'])
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar tipos_documentos.csv: {e}. Usando lista padrão.")
                tipos_documentos = [
                    {'tipo': 'Formulário', 'ordem': 1, 'hint': 'Descreva os principais campos coletados'},
                    {'tipo': 'Despacho', 'ordem': 2, 'hint': 'Descreva o tipo de decisão ou encaminhamento'},
                    {'tipo': 'Ofício', 'ordem': 3, 'hint': 'Descreva o assunto do ofício'},
                    {'tipo': 'Nota Técnica', 'ordem': 4, 'hint': 'Descreva o assunto principal da nota'},
                    {'tipo': 'Nota Informativa', 'ordem': 5, 'hint': 'Descreva o conteúdo informado'},
                    {'tipo': 'Tela de sistema', 'ordem': 6, 'hint': '⚠️ Coloque a transação no detalhamento (ex: ME21N, PA30)'},
                    {'tipo': 'Outro', 'ordem': 7, 'hint': 'Especifique qual tipo de documento'}
                ]

            sm.dados_interface = {
                'tipos_documentos': tipos_documentos
            }

            resposta = (
                f"Perfeito! 🌟\n\n"
                f"Agora vamos detalhar os documentos, formulários e modelos que fazem parte da sua atividade.\n"
                f"Basta preencher e confirmar — cada item será numerado automaticamente.\n\n"
                f"Use o formulário abaixo:"
            )
            return resposta, sm

        # Processar JSON do frontend
        try:
            import json as json_lib

            # DEBUG: Log da mensagem recebida
            logger.info(f"[DEBUG DOCUMENTOS] Mensagem recebida: {mensagem[:200]}")
            logger.info(f"[DEBUG DOCUMENTOS] Flag enviou_interface_docs: {hasattr(sm, '_enviou_interface_docs')}")

            # Parsear JSON estruturado
            if mensagem.strip().startswith('{'):
                dados = json_lib.loads(mensagem.strip())
                documentos_lista = dados.get('documentos', [])
            elif msg_lower in ['[]', 'nenhum', 'nao', 'não', 'pular', 'encerrar']:
                documentos_lista = []
            else:
                # Fallback: aceitar lista direta
                documentos_lista = json_lib.loads(mensagem.strip()) if mensagem.strip().startswith('[') else []

            # Numerar automaticamente para Helena Etapas
            documentos_numerados = []
            for i, doc in enumerate(documentos_lista, 1):
                doc_numerado = {
                    **doc,
                    'numero': i,
                    'descricao_formatada': f"{i}. {doc.get('tipo', 'Documento')} ({doc.get('origem', '—')})"
                }
                documentos_numerados.append(doc_numerado)

            sm.dados_coletados['documentos'] = documentos_numerados
            sm.tipo_interface = 'entrada_processo'  # Nova interface estruturada
            sm.dados_interface = {
                'areas_organizacionais': self._carregar_areas_organizacionais(),
                'orgaos_centralizados': self._carregar_orgaos_centralizados()
            }
            del sm._enviou_interface_docs

            # Avançar para fluxos (entrada do processo)
            sm.estado = EstadoPOP.FLUXOS

            resposta = (
                f"👏 Ótimo trabalho até aqui!\n\n"
                f"Registrei {len(documentos_numerados)} documento(s). ✅\n\n"
                "Agora quero entender como o seu processo começa — ou seja, de onde ele vem antes de chegar até você.\n\n"
                "💡 Pense assim: toda atividade tem um 'ponto de partida'.\n"
                "Pode ser uma demanda de outro setor, um pedido do usuário, ou até uma orientação de controle, como CGU ou TCU.\n\n"
                "Me conta, de onde costuma vir o processo que você executa?"
            )
            return resposta, sm

        except Exception as e:
            import traceback
            logger.error(f"[ERRO DOCUMENTOS] Erro ao processar documentos: {e}")
            logger.error(f"[ERRO DOCUMENTOS] Traceback: {traceback.format_exc()}")
            logger.error(f"[ERRO DOCUMENTOS] Mensagem original: {mensagem[:500]}")
            # Erro - pedir novamente
            sm.tipo_interface = 'documentos_form'
            sm.dados_interface = {}

            resposta = (
                "[ERRO] Erro ao processar documentos. Por favor, use o formulário para adicionar os documentos.\n\n"
                "Se não houver documentos, clique em 'Encerrar lista'."
            )
            return resposta, sm

    def _processar_fluxos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de fluxos (entrada e saída)"""
        msg_lower = mensagem.lower().strip()

        # Se ainda não coletou fluxos de entrada
        if not sm.dados_coletados.get('fluxos_entrada'):
            # Limpar interface após seleção
            sm.tipo_interface = None
            sm.dados_interface = {}

            if msg_lower in ['nenhum', 'nao', 'não', 'nao sei']:
                sm.dados_coletados['fluxos_entrada'] = []
            else:
                # Processar resposta (pode ser simples ou separada por |)
                fluxos = [f.strip() for f in mensagem.replace('\n', ',').split('|') if f.strip()]
                sm.dados_coletados['fluxos_entrada'] = fluxos

            resposta = (
                f"Perfeito! Registrei {len(sm.dados_coletados['fluxos_entrada'])} origem(ns) de entrada. ✅\n\n"
                "E para onde VAI o resultado desta atividade depois que você conclui?\n\n"
                "Ex: 'Para outra área da DECIPEX', 'Devolvido ao servidor', 'Publicado no DOU'\n\n"
                "Digite os destinos de saída (separados por vírgula ou digite 'nenhum'):"
            )
        else:
            # Coletar fluxos de saída
            if msg_lower in ['nenhum', 'nao', 'não']:
                sm.dados_coletados['fluxos_saida'] = []
            else:
                fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]
                sm.dados_coletados['fluxos_saida'] = fluxos

            # Ir para PONTOS_ATENCAO (último campo antes da revisão)
            sm.estado = EstadoPOP.PONTOS_ATENCAO
            nome = sm.nome_usuario or "você"

            resposta = (
                f"Ótimo! Registrei {len(sm.dados_coletados['fluxos_saida'])} fluxo(s) de saída.\n\n"
                f"Agora terminamos de mapear nosso processo, {nome}! Mas falta um último ponto importante pra refletirmos juntos.\n\n"
                f"🚨 **PONTOS DE ATENÇÃO**\n\n"
                f"Ao pensar na sua atividade, tem algo que você acha importante chamar atenção?\n\n"
                f"Essa é a hora de dizer pra quem for usar seu POP: **PRESTE ATENÇÃO NESSE PONTO!**\n\n"
                f"Ex: 'Auditar situação desde centralização', 'Observar prazos de retroatividade'\n\n"
                f"Digite os pontos de atenção ou 'nenhum' se não houver:"
            )

        return resposta, sm

    def _processar_pontos_atencao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pontos de atenção (último campo antes da revisão)

        Após coletar, vai para REVISAO_PRE_DELEGACAO
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

        # Aceitar respostas negativas
        if msg_lower in ['não', 'nao', 'nenhum', 'não há', 'nao ha', 'não tem', 'nao tem', 'sem pontos', 'pular', 'skip']:
            sm.dados_coletados['pontos_atencao'] = "Não há pontos especiais de atenção."
        else:
            sm.dados_coletados['pontos_atencao'] = mensagem.strip()

        # Ir para REVISAO_PRE_DELEGACAO
        sm.estado = EstadoPOP.REVISAO_PRE_DELEGACAO

        # Gerar código CAP se ainda não foi gerado
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Gerar resumo completo
        resumo = self._gerar_resumo_pop(sm)

        resposta = (
            f"Perfeito, {nome}! Seu POP está completo!\n\n"
            f"{resumo}\n\n"
            f"**Deseja alterar algo ou podemos seguir para as etapas detalhadas?**\n\n"
            f"• Digite **'tudo certo'** ou **'seguir'** para continuar\n"
            f"• Digite **'editar'** se quiser alterar algum campo"
        )

        # Interface com botões
        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Tudo certo, pode seguir ✅',
            'botao_editar': 'Deixa eu arrumar uma coisa ✏️',
            'valor_confirmar': 'SEGUIR',
            'valor_editar': 'EDITAR'
        }

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
            # Usuário confirmou - avançar para delegação com troféu
            sm.estado = EstadoPOP.DELEGACAO_ETAPAS

            resposta = (
                f"🏆 **PRIMEIRA FASE CONCLUÍDA!** 🏆\n\n"
                f"{nome}, você está indo muito bem!\n\n"
                f"Agora a Helena especializada em etapas vai te guiar no detalhamento operacional.\n\n"
                f"**Iniciando mapeamento de etapas...** 🎯"
            )

            return resposta, sm

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
            '6': ('Documentos de Entrada', EstadoPOP.DOCUMENTOS),
            '7': ('Documentos de Saída', EstadoPOP.DOCUMENTOS),
            '8': ('Fluxos Entrada/Saída', EstadoPOP.FLUXOS),
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
        """Processa delegação para Helena Etapas"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['ok', 'continuar', 'sim', 'vamos', 'próximo']):
            sm.concluido = True
            sm.estado = EstadoPOP.FINALIZADO

            resposta = (
                f"Perfeito, {sm.nome_usuario}! Os dados iniciais do processo foram coletados com sucesso.\n\n"
                "Agora vou transferir você para o Helena Etapas para detalharmos cada etapa operacional.\n\n"
                "Até logo!"
            )
        else:
            resposta = (
                "Não entendi. Digite 'ok' ou 'continuar' para prosseguir para o detalhamento das etapas."
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
            logger.info(f"🔍 [CAP] Buscando no CSV:")
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
                logger.info(f"✅ [CAP] Encontrado no CSV: {codigo_csv}")
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
            elif 'codigo' in self.arquitetura.df.columns and not linha.empty:
                codigo_csv = linha['codigo'].iloc[0]
                logger.info(f"✅ [CAP] Encontrado no CSV: {codigo_csv}")
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
            else:
                logger.warning(f"⚠️ [CAP] NÃO encontrado no CSV com match exato. Gerando por índice.")
        except Exception as e:
            logger.error(f"❌ [CAP] Erro ao buscar no CSV: {e}")
            pass

        # Gerar código baseado em índices hierárquicos
        try:
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
            "operadores": dados.get("operadores", []),
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
            EstadoPOP.DOCUMENTOS: "documentos",
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
