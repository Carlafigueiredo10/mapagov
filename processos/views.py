# processos/views.py - Sistema Multi-Produto Helena com LangChain + PDF + Sessão Persistente

import json
import openai
import os
import logging
import time
import uuid as uuid_mod
from dotenv import load_dotenv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import pypdf
from datetime import datetime
from django.utils import timezone

from .models import POP, PopDraft

# Logger
logger = logging.getLogger(__name__)

# ⚡ OTIMIZAÇÃO MEMÓRIA: analyze_risks_helena movido para lazy import (não usado no startup)
# from .domain.helena_produtos.helena_analise_riscos import analyze_risks_helena
from .utils import (
    ValidadorUtils, FormatadorUtils, CodigoUtils,
    ArquivoUtils, LogUtils, SegurancaUtils,
    validar_entrada_helena, preparar_dados_para_pdf,
    PDFGenerator  # ← ADICIONADO
)

# ============================================================================
# VIEWS ANTIGAS REMOVIDAS - MIGRADAS PARA REACT
# ============================================================================
# Todas as views de templates (landing, portal, chat, etc.) foram removidas.
# O frontend agora é 100% React, servido pelo catch-all do mapagov/urls.py
# ============================================================================
# APIs - CHAT COM HELENA (SISTEMA MULTI-PRODUTO) - VERSÃO COM SESSÃO PERSISTENTE
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_api_view(request):
    """API para conversa com Helena - Sistema Multi-Produto com Sessão Persistente"""

    # --- Diagnóstico: req_id + timing ---
    req_id = str(uuid_mod.uuid4())[:8]
    t0 = time.monotonic()
    body_len = len(request.body) if request.body else 0

    try:
        load_dotenv()

        # Receber dados do JavaScript
        data = json.loads(request.body)
        user_message = data.get('message', '')
        contexto = data.get('contexto', 'geral')
        dados_atuais = data.get('dados_atuais', {})
        session_id = data.get('session_id', 'default')

        # Contagem de etapas no payload (diagnóstico bug 7-etapas)
        n_etapas = 0
        try:
            msg_parsed = json.loads(user_message) if user_message.strip().startswith('{') else None
            if isinstance(msg_parsed, dict):
                etapas_list = msg_parsed.get('etapas', [])
                if isinstance(etapas_list, list):
                    n_etapas = len(etapas_list)
        except (json.JSONDecodeError, TypeError):
            pass

        logger.info(
            "[DIAG] req=%s body=%dB ctx=%s n_etapas=%d sid=...%s",
            req_id, body_len, contexto, n_etapas, str(session_id)[-6:]
        )
        
        # Validação de entrada com segurança
        valido, msg_erro = validar_entrada_helena(user_message)
        if not valido:
            return JsonResponse({
                'resposta': f'Entrada inválida: {msg_erro}',
                'erro': 'VALIDACAO_FALHOU'
            }, status=400)
        
        # Log da interação
        log_entrada = LogUtils.criar_log_entrada(
            usuario=session_id,
            acao="chat_helena",
            dados={"contexto": contexto, "tamanho_mensagem": len(user_message)}
        )
        
        # ========== ROTEAMENTO POR PRODUTO (COM SESSÃO PERSISTENTE) ==========
        
        # HELENA MAPEAMENTO: Chat simples, sem sessão persistente
        if contexto == 'mapeamento':
            # OTIMIZACAO: Import lazy
            from .domain.helena_mapeamento.helena_mapeamento import helena_mapeamento
            resposta = helena_mapeamento(user_message)
            return JsonResponse({'resposta': resposta, 'success': True})
        
        # P1: Gerador de POP (RENOVADO - API v2.0 com POPStateMachine)
        # ✅ ROTEADOR POP <-> ETAPAS (transição invisível)
        if contexto in ['gerador_pop', 'mapeamento_natural']:
            # Constantes de modo
            MODO_POP = 'pop'
            MODO_ETAPAS = 'etapas'

            # OTIMIZACAO: Import lazy - so carrega quando necessario
            from .domain.helena_mapeamento.helena_pop import HelenaPOP, POPStateMachine
            from .domain.helena_mapeamento.helena_etapas import HelenaEtapas

            # FIX: Usar session_id do frontend para criar chave unica
            session_key = f'helena_pop_state_{session_id}'
            sid_tail = str(session_id)[-6:]

            # Obter ou criar session_data (dicionário serializado)
            if session_key not in request.session or not request.session.get(session_key):
                # Primeira mensagem - criar novo state machine vazio
                session_data = POPStateMachine().to_dict()
                logger.debug(f"[SESSAO] Nova sessão criada: {session_key}")
            else:
                # Mensagens seguintes - usar estado existente
                session_data = request.session[session_key]
                logger.debug(f"[SESSAO] Restaurada: estado={session_data.get('estado')}")

            # ✅ ROTEADOR: Verificar modo atual (pop ou etapas)
            modo_inicial = session_data.get('_helena_modo', MODO_POP)

            # Sync nome_usuario do frontend (edição no header)
            nome_frontend = data.get('nome_usuario')
            if nome_frontend and nome_frontend.strip():
                session_data['nome_usuario'] = nome_frontend.strip()

            if modo_inicial == MODO_ETAPAS:
                helena = HelenaEtapas()
                resultado = helena.processar(user_message, session_data)
            else:
                helena = HelenaPOP()
                resultado = helena.processar(user_message, session_data)

            meta = (resultado or {}).get('metadados', {})

            # ✅ TRANSIÇÃO: pop -> etapas (imediata na mesma request)
            if modo_inicial != MODO_ETAPAS and meta.get('mudar_contexto') == MODO_ETAPAS:
                logger.info(f"[HELENA] transicao=pop->etapas sid=...{sid_tail}")
                session_data['_helena_modo'] = MODO_ETAPAS
                session_data['_helena_bootstrap'] = meta.get('dados_herdados') or {}
                try:
                    helena_etapas = HelenaEtapas()
                    resultado = helena_etapas.processar(user_message, session_data)
                    meta = (resultado or {}).get('metadados', {})
                except Exception as e:
                    logger.exception(f"[HELENA] erro transicao etapas sid=...{sid_tail}")
                    session_data['_helena_modo'] = MODO_POP
                    # mantém resultado do POP

            # ✅ TRANSIÇÃO: etapas -> pop
            if meta.get('retornar_para') == MODO_POP:
                logger.info(f"[HELENA] transicao=etapas->pop sid=...{sid_tail}")
                session_data['_helena_modo'] = MODO_POP
                session_data.pop('_helena_bootstrap', None)
                session_data.pop('helena_etapas', None)

            modo_final = session_data.get('_helena_modo', MODO_POP)
            logger.debug(f"[HELENA] modo={modo_inicial} -> {modo_final}")

            # Salvar novo estado na sessão
            # ✅ SIMPLIFICADO: Em modo etapas, session_data já foi modificado in-place
            # Em modo POP, resultado['novo_estado'] contém o POPStateMachine atualizado
            if modo_final == MODO_ETAPAS:
                # helena_etapas modifica session_data['helena_etapas'] in-place
                novo_session_data = session_data
            else:
                # helena_pop retorna novo_estado com o POPStateMachine
                novo_session_data = resultado.get('novo_estado', session_data)
                # Mesclar campos do roteador (caso tenha vindo de transição etapas->pop)
                novo_session_data['_helena_modo'] = MODO_POP

            request.session[session_key] = novo_session_data

            # Forcar Django a salvar a sessao modificada
            request.session.modified = True

            # ========== DRAFT: Persistir rascunho no banco ==========
            estado_atual = novo_session_data.get('estado', '')
            try:
                if estado_atual == 'etapa_form' and user_message.strip().lower() in ('vamos', '__confirmar_dupla__', '__confirmar__'):
                    # VAMOS → criar draft vazio com dados já coletados
                    PopDraft.objects.update_or_create(
                        session_id=session_id,
                        defaults={
                            'user': request.user if request.user.is_authenticated else None,
                            'area': novo_session_data.get('area_selecionada', ''),
                            'process_code': novo_session_data.get('codigo_cap', ''),
                            'etapa_atual': estado_atual,
                            'payload_json': novo_session_data,
                        }
                    )
                    logger.info(f"[POP-DRAFT] Draft criado (VAMOS) sid=...{sid_tail}")
                elif user_message.strip().lower() in ('pausa', 'pausar', 'depois', 'mais tarde', 'salvar'):
                    # PAUSA → salvar estado atual como rascunho
                    PopDraft.objects.update_or_create(
                        session_id=session_id,
                        defaults={
                            'user': request.user if request.user.is_authenticated else None,
                            'area': novo_session_data.get('area_selecionada', ''),
                            'process_code': novo_session_data.get('codigo_cap', ''),
                            'etapa_atual': estado_atual,
                            'payload_json': novo_session_data,
                        }
                    )
                    logger.info(f"[POP-DRAFT] Draft salvo (PAUSA) sid=...{sid_tail}")
            except Exception as e:
                logger.warning(f"[POP-DRAFT] Falha ao salvar draft: {e}")

            # Log específico da Helena
            log_helena = LogUtils.log_helena_interacao(
                usuario=session_id,
                pergunta=user_message,
                resposta=resultado.get('resposta', ''),
                estado=novo_session_data.get('estado', 'unknown')
            )

            # Serialização JSON robusta
            json_str = json.dumps(resultado, ensure_ascii=False, default=str)

            return JsonResponse(
                json.loads(json_str),
                safe=False,
                json_dumps_params={"ensure_ascii": False, "indent": None}
            )
        
        # P2: Gerador de Fluxograma (com sessao)
        elif contexto == 'fluxograma':
            # OTIMIZACAO: Import lazy
            from .domain.helena_fluxograma.flowchart_orchestrator import HelenaFluxogramaOrchestrator as HelenaFluxograma
            
            session_key = 'helena_fluxograma_state'
            
            if session_key not in request.session:
                helena = HelenaFluxograma()
            else:
                helena = HelenaFluxograma()
                state = request.session[session_key]
                # Restaurar estado específico do fluxograma
                helena.estado = state.get('estado', 'inicial')
                helena.dados = state.get('dados', {})
            
            resultado = helena.processar_mensagem(user_message)
            
            # Salvar estado
            request.session[session_key] = {
                'estado': helena.estado,
                'dados': helena.dados
            }
            request.session.modified = True
            
            return JsonResponse(resultado)
        
        # P3: Dossie PDF (com sessao)
        elif contexto == 'dossie':
            # OTIMIZACAO: Import lazy
            from .domain.helena_produtos.helena_dossie import HelenaDossie
            
            session_key = 'helena_dossie_state'
            
            if session_key not in request.session:
                helena = HelenaDossie()
            else:
                helena = HelenaDossie()
                state = request.session[session_key]
                helena.estado = state.get('estado', 'inicial')
                helena.dados = state.get('dados', {})
            
            resultado = helena.processar_mensagem(user_message)
            
            request.session[session_key] = {
                'estado': helena.estado,
                'dados': helena.dados
            }
            request.session.modified = True
            
            return JsonResponse(resultado)
        
        # P4: Dashboard
        elif contexto == 'dashboard':
            # OTIMIZACAO: Import lazy
            from .domain.helena_produtos.helena_dashboard import HelenaDashboard
            helena = HelenaDashboard()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P5: Analise de Riscos (com sessao) - MODO CONVERSACIONAL HIBRIDO
        elif contexto == 'analise_riscos':
            # OTIMIZACAO: Import lazy
            from ..z_md.helena_analise_riscos import HelenaAnaliseRiscos

            session_key = 'helena_riscos_state'

            if session_key not in request.session:
                helena = HelenaAnaliseRiscos()
            else:
                helena = HelenaAnaliseRiscos()
                state = request.session[session_key]
                # Restaurar estado completo da classe conversacional
                helena.estado = state.get('estado', 'inicial')
                helena.dados_processo = state.get('dados_processo', {})
                helena.respostas_brutas = state.get('respostas_brutas', {})
                helena.respostas_normalizadas = state.get('respostas_normalizadas', {})
                helena.etapa_atual = state.get('etapa_atual', 0)
                helena.conversas = state.get('conversas', [])
                helena.pergunta_atual_idx = state.get('pergunta_atual_idx', 0)
                helena.secao_atual_idx = state.get('secao_atual_idx', 0)

            resultado = helena.processar_mensagem(user_message)

            # Salvar estado completo
            request.session[session_key] = {
                'estado': helena.estado,
                'dados_processo': helena.dados_processo,
                'respostas_brutas': helena.respostas_brutas,
                'respostas_normalizadas': helena.respostas_normalizadas,
                'etapa_atual': helena.etapa_atual,
                'conversas': helena.conversas,
                'pergunta_atual_idx': helena.pergunta_atual_idx,
                'secao_atual_idx': helena.secao_atual_idx
            }
            request.session.modified = True

            return JsonResponse(resultado)
        
        # P6: Relatório de Riscos (DESATIVADO - arquivo deletado)
        # elif contexto == 'relatorio_riscos':
        #     from .domain.helena_produtos.helena_relatorio_riscos import HelenaRelatorioRiscos
        #     helena = HelenaRelatorioRiscos()
        #     resultado = helena.processar_mensagem(user_message)
        #     return JsonResponse(resultado)
        
        # P7: Plano de Acao (MIGRADO PARA PLANEJAMENTO ESTRATÉGICO)
        elif contexto == 'plano_acao':
            # Redireciona para planejamento estratégico
            from ..z_md.helena_planejamento_estrategico import HelenaPlanejamentoEstrategico
            helena = HelenaPlanejamentoEstrategico()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P8: Dossie de Governanca
        elif contexto == 'governanca':
            # OTIMIZACAO: Import lazy
            from .domain.helena_produtos.helena_governanca import HelenaGovernanca
            helena = HelenaGovernanca()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P9: Gerador de Documentos
        elif contexto == 'documentos':
            # OTIMIZACAO: Import lazy
            from .domain.helena_produtos.helena_documentos import HelenaDocumentos
            helena = HelenaDocumentos()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P10: Relatorio de Conformidade
        elif contexto == 'conformidade':
            # OTIMIZACAO: Import lazy
            from .domain.helena_produtos.helena_conformidade import HelenaConformidade
            helena = HelenaConformidade()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P11: Análise de Artefatos (DESATIVADO - arquivo renomeado para helena_artefatos_comunicacao.py)
        # elif contexto == 'artefatos':
        #     from .domain.helena_produtos.helena_artefatos import HelenaArtefatos
        #     helena = HelenaArtefatos()
        #     resultado = helena.processar_mensagem(user_message)
        #     return JsonResponse(resultado)
        
        # Contexto não reconhecido
        else:
            return JsonResponse({
                'resposta': f'Contexto "{contexto}" não reconhecido. Use: gerador_pop, fluxograma, analise_riscos, etc.',
                'erro': 'CONTEXTO_INVALIDO'
            }, status=400)
            
    except Exception as e:
        elapsed = time.monotonic() - t0
        logger.exception(
            "[ERROR] req=%s body=%dB elapsed=%.2fs | Erro na API Helena: %s",
            req_id, body_len, elapsed, e
        )

        error_payload = {
            'resposta': 'Desculpe, ocorreu um erro técnico. Pode repetir a pergunta?',
            'dados_extraidos': {},
            'conversa_completa': False,
            'erro': str(e),
        }

        # Em DEBUG, incluir contexto para diagnóstico no frontend
        if settings.DEBUG:
            error_payload['_diag'] = {
                'req_id': req_id,
                'body_bytes': body_len,
                'elapsed_s': round(elapsed, 2),
                'exception': f"{type(e).__name__}: {e}",
            }

        return JsonResponse(error_payload, status=500)

