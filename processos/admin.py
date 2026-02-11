from django.contrib import admin
from .models import ProcessoMestre, POP, Area, PopVersion
from .models_auth import UserProfile, AccessApproval
from import_export.admin import ImportExportModelAdmin


@admin.register(ProcessoMestre)
class ProcessoMestreAdmin(ImportExportModelAdmin):
    list_display = ('codigo_arquitetura', 'atividade', 'macroprocesso')


@admin.register(Area)
class AreaAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'nome_curto', 'prefixo', 'ordem', 'ativo', 'area_pai')
    list_filter = ('ativo', 'tem_subareas')
    search_fields = ('codigo', 'nome', 'nome_curto')
    prepopulated_fields = {'slug': ('codigo',)}


@admin.register(POP)
class POPAdmin(admin.ModelAdmin):
    list_display = ('nome_processo', 'codigo_processo', 'area', 'status', 'versao', 'updated_at')
    list_filter = ('status', 'area')
    search_fields = ('nome_processo', 'codigo_processo')
    readonly_fields = ('uuid', 'integrity_hash', 'autosave_sequence')


@admin.register(PopVersion)
class PopVersionAdmin(admin.ModelAdmin):
    list_display = ('pop', 'versao', 'is_current', 'published_at', 'published_by')
    list_filter = ('is_current',)
    readonly_fields = ('payload', 'integrity_hash')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_type', 'email_verified', 'access_status', 'orgao', 'created_at')
    list_filter = ('profile_type', 'access_status', 'email_verified')
    search_fields = ('user__username', 'user__email', 'nome_completo')
    readonly_fields = ('created_at', 'updated_at', 'email_verified_at', 'approved_at', 'rejected_at')


@admin.register(AccessApproval)
class AccessApprovalAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'admin', 'vote', 'voted_at')
    list_filter = ('vote',)
    readonly_fields = ('voted_at',)