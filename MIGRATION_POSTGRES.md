# Migração para PostgreSQL

Este guia descreve como migrar o projeto de SQLite para PostgreSQL de forma segura.

## 1. Motivação
- Conexões concorrentes estáveis
- Integridade e performance sob carga
- Melhor suporte a JSONB / índices / full text

## 2. Preparar Ambiente
1. Criar instância Postgres (Neon / Render / Railway / RDS / Docker local).
2. Anotar URL de conexão no formato:
   ```
   postgres://usuario:senha@host:5432/nome_do_banco
   ```
3. Definir variável `DATABASE_URL` no ambiente (.env / painel de deploy).

## 3. Dependências
Já adicionada: `psycopg2-binary` em `requirements.txt`.
Instalar:
```
pip install -r requirements.txt
```

## 4. Configuração no settings
`mapagov/settings.py` agora lê:
- `DATABASE_URL` → Postgres
- Fallback → SQLite (`db.sqlite3`)

Opções adicionais:
- `DB_CONN_MAX_AGE=60` (padrão) – Reuso de conexões
- `DB_REQUIRE_SSL=true` + `DB_SSLMODE=require` (em produção)

## 5. Migração de Dados (se necessário)
Exportar dados do SQLite (somente apps necessários para reduzir ruído):
```bash
python manage.py dumpdata auth.user processos.POP processos.POPSnapshot processos.POPChangeLog > dump_pops.json
```
Configurar `DATABASE_URL` e então:
```bash
python manage.py migrate
python manage.py loaddata dump_pops.json
```

## 6. Verificação Pós-Migração
```bash
python manage.py shell -c "from processos.models import POP; print('POPs:', POP.objects.count())"
python manage.py check
```
Testar endpoints críticos:
- `POST /api/pop-autosave/`
- `POST /api/pop-backup-session/`
- `POST /api/pop-restore-snapshot/`
- `POST /api/pop-snapshot-diff/`
- `GET  /api/pop-historico/<id>/`

## 7. Teste de Rollback (Importante)
Simular:
1. `python manage.py dumpdata > full_backup.json`
2. Dropar e recriar banco vazio
3. `python manage.py migrate`
4. `python manage.py loaddata full_backup.json`
5. Validar integridade e contagens.

## 8. Índices Recomendados (após volume inicial)
```sql
CREATE INDEX IF NOT EXISTS pop_status_idx ON processos_pop (status);
CREATE INDEX IF NOT EXISTS pop_session_status_idx ON processos_pop (session_id, status);
CREATE INDEX IF NOT EXISTS pop_created_at_idx ON processos_pop (created_at);
```
Para snapshots (se crescer muito):
```sql
CREATE INDEX IF NOT EXISTS popsnapshot_pop_id_idx ON processos_popsnapshot (pop_id);
```

## 9. Backup e Retenção
- Usar snapshots automáticos do provedor (diário + retenção semanal). 
- Adicional: dump lógico diário armazenado em storage externo.

## 10. Segurança
- Nunca commitar `.env` com credenciais.
- Usar segredos do provedor (Render / Railway / etc.).
- Ativar SSL quando disponível.

## 11. Monitoramento e Saúde
- Criar endpoint `/healthz` opcional (retornar `{status: ok}`)
- Monitorar número de conexões `pg_stat_activity` se usar pool.
- Configurar Sentry ou equivalente para exceções.

## 12. Planejamento Futuro
Quando passar de:
- 100k snapshots → considerar particionamento por data.
- Crescimento de busca textual → usar tsvector ou engine externa.

## 13. Checklist Rápido
| Etapa | Status |
|-------|--------|
| Dependências instaladas | ✅ |
| DATABASE_URL definido | ☐ |
| Migrações aplicadas | ☐ |
| Dump/Load (se necessário) | ☐ |
| Endpoints testados | ☐ |
| Índices criados | ☐ |
| Backup automatizado | ☐ |

## 14. Perguntas Frequentes
**Posso manter SQLite para dev?** Sim (fallback). 
**Posso usar `dj-database-url`?** Opcional, atual já resolve.
**Preciso de JSONB?** Se começar a fazer queries internas em `raw_payload` ou payloads de snapshot.

---
Em caso de dúvida, execute em `dry-run` primeiro ou faça um clone do banco antes de operações destrutivas.
