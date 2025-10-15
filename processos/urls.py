# processos/urls.py - URLs completas do sistema com APIs renovadas

from django.urls import path
from . import views
from .views import helena_mapeamento_api

urlpatterns = [
    # ============================================================================
    # PÁGINAS DO SISTEMA - MIGRADAS PARA REACT
    # ============================================================================

    # TODAS AS ROTAS DE PÁGINAS FORAM MIGRADAS PARA REACT (frontend/)
    # O catch-all do mapagov/urls.py serve o React SPA para todas as rotas não-API
    # path('', views.landing_temp, name='landing'),  # Agora servido pelo React
    # path('portal/', views.portal_temp, name='portal'),  # Agora servido pelo React
    # path('chat/', views.chat_temp, name='chat-page'),  # Agora servido pelo React
    # path('riscos/fluxo/', views.riscos_fluxo, name='riscos_fluxo'),  # Agora servido pelo React
    # path('fluxograma/', views.fluxograma_temp, name='fluxograma'),  # Agora servido pelo React

    # ============================================================================
    # APIs HELENA - CHAT CONVERSACIONAL (BÁSICAS - FUNCIONAIS)
    # ============================================================================

    path('api/chat/', views.chat_api_view, name='chat-api'),
    path('api/chat-recepcao/', views.chat_recepcao_api, name='chat_recepcao_api'),
    path('api/helena-mapeamento/', helena_mapeamento_api, name='helena_mapeamento_api'),

    # APIs de autosave/snapshot/histórico - TEMPORARIAMENTE DESABILITADAS (views não commitadas)
    # path('api/reiniciar-conversa-helena/', views.reiniciar_conversa_helena, name='reiniciar_helena'),
    # path('api/pop-autosave/', views.autosave_pop, name='pop_autosave'),
    # path('api/pop-backup-session/', views.backup_session_pops, name='pop_backup_session'),
    # path('api/pop-restore-snapshot/', views.restore_pop_snapshot, name='pop_restore_snapshot'),
    # path('api/pop-snapshot-milestone/', views.marcar_milestone_snapshot, name='pop_snapshot_milestone'),
    # path('api/pop-snapshot-diff/', views.diff_snapshots, name='pop_snapshot_diff'),
    # path('api/pop-historico/<int:pop_id>/', views.listar_historico_pop, name='pop_historico'),
    # path('api/helena-ajuda-arquitetura/', views.helena_ajuda_arquitetura, name='helena_ajuda_arquitetura'),

    # ============================================================================
    # APIs PDF E DOCUMENTOS (FUNCIONAIS)
    # ============================================================================

    path('api/gerar-pdf-pop/', views.gerar_pdf_pop, name='gerar_pdf_pop'),
    path('api/download-pdf/<str:nome_arquivo>/', views.download_pdf, name='download_pdf'),
    path('api/validar-dados-pop/', views.validar_dados_pop, name='validar_dados_pop'),
    # path('api/validar-codigo-processo/', views.validar_codigo_processo, name='validar_codigo_processo'),  # View não existe

    # ============================================================================
    # APIs RAG E SUGESTÕES (FUNCIONAIS)
    # ============================================================================

    path('api/consultar-rag-sugestoes/', views.consultar_rag_sugestoes, name='consultar_rag'),

    # ============================================================================
    # APIs EXTRAÇÃO E ANÁLISE PDF (FUNCIONAIS)
    # ============================================================================

    path('api/extract-pdf/', views.extract_pdf_text, name='extract_pdf'),
    # path('api/analyze-risks/', views.analyze_risks_helena, name='analyze_risks'),  # View não existe
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