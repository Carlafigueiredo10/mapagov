# 🚀 Checklist de Deploy no Render

Este documento lista **todos os pontos de atenção** para deploy do MapaGov no Render, baseado em problemas reais enfrentados durante o desenvolvimento.

---

## 📋 Pré-Deploy: Checklist Obrigatório

### 1. ✅ Testar Localmente ANTES de Commitar

```bash
# Terminal 1: Backend Django
python manage.py runserver 8000

# Terminal 2: Frontend React (dev)
cd frontend
npm run dev

# Acessar: http://localhost:5174
# Testar: Chat, Helena, todas as funcionalidades novas
```

**IMPORTANTE:** Se não funciona local, NÃO vai funcionar no Render!

---

### 2. ✅ Build do Frontend e Commit

```bash
# Build de produção
cd frontend
npm run build

# Verificar se gerou arquivos
ls dist/index.html          # Deve existir (~480 bytes)
ls dist/assets/             # Deve ter vários arquivos .js e .css

# Adicionar ao Git (dist está no .gitignore!)
git add -f frontend/dist/
git status  # Verificar que dist/ está sendo commitado
```

**PEGADINHA #1:** `frontend/dist/` está no `.gitignore`! Sempre usar `-f` para forçar.

---

### 3. ✅ Verificar Views e URLs

```bash
# Verificar que NÃO há funções comentadas/não-existentes em urls.py
grep "views\." processos/urls.py

# Cada função deve existir em processos/views.py
# Se não existe, COMENTE a linha no urls.py!
```

**PEGADINHA #2:** URLs apontando para funções inexistentes causam `AttributeError` no deploy.

**Exemplo de erro:**
```
AttributeError: module 'processos.views' has no attribute 'autosave_pop'
```

**Solução:** Comentar a rota ou implementar a função.

---

### 4. ✅ Verificar requirements.txt

Toda vez que adicionar nova dependência Python:

```bash
pip freeze > requirements.txt

# Verificar se está lá
grep "nova-biblioteca" requirements.txt
```

**Dependências críticas para produção:**
- `psycopg2-binary==2.9.10` (PostgreSQL)
- `gunicorn` (servidor WSGI)
- `whitenoise` (servir arquivos estáticos)
- `django-cors-headers` (CORS para React)

**PEGADINHA #3:** `sentry-sdk` é OPCIONAL. Se não configurar `SENTRY_DSN`, não causará erro (código trata exceção).

---

### 5. ✅ Commit e Push

```bash
git add -A
git status  # Revisar tudo que vai subir

# Commit descritivo
git commit -m "feat: adiciona produto helena_dashboard

- Implementa geração de dashboard
- Adiciona rotas da API
- Testa localmente com sucesso
"

git push origin main
```

**PEGADINHA #4:** NÃO commitar:
- `db.sqlite3` (banco local)
- `.env` (secrets)
- `nul` (arquivo Windows inválido)
- `chroma_db/` (banco vetorial - grande demais)

---

## 🔧 Configuração do Render (Uma Vez)

### 1. ✅ Criar Web Service

- **Name:** mapagov
- **Region:** Oregon (US West)
- **Branch:** main
- **Build Command:** `bash build.sh`
- **Start Command:** `gunicorn mapagov.wsgi:application`

---

### 2. ✅ Variáveis de Ambiente

Configurar em **Environment** → **Add Environment Variable**:

| Variável | Valor | Obrigatório? |
|----------|-------|--------------|
| `DEBUG` | `False` | ✅ Sim |
| `SECRET_KEY` | (gerar novo) | ✅ Sim |
| `ALLOWED_HOSTS` | `mapagov.onrender.com,.onrender.com` | ✅ Sim |
| `DATABASE_URL` | (copiar do PostgreSQL) | ✅ Sim |
| `OPENAI_API_KEY` | `sk-...` | ✅ Sim |
| `CORS_ALLOWED_ORIGINS` | `https://mapagov.onrender.com` | ✅ Sim |
| `SENTRY_DSN` | (opcional) | ❌ Não |

**Como gerar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**PEGADINHA #5:** `DATABASE_URL` deve ser o **Internal Database URL** (não o External!).

---

### 3. ✅ Criar PostgreSQL Database

