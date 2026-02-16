#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste: Verificar carregamento de áreas do CSV

Uso: python test_areas_csv.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
django.setup()

from processos.domain.helena_produtos.helena_pop import HelenaPOP

print("=" * 80)
print("TESTE: Carregamento de Áreas Organizacionais do CSV")
print("=" * 80)

# Criar instância de HelenaPOP
helena = HelenaPOP()

# Verificar áreas carregadas
areas = helena.AREAS_DECIPEX
print(f"\n✅ Total de áreas carregadas: {len(areas)}\n")

# Mostrar todas as áreas
for num, info in areas.items():
    print(f"{num}. {info['codigo']:10} | {info['nome']}")

# Verificar se há nomes errados
nomes_errados = ['REVESTIMENTO', 'DIGERIR']
print(f"\n🔍 Verificando se há nomes errados...")
for num, info in areas.items():
    if any(erro in info['nome'].upper() for erro in nomes_errados):
        print(f"❌ ERRO ENCONTRADO: {info['codigo']} - {info['nome']}")
    if any(erro in info['codigo'].upper() for erro in nomes_errados):
        print(f"❌ ERRO ENCONTRADO: {info['codigo']} - {info['nome']}")

print("\n✅ Teste concluído!")
print("=" * 80)
