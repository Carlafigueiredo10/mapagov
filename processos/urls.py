# processos/urls.py - URLs completas do sistema com APIs renovadas

from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views
from .views import helena_mapeamento_api
from processos.api import chat_api  # FASE 1 - Nova API
from processos.api import planejamento_estrategico_api as pe_api  # Planejamento Estratégico API
from processos.api import analise_riscos_api as ar_api  # Analise de Riscos API
from processos.api import analise_riscos_export as ar_export  # Exportacao Word/PDF
from processos.api.catalogo_api import AreaViewSet, POPViewSet, pop_por_area_codigo, resolve_pop
from processos.api.catalogo_pdf import gerar_pdf_catalogo
from processos.api.catalogo_search import search_pops
from processos.api.catalogo_stats import stats_global, stats_area
from processos.api import auth_api, admin_api  # Auth & Access Control
from processos.infra import metrics  # FASE 3 - Prometheus Metrics

# DRF Router para CRUD de catalogo (Areas + POPs)
# SimpleRouter (sem root view) para nao conflitar com o React SPA em /
router = SimpleRouter()
router.register(r'api/areas', AreaViewSet, basename='area')
router.register(r'api/pops', POPViewSet, basename='pop-catalogo')

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
    # APIs HELENA POP - Padrao: Chat-driven State Machine
    # O POP NAO segue REST. A state machine e acionada via POST /api/chat/
    # com contexto='gerador_pop'. Ver docs/api-patterns.md
    # ============================================================================

    path('api/chat/', views.chat_api_view, name='chat-api'),
    path('api/chat-recepcao/', views.chat_recepcao_api, name='chat_recepcao_api'),
    path('api/helena-mapeamento/', helena_mapeamento_api, name='helena_mapeamento_api'),

    # Helena Ajuda Inteligente - Classificação de Atividade (ATIVA)
    path('api/helena-ajuda-arquitetura/', views.helena_ajuda_arquitetura, name='helena_ajuda_arquitetura'),

    # ============================================================================
    # APIs CHAT V2 - Padrao: Sessao unificada com roteamento automatico
    # Endpoint unico que roteia entre produtos via contexto. Ver docs/api-patterns.md
    # ============================================================================
    path('api/chat-v2/', chat_api.chat_v2, name='chat-v2'),
    path('api/chat-v2/mudar-contexto/', chat_api.mudar_contexto, name='chat-v2-mudar-contexto'),
    path('api/chat-v2/produtos/', chat_api.listar_produtos, name='chat-v2-produtos'),
    path('api/chat-v2/sessao/<str:session_id>/', chat_api.info_sessao, name='chat-v2-info-sessao'),
    path('api/chat-v2/sessao/<str:session_id>/mensagens/', chat_api.buscar_mensagens, name='chat-v2-mensagens'),
    path('api/chat-v2/finalizar/', chat_api.finalizar_sessao, name='chat-v2-finalizar'),

    # ============================================================================
    # APIs PLANEJAMENTO ESTRATEGICO - Padrao: REST (IDs int) + Conversacional
    # Combina CRUD (/listar, /<id>/) com /iniciar/ e /processar/
    # Ver docs/api-patterns.md
    # ============================================================================
    path('api/planejamento-estrategico/iniciar/', pe_api.iniciar_planejamento, name='pe-iniciar'),
    path('api/planejamento-estrategico/processar/', pe_api.processar_mensagem, name='pe-processar'),
    path('api/planejamento-estrategico/salvar/', pe_api.salvar_planejamento, name='pe-salvar'),
    path('api/planejamento-estrategico/listar/', pe_api.listar_planejamentos, name='pe-listar'),
    path('api/planejamento-estrategico/<int:planejamento_id>/', pe_api.obter_planejamento, name='pe-obter'),
    path('api/planejamento-estrategico/<int:planejamento_id>/aprovar/', pe_api.aprovar_planejamento, name='pe-aprovar'),
    path('api/planejamento-estrategico/<int:planejamento_id>/revisar/', pe_api.criar_revisao, name='pe-revisar'),
    path('api/planejamento-estrategico/<int:planejamento_id>/exportar/', pe_api.exportar_planejamento, name='pe-exportar'),
    path('api/planejamento-estrategico/modelos/', pe_api.obter_modelos, name='pe-modelos'),
    path('api/planejamento-estrategico/diagnostico/', pe_api.obter_diagnostico, name='pe-diagnostico'),
    path('api/planejamento-estrategico/recomendar/', pe_api.calcular_recomendacao, name='pe-recomendar'),
    path('api/planejamento-estrategico/iniciar-modelo/', pe_api.iniciar_modelo_direto, name='pe-iniciar-modelo'),
    path('api/planejamento-estrategico/confirmar-modelo/', pe_api.confirmar_modelo, name='pe-confirmar-modelo'),

    # ============================================================================
    # APIs ANALISE DE RISCOS - Padrao: REST CRUD com identificadores UUID
    # Ver docs/api-patterns.md
    # ============================================================================
    path('api/analise-riscos/criar/', ar_api.criar_analise, name='ar-criar'),
    path('api/analise-riscos/listar/', ar_api.listar_analises, name='ar-listar'),
    path('api/analise-riscos/<uuid:analise_id>/', ar_api.detalhar_analise, name='ar-detalhar'),
    path('api/analise-riscos/<uuid:analise_id>/questionario/', ar_api.atualizar_questionario, name='ar-questionario'),
    path('api/analise-riscos/<uuid:analise_id>/etapa/', ar_api.atualizar_etapa, name='ar-etapa'),
    path('api/analise-riscos/<uuid:analise_id>/finalizar/', ar_api.finalizar_analise, name='ar-finalizar'),
    path('api/analise-riscos/<uuid:analise_id>/riscos/', ar_api.adicionar_risco, name='ar-adicionar-risco'),
    path('api/analise-riscos/<uuid:analise_id>/riscos/<uuid:risco_id>/analise/', ar_api.analisar_risco, name='ar-analisar-risco'),
    path('api/analise-riscos/<uuid:analise_id>/riscos/<uuid:risco_id>/', ar_api.remover_risco, name='ar-remover-risco'),
    path('api/analise-riscos/<uuid:analise_id>/riscos/<uuid:risco_id>/respostas/', ar_api.adicionar_resposta, name='ar-adicionar-resposta'),

    # ============================================================================
    # APIs ANALISE DE RISCOS v2 - Novo fluxo (contexto + blocos + inferencia)
    # ============================================================================
    path('api/analise-riscos/v2/criar/', ar_api.criar_analise_v2, name='ar-v2-criar'),
    path('api/analise-riscos/<uuid:analise_id>/contexto/', ar_api.salvar_contexto_v2, name='ar-v2-contexto'),
    path('api/analise-riscos/<uuid:analise_id>/blocos/', ar_api.salvar_blocos_v2, name='ar-v2-blocos'),
    path('api/analise-riscos/<uuid:analise_id>/inferir/', ar_api.inferir_riscos_v2, name='ar-v2-inferir'),
    path('api/analise-riscos/<uuid:analise_id>/exportar/', ar_export.exportar_analise, name='ar-exportar'),

    # ============================================================================
    # OBSERVABILITY - FASE 3 📊
    # ============================================================================
    path('metrics/', metrics.metrics_view, name='prometheus-metrics'),  # Prometheus endpoint

    # APIs de autosave/snapshot/histórico
    # path('api/reiniciar-conversa-helena/', views.reiniciar_conversa_helena, name='reiniciar_helena'),
    path('api/pop-autosave/', views.autosave_pop, name='pop_autosave'),  # Auto-save real (PostgreSQL)
    path('api/pop/<str:identifier>/', views.get_pop, name='get_pop'),  # Carrega POP salvo
    path('api/pop-draft/save/', views.pop_draft_save, name='pop_draft_save'),  # Salva rascunho (PAUSA)
    path('api/pop-draft/<str:session_id>/', views.pop_draft_load, name='pop_draft_load'),  # Carrega rascunho
    # path('api/pop-backup-session/', views.backup_session_pops, name='pop_backup_session'),
    # path('api/pop-restore-snapshot/', views.restore_pop_snapshot, name='pop_restore_snapshot'),
    # path('api/pop-snapshot-milestone/', views.marcar_milestone_snapshot, name='pop_snapshot_milestone'),
    # path('api/pop-snapshot-diff/', views.diff_snapshots, name='pop_snapshot_diff'),
    # path('api/pop-historico/<int:pop_id>/', views.listar_historico_pop, name='pop_historico'),

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
    path('api/fluxograma-steps/', views.fluxograma_steps_api, name='fluxograma_steps_api'),

    # ============================================================================
    # APIs CATALOGO POP - CRUD + Resolve + Stats (Etapas 1-5)
    # Rotas manuais VEM ANTES do router.urls para nao conflitar
    # ============================================================================

    # PDF sob demanda version-aware (ANTES do detalhe para nao conflitar com <path:codigo>)
    path('api/areas/<slug:slug>/pops/<path:codigo>/pdf/', gerar_pdf_catalogo, name='pop-pdf-catalogo'),

    # Detalhe por area+codigo (usa <path:> para aceitar pontos em codigo tipo 6.1.1.1.5)
    path('api/areas/<slug:slug>/pops/<path:codigo>/', pop_por_area_codigo, name='pop-por-area-codigo'),

    # Resolve CAP via query params (evita conflito com router)
    path('api/pops/resolve/', resolve_pop, name='pop-resolve'),

    # Busca full-text
    path('api/pops/search/', search_pops, name='pop-search'),

    # Metricas
    path('api/stats/', stats_global, name='stats-global'),
    path('api/stats/areas/<str:slug>/', stats_area, name='stats-area'),

    # ============================================================================
    # AUTH API — Registro, Login, Verificação, Senha
    # ============================================================================
    path('api/auth/csrf/', auth_api.get_csrf, name='auth-csrf'),
    path('api/auth/register/', auth_api.register, name='auth-register'),
    path('api/auth/verify-email/<str:uidb64>/<str:token>/', auth_api.verify_email, name='auth-verify-email'),
    path('api/auth/login/', auth_api.login_view, name='auth-login'),
    path('api/auth/logout/', auth_api.logout_view, name='auth-logout'),
    path('api/auth/me/', auth_api.me, name='auth-me'),
    path('api/auth/password-reset/', auth_api.password_reset, name='auth-password-reset'),
    path('api/auth/password-reset-confirm/', auth_api.password_reset_confirm, name='auth-password-reset-confirm'),

    # ============================================================================
    # ADMIN API — Aprovação de cadastros, auditoria
    # ============================================================================
    path('api/admin/pending-users/', admin_api.list_pending, name='admin-pending'),
    path('api/admin/users/<int:user_id>/vote/', admin_api.cast_vote, name='admin-vote'),
    path('api/admin/users/<int:user_id>/', admin_api.user_detail, name='admin-user-detail'),
    path('api/admin/audit-log/', admin_api.audit_log, name='admin-audit'),

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

# DRF Router URLs (Areas + POPs CRUD)
urlpatterns += router.urls