- **Name:** mapagov-db
- **Region:** Oregon (US West) - **mesma região do Web Service!**
- **Plan:** Free

**Copiar o Internal Database URL:**
```
postgres://usuario:senha@dpg-xxxxx/mapagov_db_yyyy
```

Colar em `DATABASE_URL` do Web Service.

**PEGADINHA #6:** SQLite NÃO funciona em produção! Sempre PostgreSQL.

---

## 🐛 Troubleshooting: Erros Comuns

### ❌ Erro: `ModuleNotFoundError: No module named 'X'`

**Causa:** Dependência faltando no `requirements.txt`

**Solução:**
```bash
pip install X
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: adiciona dependência X"
git push
```

---

### ❌ Erro: `AttributeError: module 'processos.views' has no attribute 'funcao'`

**Causa:** URL aponta para função que não existe

**Solução:**
```python
# processos/urls.py
# path('api/endpoint/', views.funcao, name='endpoint'),  # COMENTAR!
```

Commitar e fazer push.

---

### ❌ Erro: 502 Bad Gateway (site não carrega)

**Possíveis causas:**

1. **Assets do React não estão sendo servidos**
   - Verificar se `frontend/dist/` foi commitado com `-f`
   - Verificar logs: procurar por "404" nas requisições de `.js` e `.css`

