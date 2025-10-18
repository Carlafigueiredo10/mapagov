# 🚀 Deploy MapaGov no Google Cloud

Guia completo para fazer deploy do MapaGov usando Google Cloud Platform (GCP).

## ✅ Status do Deploy (Atualizado em 16/10/2025 - DEPLOY COMPLETO!)

### 🎉 SISTEMA 100% FUNCIONAL EM PRODUÇÃO!

**URL de Produção:** https://mapagov-113328225062.us-central1.run.app

### O que está FUNCIONANDO:
- ✅ **Frontend React** carregando perfeitamente (landing page, Helena IA, interface completa)
- ✅ **Backend Django** rodando com todas as APIs
- ✅ **PostgreSQL Cloud SQL** conectado e funcional
- ✅ **Admin Django** acessível em `/admin` (user: admin)
- ✅ **Secrets** configurados e funcionando
- ✅ **Build automático** do Docker (frontend + backend)
- ✅ **Deploy automático** no Cloud Run

### Problemas Resolvidos Durante o Deploy:
1. ✅ **SQLite em produção bloqueado** → Solução: `SKIP_DB_CHECK=1` durante collectstatic
2. ✅ **CSRF_TRUSTED_ORIGINS** → Adicionado domínio completo do Cloud Run
3. ✅ **TemplateDoesNotExist** → Frontend build falhando silenciosamente
4. ✅ **Vite not found** → Dockerfile usava `--only=production` (não instalava devDependencies)
5. ✅ **Frontend dist vazio** → Fallback `|| mkdir -p dist` escondia erros do build

### Próximos Passos (Opcionais):
- 🔜 Configurar domínio customizado `mapagov.com.br`
- 🔜 Configurar monitoramento (Sentry)
- 🔜 Otimizar performance (CDN, cache)

---

## 🐛 Problemas Resolvidos Durante o Deploy (Referência Completa)

Esta seção documenta TODOS os problemas encontrados e suas soluções, para que você não precise sofrer no próximo deploy!

### ❌ Problema 1: SQLite em Produção Bloqueado Durante Build

**Erro Completo:**
```
RuntimeError: ❌ PRODUÇÃO COM SQLITE DETECTADA! SQLite não suporta concorrência e não escala.
Defina DATABASE_URL para PostgreSQL
```

**Causa:**
- Django `settings.py` valida se está usando SQLite em produção e bloqueia
- Durante o build do Docker, `python manage.py collectstatic` tenta acessar o banco
- Mas o PostgreSQL Cloud SQL não está disponível durante o build!

**Solução Aplicada:**

1. **Dockerfile** (linhas 61-63):
```dockerfile
# Temporariamente permite SQLite durante collectstatic no build
ENV SKIP_DB_CHECK=1
RUN python manage.py collectstatic --noinput || echo "WARN: collectstatic failed"
ENV SKIP_DB_CHECK=0
```

2. **mapagov/settings.py** (linhas 151-157):
```python
# Permite SQLite apenas durante collectstatic no Docker build (SKIP_DB_CHECK=1)
SKIP_DB_CHECK = os.getenv('SKIP_DB_CHECK', '0') == '1'
if not DEBUG and not SKIP_DB_CHECK and DATABASES['default']['ENGINE'].endswith('sqlite3'):
    raise RuntimeError(
        "❌ PRODUÇÃO COM SQLITE DETECTADA! SQLite não suporta concorrência e não escala.\n"
        "Defina DATABASE_URL para PostgreSQL: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'\n"
        "Veja MIGRATION_POSTGRES.md para instruções completas."
    )
```

**Arquivos Modificados:**
- [Dockerfile](Dockerfile) (linhas 61-63)
- [mapagov/settings.py](mapagov/settings.py) (linhas 151-157)

---

### ❌ Problema 2: CSRF Verification Failed (403 Forbidden)

**Erro Completo:**
```
Verificação CSRF falhou. Pedido cancelado.
CSRF token missing or incorrect.
```

**Causa:**
- Django protege formulários contra CSRF attacks
- O domínio do Cloud Run (`https://mapagov-113328225062.us-central1.run.app`) não estava na lista de origens confiáveis
- Django rejeitava todos os formulários (login, chat, etc.)

