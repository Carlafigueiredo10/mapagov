"""
FASE 2 - Row-Level Security (RLS) para Multi-tenancy

Implementa políticas de segurança a nível de linha no PostgreSQL:
- Usuários só veem dados do próprio Orgão
- Superusers têm acesso total (auditoria)
- Políticas separadas para SELECT, INSERT, UPDATE, DELETE

Benefícios:
- Segurança a nível de banco de dados (não apenas aplicação)
- Proteção contra SQL injection e bugs de autorização
- Compliance com LGPD (isolamento de dados)

NOTA: Esta migration só é aplicada em PostgreSQL. SQLite será pulado (RLS não suportado).
"""

from django.db import migrations, connection


def is_postgresql():
    """Verifica se o banco é PostgreSQL"""
    return connection.vendor == 'postgresql'


def apply_rls_policies(apps, schema_editor):
    """Aplica políticas RLS APENAS em PostgreSQL"""
    if not is_postgresql():
        print("[SKIP] RLS policies não aplicadas - SQLite em uso (dev). Use PostgreSQL em produção.")
        return

    with connection.cursor() as cursor:
        # 1. HABILITAR RLS
        cursor.execute("ALTER TABLE processos_chatsession ENABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE processos_chatmessage ENABLE ROW LEVEL SECURITY;")

        # 2. POLÍTICAS DE SELECT
        cursor.execute("""
            CREATE POLICY chatsession_select_policy ON processos_chatsession
                FOR SELECT
                USING (
                    (current_setting('app.is_superuser', true)::boolean = true)
                    OR
                    (orgao_id = current_setting('app.current_orgao_id', true)::integer)
                );
        """)

        cursor.execute("""
            CREATE POLICY chatmessage_select_policy ON processos_chatmessage
                FOR SELECT
                USING (
                    (current_setting('app.is_superuser', true)::boolean = true)
                    OR
                    EXISTS (
                        SELECT 1 FROM processos_chatsession cs
                        WHERE cs.id = processos_chatmessage.session_id
                        AND cs.orgao_id = current_setting('app.current_orgao_id', true)::integer
                    )
                );
        """)

        # 3. POLÍTICAS DE INSERT
        cursor.execute("""
            CREATE POLICY chatsession_insert_policy ON processos_chatsession
                FOR INSERT
                WITH CHECK (
                    orgao_id = current_setting('app.current_orgao_id', true)::integer
                );
        """)

        cursor.execute("""
            CREATE POLICY chatmessage_insert_policy ON processos_chatmessage
                FOR INSERT
                WITH CHECK (
                    EXISTS (
                        SELECT 1 FROM processos_chatsession cs
                        WHERE cs.id = session_id
                        AND cs.orgao_id = current_setting('app.current_orgao_id', true)::integer
                    )
                );
        """)

        # 4. POLÍTICAS DE UPDATE
        cursor.execute("""
            CREATE POLICY chatsession_update_policy ON processos_chatsession
                FOR UPDATE
                USING (
                    orgao_id = current_setting('app.current_orgao_id', true)::integer
                );
        """)

        cursor.execute("""
            CREATE POLICY chatmessage_update_policy ON processos_chatmessage
                FOR UPDATE
                USING (
                    EXISTS (
                        SELECT 1 FROM processos_chatsession cs
                        WHERE cs.id = session_id
                        AND cs.orgao_id = current_setting('app.current_orgao_id', true)::integer
                    )
                );
        """)

        # 5. POLÍTICAS DE DELETE
        cursor.execute("""
            CREATE POLICY chatsession_delete_policy ON processos_chatsession
                FOR DELETE
                USING (
                    orgao_id = current_setting('app.current_orgao_id', true)::integer
                );
        """)

        cursor.execute("""
            CREATE POLICY chatmessage_delete_policy ON processos_chatmessage
                FOR DELETE
                USING (
                    EXISTS (
                        SELECT 1 FROM processos_chatsession cs
                        WHERE cs.id = session_id
                        AND cs.orgao_id = current_setting('app.current_orgao_id', true)::integer
                    )
                );
        """)

    print("[OK] RLS policies aplicadas com sucesso!")


def reverse_rls_policies(apps, schema_editor):
    """Remove políticas RLS APENAS em PostgreSQL"""
    if not is_postgresql():
        return

    with connection.cursor() as cursor:
        # Remover políticas
        cursor.execute("DROP POLICY IF EXISTS chatsession_select_policy ON processos_chatsession;")
        cursor.execute("DROP POLICY IF EXISTS chatmessage_select_policy ON processos_chatmessage;")
        cursor.execute("DROP POLICY IF EXISTS chatsession_insert_policy ON processos_chatsession;")
        cursor.execute("DROP POLICY IF EXISTS chatmessage_insert_policy ON processos_chatmessage;")
        cursor.execute("DROP POLICY IF EXISTS chatsession_update_policy ON processos_chatsession;")
        cursor.execute("DROP POLICY IF EXISTS chatmessage_update_policy ON processos_chatmessage;")
        cursor.execute("DROP POLICY IF EXISTS chatsession_delete_policy ON processos_chatsession;")
        cursor.execute("DROP POLICY IF EXISTS chatmessage_delete_policy ON processos_chatmessage;")

        # Desabilitar RLS
        cursor.execute("ALTER TABLE processos_chatsession DISABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE processos_chatmessage DISABLE ROW LEVEL SECURITY;")


class Migration(migrations.Migration):
    dependencies = [
        ('processos', '0007_add_chat_models_fase1'),
    ]

    operations = [
        # Aplica políticas RLS APENAS em PostgreSQL (pula em SQLite para dev)
        migrations.RunPython(
            code=apply_rls_policies,
            reverse_code=reverse_rls_policies
        ),
    ]
