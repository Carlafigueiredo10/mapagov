# processos/views.py - Código completo unificado e corrigido

import json
import openai
import os  # <-- ADICIONADO para variáveis de ambiente
from dotenv import load_dotenv  # <-- ADICIONADO para ler o arquivo .env
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import pypdf
from .helena_risks import analyze_risks_helena

# Importar prompts (se existir arquivo separado)
try:
    from .prompts import HELENA_SYSTEM_PROMPT
except ImportError:
    # Prompt padrão se não existir arquivo separado
    HELENA_SYSTEM_PROMPT = """
    Você é Helena, assistente especializada em GRC (Governança, Riscos e Conformidade) para o setor público brasileiro.
    Sua função é extrair informações de forma natural para criar POPs estruturados seguindo padrões DECIPEX/MGI.
    
    Sempre responda em JSON com esta estrutura:
    {
        "type": "ASK|FILL|POP_DRAFT",
        "text": "sua resposta amigável",
        "field": "campo_extraído",
        "value": "valor_extraído"
    }
    
    Campos que você deve extrair:
    - processo: nome do processo
    - objetivo: finalidade do processo
    - entrega_esperada: resultado final
    - beneficiario: quem recebe o serviço
    - base_normativa: leis e normas aplicáveis
    - sistemas_utilizados: sistemas informatizados
    - responsavel: setor responsável
    - etapas: principais etapas do processo
    """

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