**Tentativas que NÃO funcionaram:**
1. ❌ Usar wildcard `CSRF_TRUSTED_ORIGINS = ['https://*.run.app']` → Django não suporta wildcards
2. ❌ Adicionar só via variável de ambiente → não era lida no startup
3. ❌ Desabilitar CSRF temporariamente → péssima prática de segurança

**Solução Aplicada:**

**mapagov/settings.py** (linhas 29-38):
```python
# CSRF Trusted Origins (para formulários de login/admin)
CSRF_TRUSTED_ORIGINS = [
    'https://mapagov-113328225062.us-central1.run.app',  # Domínio COMPLETO do Cloud Run
    'https://mapagov.onrender.com',
]

# Adicionar origens de produção via variável de ambiente
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins_env.split(',')])
```

**Como adicionar novo domínio:**
1. Se for customizado (ex: `mapagov.com.br`), adicione direto no código:
   ```python
   CSRF_TRUSTED_ORIGINS = [
       'https://mapagov.com.br',
       'https://mapagov-113328225062.us-central1.run.app',
   ]
   ```

2. Ou via variável de ambiente no Cloud Run:
   ```bash
   gcloud run services update mapagov \
     --region us-central1 \
     --set-env-vars CSRF_TRUSTED_ORIGINS="https://mapagov.com.br"
   ```

**Arquivos Modificados:**
- [mapagov/settings.py](mapagov/settings.py) (linhas 29-38)

---

### ❌ Problema 3: TemplateDoesNotExist - index.html não encontrado

**Erro Completo:**
```
TemplateDoesNotExist at /
index.html
```

**Causa:**
- Django usa fallback route pra servir React SPA: qualquer URL não capturada vai pra `index.html`
- Mas o `frontend/dist/index.html` não estava sendo gerado no build
- Quando descomentamos o fallback, Django procurava `index.html` que não existia

**Por que estava faltando?**
→ Ver **Problemas 4 e 5** abaixo (build do Vite falhando)

**Solução Temporária Aplicada:**
- Comentamos temporariamente as linhas 30-34 do `mapagov/urls.py` para não buscar o index.html
- Backend funcionou, mas frontend não carregava

**Solução Definitiva:**
1. Corrigir build do frontend (Problemas 4 e 5)
2. Verificar que `frontend/dist/index.html` existe e tem conteúdo
3. Descomentar fallback route em `mapagov/urls.py`

**mapagov/urls.py** (linhas 30-34) - Estado FINAL (descomentado):
```python
# Servir frontend React como fallback para SPA
urlpatterns += [
    re_path(r'^(?!api/|admin/|static/|media/|assets/).*$',
            TemplateView.as_view(template_name='index.html'),
            name='react-frontend'),
]
```

**⚠️ IMPORTANTE:** NUNCA descomente isso sem antes verificar:
```bash
# 1. Verificar que index.html existe E tem conteúdo
ls -lh frontend/dist/index.html
# Deve mostrar tamanho > 0 bytes (ex: 2.1K)

# 2. Verificar que o build rodou com sucesso
grep "build completed" logs-do-docker.txt

# 3. Verificar que collectstatic copiou o arquivo
ls -lh staticfiles/index.html
```

**Arquivos Modificados:**
- [mapagov/urls.py](mapagov/urls.py) (linhas 30-34)

---

### ❌ Problema 4: Vite Command Not Found (ROOT CAUSE!)

**Erro Completo:**
```
sh: line 1: vite: command not found
npm run build failed
```

**Causa RAIZ de todos os problemas de frontend:**
- **Dockerfile linha 17** usava: `RUN npm ci --only=production`
- Flag `--only=production` NÃO instala `devDependencies`
- **Vite está em devDependencies!** (frontend/package.json)
- Sem Vite, `npm run build` falha
- Build falha → `frontend/dist/` fica vazio ou com arquivo de 0 bytes

**Solução Aplicada:**

**Dockerfile** (linha 17) - ANTES:
```dockerfile
RUN npm ci --only=production || echo "WARN: npm ci failed, frontend may not work"
```

**Dockerfile** (linha 17) - DEPOIS:
```dockerfile
RUN npm ci || echo "WARN: npm ci failed, frontend may not work"
```

