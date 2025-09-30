# processos/views.py - Sistema Multi-Produto Helena com LangChain + PDF + Sessão Persistente

import json
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings
import pypdf
from datetime import datetime
from .helena_risks import analyze_risks_helena
from .utils import (
    ValidadorUtils, FormatadorUtils, CodigoUtils, 
    ArquivoUtils, LogUtils, SegurancaUtils,
    validar_entrada_helena, preparar_dados_para_pdf,
    PDFGenerator  # ← ADICIONADO
)

# ============================================================================
# VIEWS PARA TEMPLATES (PÁGINAS)
# ============================================================================

def landing_temp(request):
    """Página inicial do sistema"""
    return render(request, 'landing.html')

def portal_temp(request):
    """Portal do sistema"""
    return render(request, 'portal.html')

def chat_temp(request):
    """Página do chat com Helena"""
    return render(request, 'chat.html')

def riscos_fluxo(request):
    """Página do fluxo de análise de riscos"""
    return render(request, 'riscos/fluxo.html')

def fluxograma_temp(request):
    """Página do gerador de fluxogramas via PDF"""
    return render(request, 'fluxograma.html')

# ============================================================================
# APIs - CHAT COM HELENA (SISTEMA MULTI-PRODUTO) - VERSÃO COM SESSÃO PERSISTENTE
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_api_view(request):
    """API para conversa com Helena - Sistema Multi-Produto com Sessão Persistente"""
    
    try:
        load_dotenv()
        
        # Receber dados do JavaScript
        data = json.loads(request.body)
        user_message = data.get('message', '')
        contexto = data.get('contexto', 'geral')
        dados_atuais = data.get('dados_atuais', {})
        session_id = data.get('session_id', 'default')
        
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
        
        # P1: Gerador de POP (RENOVADO - com sessão completa)
        if contexto in ['gerador_pop', 'mapeamento_natural']:
            from .helena_produtos.helena_pop import HelenaPOP
            
            # Chave única para este contexto na sessão
            session_key = 'helena_pop_state'
            
            # Verificar se há estado salvo na sessão
            if session_key not in request.session:
                # Primeira mensagem - criar nova Helena
                helena = HelenaPOP()
                
                # ============== DEBUG: Criação inicial ==============
                print(f"\n{'='*60}")
                print(f"🟢 NOVA HELENA CRIADA")
                print(f"   Estado inicial: {helena.estado}")
                print(f"   Session key: {session_key}")
                print(f"   Sessão vazia: {session_key} não existia")
                print(f"{'='*60}\n")
                # ===================================================
            else:
                # Mensagens seguintes - restaurar estado
                helena = HelenaPOP()
                state = request.session[session_key]
                
                # ============== DEBUG: Estado ANTES de restaurar ==============
                print(f"\n{'='*60}")
                print(f"🔵 RESTAURANDO HELENA da sessão")
                print(f"   Estado na sessão: {state.get('estado')}")
                print(f"   Nome na sessão: {state.get('nome_usuario')}")
                print(f"   Dados na sessão: {len(state.get('dados', {}))} campos")
                print(f"{'='*60}\n")
                # ============================================================
                
                # Restaurar TODOS os atributos críticos
                helena.estado = state.get('estado', 'nome')
                helena.nome_usuario = state.get('nome_usuario')
                helena.area_selecionada = state.get('area_selecionada')
                helena.dados = state.get('dados', {})
                helena.sistemas_selecionados = state.get('sistemas_selecionados', [])
                helena.etapas_processo = state.get('etapas_processo', [])
                helena.etapa_atual_campo = state.get('etapa_atual_campo', 0)
                helena.conversas = state.get('conversas', [])
                
                # ============== DEBUG: Estado APÓS restaurar ==============
                print(f"✅ HELENA RESTAURADA")
                print(f"   Estado: {helena.estado}")
                print(f"   Nome: {helena.nome_usuario}")
                print(f"   Área: {helena.area_selecionada}")
                print(f"   Dados: {len(helena.dados)} campos")
                print(f"   Etapas: {len(helena.etapas_processo)} total")
                print(f"   Conversas: {len(helena.conversas)} mensagens")
                print(f"{'='*60}\n")
                # =========================================================
            
            # Processar mensagem do usuário
            resultado = helena.processar_mensagem(user_message)
            
            # ============== DEBUG: Estado após processamento ==============
            print(f"\n{'='*60}")
            print(f"✅ APÓS PROCESSAR '{user_message[:50]}...'")
            print(f"   Estado atual: {helena.estado}")
            print(f"   Nome usuário: {helena.nome_usuario}")
            print(f"   Área selecionada: {helena.area_selecionada}")
            print(f"   Campos preenchidos: {list(helena.dados.keys())}")
            print(f"   Total etapas: {len(helena.etapas_processo)}")
            print(f"   Etapa atual: {helena.etapa_atual_campo}/{len(helena.etapas_processo)}")
            print(f"   Total conversas: {len(helena.conversas)}")
            print(f"{'='*60}\n")
            # ============================================================
            
            # Salvar estado atualizado na sessão
            request.session[session_key] = {
                'estado': helena.estado,
                'nome_usuario': helena.nome_usuario,
                'area_selecionada': helena.area_selecionada,
                'dados': helena.dados,
                'sistemas_selecionados': helena.sistemas_selecionados,
                'etapas_processo': helena.etapas_processo,
                'etapa_atual_campo': helena.etapa_atual_campo,
                'conversas': helena.conversas
            }
            
            # Forçar Django a salvar a sessão modificada
            request.session.modified = True
            
            print(f"💾 Estado salvo na sessão Django")
            print(f"🔑 Session key: {session_key}")
            print(f"📦 Próximo estado será: {helena.estado}\n")
            
            # Log específico da Helena
            log_helena = LogUtils.log_helena_interacao(
                usuario=session_id,
                pergunta=user_message,
                resposta=resultado.get('resposta', ''),
                estado=helena.estado
            )
            
            return JsonResponse(resultado)
        
        # P2: Gerador de Fluxograma (com sessão)
        elif contexto == 'fluxograma':
            from .helena_produtos.helena_fluxograma import HelenaFluxograma
            
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
        
        # P3: Dossiê PDF (com sessão)
        elif contexto == 'dossie':
            from .helena_produtos.helena_dossie import HelenaDossie
            
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
            from .helena_produtos.helena_dashboard import HelenaDashboard
            helena = HelenaDashboard()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P5: Análise de Riscos (com sessão)
        elif contexto == 'analise_riscos':
            from .helena_produtos.helena_analise_riscos import HelenaAnaliseRiscos
            
            session_key = 'helena_riscos_state'
            
            if session_key not in request.session:
                helena = HelenaAnaliseRiscos()
            else:
                helena = HelenaAnaliseRiscos()
                state = request.session[session_key]
                helena.estado = state.get('estado', 'inicial')
                helena.dados_processo = state.get('dados_processo', {})
                helena.riscos_identificados = state.get('riscos_identificados', [])
            
            resultado = helena.processar_mensagem(user_message)
            
            request.session[session_key] = {
                'estado': helena.estado,
                'dados_processo': helena.dados_processo,
                'riscos_identificados': helena.riscos_identificados
            }
            request.session.modified = True
            
            return JsonResponse(resultado)
        
        # P6: Relatório de Riscos
        elif contexto == 'relatorio_riscos':
            from .helena_produtos.helena_relatorio_riscos import HelenaRelatorioRiscos
            helena = HelenaRelatorioRiscos()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P7: Plano de Ação
        elif contexto == 'plano_acao':
            from .helena_produtos.helena_plano_acao import HelenaPlanoAcao
            helena = HelenaPlanoAcao()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P8: Dossiê de Governança
        elif contexto == 'governanca':
            from .helena_produtos.helena_governanca import HelenaGovernanca
            helena = HelenaGovernanca()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P9: Gerador de Documentos
        elif contexto == 'documentos':
            from .helena_produtos.helena_documentos import HelenaDocumentos
            helena = HelenaDocumentos()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P10: Relatório de Conformidade
        elif contexto == 'conformidade':
            from .helena_produtos.helena_conformidade import HelenaConformidade
            helena = HelenaConformidade()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P11: Análise de Artefatos
        elif contexto == 'artefatos':
            from .helena_produtos.helena_artefatos import HelenaArtefatos
            helena = HelenaArtefatos()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # Contexto não reconhecido
        else:
            return JsonResponse({
                'resposta': f'Contexto "{contexto}" não reconhecido. Use: gerador_pop, fluxograma, analise_riscos, etc.',
                'erro': 'CONTEXTO_INVALIDO'
            }, status=400)
            
    except Exception as e:
        print(f"❌ Erro na API Helena: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'resposta': 'Desculpe, ocorreu um erro técnico. Pode repetir a pergunta?',
            'dados_extraidos': {},
            'conversa_completa': False,
            'erro': str(e)
        }, status=500)

