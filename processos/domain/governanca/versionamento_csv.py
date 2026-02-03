"""
Versionamento do CSV de Arquitetura

Responsabilidade única: controle de versões e auditoria do CSV de atividades.
"""

import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

import pandas as pd

from processos.models_new import AtividadeSugerida, HistoricoAtividade

logger = logging.getLogger(__name__)


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