**Por que `--only=production` estava lá?**
- Má prática copiada de tutoriais antigos
- Ideia era reduzir tamanho do container
- Mas Vite é necessário pra BUILD, mesmo em produção!

**Como verificar se Vite foi instalado:**
```bash
# No Cloud Shell, após rodar npm ci:
ls -la frontend/node_modules/.bin/vite
# Deve existir
```

**Arquivos Modificados:**
- [Dockerfile](Dockerfile) (linha 17)

---

### ❌ Problema 5: Frontend Build Falhando Silenciosamente

**Erro Oculto:**
```
npm run build
# Falha, mas Dockerfile continua sem reportar erro
```

**Causa:**
- **Dockerfile linha 23** tinha fallback que escondia erros:
  ```dockerfile
  RUN npm run build || mkdir -p dist && echo "WARN: Frontend build failed, using empty dist"
  ```
- Se `npm run build` falhasse, criava pasta `dist` vazia
- Docker build continuava "com sucesso"
- Resultado: `frontend/dist/index.html` vazio (0 bytes)

**Solução Aplicada:**

**Dockerfile** (linha 23) - ANTES:
```dockerfile
RUN npm run build || mkdir -p dist && echo "WARN: Frontend build failed, using empty dist"
```

**Dockerfile** (linha 23) - DEPOIS:
```dockerfile
RUN npm run build
```

**Por que remover o fallback?**
- **Fail-fast é melhor!** Se build falha, deploy deve falhar também
- Frontend vazio é pior que deploy falhado
- Erros ficam visíveis nos logs do Cloud Build

**Como verificar se build funcionou:**
```bash
# Após npm run build, verificar se arquivos foram gerados:
ls -lah frontend/dist/
# Deve ter: index.html, assets/, vite.svg

# index.html deve ter conteúdo:
wc -c frontend/dist/index.html
# Deve ser > 0 bytes (ex: 2154 bytes)
```

**Arquivos Modificados:**
- [Dockerfile](Dockerfile) (linha 23)

---

### ❌ Problema 6: Serviço Duplicado Criado por Engano

**Erro:**
```bash
# Criamos por engano:
gcloud run deploy mapagov-backend ...
# Em vez de atualizar o existente:
gcloud run deploy mapagov ...
```

**Causa:**
- Não verificamos se serviço `mapagov` já existia
- Usamos nome diferente (`mapagov-backend`)
- Cloud Run criou serviço NOVO em vez de atualizar

**Resultado:**
- 2 serviços rodando: `mapagov` (vazio) e `mapagov-backend` (funcional)
- Confusão sobre qual URL usar
- Gasto desnecessário de recursos

**Solução Aplicada:**

1. **Listar serviços ANTES de deploy:**
```bash
gcloud run services list --region us-central1
```

2. **Deletar serviço duplicado:**
```bash
gcloud run services delete mapagov-backend --region us-central1
```

3. **Deploy com nome correto:**
```bash
gcloud run deploy mapagov \
  --image gcr.io/neat-environs-472910-g9/mapagov:latest \
  --region us-central1
```

**Prevenção:**
- **SEMPRE** rode `gcloud run services list` ANTES de deploy
- Confirme o nome do serviço existente
- Use exatamente o mesmo nome para atualizar

**Documentação Atualizada:**
- Adicionado seção "⚠️ SEMPRE VERIFICAR SERVIÇOS EXISTENTES" em [DEPLOY_GOOGLE_CLOUD.md](DEPLOY_GOOGLE_CLOUD.md) (linhas 285-311)

---

### ❌ Problema 7: Cloud Shell sem Espaço em Disco

**Erro:**
```
No space left on device
/home/your_user: 100% full (4.6GB used of 5GB)
```

**Causa:**
- Cloud Shell tem limite de 5GB no `/home`
- Cache do Python e npm acumulando
- `~/.cache/` e `~/.local/lib/python*/site-packages/` ocupando muito espaço

**Solução Aplicada:**

```bash
# 1. Verificar uso de espaço
df -h /home

# 2. Limpar cache npm
rm -rf ~/.cache/*
# Liberou ~3.8GB

# 3. Limpar pacotes Python desnecessários
rm -rf ~/.local/lib/python*/site-packages/*
# Liberou ~700MB

# 4. Verificar novamente
df -h /home
# /home: 15% used (750MB of 5GB)
```

