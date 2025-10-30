#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FASE 6 - TESTE DE INTEGRAÇÃO COMPLETO
Valida o fluxo completo: Nome → Transição Épica → Handoff → PDF

Execute com:
    python processos/test_fluxo_completo_fase6.py

Ou com Django:
    python manage.py test processos.test_fluxo_completo_fase6
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
django.setup()

from processos.domain.helena_produtos.helena_pop import HelenaPOP, POPStateMachine, EstadoPOP


class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_secao(titulo):
    """Imprime título de seção"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{titulo.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_sucesso(msg):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")


def print_erro(msg):
    """Imprime mensagem de erro"""
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")


def print_info(msg):
    """Imprime mensagem informativa"""
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")


def print_aviso(msg):
    """Imprime aviso"""
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")


def verificar_estado(sm, estado_esperado, descricao):
    """Verifica se está no estado esperado"""
    if sm.estado == estado_esperado:
        print_sucesso(f"{descricao} - Estado: {estado_esperado.value}")
        return True
    else:
        print_erro(f"{descricao} - Esperado: {estado_esperado.value}, Obtido: {sm.estado.value}")
        return False


def testar_fluxo_completo():
    """
    Testa o fluxo completo de ponta a ponta

    Estados a testar (21 no total):
    1. NOME_USUARIO
    2. CONFIRMA_NOME
    3. ESCOLHA_TIPO_EXPLICACAO
    4. PEDIDO_COMPROMISSO
    5. AREA_DECIPEX
    6. SUBAREA_DECIPEX (se aplicável)
    7. ARQUITETURA
    8. CONFIRMACAO_ARQUITETURA
    9. NOME_PROCESSO
    10. ENTREGA_ESPERADA
    11. CONFIRMACAO_ENTREGA (se aplicável)
    12. RECONHECIMENTO_ENTREGA (se aplicável)
    13. DISPOSITIVOS_NORMATIVOS
    14. OPERADORES
    15. SISTEMAS
    16. FLUXOS (entrada e saída)
    17. PONTOS_ATENCAO
    18. REVISAO_PRE_DELEGACAO
    19. TRANSICAO_EPICA
    20. DELEGACAO_ETAPAS
    """

    print_secao("FASE 6 - TESTE DE INTEGRAÇÃO COMPLETO")
    print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    helena = HelenaPOP()
    erros = []
    sucessos = 0
    total_transicoes = 0

    # ========================================
    # ETAPA 1: NOME_USUARIO
    # ========================================
    print_secao("ETAPA 1: Coleta de Nome")

    resultado = helena.processar("João", POPStateMachine().to_dict())
    sm = POPStateMachine()
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    if verificar_estado(sm, EstadoPOP.CONFIRMA_NOME, "Nome fornecido"):
        sucessos += 1
        if sm.nome_temporario == "João":
            print_sucesso(f"Nome temporário armazenado: {sm.nome_temporario}")
        else:
            erros.append("Nome temporário não armazenado corretamente")
            print_erro("Nome temporário não armazenado")
    else:
        erros.append("Falha na transição NOME_USUARIO → CONFIRMA_NOME")

    # ========================================
    # ETAPA 2: CONFIRMA_NOME
    # ========================================
    print_secao("ETAPA 2: Confirmação de Nome")

    resultado = helena.processar("sim", sm.to_dict())
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    if verificar_estado(sm, EstadoPOP.ESCOLHA_TIPO_EXPLICACAO, "Nome confirmado"):
        sucessos += 1
        if sm.nome_usuario == "João":
            print_sucesso(f"Nome usuário confirmado: {sm.nome_usuario}")
        else:
            erros.append("Nome usuário não confirmado")
            print_erro("Nome usuário não salvo")
    else:
        erros.append("Falha na transição CONFIRMA_NOME → ESCOLHA_TIPO_EXPLICACAO")

    # ========================================
    # ETAPA 3: ESCOLHA_TIPO_EXPLICACAO
    # ========================================
    print_secao("ETAPA 3: Tipo de Explicação")

    resultado = helena.processar("curta", sm.to_dict())
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    if verificar_estado(sm, EstadoPOP.PEDIDO_COMPROMISSO, "Explicação curta escolhida"):
        sucessos += 1

        # Verificar se tem badge de Cartógrafo
        if 'metadados' in resultado and 'badge' in resultado.get('metadados', {}):
            print_aviso("Badge ainda não deve aparecer (aparece ao aceitar compromisso)")
    else:
        erros.append("Falha na transição ESCOLHA_TIPO_EXPLICACAO → PEDIDO_COMPROMISSO")

    # ========================================
    # ETAPA 4: PEDIDO_COMPROMISSO
    # ========================================
    print_secao("ETAPA 4: Aceitar Compromisso")

    resultado = helena.processar("sim", sm.to_dict())
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    if verificar_estado(sm, EstadoPOP.AREA_DECIPEX, "Compromisso aceito"):
        sucessos += 1

        # Verificar badge de Cartógrafo
        if 'metadados' in resultado and 'badge' in resultado.get('metadados', {}):
            badge = resultado['metadados']['badge']
            if badge.get('tipo') == 'cartografo_iniciante':
                print_sucesso(f"Badge Cartógrafo detectado: {badge['titulo']}")
                print_info(f"Emoji: {badge['emoji']} | Animação: {badge['mostrar_animacao']}")
            else:
                erros.append("Badge com tipo incorreto")
                print_erro(f"Badge tipo incorreto: {badge.get('tipo')}")
        else:
            erros.append("Badge de Cartógrafo não encontrado")
            print_erro("Badge não encontrado após aceitar compromisso")
    else:
        erros.append("Falha na transição PEDIDO_COMPROMISSO → AREA_DECIPEX")

    # ========================================
    # ETAPA 5: AREA_DECIPEX
    # ========================================
    print_secao("ETAPA 5: Seleção de Área")

    resultado = helena.processar("1", sm.to_dict())  # Seleciona DIGEP
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    # Pode ir para SUBAREA_DECIPEX ou ARQUITETURA
    if sm.estado in [EstadoPOP.SUBAREA_DECIPEX, EstadoPOP.ARQUITETURA]:
        sucessos += 1
        print_sucesso(f"Área selecionada: {sm.area_selecionada.get('nome', 'N/A')}")

        if sm.estado == EstadoPOP.SUBAREA_DECIPEX:
            print_info("DIGEP tem subáreas, indo para SUBAREA_DECIPEX")

            # ========================================
            # ETAPA 6: SUBAREA_DECIPEX (condicional)
            # ========================================
            print_secao("ETAPA 6: Seleção de Subárea")

            resultado = helena.processar("1", sm.to_dict())
            sm.from_dict(resultado['novo_estado'])

            total_transicoes += 1
            if verificar_estado(sm, EstadoPOP.ARQUITETURA, "Subárea selecionada"):
                sucessos += 1
                print_sucesso(f"Subárea: {sm.subarea_selecionada}")
            else:
                erros.append("Falha na transição SUBAREA_DECIPEX → ARQUITETURA")
    else:
        erros.append(f"Falha na transição AREA_DECIPEX → Estado inesperado: {sm.estado.value}")

    # ========================================
    # ETAPA 7: ARQUITETURA (com IA/CSV)
    # ========================================
    print_secao("ETAPA 7: Arquitetura (IA sugere classificação)")

    resultado = helena.processar("Analiso documentos de aposentadoria", sm.to_dict())
    sm.from_dict(resultado['novo_estado'])

    total_transicoes += 1
    if verificar_estado(sm, EstadoPOP.CONFIRMACAO_ARQUITETURA, "IA sugeriu classificação"):
        sucessos += 1
        print_info(f"Macro: {sm.macro_selecionado}")
        print_info(f"Processo: {sm.processo_selecionado}")
        print_info(f"Subprocesso: {sm.subprocesso_selecionado}")
        print_info(f"Atividade: {sm.atividade_selecionada}")
    else:
        # Pode ter ido para SELECAO_HIERARQUICA (edição manual)
        if sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            print_aviso("Foi para seleção manual (CSV/IA não encontrou)")
            sucessos += 1
        else:
            erros.append("Falha na transição ARQUITETURA → CONFIRMACAO_ARQUITETURA")

    # ========================================
    # ETAPA 8: CONFIRMACAO_ARQUITETURA
    # ========================================
    print_secao("ETAPA 8: Confirmar Arquitetura")

    if sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
        resultado = helena.processar("sim", sm.to_dict())
        sm.from_dict(resultado['novo_estado'])

        total_transicoes += 1
        if verificar_estado(sm, EstadoPOP.NOME_PROCESSO, "Arquitetura confirmada"):
            sucessos += 1
        else:
            erros.append("Falha na transição CONFIRMACAO_ARQUITETURA → NOME_PROCESSO")

    # ========================================
    # ETAPAS 9-17: Coletar todos os dados
    # ========================================
    dados_teste = {
        EstadoPOP.NOME_PROCESSO: ("Análise de Documentos Previdenciários", EstadoPOP.ENTREGA_ESPERADA),
        EstadoPOP.ENTREGA_ESPERADA: ("Parecer técnico de análise", EstadoPOP.DISPOSITIVOS_NORMATIVOS),
        EstadoPOP.DISPOSITIVOS_NORMATIVOS: ("Lei 8.112/90", EstadoPOP.OPERADORES),
        EstadoPOP.OPERADORES: (json.dumps(["EXECUTOR", "REVISOR"]), EstadoPOP.SISTEMAS),
        EstadoPOP.SISTEMAS: (json.dumps(["SISAC"]), EstadoPOP.FLUXOS),
        EstadoPOP.FLUXOS: ("Protocolo", EstadoPOP.PONTOS_ATENCAO),
        EstadoPOP.PONTOS_ATENCAO: ("Verificar prazo de prescrição", EstadoPOP.REVISAO_PRE_DELEGACAO),
    }

    for estado_atual, (mensagem, proximo_estado) in dados_teste.items():
        if sm.estado == estado_atual:
            print_secao(f"ETAPA: {estado_atual.value.upper()}")

            resultado = helena.processar(mensagem, sm.to_dict())
            sm.from_dict(resultado['novo_estado'])

            total_transicoes += 1
            if verificar_estado(sm, proximo_estado, f"{estado_atual.value} → {proximo_estado.value}"):
                sucessos += 1
            else:
                erros.append(f"Falha na transição {estado_atual.value} → {proximo_estado.value}")

    # ========================================
    # ETAPA 18: REVISAO_PRE_DELEGACAO
    # ========================================
    print_secao("ETAPA 18: Revisão Pré-Delegação")

    if sm.estado == EstadoPOP.REVISAO_PRE_DELEGACAO:
        resultado = helena.processar("tudo certo", sm.to_dict())
        sm.from_dict(resultado['novo_estado'])

        total_transicoes += 1
        if verificar_estado(sm, EstadoPOP.TRANSICAO_EPICA, "Revisão concluída"):
            sucessos += 1
        else:
            erros.append("Falha na transição REVISAO_PRE_DELEGACAO → TRANSICAO_EPICA")

    # ========================================
    # ETAPA 19: TRANSICAO_EPICA (CRÍTICO!)
    # ========================================
    print_secao("ETAPA 19: TRANSIÇÃO ÉPICA - BADGE DE CONQUISTA")

    if sm.estado == EstadoPOP.TRANSICAO_EPICA:
        # Verificar badge de Fase Prévia Concluída
        if 'metadados' in resultado and 'badge' in resultado.get('metadados', {}):
            badge = resultado['metadados']['badge']
            if badge.get('tipo') == 'fase_previa_completa':
                print_sucesso(f"✅ Badge Fase Prévia Concluída detectado!")
                print_info(f"   Título: {badge['titulo']}")
                print_info(f"   Emoji: {badge['emoji']}")
                print_info(f"   Descrição: {badge['descricao']}")
                print_info(f"   Animação: {badge['mostrar_animacao']}")
                sucessos += 1
            else:
                erros.append("Badge com tipo incorreto na Transição Épica")
                print_erro(f"Badge tipo incorreto: {badge.get('tipo')}")
        else:
            erros.append("Badge de Transição Épica não encontrado")
            print_erro("❌ Badge não encontrado na Transição Épica")

        # Avançar para delegação
        resultado = helena.processar("VAMOS", sm.to_dict())
        sm.from_dict(resultado['novo_estado'])

        total_transicoes += 1
        if verificar_estado(sm, EstadoPOP.DELEGACAO_ETAPAS, "Transição Épica concluída"):
            sucessos += 1
        else:
            erros.append("Falha na transição TRANSICAO_EPICA → DELEGACAO_ETAPAS")
    else:
        erros.append("Não chegou na Transição Épica")
        print_erro(f"Estado atual: {sm.estado.value}, esperado: TRANSICAO_EPICA")

    # ========================================
    # ETAPA 20: DELEGACAO_ETAPAS (Handoff)
    # ========================================
    print_secao("ETAPA 20: DELEGAÇÃO PARA HELENA ETAPAS")

    if sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
        # Verificar se contexto está preparado
        formulario_pop = resultado.get('formulario_pop', {})

        print_info("Verificando dados preparados para Helena Etapas:")

        campos_essenciais = [
            'nome_processo',
            'entrega_esperada',
            'macro',
            'processo',
            'subprocesso',
            'atividade'
        ]

        campos_presentes = []
        campos_faltando = []

        for campo in campos_essenciais:
            if formulario_pop.get(campo):
                campos_presentes.append(campo)
                print_sucesso(f"   {campo}: ✓")
            else:
                campos_faltando.append(campo)
                print_erro(f"   {campo}: ✗")

        if not campos_faltando:
            print_sucesso("Todos os campos essenciais estão presentes!")
            sucessos += 1
        else:
            erros.append(f"Campos faltando para handoff: {', '.join(campos_faltando)}")
            print_erro(f"Campos faltando: {', '.join(campos_faltando)}")

        # Verificar se pode gerar PDF parcial
        print_info("\nVerificando possibilidade de gerar PDF pré-etapas:")

        campos_pdf = ['nome_processo', 'entrega_esperada', 'area']
        pode_gerar_pdf = all(formulario_pop.get(campo) for campo in campos_pdf)

        if pode_gerar_pdf:
            print_sucesso("✓ Dados suficientes para gerar PDF pré-etapas")
            sucessos += 1
        else:
            erros.append("Dados insuficientes para gerar PDF")
            print_erro("✗ Dados insuficientes para PDF")
    else:
        erros.append("Não chegou na Delegação de Etapas")
        print_erro(f"Estado atual: {sm.estado.value}, esperado: DELEGACAO_ETAPAS")

    # ========================================
    # RELATÓRIO FINAL
    # ========================================
    print_secao("RELATÓRIO FINAL")

    taxa_sucesso = (sucessos / total_transicoes * 100) if total_transicoes > 0 else 0

    print(f"\n{Colors.BOLD}Total de transições testadas:{Colors.ENDC} {total_transicoes}")
    print(f"{Colors.BOLD}Sucessos:{Colors.ENDC} {sucessos}")
    print(f"{Colors.BOLD}Erros:{Colors.ENDC} {len(erros)}")
    print(f"{Colors.BOLD}Taxa de sucesso:{Colors.ENDC} {taxa_sucesso:.1f}%\n")

    if erros:
        print_erro("ERROS ENCONTRADOS:")
        for i, erro in enumerate(erros, 1):
            print(f"  {i}. {erro}")
        print()

    # Verificação final dos 4 itens da Fase 6
    print_secao("CHECKLIST FASE 6")

    checklist = {
        "✅ Fluxo completo sem erros": len(erros) == 0,
        "✅ Badge de transição funcional": 'fase_previa_completa' in str(resultado.get('metadados', {})),
        "✅ Contexto etapas criado": sm.estado == EstadoPOP.DELEGACAO_ETAPAS,
        "✅ PDF pode ser gerado": pode_gerar_pdf if sm.estado == EstadoPOP.DELEGACAO_ETAPAS else False
    }

    for item, status in checklist.items():
        if status:
            print_sucesso(item)
        else:
            print_erro(item.replace("✅", "❌"))

    print()

    if all(checklist.values()):
        print_sucesso(f"{Colors.BOLD}🎉 FASE 6 CONCLUÍDA COM SUCESSO! 🎉{Colors.ENDC}")
        return 0
    else:
        print_erro(f"{Colors.BOLD}⚠️ FASE 6 INCOMPLETA - Revisar itens faltantes{Colors.ENDC}")
        return 1


if __name__ == '__main__':
    sys.exit(testar_fluxo_completo())
