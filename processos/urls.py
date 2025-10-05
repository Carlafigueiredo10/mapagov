# processos/urls.py - URLs completas do sistema com APIs renovadas

from django.urls import path
from . import views
from .views import helena_mapeamento_api

urlpatterns = [
    # ============================================================================
    # PÁGINAS DO SISTEMA
    # ============================================================================
    
    path('', views.landing_temp, name='landing'),
    path('portal/', views.portal_temp, name='portal'),
    path('chat/', views.chat_temp, name='chat-page'),
    path('riscos/fluxo/', views.riscos_fluxo, name='riscos_fluxo'),
    path('fluxograma/', views.fluxograma_temp, name='fluxograma'),

    # ============================================================================
    # APIs HELENA - CHAT CONVERSACIONAL
    # ============================================================================
    
    path('api/chat/', views.chat_api_view, name='chat-api'),
    path('api/chat-recepcao/', views.chat_recepcao_api, name='chat_recepcao_api'),
    path('api/reiniciar-conversa-helena/', views.reiniciar_conversa_helena, name='reiniciar_helena'),
    path('api/helena-mapeamento/', helena_mapeamento_api, name='helena_mapeamento_api'),

    # ============================================================================
    # APIs PDF E DOCUMENTOS - NOVAS
    # ============================================================================
    
    path('api/gerar-pdf-pop/', views.gerar_pdf_pop, name='gerar_pdf_pop'),
    path('api/download-pdf/<str:nome_arquivo>/', views.download_pdf, name='download_pdf'),
    path('api/validar-dados-pop/', views.validar_dados_pop, name='validar_dados_pop'),

    # ============================================================================
    # APIs RAG E SUGESTÕES - NOVAS
    # ============================================================================
    
    path('api/consultar-rag-sugestoes/', views.consultar_rag_sugestoes, name='consultar_rag'),

    # ============================================================================
    # APIs EXTRAÇÃO E ANÁLISE PDF - EXISTENTES
    # ============================================================================
    
    path('api/extract-pdf/', views.extract_pdf_text, name='extract_pdf'),
    path('api/analyze-risks/', views.analyze_risks_helena, name='analyze_risks'),
    path('api/fluxograma-from-pdf/', views.fluxograma_from_pdf, name='fluxograma_from_pdf'),

    # ============================================================================
    # APIs FUTURAS - PRODUTOS EM DESENVOLVIMENTO
    # ============================================================================
    
    # path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    # path('api/analise-riscos-completa/', views.analise_riscos_api, name='analise_riscos_api'),
    # path('api/relatorio-riscos/', views.relatorio_riscos_api, name='relatorio_riscos_api'),
    # path('api/plano-acao/', views.plano_acao_api, name='plano_acao_api'),
    # path('api/dossie-governanca/', views.dossie_governanca_api, name='dossie_governanca_api'),
    # path('api/gerador-documentos/', views.gerador_documentos_api, name='gerador_documentos_api'),
    # path('api/relatorio-conformidade/', views.relatorio_conformidade_api, name='relatorio_conformidade_api'),
    # path('api/analise-artefatos/', views.analise_artefatos_api, name='analise_artefatos_api'),

    # ============================================================================
    # API DE TESTE OPENAI - DESATIVADA TEMPORARIAMENTE
    # ============================================================================
    # path('api/test-openai/', views.test_openai, name='test_openai'),
]