# ============================================================================
# NOVAS APIs - PDF PROFISSIONAL PARA POP (MODIFICADO)
# ============================================================================

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
        
        # Preparar dados para PDF
        dados_limpos = preparar_dados_para_pdf(dados_pop)
        
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
        
        print(f"✅ PDF gerado com sucesso: {pdf_path}")
        
        # Retornar sucesso com URLs
        return JsonResponse({
            'success': True,
            'pdf_url': f'/api/download-pdf/{nome_arquivo}',
            'preview_url': f'/api/preview-pdf/{nome_arquivo}',
            'arquivo': nome_arquivo,
            'message': 'PDF gerado com sucesso!'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        
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
        from .helena_produtos.helena_pop import HelenaPOP
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
        
        print("🔄 Conversa reiniciada - Todas as sessões foram limpas")
        
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
            
            if not pop_data:
                return JsonResponse({
                    'error': 'Nenhum PDF foi analisado ainda. Faça upload primeiro.',
                    'resposta': 'Por favor, faça upload de um PDF de POP primeiro.'
                }, status=400)
            
            from .helena_produtos.helena_fluxograma import HelenaFluxograma
            helena = HelenaFluxograma(dados_pdf=pop_data)
            resultado = helena.processar_mensagem(user_message)
            
            return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao processar: {str(e)}',
            'resposta': 'Desculpe, ocorreu um erro técnico.'
        }, status=500)