**Prevenção:**
- Rodar `rm -rf ~/.cache/*` semanalmente no Cloud Shell
- Ou usar terminal local (Windows) que não tem limite de espaço

**Quando usar Cloud Shell vs Local:**
- **Cloud Shell**: Máquina não tem gcloud instalado, ou quer build mais rápido (rede do Google)
- **Local**: Tem gcloud instalado, quer usar código local sem git push

---

### ❌ Problema 8: Código Desatualizado no Cloud Shell

**Erro:**
```bash
# Fez mudança no Windows, fez git push
# Rodou build no Cloud Shell
# Build usou código ANTIGO (antes do push)
```

**Causa:**
- Cloud Shell clona repositório 1x
- Código fica em `~/mapagov`
- Depois de `git push` no Windows, código no Cloud Shell fica desatualizado
- Build usa código local do Cloud Shell, não o do GitHub

**Solução Aplicada:**

```bash
# SEMPRE rodar no Cloud Shell ANTES de build:
cd ~/mapagov
git pull origin main

# Verificar que mudanças estão lá:
grep "alguma_coisa_que_mudei" arquivo.py

# Agora sim, fazer build:
gcloud builds submit --tag gcr.io/PROJECT_ID/mapagov
```

**Alternativa:**
- Usar terminal local (Windows) com gcloud instalado
- `gcloud builds submit` envia código local diretamente, ignora GitHub

**Workflow Recomendado:**

**Opção A - Cloud Shell:**
```bash
# No Windows
git add .
git commit -m "feat: nova funcionalidade"
git push origin main

# No Cloud Shell
cd ~/mapagov
git pull origin main  # ⚠️ CRÍTICO!
gcloud builds submit --tag gcr.io/PROJECT_ID/mapagov
```

**Opção B - Terminal Local (mais fácil):**
```bash
# No Windows (com gcloud instalado)
git add .
git commit -m "feat: nova funcionalidade"
gcloud builds submit --tag gcr.io/PROJECT_ID/mapagov
git push origin main  # Opcional, só pra backup
```

---

## 📚 Lições Aprendidas

### ✅ O que funcionou bem:
1. **Multi-stage Docker build** - Frontend e backend em 1 container
2. **Secret Manager** - Credenciais seguras fora do código
3. **Cloud SQL Proxy** - Conexão segura com banco sem IP público
4. **WhiteNoise** - Servir arquivos estáticos sem nginx extra
5. **Fail-fast** - Remover fallbacks silenciosos, mostrar erros logo

### ❌ O que evitar:
1. **Nunca** usar `--only=production` com build tools (Vite, Webpack, etc.)
2. **Nunca** esconder erros de build com `|| mkdir -p dist`
3. **Nunca** assumir que "build passou" = "frontend funciona"
4. **Sempre** verificar serviços existentes antes de deploy
5. **Sempre** verificar `index.html` existe e tem conteúdo antes de descomentar fallback route

### 🔧 Checklist para Próximo Deploy:

#### Antes de fazer deploy:
- [ ] `gcloud run services list` - Verificar nome do serviço existente
- [ ] `npm run build` local - Verificar que frontend builda
- [ ] `ls -lh frontend/dist/index.html` - Verificar arquivo existe (> 0 bytes)
- [ ] `grep CSRF_TRUSTED_ORIGINS settings.py` - Verificar domínio está na lista

#### Durante o deploy:
- [ ] No Cloud Shell: `git pull origin main` - Código atualizado
- [ ] `gcloud builds submit` - Build da imagem
- [ ] Verificar logs do build - Frontend buildou com sucesso?
- [ ] `gcloud run deploy NOME_CORRETO` - Mesmo nome do serviço existente

#### Depois do deploy:
- [ ] Acessar URL - Página carrega?
- [ ] Testar chat - APIs funcionam?
- [ ] Testar login admin - CSRF ok?
- [ ] `gcloud run services logs tail` - Verificar erros

---

## 📋 Pré-requisitos

- ✅ Conta Google Cloud ativa (você tem R$ 1.860 em créditos!)
- ✅ Projeto GCP criado (`MapaGov` / ID: `neat-environs-472910-g9`)
- ✅ APIs habilitadas (Cloud Run, Cloud SQL, Cloud Build, Secret Manager, Storage)
- ✅ Código no GitHub

