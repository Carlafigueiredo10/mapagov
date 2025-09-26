# processos/urls.py - URLs completas do sistema

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================================
    # PÁGINAS DO SISTEMA
    # ============================================================================
    
    # Página institucional principal
    path('', views.landing_temp, name='landing'),
    
    # Portal do sistema 
    path('portal/', views.portal_temp, name='portal'),
    
    # Chat Helena (mapeamento de processos)
    path('chat/', views.chat_temp, name='chat-page'),
    
    # Análise de Riscos - POP
    path('riscos/fluxo/', views.riscos_fluxo, name='riscos_fluxo'),
    
    # Gerador de Fluxogramas via PDF
    path('fluxograma/', views.fluxograma_temp, name='fluxograma'),
    
    # ============================================================================
    # APIs DO SISTEMA
    # ============================================================================
    
    # API Helena - Chat conversacional para mapeamento
    path('api/chat_message/', views.chat_api_view, name='chat-api'),
    
    # API Helena Recepcionista - Landing Page (orientação geral)
    path('api/chat-recepcao/', views.chat_recepcao_api, name='chat_recepcao_api'),
    
    # API Extração PDF - Processar POPs em PDF
    path('api/extract-pdf/', views.extract_pdf_text, name='extract_pdf'),
    
    # API Helena - Análise especializada de riscos
    path('api/analyze-risks/', views.analyze_risks_helena, name='analyze_risks'),
    
    # API Fluxograma a partir de PDF - Upload e Chat
    path('api/fluxograma-from-pdf/', views.fluxograma_from_pdf, name='fluxograma_from_pdf'),
]