def analyze_pop_content(text):
    """Extrai informações estruturadas do POP"""
    
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
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        if any(palavra in line.upper() for palavra in ['CONCEDER', 'CONCESSÃO', 'RESSARCIMENTO', 'AUXÍLIO', 'APOSENTADO']):
            if len(line) > 10 and not info['titulo']:
                info['titulo'] = line
                info['atividade'] = line
        
        if not info['codigo']:
            import re
            codigo_match = re.search(r'\b\d+\.\d+\.\d+\.\d+\b', line)
            if codigo_match:
                info['codigo'] = codigo_match.group()
        
        if 'MACROPROCESSO:' in line.upper():
            info['macroprocesso'] = line.split(':', 1)[1].strip() if ':' in line else ''
        
        if 'PROCESSO:' in line.upper() and not info['processo']:
            info['processo'] = line.split(':', 1)[1].strip() if ':' in line else ''
        
        sistemas_conhecidos = ['SIGEPE', 'SouGov', 'SEI', 'SIAPE', 'CADSIAPE']
        for sistema in sistemas_conhecidos:
            if sistema in line and sistema not in info['sistemas']:
                info['sistemas'].append(sistema)
        
        if any(palavra in line for palavra in ['Lei nº', 'Lei no', 'IN nº', 'Instrução Normativa', 'Decreto']):
            normativo = line[:150]
            if normativo not in info['normativos'] and len(info['normativos']) < 5:
                info['normativos'].append(normativo)
        
        operadores_tipos = ['TÉCNICO ESPECIALIZADO', 'COORDENADOR', 'APOIO GABINETE', 'APOIO-GABINETE']
        for operador in operadores_tipos:
            if operador in line.upper() and operador not in [o.upper() for o in info['operadores']]:
                info['operadores'].append(operador.title())
        
        if any(palavra in line.upper() for palavra in ['DECIPEX', 'CGBEN', 'COAUX']) and not info['responsavel']:
            info['responsavel'] = line
    
    info['sistemas'] = list(set(info['sistemas']))
    info['normativos'] = info['normativos'][:3]
    info['operadores'] = list(set(info['operadores']))[:3]
    
    return info

# ============================================================================
# HELENA RECEPCIONISTA (LANDING PAGE) - MANTIDA
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_recepcao_api(request):
    """API para Helena Recepcionista - Landing Page"""
    try:
        print("🔵 Requisição recebida em /api/chat-recepcao/")
        
        # Parse do JSON
        data = json.loads(request.body)
        mensagem = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        print(f"🔵 Mensagem: {mensagem}")
        print(f"🔵 Session ID: {session_id}")
        
        if not mensagem:
            return JsonResponse({
                'resposta': 'Por favor, envie uma mensagem.',
                'success': False
            }, status=400)
        
        # Importar e chamar Helena com session_id
        from .helena_produtos.helena_recepcao import helena_recepcao
        print("🔵 Helena importada")
        
        resposta = helena_recepcao(mensagem, session_id)
        print(f"🔵 Resposta: {resposta[:100]}...")
        
        return JsonResponse({
            'resposta': resposta,
            'success': True
        })
        
    except Exception as e:
        print(f"🔴 ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'resposta': 'Desculpe, tive um problema técnico.',
            'error': str(e),
            'success': False
        }, status=500)
    # ============================================================================
# TESTE DE INTEGRAÇÃO COM OPENAI
# ============================================================================

from django.views.decorators.http import require_GET
from openai import OpenAI

@csrf_exempt
@require_GET
def test_openai(request):
    """API simples para testar a integração com OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Diga Olá, eu sou a Helena do DECIPEX."}],
            max_tokens=50
        )

        reply = response.choices[0].message.content
        return JsonResponse({
            "success": True,
            "mensagem": reply
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "erro": str(e)
        }, status=500)