---

## 🏗️ Arquitetura no Google Cloud

```
GitHub (código)
    ↓
Cloud Build (CI/CD automático)
    ↓
Container Registry (imagem Docker)
    ↓
Cloud Run (aplicação Django + React)
    ↓
Cloud SQL (PostgreSQL)
    ↓
Cloud Storage (arquivos estáticos + backups)
```

---

## 📝 Passo a Passo

### **PARTE 1: Criar Banco de Dados (Cloud SQL)**

1. No Console GCP, vá em **"SQL"** (menu ☰ → SQL)
2. Clique em **"Criar Instância"**
3. Escolha **PostgreSQL**
4. Configure:
   - **Nome da instância**: `mapagov-db`
   - **Senha do root**: Crie uma senha forte (salve em local seguro!)
   - **Região**: `us-central1` (Iowa - mais barato)
   - **Versão PostgreSQL**: `15` ou superior
   - **Configuração de máquina**:
     - Desenvolvimento: **Shared Core (1 vCPU)** → ~$10/mês
     - Produção: **Dedicated (2 vCPU, 7.5 GB)** → ~$70/mês
   - **Armazenamento**: 10 GB (SSD)
   - **Backups automáticos**: ✅ Habilitado

5. Clique em **"Criar instância"** (leva ~5 minutos)

6. Após criar, anote:
   - **Connection name**: `neat-environs-472910-g9:us-central1:mapagov-db`
   - **IP público**: (não vamos usar, mas anote)

7. Criar banco de dados:
   - Vá na aba **"Databases"**
   - Clique em **"Create database"**
   - Nome: `mapagov`
   - Charset: `UTF8`

8. Criar usuário (opcional):
   - Vá na aba **"Users"**
   - Clique em **"Add user account"**
   - Username: `mapagov_user`
   - Senha: (salve em local seguro!)

---

### **PARTE 2: Configurar Secrets (Secret Manager)**

Vamos armazenar credenciais de forma segura:

1. No Console GCP, vá em **"Secret Manager"** (menu ☰ → Security → Secret Manager)

2. Criar 3 secrets:

#### a) **Django SECRET_KEY**
- Clique em **"Create Secret"**
- Nome: `django_secret_key`
- Valor: Gere uma chave segura:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- Clique em **"Create Secret"**

#### b) **OpenAI API Key**
- Nome: `openai_api_key`
- Valor: Sua chave da OpenAI (`sk-proj-...`)
- Clique em **"Create Secret"**

#### c) **Database Password**
- Nome: `db_password`
- Valor: Senha do PostgreSQL que você criou
- Clique em **"Create Secret"**

---

### **PARTE 3: Configurar Cloud Storage (opcional, para backups)**

1. No Console GCP, vá em **"Cloud Storage"** (menu ☰ → Storage → Buckets)
2. Clique em **"Create Bucket"**
3. Configure:
   - **Nome**: `mapagov-backups` (deve ser globalmente único)
   - **Região**: `us-central1`
   - **Storage class**: `Standard`
   - **Acesso**: `Uniform`
4. Clique em **"Create"**

---

### **PARTE 4: Deploy Inicial (Método Manual)**

Vamos fazer o primeiro deploy manualmente para testar:

1. **Instalar Google Cloud CLI** no seu computador:
   - Windows: https://cloud.google.com/sdk/docs/install
   - Ou use o Cloud Shell (ícone `>_` no topo do console)

2. **Autenticar**:
   ```bash
   gcloud auth login
   gcloud config set project neat-environs-472910-g9
   ```

3. **No diretório do projeto** (`c:\Users\Roberto\.vscode\mapagov`):
   ```bash
   # Build da imagem
   gcloud builds submit --tag gcr.io/neat-environs-472910-g9/mapagov

   # Deploy no Cloud Run
   gcloud run deploy mapagov \
     --image gcr.io/neat-environs-472910-g9/mapagov \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 120 \
     --max-instances 10 \
     --min-instances 0 \
     --port 8080 \
     --set-env-vars DEBUG=False,ENVIRONMENT=production \
     --set-secrets SECRET_KEY=django_secret_key:latest,OPENAI_API_KEY=openai_api_key:latest,DB_PASSWORD=db_password:latest \
     --add-cloudsql-instances neat-environs-472910-g9:us-central1:mapagov-db \
     --set-env-vars CLOUD_SQL_CONNECTION_NAME=neat-environs-472910-g9:us-central1:mapagov-db,DB_NAME=mapagov,DB_USER=postgres
   ```

