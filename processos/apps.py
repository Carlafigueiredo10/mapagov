from django.apps import AppConfig


class ProcessosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'processos'

    def ready(self):
        import os
        import sys

        # Não pré-carregar em: migrations, testes, collectstatic
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'test', 'collectstatic']):
            return

        # Em dev com autoreload: só carregar no processo filho (RUN_MAIN=true)
        # Em produção (gunicorn): RUN_MAIN não existe, sempre carrega
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return

        from processos.domain.helena_mapeamento.busca_atividade_pipeline import precarregar_modelo_semantico
        precarregar_modelo_semantico()