# ============================================================================
# APIs - CHAT COM HELENA
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_api_view(request):
    """API para conversa natural com Helena - extração automática de dados"""
    
    try:
        # Carrega as variáveis do arquivo .env (se existir)
        load_dotenv() # <-- ADICIONADO

        # Receber dados do JavaScript
        data = json.loads(request.body)
        user_message = data.get('message', '')
        contexto = data.get('contexto', 'geral')
        dados_atuais = data.get('dados_atuais', {})
        
        # Montar contexto para Helena
        contexto_atual = ""
        if dados_atuais:
            contexto_atual = f"\n\nDADOS JÁ COLETADOS:\n{json.dumps(dados_atuais, indent=2, ensure_ascii=False)}"
        
        # --- MUDANÇA DE SEGURANÇA APLICADA AQUI ---
        # Pega a chave de API do ambiente, de forma segura
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return JsonResponse({
                'resposta': 'Erro de configuração no servidor: a chave da API não foi encontrada.',
                'error': 'OPENAI_API_KEY não está configurada no ambiente.'
            }, status=500)

        # Chamar OpenAI com a chave segura
        client = openai.OpenAI(api_key=api_key) # <-- CORRIGIDO
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": HELENA_SYSTEM_PROMPT + contexto_atual
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        helena_response = response.choices[0].message.content
        
        # Processar resposta JSON da Helena
        try:
            helena_data = json.loads(helena_response)
            
            # Extrair informações
            response_type = helena_data.get('type', 'ASK')
            text = helena_data.get('text', '')
            field = helena_data.get('field')
            value = helena_data.get('value')
            
            # Atualizar dados extraídos
            dados_extraidos = {}
            conversa_completa = False
            
            if response_type == 'FILL' and field and value:
                dados_extraidos[field] = value
                
            elif response_type == 'POP_DRAFT':
                conversa_completa = True
                # Verificar se tem dados suficientes
                campos_obrigatorios = ['processo', 'objetivo', 'entrega_esperada']
                faltando = [campo for campo in campos_obrigatorios if campo not in dados_atuais]
                
                if faltando:
                    text = f"Ainda preciso de algumas informações: {', '.join(faltando)}. Pode me ajudar?"
                    conversa_completa = False
            
            return JsonResponse({
                'resposta': text,
                'dados_extraidos': dados_extraidos,
                'conversa_completa': conversa_completa,
                'tipo_resposta': response_type
            })
            
        except json.JSONDecodeError:
            # Se Helena não retornou JSON válido, usar resposta como texto
            return JsonResponse({
                'resposta': helena_response,
                'dados_extraidos': {},
                'conversa_completa': False,
                'tipo_resposta': 'ASK'
            })
            
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
        # Ler PDF usando pypdf
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Verificar se extraiu texto
                text += page_text + "\n"
        
        if not text.strip():
            return JsonResponse({'error': 'Não foi possível extrair texto do PDF'}, status=400)
        
        # Extrair informações estruturadas do POP
        pop_info = analyze_pop_content(text)
        
        return JsonResponse({
            'text': text[:2000] + "..." if len(text) > 2000 else text,  # Primeiros 2000 caracteres
            'pop_info': pop_info,
            'success': True,
            'file_name': pdf_file.name,
            'pages_count': len(reader.pages)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro ao processar PDF: {str(e)}'}, status=500)

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
        
        # Buscar título/atividade principal
        if any(palavra in line.upper() for palavra in ['CONCEDER', 'CONCESSÃO', 'RESSARCIMENTO', 'AUXÍLIO', 'APOSENTADO']):
            if len(line) > 10 and not info['titulo']:
                info['titulo'] = line
                info['atividade'] = line
        
        # Buscar código (formato x.x.x.x)
        if not info['codigo']:
            import re
            codigo_match = re.search(r'\b\d+\.\d+\.\d+\.\d+\b', line)
            if codigo_match:
                info['codigo'] = codigo_match.group()
        
        # Buscar macroprocesso
        if 'MACROPROCESSO:' in line.upper():
            info['macroprocesso'] = line.split(':', 1)[1].strip() if ':' in line else ''
        
        # Buscar processo
        if 'PROCESSO:' in line.upper() and not info['processo']:
            info['processo'] = line.split(':', 1)[1].strip() if ':' in line else ''
        
        # Buscar sistemas utilizados
        sistemas_conhecidos = ['SIGEPE', 'SouGov', 'SEI', 'SIAPE', 'CADSIAPE']
        for sistema in sistemas_conhecidos:
            if sistema in line and sistema not in info['sistemas']:
                info['sistemas'].append(sistema)
        
        # Buscar normativos
        if any(palavra in line for palavra in ['Lei nº', 'Lei no', 'IN nº', 'Instrução Normativa', 'Decreto']):
            # Limitar tamanho e adicionar se não existe
            normativo = line[:150]  # Limitar caracteres
            if normativo not in info['normativos'] and len(info['normativos']) < 5:
                info['normativos'].append(normativo)
        
        # Buscar tipos de operadores
        operadores_tipos = ['TÉCNICO ESPECIALIZADO', 'COORDENADOR', 'APOIO GABINETE', 'APOIO-GABINETE']
        for operador in operadores_tipos:
            if operador in line.upper() and operador not in [o.upper() for o in info['operadores']]:
                info['operadores'].append(operador.title())
        
        # Buscar responsável/órgão
        if any(palavra in line.upper() for palavra in ['DECIPEX', 'CGBEN', 'COAUX']) and not info['responsavel']:
            info['responsável'] = line
    
    # Limpeza final - remover itens vazios
    info['sistemas'] = list(set(info['sistemas']))  # Remover duplicatas
    info['normativos'] = info['normativos'][:3]  # Máximo 3 normativos
    info['operadores'] = list(set(info['operadores']))[:3]  # Máximo 3 operadores
    
    return info

# ============================================================================
# ANÁLISE INTELIGENTE DE RISCOS COM IA
# ============================================================================

@csrf_exempt  
@require_http_methods(["POST"])  # <-- CORRIGIDO: era require_methods
def analyze_risks_ai(request):
    """API endpoint para análise de riscos com Helena especializada"""
    try:
        data = json.loads(request.body)
        pop_text = data.get('pop_text', '')
        pop_info = data.get('pop_info', {})
        answers = data.get('answers', {})
        
        # Validar se tem dados mínimos
        if not pop_text and not pop_info:
            return JsonResponse({
                'success': False, 
                'error': 'Dados do POP não fornecidos'
            }, status=400)
        
        # Chamar Helena especializada
        result = analyze_risks_helena(pop_text, pop_info, answers)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Erro na análise: {str(e)}'
        }, status=500)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def gerar_pop_completo(dados_processo):
    """Gera POP estruturado com todos os dados coletados"""
    
    template_pop = f"""
PROCEDIMENTO OPERACIONAL PADRÃO (POP)

1. NOME DO PROCESSO: {dados_processo.get('processo', 'Não informado')}

2. MACROPROCESSO: {dados_processo.get('macroprocesso', 'Não informado')}

3. OBJETIVO: {dados_processo.get('objetivo', 'Não informado')}

4. ENTREGA ESPERADA: {dados_processo.get('entrega_esperada', 'Não informado')}

5. BENEFICIÁRIO: {dados_processo.get('beneficiario', 'Não informado')}

6. BASE NORMATIVA: {dados_processo.get('base_normativa', 'Não informado')}

7. SISTEMAS UTILIZADOS: {dados_processo.get('sistemas_utilizados', 'Não informado')}

8. RESPONSÁVEL: {dados_processo.get('responsavel', 'Não informado')}

9. ETAPAS PRINCIPAIS:
{dados_processo.get('etapas', 'Não informado')}
"""
    
    return template_pop