4. Aguarde o deploy (leva ~5-10 min no primeiro deploy)

5. No final, você verá uma URL: `https://mapagov-XXXX-uc.a.run.app`

6. **Rodar migrations** (primeira vez):
   ```bash
   # Conectar ao Cloud Run e rodar migrations
   gcloud run services update mapagov \
     --region us-central1 \
     --command "python,manage.py,migrate"
   ```

---

### **PARTE 5: CI/CD Automático (Cloud Build)**

Agora vamos configurar deploy automático a cada push no GitHub:

1. No Console GCP, vá em **"Cloud Build"** (menu ☰ → Cloud Build → Triggers)

2. Clique em **"Connect Repository"**

3. Escolha **GitHub** → Autorize → Selecione o repositório `mapagov`

4. Clique em **"Create Trigger"**:
   - **Nome**: `deploy-mapagov-main`
   - **Evento**: Push to a branch
   - **Branch**: `^main$`
   - **Build Configuration**: Cloud Build configuration file
   - **Location**: `cloudbuild.yaml`

5. Clique em **"Create"**

6. **Teste**: Faça um commit e push na branch `main`:
   ```bash
   git add .
   git commit -m "feat: deploy no Google Cloud"
   git push origin main
   ```

7. Acompanhe o build em **Cloud Build → History**

---

## 🔧 Configurações Importantes

### Variáveis de Ambiente

O Cloud Run vai receber automaticamente:
- `DEBUG=False`
- `ENVIRONMENT=production`
- `GIT_COMMIT_SHA` (automático)
- `PORT` (automático, geralmente 8080)
- `CLOUD_SQL_CONNECTION_NAME`
- `DB_NAME=mapagov`
- `DB_USER=postgres`

### Secrets (via Secret Manager)

- `SECRET_KEY` → `django_secret_key:latest`
- `OPENAI_API_KEY` → `openai_api_key:latest`
- `DB_PASSWORD` → `db_password:latest`

---

## 💰 Estimativa de Custos (com créditos gratuitos)

### **Free Tier Permanente** (sempre grátis):
- Cloud Run: 2 milhões de requests/mês
- Cloud Build: 120 builds/dia
- Secret Manager: 6 secrets ativos

### **Custos Estimados** (após free tier):
| Serviço | Configuração | Custo/mês |
|---------|--------------|-----------|
| Cloud SQL | Shared Core (1 vCPU) | $10-15 |
| Cloud SQL | Dedicated (2 vCPU) | $70-90 |
| Cloud Run | 2 GB RAM, baixo tráfego | $5-10 |
| Cloud Storage | 10 GB | $0.20 |
| **Total** | **Desenvolvimento** | **~$15-25/mês** |
| **Total** | **Produção** | **~$75-100/mês** |

**Você tem R$ 1.860 (~$360) em créditos**, então pode rodar **GRÁTIS por 1 ano**!

---

## 🔍 Monitoramento

### Ver Logs
```bash
# Logs em tempo real
gcloud run services logs tail mapagov --region us-central1

# Logs no Console
Console GCP → Cloud Run → mapagov → Logs
```

### Métricas
Console GCP → Cloud Run → mapagov → Metrics

### Erros (Sentry)
Configure `SENTRY_DSN` no Secret Manager (opcional)

---

## 🛠️ Comandos Úteis

### ⚠️ SEMPRE VERIFICAR SERVIÇOS EXISTENTES ANTES DE DEPLOY

**IMPORTANTE:** Sempre liste os serviços ANTES de fazer deploy para não criar serviços duplicados por engano!

```bash
# SEMPRE rode isso ANTES de fazer deploy
gcloud run services list --region us-central1
```

Verifique o nome do serviço existente (normalmente `mapagov`), depois use no deploy:

