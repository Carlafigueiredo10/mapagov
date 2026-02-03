# -*- coding: utf-8 -*-
"""
===============================================================================
Script para pre-computar embeddings do corpus de atividades DECIPEX
===============================================================================

USO:
    python scripts/gerar_embeddings_corpus.py

SAIDA (3 arquivos):
    documentos_base/corpus_embeddings.npy   - matriz float32 normalizada
    documentos_base/corpus_meta.json        - metadados de cada atividade
    documentos_base/corpus_fingerprint.json - hash do CSV + modelo

QUANDO RODAR:
    - Quando o CSV de atividades mudar
    - Apos adicionar novas atividades ao catalogo
    - Commitar os 3 arquivos JUNTOS no repositorio

REGRAS:
    - Ordem dos vetores == ordem do corpus_meta.json
    - Vetores ja normalizados (prontos para cosine)
    - fingerprint permite validar alinhamento

===============================================================================
"""

import numpy as np
import pandas as pd
import json
import hashlib
import os
import sys
from datetime import datetime

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def calcular_hash_arquivo(filepath: str) -> str:
    """Calcula SHA256 de um arquivo."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # Primeiros 16 chars


def gerar_embeddings():
    """Gera embeddings do corpus e salva em 3 arquivos."""

    print("=" * 70)
    print("[EMBEDDINGS] GERADOR DE EMBEDDINGS - Helena POP v4.0")
    print("=" * 70)

    # Paths
    csv_path = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv'
    embeddings_path = 'documentos_base/corpus_embeddings.npy'
    meta_path = 'documentos_base/corpus_meta.json'
    fingerprint_path = 'documentos_base/corpus_fingerprint.json'

    model_name = 'paraphrase-multilingual-MiniLM-L12-v2'

    # 1. Carregar CSV
    print(f"\n[1] Carregando CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    df = df.fillna('')
    print(f"    [OK] {len(df)} atividades carregadas")

    # 2. Calcular hash do CSV (para fingerprint)
    csv_hash = calcular_hash_arquivo(csv_path)
    print(f"    Hash do CSV: {csv_hash}")

    # 3. Preparar corpus_meta.json (metadados alinhados com embeddings)
    print("\n[2] Preparando metadados do corpus...")
    corpus_meta = []
    corpus_textos = []

    for idx, row in df.iterrows():
        texto = f"{row['Macroprocesso']} {row['Processo']} {row['Subprocesso']} {row['Atividade']}"
        texto = texto.strip()

        meta = {
            'idx': int(idx),
            'numero': str(row.get('Numero', '')).strip(),
            'texto': texto,
            'macroprocesso': row['Macroprocesso'],
            'processo': row['Processo'],
            'subprocesso': row['Subprocesso'],
            'atividade': row['Atividade']
        }
        corpus_meta.append(meta)
        corpus_textos.append(texto)

    print(f"    [OK] {len(corpus_meta)} metadados preparados")

    # 4. Carregar modelo
    print("\n[3] Carregando modelo SentenceTransformer...")
    print(f"    ({model_name})")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    print("    [OK] Modelo carregado")

    # 5. Gerar embeddings normalizados
    print("\n[4] Gerando embeddings do corpus...")
    print("    (isso pode demorar alguns segundos)")
    embeddings = model.encode(
        corpus_textos,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True  # Ja normaliza para busca por cosine
    )
    embeddings = embeddings.astype(np.float32)
    print(f"    [OK] Shape: {embeddings.shape}")
    print(f"    [OK] Dtype: {embeddings.dtype}")

    # 6. Salvar corpus_embeddings.npy
    print(f"\n[5] Salvando embeddings: {embeddings_path}")
    np.save(embeddings_path, embeddings)
    emb_size = os.path.getsize(embeddings_path) / (1024 * 1024)
    print(f"    [OK] {emb_size:.2f} MB")

    # 7. Salvar corpus_meta.json
    print(f"\n[6] Salvando metadados: {meta_path}")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(corpus_meta, f, ensure_ascii=False, indent=2)
    meta_size = os.path.getsize(meta_path) / 1024
    print(f"    [OK] {meta_size:.1f} KB")

    # 8. Salvar corpus_fingerprint.json
    print(f"\n[7] Salvando fingerprint: {fingerprint_path}")
    fingerprint = {
        'csv_path': csv_path,
        'csv_hash': csv_hash,
        'model_name': model_name,
        'n_atividades': len(df),
        'embedding_dim': int(embeddings.shape[1]),
        'gerado_em': datetime.now().isoformat(),
        'versao': '4.0'
    }
    with open(fingerprint_path, 'w', encoding='utf-8') as f:
        json.dump(fingerprint, f, ensure_ascii=False, indent=2)
    print("    [OK] Fingerprint salvo")

    # 9. Validacao cruzada
    print("\n[8] Validando alinhamento...")
    assert len(corpus_meta) == embeddings.shape[0], "ERRO: metadados e embeddings desalinhados!"
    print(f"    [OK] {len(corpus_meta)} metadados == {embeddings.shape[0]} embeddings")

    # 10. Teste rapido de busca
    print("\n[9] Teste rapido de busca...")
    query = "demandas judiciais"
    query_emb = model.encode(query, normalize_embeddings=True)
    scores = np.dot(embeddings, query_emb)
    top_idx = np.argmax(scores)
    top_score = scores[top_idx]
    top_meta = corpus_meta[top_idx]
    print(f"    Query: '{query}'")
    print(f"    Top match: '{top_meta['atividade']}' (score: {top_score:.3f})")

    print("\n" + "=" * 70)
    print("[OK] EMBEDDINGS GERADOS COM SUCESSO!")
    print("=" * 70)
    print(f"\nArquivos gerados:")
    print(f"   1. {embeddings_path} ({emb_size:.2f} MB)")
    print(f"   2. {meta_path} ({meta_size:.1f} KB)")
    print(f"   3. {fingerprint_path}")
    print(f"\nProximo passo: commitar os 3 arquivos JUNTOS")
    print("   git add documentos_base/corpus_embeddings.npy")
    print("   git add documentos_base/corpus_meta.json")
    print("   git add documentos_base/corpus_fingerprint.json")
    print("   git commit -m 'feat: embeddings pre-computados v4.0'")
    print("   git push")


if __name__ == '__main__':
    gerar_embeddings()