# ============================================================================
# NOVAS APIs - PDF PROFISSIONAL PARA POP (MODIFICADO)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def helena_mapeamento_api(request):
    """
    API para conversar com a Helena Mapeamento (especialista em POP e mapeamento de processos).
    Chat simples, sem sessão persistente.
    """
    try:
        data = json.loads(request.body)
        mensagem = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not mensagem:
            return JsonResponse({
                'resposta': 'Por favor, envie uma mensagem.',
                'success': False
            }, status=400)
        
        # 🚀 OTIMIZAÇÃO: Import lazy
        from .domain.helena_mapeamento.helena_mapeamento import helena_mapeamento
        
        # Chamar Helena Mapeamento (chat simples)
        resposta = helena_mapeamento(mensagem)
        
        # Log da interação
        LogUtils.criar_log_entrada(
            usuario=session_id,
            acao="helena_mapeamento",
            dados={"tamanho_mensagem": len(mensagem)}
        )
        
        return JsonResponse({
            'resposta': resposta,
            'success': True
        })
        
    except Exception as e:
        logger.exception(f"[ERROR] Erro na Helena Mapeamento: {e}")

        return JsonResponse({
            'resposta': f'Erro ao processar mensagem: {str(e)}',
            'success': False
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def helena_ajuda_arquitetura(request):
    """
    API para Helena Ajuda Inteligente - Classificação de Atividade na Arquitetura
    Analisa descrição do usuário e sugere arquitetura completa (Macro/Processo/Subprocesso/Atividade)
    """
    try:
        data = json.loads(request.body)
        descricao = data.get('descricao', '')
        nivel_atual = data.get('nivel_atual', 'macro')
        contexto = data.get('contexto', {})
        session_id = data.get('session_id', 'default')

        if not descricao or len(descricao.strip()) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Por favor, descreva sua atividade com pelo menos 10 caracteres.'
            }, status=400)

        # Import lazy da função de análise
        from .domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena, validar_sugestao_contra_csv
        from .dados_decipex import ArquiteturaDecipex

        print(f"\n[HELENA-AJUDA] Analisando atividade...")
        print(f"   Descrição: {descricao[:100]}...")
        print(f"   Nível atual: {nivel_atual}")
        print(f"   Contexto: {contexto}")

        # Chamar Helena Ajuda Inteligente
        resultado = analisar_atividade_com_helena(
            descricao_usuario=descricao,
            nivel_atual=nivel_atual,
            contexto_ja_selecionado=contexto
        )

        if not resultado.get('sucesso'):
            return JsonResponse({
                'success': False,
                'error': resultado.get('erro', 'Erro desconhecido ao analisar atividade'),
                'resposta_bruta': resultado.get('resposta_bruta')
            }, status=500)

        # Validar sugestão contra CSV de arquitetura
        arquitetura = ArquiteturaDecipex()
        validacao = validar_sugestao_contra_csv(resultado['sugestao'], arquitetura)

        # Log da análise
        LogUtils.criar_log_entrada(
            usuario=session_id,
            acao="helena_ajuda_arquitetura",
            dados={
                "descricao_tamanho": len(descricao),
                "nivel": nivel_atual,
                "confianca": resultado.get('confianca', 'media')
            }
        )

        print(f"[HELENA-AJUDA] Sugestão gerada com sucesso!")
        print(f"   Macroprocesso: {resultado['sugestao']['macroprocesso']}")
        print(f"   Processo: {resultado['sugestao']['processo']}")
        print(f"   Subprocesso: {resultado['sugestao']['subprocesso']}")
        print(f"   Atividade: {resultado['sugestao']['atividade']}")
        print(f"   Confiança: {resultado.get('confianca', 'media')}")

        return JsonResponse({
            'success': True,
            'sugestao': resultado['sugestao'],
            'justificativa': resultado.get('justificativa', ''),
            'confianca': resultado.get('confianca', 'media'),
            'validacao': validacao
        })

    except Exception as e:
        print(f"[ERROR] Erro na Helena Ajuda Arquitetura: {e}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'error': f'Erro ao processar análise: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def gerar_pdf_pop(request):
    """API para gerar PDF profissional do POP"""
    try:
        data = json.loads(request.body)
        dados_pop = data.get('dados_pop', {})
        session_id = data.get('session_id', 'default')
        
        # Validar dados mínimos
        if not dados_pop or not dados_pop.get('nome_processo'):
            return JsonResponse({
                'error': 'Dados do POP incompletos. Nome do processo é obrigatório.',
                'success': False
            }, status=400)
        
        # Preparar dados para PDF (adapter normaliza schema novo + legado)
        from processos.export.pop_adapter import preparar_pop_para_pdf
        n_etapas_in = len(dados_pop.get('etapas', []))
        dados_limpos = preparar_pop_para_pdf(dados_pop)
        n_etapas_out = len(dados_limpos.get('etapas', []))
        if n_etapas_in > 0 and n_etapas_out == 0:
            logger.warning(f"[GUARD gerar_pdf_pop] ANOMALIA: adapter dropou etapas ({n_etapas_in} → 0)")
        elif n_etapas_in == 0:
            logger.warning(f"[GUARD gerar_pdf_pop] PDF sem etapas (frontend enviou 0)")

        # Validar estrutura completa
        campos_obrigatorios = ['nome_processo', 'area', 'entrega_esperada']
        campos_faltando = [c for c in campos_obrigatorios if not dados_limpos.get(c)]
        
        if campos_faltando:
            return JsonResponse({
                'error': f'Campos obrigatórios faltando: {", ".join(campos_faltando)}',
                'success': False
            }, status=400)
        
        # Gerar nome de arquivo seguro
        nome_arquivo = ArquivoUtils.gerar_nome_arquivo_seguro(
            dados_limpos.get('nome_processo', 'POP'), 
            'pdf'
        )
        
        # Instanciar gerador e criar PDF
        generator = PDFGenerator()
        pdf_path = generator.gerar_pop_completo(dados_limpos, nome_arquivo)
        
        # Verificar se PDF foi gerado
        if not pdf_path or not os.path.exists(pdf_path):
            return JsonResponse({
                'error': 'Erro ao gerar PDF. Verifique os logs do servidor.',
                'success': False
            }, status=500)
        
        # Log da geração
        log_pdf = LogUtils.criar_log_entrada(
            usuario=session_id,
            acao="gerar_pdf_pop",
            dados={
                "nome_processo": dados_limpos.get('nome_processo'),
                "codigo": dados_limpos.get('codigo_processo'),
                "arquivo": nome_arquivo,
                "tamanho_kb": os.path.getsize(pdf_path) / 1024
            }
        )
        
        print(f"[OK] PDF gerado com sucesso: {pdf_path}")
        
        # Retornar sucesso com URLs
        return JsonResponse({
            'success': True,
            'pdf_url': f'/api/download-pdf/{nome_arquivo}',
            'preview_url': f'/api/preview-pdf/{nome_arquivo}',
            'arquivo': nome_arquivo,
            'message': 'PDF gerado com sucesso!'
        })
        
    except Exception as e:
        import traceback
        logger.error(f"[gerar_pdf_pop] Erro ao gerar PDF: {e}\n{traceback.format_exc()}")

        return JsonResponse({
            'error': f'Erro ao gerar PDF: {str(e)}',
            'success': False
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def preview_pdf(request, nome_arquivo):
    """API para preview HTML do PDF antes do download"""
    try:
        # Validar nome do arquivo
        if not nome_arquivo.endswith('.pdf'):
            return JsonResponse({'error': 'Arquivo inválido'}, status=400)
        
        # Caminho seguro do arquivo
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', nome_arquivo)
        
        if not os.path.exists(pdf_path):
            return JsonResponse({'error': 'Arquivo não encontrado'}, status=404)
        
        # Recuperar dados do PDF da sessão (se disponível)
        session_key = 'helena_pop_state'
        dados_pop = {}
        
        if session_key in request.session:
            state = request.session[session_key]
            dados_pop = state.get('dados', {})
        
        # Renderizar template de preview
        return render(request, 'preview_pdf.html', {
            'pdf_url': f'/api/download-pdf/{nome_arquivo}',
            'nome_arquivo': nome_arquivo,
            'dados_pop': dados_pop,
            'pode_editar': True
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro no preview: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def download_pdf(request, nome_arquivo):
    """API para download do PDF gerado"""
    try:
        # Validar nome do arquivo
        if not nome_arquivo.endswith('.pdf'):
            return JsonResponse({'error': 'Arquivo inválido'}, status=400)
        
        # Caminho seguro do arquivo
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', nome_arquivo)
        
        if not os.path.exists(pdf_path):
            return JsonResponse({'error': 'Arquivo não encontrado'}, status=404)
        
        # Ler arquivo
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
            return response
            
    except Exception as e:
        return JsonResponse({'error': f'Erro no download: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def validar_dados_pop(request):
    """API para validar dados do POP em tempo real"""
    try:
        data = json.loads(request.body)
        campo = data.get('campo', '')
        valor = data.get('valor', '')
        
        # Validações específicas por campo
        if campo == 'nome_processo':
            valido, mensagem = ValidadorUtils.validar_nome_processo(valor)
        elif campo == 'cpf':
            valido = ValidadorUtils.validar_cpf(valor)
            mensagem = "CPF válido" if valido else "CPF inválido"
        elif campo == 'email':
            valido = ValidadorUtils.validar_email(valor)
            mensagem = "Email válido" if valido else "Email inválido"
        elif campo == 'codigo_processo':
            valido = CodigoUtils.validar_codigo_processo(valor)
            mensagem = "Código válido" if valido else "Código inválido"
        else:
            valido = True
            mensagem = "Campo validado"
        
        return JsonResponse({
            'valido': valido,
            'mensagem': mensagem,
            'campo': campo
        })
        
    except Exception as e:
        return JsonResponse({
            'valido': False,
            'mensagem': f'Erro na validação: {str(e)}',
            'campo': campo
        })

@csrf_exempt
@require_http_methods(["POST"])
def consultar_rag_sugestoes(request):
    """API para consultar RAG e obter sugestões contextuais"""
    try:
        data = json.loads(request.body)
        campo = data.get('campo', '')
        area = data.get('area', '')
        contexto = data.get('contexto', '')
        
        # Importar Helena para usar RAG
        from .domain.helena_mapeamento.helena_pop import HelenaPOP
        helena = HelenaPOP()
        
        if helena.vectorstore:
            # Construir query contextual
            query = f"{campo} {area} {contexto} DECIPEX"
            docs = helena.vectorstore.similarity_search(query, k=3)
            
            # Extrair sugestões
            sugestoes = []
            for doc in docs:
                content = doc.page_content
                # Extrair trechos relevantes
                linhas = content.split('\n')
                for linha in linhas:
                    if campo.lower() in linha.lower() and len(linha.strip()) > 10:
                        sugestoes.append(linha.strip()[:200])
                        if len(sugestoes) >= 3:
                            break
            
            return JsonResponse({
                'success': True,
                'sugestoes': sugestoes[:3],
                'campo': campo,
                'fonte': 'RAG'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'RAG não disponível',
                'sugestoes': []
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao consultar RAG: {str(e)}',
            'sugestoes': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def reiniciar_conversa_helena(request):
    """API para reiniciar conversa com Helena - LIMPA TODAS AS SESSÕES"""
    try:
        # Limpar TODAS as sessões dos produtos Helena
        session_keys = [
            'helena_pop_state',
            'helena_fluxograma_state',
            'helena_dossie_state',
            'helena_riscos_state',
            'pop_data_fluxograma'
        ]
        
        for key in session_keys:
            if key in request.session:
                del request.session[key]
        
        # Forçar salvamento
        request.session.modified = True
        
        session_id = request.POST.get('session_id', 'default')
        
        # Log da reinicialização
        log_reset = LogUtils.criar_log_entrada(
            usuario=session_id,
            acao="reiniciar_helena",
            dados={"sessoes_limpas": session_keys}
        )
        
        print("[RESET] Conversa reiniciada - Todas as sessoes foram limpas")
        
        return JsonResponse({
            'success': True,
            'message': 'Conversa reiniciada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao reiniciar: {str(e)}'
        })

# ============================================================================
# APIs - ANÁLISE DE RISCOS E PDF (MANTIDAS)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def extract_pdf_text(request):
    """API para extrair texto e informações de POP em PDF"""
    
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)
    
    pdf_file = request.FILES['pdf_file']
    
    if not pdf_file.name.endswith('.pdf'):
        return JsonResponse({'error': 'Arquivo deve ser PDF'}, status=400)
    
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            return JsonResponse({'error': 'Não foi possível extrair texto do PDF'}, status=400)
        
        pop_info = analyze_pop_content(text)
        
        return JsonResponse({
            'text': text[:2000] + "..." if len(text) > 2000 else text,
            'pop_info': pop_info,
            'success': True,
            'file_name': pdf_file.name,
            'pages_count': len(reader.pages)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro ao processar PDF: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def fluxograma_from_pdf(request):
    """API para gerar fluxograma a partir de PDF de POP - Upload e Chat"""
    try:
        if 'pdf_file' in request.FILES:
            # FASE 1: Upload e extração
            pdf_file = request.FILES['pdf_file']
            
            if not pdf_file.name.endswith('.pdf'):
                return JsonResponse({'error': 'Arquivo deve ser PDF'}, status=400)
            
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                return JsonResponse({'error': 'Não foi possível extrair texto do PDF'}, status=400)
            
            pop_info = analyze_pop_content(text)
            request.session['pop_data_fluxograma'] = pop_info
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'pop_info': pop_info,
                'message': 'PDF analisado com sucesso! Agora converse com Helena para gerar o fluxograma.',
                'file_name': pdf_file.name
            })
        
        else:
            # FASE 2: Processamento de mensagens do chat
            data = json.loads(request.body)
            user_message = data.get('message', '')
            pop_data = request.session.get('pop_data_fluxograma', {})

            from .domain.helena_fluxograma.flowchart_orchestrator import HelenaFluxogramaOrchestrator as HelenaFluxograma

            # Restaurar estado conversacional da sessão Django
            session_key = 'helena_fluxograma_state'
            session_data = request.session.get(session_key, {})

            # pop_data pode ser {} (modo manual sem PDF) — agent trata gracefully
            helena = HelenaFluxograma(dados_pdf=pop_data or None)
            resultado = helena.processar(user_message, session_data)

            # Salvar estado atualizado (session_data mutado in-place pelo agente)
            request.session[session_key] = session_data
            request.session.modified = True

            # Incluir dados estruturados quando fluxo completo
            if resultado.get('completo'):
                resultado['steps'] = _build_labeled_steps(session_data.get('etapas', []))
                resultado['decisoes'] = session_data.get('decisoes', [])

            return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao processar: {str(e)}',
            'resposta': 'Desculpe, ocorreu um erro técnico.'
        }, status=500)


def _build_labeled_steps(etapas):
    """Adiciona label posicional (Etapa 1, Etapa 2, ...) a cada etapa."""
    return [
        {'id': e['id'], 'label': f'Etapa {i}', 'texto': e['texto']}
        for i, e in enumerate(etapas, start=1)
    ]


@csrf_exempt
@require_http_methods(["POST"])
def fluxograma_steps_api(request):
    """
    API para manipulação direta de etapas (insert, edit, remove).
    Reutiliza FlowchartAgent._executar_comando().
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')

        session_key = 'helena_fluxograma_state'
        session_data = request.session.get(session_key, {})

        if not session_data.get('fluxograma_gerado') and not session_data.get('etapas'):
            return JsonResponse(
                {'ok': False, 'mensagem': 'Fluxograma ainda não foi gerado.'},
                status=400,
            )

        from .domain.helena_fluxograma.agents.flowchart_agent import FlowchartAgent

        agent = FlowchartAgent()
        ctx = agent._init_contexto(session_data)

        # Montar comando
        if action == 'insert_after':
            cmd = {
                'tipo': 'inserir_etapa',
                'apos_id': data.get('after_step_id'),
                'texto': data.get('texto', ''),
            }
        elif action == 'edit':
            cmd = {
                'tipo': 'editar_etapa',
                'id': data.get('step_id'),
                'texto': data.get('texto', ''),
            }
        elif action == 'remove':
            cmd = {
                'tipo': 'remover_etapa',
                'id': data.get('step_id'),
            }
        else:
            return JsonResponse(
                {'ok': False, 'mensagem': f'Ação desconhecida: {action}'},
                status=400,
            )

        resultado = agent._executar_comando(cmd, ctx)

        if 'erro' in resultado:
            return JsonResponse(
                {'ok': False, 'mensagem': resultado['erro']},
                status=400,
            )

        mermaid_code = agent.gerar_mermaid(ctx)
        steps = _build_labeled_steps(ctx.get('etapas', []))

        new_step_id = None
        if action == 'insert_after':
            new_step_id = ctx.get('proximo_etapa_id', 1) - 1

        request.session[session_key] = session_data
        request.session.modified = True

        return JsonResponse({
            'ok': True,
            'mensagem': resultado['mensagem'],
            'steps': steps,
            'decisoes': ctx.get('decisoes', []),
            'fluxograma_mermaid': mermaid_code,
            'new_step_id': new_step_id,
        })

    except Exception as e:
        logger.error(f"[fluxograma_steps_api] Erro: {e}", exc_info=True)
        return JsonResponse(
            {'ok': False, 'mensagem': f'Erro interno: {str(e)}'},
            status=500,
        )


def analyze_pop_content(text):
    """
    Extrai informações estruturadas do POP
    VERSÃO 2.0 - Compatível com POPs antigos E novos (helena_pop.py)
    """

    info = {
        'titulo': '',
        'codigo': '',
        'macroprocesso': '',
        'processo': '',
        'atividade': '',
        'sistemas': [],
        'normativos': [],
        'operadores': [],
        'responsavel': ''
    }

    lines = text.split('\n')

    # Detectar formato do POP
    is_new_format = '3. SISTEMAS UTILIZADOS/ ACESSOS NECESSÁRIOS' in text or 'sistemas_utilizados' in text.lower()

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # TÍTULO/ATIVIDADE
        if any(palavra in line.upper() for palavra in ['CONCEDER', 'CONCESSÃO', 'RESSARCIMENTO', 'AUXÍLIO', 'APOSENTADO', 'REVERSÃO']):
            if len(line) > 10 and not info['titulo']:
                info['titulo'] = line
                info['atividade'] = line

        # CÓDIGO DO PROCESSO
        if not info['codigo']:
            import re
            # Padrão: X.X.X.X ou similar
            codigo_match = re.search(r'\b\d+\.\d+\.\d+\.\d+\b', line)
            if codigo_match:
                info['codigo'] = codigo_match.group()

        # MACROPROCESSO
        if 'MACROPROCESSO:' in line.upper() or 'MACROPROCESSO' in line.upper():
            partes = line.split(':', 1)
            if len(partes) > 1:
                info['macroprocesso'] = partes[1].strip()

        # PROCESSO
        if 'PROCESSO:' in line.upper() and not info['processo']:
            partes = line.split(':', 1)
            if len(partes) > 1:
                info['processo'] = partes[1].strip()

        # SISTEMAS - LISTA COMPLETA (50+ sistemas da HelenaPOP)
        # 1. Sistemas conhecidos - MESMA FONTE que helena_pop.py
        sistemas_conhecidos = [
            # Gestão de Pessoal
            'SIAPE', 'E-SIAPE', 'SIGEPE', 'SIGEP - AFD', 'E-Pessoal TCU', 'SIAPNET', 'SIGAC',
            # Documentos
            'SEI', 'DOINET', 'DOU', 'SOUGOV', 'PETRVS',
            # Transparência
            'Portal da Transparência', 'CNIS', 'Site CGU-PAD',
            'Sistema de Pesquisa Integrada do TCU', 'Consulta CPF RFB',
            # Previdência
            'SISTEMA COMPREV', 'BG COMPREV',
            # Comunicação
            'TEAMS', 'OUTLOOK',
            # Outros
            'DW', 'CADSIAPE', 'SIAPE-Saúde', 'SISAC', 'SCDP',
            'SICONV', 'SIGEF', 'SIAFI', 'SouGov.br',
            # Variações comuns
            'SouGov', 'e-Pessoal', 'ePessoal', 'SIGEPE-Saúde'
        ]

        # Detecta sistemas na linha atual (case-insensitive)
        line_upper = line.upper()
        for sistema in sistemas_conhecidos:
            sistema_upper = sistema.upper()
            if sistema_upper in line_upper:
                # Adiciona o sistema com capitalização original
                if sistema not in info['sistemas']:
                    info['sistemas'].append(sistema)

        # 2. Padrão de seção "3. SISTEMAS UTILIZADOS"
        if i > 0 and '3.' in lines[i-1] and 'SISTEMA' in lines[i-1].upper():
            # Próximas linhas são sistemas até encontrar próxima seção (4., linha vazia, etc)
            j = i
            while j < len(lines) and lines[j].strip():
                sistema_line = lines[j].strip()
                # Para quando encontrar próxima seção numerada
                if re.match(r'^\d+\.', sistema_line):
                    break
                # Adiciona se não for vazio e não for título
                if sistema_line and 'SISTEMA' not in sistema_line.upper():
                    if sistema_line not in info['sistemas']:
                        info['sistemas'].append(sistema_line)
                j += 1

        # 3. Detecção inteligente de sistemas (palavras-chave)
        if any(kw in line.upper() for kw in ['ACESSO AO', 'LOGIN', 'MÓDULO', 'PORTAL']):
            # Tenta extrair nome do sistema
            palavras = line.split()
            for palavra in palavras:
                if len(palavra) > 3 and palavra.isupper():
                    if palavra not in info['sistemas'] and palavra not in ['ACESSO', 'LOGIN', 'MÓDULO', 'PORTAL']:
                        info['sistemas'].append(palavra)

        # NORMATIVOS
        if any(palavra in line for palavra in ['Lei nº', 'Lei no', 'Lei n°', 'IN nº', 'Instrução Normativa', 'Decreto', 'Portaria']):
            normativo = line[:150]
            if normativo not in info['normativos'] and len(info['normativos']) < 5:
                info['normativos'].append(normativo)

        # OPERADORES
        operadores_tipos = ['TÉCNICO ESPECIALIZADO', 'COORDENADOR', 'APOIO GABINETE', 'APOIO-GABINETE', 'OPERADOR']
        for operador in operadores_tipos:
            if operador in line.upper() and operador not in [o.upper() for o in info['operadores']]:
                info['operadores'].append(operador.title())

        # RESPONSÁVEL
        if any(palavra in line.upper() for palavra in ['DECIPEX', 'CGBEN', 'COAUX', 'RESPONSÁVEL']) and not info['responsavel']:
            info['responsavel'] = line

    # Limpeza final
    info['sistemas'] = list(set(info['sistemas']))[:10]  # Limita a 10 sistemas únicos
    info['normativos'] = info['normativos'][:3]
    info['operadores'] = list(set(info['operadores']))[:3]

    # LOG de debug
    print(f"\n{'='*80}")
    print("[ANALYSIS] ANALISE DE POP CONCLUIDA")
    print(f"   Título: {info['titulo'][:50]}...")
    print(f"   Código: {info['codigo']}")
    print(f"   Sistemas encontrados ({len(info['sistemas'])}): {info['sistemas']}")
    print(f"   Formato detectado: {'NOVO (helena_pop)' if is_new_format else 'ANTIGO'}")
    print(f"{'='*80}\n")

    return info

# ============================================================================
# HELENA RECEPCIONISTA (LANDING PAGE) - MANTIDA
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_recepcao_api(request):
    """API para Helena Recepcionista - Landing Page"""
    try:
        logger.info("[CHAT RECEPCAO] Requisicao recebida em /api/chat-recepcao/")

        # Parse do JSON
        data = json.loads(request.body)
        mensagem = data.get('message', '')
        session_id = data.get('session_id', 'default')

        logger.info(f"[CHAT RECEPCAO] Mensagem: {mensagem}")
        logger.info(f"[CHAT RECEPCAO] Session ID: {session_id}")

        if not mensagem:
            return JsonResponse({
                'resposta': 'Por favor, envie uma mensagem.',
                'success': False
            }, status=400)

        # Importar e chamar Helena com session_id
        from .domain.helena_recepcao import HelenaRecepcaoOrchestrator
        logger.info("[CHAT RECEPCAO] Helena importada")

        # Obter ou criar estado da sessão
        session_key = f'helena_recepcao_{session_id}'
        session_data = request.session.get(session_key, {})

        # Processar com orquestrador
        orchestrator = HelenaRecepcaoOrchestrator()
        resultado = orchestrator.processar(mensagem, session_data)

        # Salvar estado da sessão
        request.session[session_key] = session_data
        request.session.modified = True

        resposta = resultado.get('resposta', 'Desculpe, não entendi.')
        logger.info(f"[CHAT RECEPCAO] Resposta gerada: {len(resposta)} caracteres")

        return JsonResponse({
            'resposta': resposta,
            'success': True,
            'tipo_interface': resultado.get('tipo_interface'),
            'dados_interface': resultado.get('dados_interface'),
            'route': resultado.get('route'),
            'acao': resultado.get('acao'),
        }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        logger.error(f"[CHAT RECEPCAO] ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'resposta': 'Desculpe, tive um problema técnico.',
            'error': str(e),
            'success': False
        }, status=500)


# ============================================================================
# API DE AUTO-SAVE - FASE 2
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def autosave_pop(request):
    """
    API de auto-save para o FormularioPOP.tsx

    Recebe dados do POP e salva incrementalmente no PostgreSQL.
    Cria POP na primeira chamada, atualiza nas subsequentes.
    Snapshot automatico a cada 5 saves.

    POST /api/pop-autosave/
    Body: {
        "id": int | null,
        "uuid": str | null,
        "session_id": "uuid",
        "nome_processo": "...",
        "raw_payload": "{...}",
        ...campos do formulario
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id obrigatório'
            }, status=400)

        logger.info(f"[AUTO-SAVE] Sessao: {session_id}")

        # Lookup: id → uuid → session_id (mais recente nao-deletado)
        pop = None
        pop_id = data.get('id')
        pop_uuid = data.get('uuid')

        if pop_id:
            pop = POP.objects.filter(pk=pop_id, is_deleted=False).first()

        if not pop and pop_uuid:
            pop = POP.objects.filter(uuid=pop_uuid, is_deleted=False).first()

        if not pop:
            pop = POP.objects.filter(
                session_id=session_id, is_deleted=False
            ).order_by('-updated_at').first()

        # Controle de concorrência: rejeitar se hash divergiu (409 Conflict)
        client_hash = data.get('integrity_hash')
        if client_hash and pop and pop.pk and pop.integrity_hash and client_hash != pop.integrity_hash:
            return JsonResponse({
                'success': False,
                'error': 'CONFLICT',
                'conflict': {
                    'server_hash': pop.integrity_hash,
                    'server_sequence': pop.autosave_sequence,
                    'server_updated_at': pop.updated_at.isoformat() if pop.updated_at else None,
                }
            }, status=409)

        # Criar se nao existe
        if not pop:
            pop = POP(
                session_id=session_id,
                status='draft',
                created_by=request.user if request.user.is_authenticated else None,
            )
            logger.info(f"[AUTO-SAVE] Criando novo POP para sessao {session_id}")

        # Mapear campos frontend → modelo
        area = data.get('area')
        if isinstance(area, dict):
            pop.area_codigo = area.get('codigo', '')
            pop.area_nome = area.get('nome', '')
            # Resolver FK para Area model
            if pop.area_codigo:
                from processos.models import Area
                area_obj = Area.objects.filter(codigo=pop.area_codigo).first()
                if area_obj:
                    pop.area = area_obj

        campos_diretos = {
            'macroprocesso': 'macroprocesso',
            'codigo_processo': 'codigo_processo',
            'nome_processo': 'nome_processo',
            'processo_especifico': 'processo_especifico',
            'entrega_esperada': 'entrega_esperada',
            'dispositivos_normativos': 'dispositivos_normativos',
            'pontos_atencao': 'pontos_atencao',
        }
        for frontend_key, model_field in campos_diretos.items():
            val = data.get(frontend_key)
            if val is not None:
                # Não salvar placeholders como codigo_processo (causa colisão UNIQUE)
                if model_field == 'codigo_processo' and val in ('Aguardando...', ''):
                    val = None
                setattr(pop, model_field, val)

        # Campos JSON
        campos_json = {
            'sistemas': 'sistemas_utilizados',
            'etapas': 'etapas',
            'documentos_utilizados': 'documentos_utilizados',
            'fluxos_entrada': 'fluxos_entrada',
            'fluxos_saida': 'fluxos_saida',
        }
        for frontend_key, model_field in campos_json.items():
            val = data.get(frontend_key)
            if val is not None:
                # Normalizar etapas antes de gravar (garante id, ordem, schema canonico)
                if frontend_key == 'etapas' and isinstance(val, list):
                    from processos.domain.helena_mapeamento.normalizar_etapa import normalizar_etapas
                    val = normalizar_etapas(val)
                setattr(pop, model_field, val)

        # Operadores: frontend envia list, modelo aceita TextField
        operadores = data.get('operadores')
        if operadores is not None:
            if isinstance(operadores, list):
                pop.operadores = ', '.join(operadores)
            else:
                pop.operadores = str(operadores)

        # Raw payload para reconstrucao/debug
        raw = data.get('raw_payload')
        if raw:
            pop.raw_payload = json.loads(raw) if isinstance(raw, str) else raw

        # Incrementar sequencia e timestamps
        pop.autosave_sequence = (pop.autosave_sequence or 0) + 1
        pop.last_autosave_at = timezone.now()
        pop.status = pop.status or 'draft'

        # Computar integrity_hash antes de salvar
        pop.integrity_hash = pop.compute_integrity_hash()

        # Save com retry em caso de colisão de codigo_processo (UniqueConstraint)
        from django.db import IntegrityError, transaction
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            try:
                with transaction.atomic():
                    pop.save()
                break
            except IntegrityError as e:
                if 'unique_cap_ativo' in str(e) and pop.codigo_processo and tentativa < max_tentativas - 1:
                    cap = pop.codigo_processo
                    partes = cap.rsplit('.', 1)
                    if len(partes) == 2:
                        try:
                            novo_num = int(partes[1]) + 1
                            pop.codigo_processo = f"{partes[0]}.{novo_num}"
                        except ValueError:
                            pop.codigo_processo = f"{cap}-{tentativa + 2}"
                    else:
                        pop.codigo_processo = f"{cap}-{tentativa + 2}"
                    pop.integrity_hash = pop.compute_integrity_hash()
                    logger.warning(f"[AUTO-SAVE] Colisão CAP, tentativa {tentativa + 2}: {pop.codigo_processo}")
                else:
                    raise

        # Snapshot a cada 5 saves
        snapshot_created = False
        if pop.autosave_sequence % 5 == 0:
            try:
                pop.create_snapshot(autosave=True)
                snapshot_created = True
                logger.info(f"[AUTO-SAVE] Snapshot criado (seq={pop.autosave_sequence})")
            except Exception as snap_err:
                logger.warning(f"[AUTO-SAVE] Falha ao criar snapshot: {snap_err}")

        logger.info(f"[AUTO-SAVE] POP {pop.pk} salvo (seq={pop.autosave_sequence})")

        return JsonResponse({
            'success': True,
            'pop': {
                'id': pop.pk,
                'uuid': str(pop.uuid),
                'autosave_sequence': pop.autosave_sequence,
            },
            'integrity_hash': pop.integrity_hash,
            'snapshot_created': snapshot_created,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)

    except Exception as e:
        logger.exception(f"[AUTO-SAVE] Erro: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_pop(request, identifier):
    """
    Carrega POP salvo do backend.

    GET /api/pop/<identifier>/
    identifier pode ser UUID ou session_id.

    Retorna dados completos do POP para o frontend reconstruir o formulario.
    """
    try:
        pop = None

        # Tentar UUID primeiro
        try:
            import uuid as uuid_mod
            uuid_mod.UUID(identifier)
            pop = POP.objects.filter(uuid=identifier, is_deleted=False).first()
        except (ValueError, AttributeError):
            pass

        # Fallback: session_id
        if not pop:
            pop = POP.objects.filter(
                session_id=identifier, is_deleted=False
            ).order_by('-updated_at').first()

        if not pop:
            return JsonResponse({
                'success': False,
                'error': 'POP não encontrado'
            }, status=404)

        return JsonResponse({
            'success': True,
            'pop': {
                'id': pop.pk,
                'uuid': str(pop.uuid),
                'session_id': pop.session_id,
                'integrity_hash': pop.integrity_hash,
                'autosave_sequence': pop.autosave_sequence,
                'status': pop.status,
                'dados': pop.get_dados_completos(),
                'updated_at': pop.updated_at.isoformat() if pop.updated_at else None,
            }
        })

    except Exception as e:
        logger.exception(f"[GET-POP] Erro: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# APIs POP DRAFT - Rascunho do wizard (PAUSA / retomada)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def pop_draft_save(request):
    """
    Cria ou atualiza rascunho do POP.

    POST /api/pop-draft/save/
    Body: {
        "session_id": "uuid",
        "area": "DIGEP",
        "process_code": "7.1.1.1",
        "etapa_atual": "transicao_epica",
        "payload_json": { ... dados coletados ... }
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id obrigatório'
            }, status=400)

        user = request.user if request.user.is_authenticated else None

        # Upsert: busca draft existente pela session_id, ou cria novo
        draft, created = PopDraft.objects.update_or_create(
            session_id=session_id,
            defaults={
                'user': user,
                'area': data.get('area', ''),
                'process_code': data.get('process_code', ''),
                'etapa_atual': data.get('etapa_atual', 'nome_usuario'),
                'payload_json': data.get('payload_json', {}),
            }
        )

        logger.info(f"[POP-DRAFT] {'Criado' if created else 'Atualizado'} draft {draft.pk} session={session_id}")

        return JsonResponse({
            'success': True,
            'draft_id': draft.pk,
            'created': created,
        })

    except Exception as e:
        logger.exception(f"[POP-DRAFT] Erro ao salvar: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pop_draft_load(request, session_id):
    """
    Carrega rascunho mais recente do POP.

    GET /api/pop-draft/<session_id>/
    """
    try:
        draft = PopDraft.objects.filter(session_id=session_id).first()

        if not draft:
            return JsonResponse({
                'success': False,
                'error': 'Rascunho não encontrado'
            }, status=404)

        return JsonResponse({
            'success': True,
            'draft': {
                'id': draft.pk,
                'session_id': draft.session_id,
                'area': draft.area,
                'process_code': draft.process_code,
                'etapa_atual': draft.etapa_atual,
                'payload_json': draft.payload_json,
                'updated_at': draft.updated_at.isoformat(),
            }
        })

    except Exception as e:
        logger.exception(f"[POP-DRAFT] Erro ao carregar: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)