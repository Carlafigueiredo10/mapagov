from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('processos.urls')),  # Inclui URLs do app processos na raiz
]

# Servir arquivos de mídia (uploads, PDFs) em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Servir assets do React em desenvolvimento
    urlpatterns += static('/assets/', document_root=settings.BASE_DIR / 'frontend' / 'dist' / 'assets')

# ============================================================================
# SERVIR FRONTEND REACT - Fallback para SPA (Single Page Application)
# ============================================================================
# Todas as rotas não capturadas pelas APIs do Django devem servir o index.html
# do React, permitindo que o React Router funcione corretamente

from django.views.generic import TemplateView

# Servir index.html do React para todas as rotas do frontend
# IMPORTANTE: Isso deve vir por último, depois de todas as URLs da API
urlpatterns += [
    re_path(r'^(?!api/|admin/|static/|media/|assets/).*$',
            TemplateView.as_view(template_name='index.html'),
            name='react-frontend'),
]