2. **Django catch-all capturando /assets/**
   - Verificar `mapagov/urls.py`: regex deve ter `(?!api/|admin/|static/|media/|assets/)`

3. **Vite base URL incorreto**
   - Verificar `frontend/vite.config.ts`: `base: mode === 'production' ? '/static/' : '/'`

**Solução:** Ver seção "Arquitetura de Servir Assets" abaixo.

---

### ❌ Erro: `npm ci` falhou (package-lock.json não encontrado)

**Causa:** `npm ci` requer `package-lock.json` commitado

**Solução:** Usar `npm install` no `build.sh`:
```bash
# build.sh (linha 14)
npm install  # NÃO usar npm ci
```

---

### ❌ Erro: Vite build - `Could not resolve entry module "index.html"`

**Causa:** Arquivos do frontend não foram commitados

**Solução:**
```bash
git add -f frontend/
git commit -m "fix: adiciona arquivos do frontend"
git push
```

---

### ❌ Site mostra templates Django antigos (não React)

**Causa:** Rotas Django em `processos/urls.py` interceptando antes do catch-all do React

**Solução:** Comentar rotas de páginas:
```python
# processos/urls.py
# urlpatterns = [
#     path('', views.landing_temp, name='landing'),  # COMENTAR
#     path('chat/', views.chat_temp, name='chat'),   # COMENTAR
# ]
```

---

## 🏗️ Arquitetura de Servir Assets (React + Django)

### Como funciona em Produção:

```
Usuário → https://mapagov.onrender.com/
         ↓
    Gunicorn (Django)
         ↓
    WhiteNoise (arquivos estáticos)
         ↓
    /static/index.html         → frontend/dist/index.html
    /static/assets/index-*.js  → frontend/dist/assets/index-*.js
    /static/assets/index-*.css → frontend/dist/assets/index-*.css
```

### Fluxo de Configuração:

1. **Vite gera build** com `base: '/static/'` (apenas em produção)
   ```html
   <!-- frontend/dist/index.html -->
   <script src="/static/assets/index-CosUbrV4.js"></script>
   ```

2. **Django collectstatic** copia `frontend/dist/` para `staticfiles/`
   ```
   staticfiles/
   ├── index.html
   ├── assets/
   │   ├── index-*.js
   │   └── index-*.css
   ```

3. **WhiteNoise serve** arquivos de `staticfiles/` com prefixo `/static/`

4. **Django catch-all** serve `index.html` para rotas do React (`/`, `/chat`, etc.)
   ```python
   # mapagov/urls.py
   re_path(r'^(?!api/|admin/|static/|media/|assets/).*$',
           TemplateView.as_view(template_name='index.html'))
   ```

**PEGADINHA #7:** Se `/assets/` NÃO estiver na regex de exclusão, Django retorna `index.html` para requisições de `.js`!

---

## 📦 Estrutura de Arquivos Críticos

```
mapagov/
├── build.sh                    # Script de build do Render
├── Procfile                    # Comando de start (gunicorn)
├── runtime.txt                 # Versão do Python (3.13.0)
├── requirements.txt            # Dependências Python
├── mapagov/
│   ├── settings.py             # Configuração Django
│   │   ├── STATICFILES_DIRS    # Inclui frontend/dist/
│   │   ├── TEMPLATES['DIRS']   # Inclui frontend/dist/
│   │   └── ALLOWED_HOSTS       # .onrender.com
│   └── urls.py                 # Catch-all do React
├── processos/
│   ├── urls.py                 # APIs e rotas
│   └── views.py                # Funções das APIs
└── frontend/
    ├── vite.config.ts          # base: condicional
    ├── dist/                   # Build de produção (COMMITADO!)
    │   ├── index.html
    │   └── assets/
    │       ├── index-*.js
    │       └── index-*.css
    └── package.json
```

---

## ⏱️ Tempo de Deploy

**Primeiro deploy:** 20-30 minutos
**Deploys subsequentes:** 5-10 minutos (com cache)

### Etapas (deploy completo):

1. **Download do código** (30s)
2. **npm install** (5-8 min) - cache acelera
3. **npm run build** (3-5 min)
4. **pip install** (5-8 min) - cache acelera
5. **collectstatic** (2-3 min)
6. **migrate** (1-2 min)
7. **Restart** (1 min)

**DICA:** Deploys ficam mais rápidos após o primeiro (cache de dependências).

---

## 🔄 Workflow de Deploy (Resumo)

```bash
# 1. Desenvolver e testar LOCAL
python manage.py runserver 8000    # Terminal 1
cd frontend && npm run dev          # Terminal 2
# Testar em http://localhost:5174

# 2. Build do frontend
cd frontend
npm run build

# 3. Verificar arquivos
ls dist/index.html
ls dist/assets/

# 4. Commit (forçar dist/)
git add -f frontend/dist/
git add processos/urls.py processos/views.py  # Se alterou APIs
git commit -m "feat: adiciona produto helena_X"
git push origin main

# 5. Aguardar deploy no Render (15-30 min)
# Monitorar logs em: https://dashboard.render.com

# 6. Testar produção
# https://mapagov.onrender.com
```

---

## 🎯 Checklist Final Antes de Push

- [ ] Código testado localmente
- [ ] Frontend build gerado (`npm run build`)
- [ ] `frontend/dist/` commitado com `-f`
- [ ] Todas as funções em `urls.py` existem em `views.py`
- [ ] Novas dependências estão no `requirements.txt`
- [ ] Commit descritivo com mensagem clara
- [ ] Não commitou arquivos sensíveis (`.env`, `db.sqlite3`)

---

## 🆘 Em Caso de Erro no Deploy

1. **Ler os logs** no Render Dashboard
2. **Identificar o erro** (módulo faltando, import quebrado, etc.)
3. **Corrigir localmente** e testar
4. **Commitar apenas a correção** (não misturar fixes com features)
5. **Push** - Render faz auto-deploy
6. **Aguardar** novo deploy (5-10 min se só fix pequeno)

**DICA:** Cada push gera novo deploy. Evite commits desnecessários (gera fila de deploys).

---

## 📚 Referências Úteis

- **Render Docs:** https://render.com/docs
- **Django WhiteNoise:** https://whitenoise.readthedocs.io/
- **Vite Config:** https://vitejs.dev/config/
- **PostgreSQL Render:** https://render.com/docs/databases

---

## 🔮 Próximos Passos (Produtos Futuros)

Ao desenvolver os **8 produtos Helena restantes**:

1. Criar funções em `processos/views.py`
2. Adicionar rotas em `processos/urls.py`
3. **SEMPRE testar local primeiro**
4. Seguir este checklist para deploy
5. Fazer **1 commit por produto** (facilita rollback se der erro)

**Exemplo de commit ideal:**
```
feat: adiciona produto helena_dashboard

- Implementa helena_dashboard.py com LangChain
- Adiciona API /api/helena-dashboard/
- Testa chat com sucesso localmente
- Frontend consome nova API

Closes #XX
```

---

**Última atualização:** 2025-10-15
**Versão:** 1.0
**Autor:** Equipe MapaGov com Claude Code