```bash
# Deploy CORRETO (atualiza serviço existente)
gcloud run deploy mapagov \
  --image gcr.io/neat-environs-472910-g9/mapagov:latest \
  --region us-central1

# Deploy ERRADO (cria serviço novo por engano!)
gcloud run deploy mapagov-backend \  # ❌ Nome diferente = serviço novo!
  --image gcr.io/neat-environs-472910-g9/mapagov:latest \
  --region us-central1
```

**Se criou serviço por engano, delete:**
```bash
gcloud run services delete mapagov-backend --region us-central1
```

### Ver serviços rodando
```bash
gcloud run services list --region us-central1
```

### Atualizar variáveis de ambiente
```bash
gcloud run services update mapagov \
  --region us-central1 \
  --set-env-vars DEBUG=False,NOVA_VAR=valor
```

### Rodar comando no container
```bash
gcloud run services update mapagov \
  --region us-central1 \
  --command "python,manage.py,migrate"
```

### Deletar serviço
```bash
gcloud run services delete mapagov --region us-central1
```

---

## 🐛 Troubleshooting

### ⚠️ IMPORTANTE: Cloud Shell vs Local

**PROBLEMA COMUM:** Rodar `gcloud builds submit` no Cloud Shell sem ter o código atualizado.

**SOLUÇÃO:**
```bash
# Se usar Cloud Shell, SEMPRE faça antes:
cd ~/mapagov
git pull origin main  # Puxa últimas mudanças do GitHub
grep "alguma_coisa" arquivo.py  # Confirma que o código está atualizado
gcloud builds submit --tag gcr.io/PROJECT_ID/mapagov
```

**OU use terminal local:**
```bash
# No Windows/Mac/Linux (com gcloud instalado)
cd /caminho/do/projeto
gcloud builds submit --tag gcr.io/PROJECT_ID/mapagov
# Envia código local direto, não depende do GitHub
```

---

### Erro: "PRODUÇÃO COM SQLITE DETECTADA!" durante build

**Causa:** Django tenta rodar `collectstatic` mas detecta SQLite em produção.

**Solução:** ✅ **JÁ RESOLVIDO** no código atual:
- `Dockerfile` usa `ENV SKIP_DB_CHECK=1` durante collectstatic
- `settings.py` tem verificação `if not SKIP_DB_CHECK` para permitir SQLite só no build

**Verificar se está aplicado:**
```bash
grep SKIP_DB_CHECK Dockerfile
grep SKIP_DB_CHECK mapagov/settings.py
```

Se não estiver, atualize o código:
```bash
git pull origin main
```

---

### Erro: "Frontend build failed, using empty dist"

**Causa:** `npm run build` falhou no Dockerfile (comum com dependências antigas ou falta de memória).

**Não é crítico!** O Dockerfile tem fallback:
```dockerfile
RUN npm run build || mkdir -p dist && echo "WARN: Frontend build failed, using empty dist"
```

**Para corrigir de verdade:**
1. Atualize dependências do frontend localmente:
   ```bash
   cd frontend
   npm update
   npm run build  # Testa local
   ```
2. Commit e push
3. Rebuild no Cloud

**OU** sirva o frontend separado (Vercel/Netlify) e use o Django só como API.

---

### Erro: "Service not ready" ou 500 Error
- Verifique logs: `gcloud run services logs tail mapagov --region us-central1`
- Ou acesse: Console GCP → Cloud Run → mapagov → Logs
- Provável causa: Migrations não rodaram ou variáveis de ambiente incorretas

### Erro: "Secret not found"
- Verifique se os secrets existem no Secret Manager
- Verifique os nomes: `django_secret_key`, `openai_api_key`, `db_password`
- Dê permissão ao Cloud Run Service Account:
  ```bash
  gcloud secrets add-iam-policy-binding django_secret_key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
  ```

### Erro: "Cloud SQL connection failed"
- Verifique se o Cloud SQL está rodando
- Verifique o `CLOUD_SQL_CONNECTION_NAME` (formato: `project:region:instance`)
- Teste a conexão: Console GCP → SQL → mapagov-db → Connections
- Verifique se o Cloud Run tem permissão pra acessar o Cloud SQL (IAM)

