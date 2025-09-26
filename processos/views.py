# processos/views.py - Sistema Multi-Produto Helena com LangChain

import json
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import pypdf
from .helena_risks import analyze_risks_helena

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
# APIs - CHAT COM HELENA (SISTEMA MULTI-PRODUTO)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_api_view(request):
    """API para conversa com Helena - Sistema Multi-Produto com LangChain"""
    
    try:
        load_dotenv()
        
        # Receber dados do JavaScript
        data = json.loads(request.body)
        user_message = data.get('message', '')
        contexto = data.get('contexto', 'geral')
        dados_atuais = data.get('dados_atuais', {})
        
        # ========== ROTEAMENTO POR PRODUTO (LangChain) ==========
        
        # P1: Gerador de POP (aceita ambos os contextos)
        if contexto in ['gerador_pop', 'mapeamento_natural']:
            from .helena_produtos.helena_pop import HelenaPOP
            helena = HelenaPOP()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P2: Gerador de Fluxograma
        elif contexto == 'fluxograma':
            from .helena_produtos.helena_fluxograma import HelenaFluxograma
            helena = HelenaFluxograma()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P3: Dossiê PDF
        elif contexto == 'dossie':
            from .helena_produtos.helena_dossie import HelenaDossie
            helena = HelenaDossie()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P4: Dashboard
        elif contexto == 'dashboard':
            from .helena_produtos.helena_dashboard import HelenaDashboard
            helena = HelenaDashboard()
            resultado = helena.processar_mensagem(user_message)
            return JsonResponse(resultado)
        
        # P5: Análise de Riscos
        elif contexto == 'analise_riscos':
            from .helena_produtos.helena_analise_riscos import HelenaAnaliseRiscos
            helena = HelenaAnaliseRiscos()
            resultado = helena.processar_mensagem(user_message)
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
        print(f"Erro na API Helena: {e}")
        return JsonResponse({
            'resposta': 'Desculpe, ocorreu um erro técnico. Pode repetir a pergunta?',
            'dados_extraidos': {},
            'conversa_completa': False,
            'erro': str(e)
        }, status=500)

# ============================================================================
# APIs - ANÁLISE DE RISCOS E PDF
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
            info['responsável'] = line
    
    info['sistemas'] = list(set(info['sistemas']))
    info['normativos'] = info['normativos'][:3]
    info['operadores'] = list(set(info['operadores']))[:3]
    
    return info

# ============================================================================
# HELENA RECEPCIONISTA (LANDING PAGE)
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