from django.contrib import admin
from .models import ProcessoMestre, POP
from import_export.admin import ImportExportModelAdmin # Importamos a nova funcionalidade

# Removemos o registro antigo do ProcessoMestre daqui
# admin.site.register(ProcessoMestre)

@admin.register(ProcessoMestre)
class ProcessoMestreAdmin(ImportExportModelAdmin):
    list_display = ('codigo_arquitetura', 'atividade', 'macroprocesso')

# Mantemos o registro simples do POP por enquanto
admin.site.register(POP)