### Erro: "Frontend não carrega" ou WARNING staticfiles.W004
- ✅ **RESOLVIDO**: Dockerfile agora builda o frontend automaticamente
- ✅ **RESOLVIDO**: settings.py verifica se `frontend/dist` existe antes de adicionar
- Se ainda falhar, verifique logs do Cloud Build para ver se `npm run build` rodou

### Erro: "ERR_TOO_MANY_REDIRECTS" (Loop de SSL)
- ✅ **RESOLVIDO**: `SECURE_SSL_REDIRECT = False` em production
- Cloud Run proxy já gerencia HTTPS automaticamente

### Build muito lento (>10 minutos)

**Otimizações:**
1. Use `.gcloudignore` para não enviar arquivos desnecessários:
   ```
   node_modules/
   __pycache__/
   db.sqlite3
   media/
   logs/
   backups/
   chroma_db/
   ```

2. Use cache de layers do Docker (multi-stage build já otimizado)

3. Aumente máquina de build no `cloudbuild.yaml`:
   ```yaml
   options:
     machineType: 'N1_HIGHCPU_8'  # Mais rápido (mas usa mais créditos)
   ```

---

## 📚 Próximos Passos

### 1. **Domínio Customizado** (transformar a URL feia em mapagov.com.br)

#### Passo 1: Comprar o domínio
- **Registro.br** (para `.com.br`): https://registro.br → R$ 40/ano
- **Google Domains** (para `.com`): domains.google.com → ~$12/ano
- **Namecheap** (alternativa): namecheap.com → ~$10/ano

#### Passo 2: Configurar no Cloud Run
1. No Console GCP, vá em: **Cloud Run → mapagov → Manage Custom Domains**
2. Clique em **"Add Mapping"**
3. Selecione seu domínio ou clique em **"Verify a new domain"**
4. Escolha o domínio: `mapagov.com.br` ou `www.mapagov.com.br`
5. O Google vai te dar os **registros DNS** para adicionar:
   ```
   Tipo: A
   Nome: @
   Valor: IP fornecido pelo Google

   Tipo: AAAA
   Nome: @
   Valor: IPv6 fornecido pelo Google
   ```

#### Passo 3: Configurar DNS no Registro.br (ou seu provedor)
1. Acesse o painel do Registro.br
2. Vá em **DNS** → **Editar Zona**
3. Adicione os registros que o Google forneceu
4. **Aguarde 24-48h** para propagação DNS (mas geralmente funciona em 1-2h)

#### Passo 4: Testar
```bash
# Verificar se DNS propagou
nslookup mapagov.com.br

# Acessar
https://mapagov.com.br
```

**SSL/HTTPS**: Automático! O Google Cloud cuida disso.

---

### 2. **Backup Automático**
- ✅ Cloud SQL já faz backup automático
- ✅ Código está no GitHub
- 🔜 Configure backups do banco:
  ```bash
  python manage.py backup_db --upload --tag semanal
  ```

---

### 3. **Escalabilidade**
Ajuste conforme necessário:
```bash
gcloud run services update mapagov \
  --region us-central1 \
  --min-instances 1 \  # Sempre 1 instância ativa (sem cold start)
  --max-instances 20   # Até 20 instâncias em picos de acesso
```

**Nota:** `min-instances 0` = grátis mas tem "cold start" (demora 5-10s na primeira requisição)

---

### 4. **Monitoramento Avançado** (opcional)
- **Sentry**: Monitoramento de erros (gratuito até 5k eventos/mês)
  1. Crie conta: https://sentry.io
  2. Adicione `SENTRY_DSN` no Secret Manager
  3. Deploy novamente

- **Google Cloud Monitoring**: Dashboards e alertas
  - Já vem incluso! Veja em: Cloud Run → mapagov → Metrics

---

## 🎉 Pronto!

Seu MapaGov está rodando no Google Cloud!

**URL de produção**: `https://mapagov-XXXX-uc.a.run.app`

Para acessar:
1. Abra a URL no navegador
2. Faça login no admin: `https://mapagov-XXXX-uc.a.run.app/admin`
3. Teste a Helena: `https://mapagov-XXXX-uc.a.run.app/chat`

---

## 📞 Suporte

- Documentação GCP: https://cloud.google.com/run/docs
- Logs: Console GCP → Cloud Run → Logs
- Custos: Console GCP → Billing

---

**Criado com [Claude Code](https://claude.com/claude-code)**
