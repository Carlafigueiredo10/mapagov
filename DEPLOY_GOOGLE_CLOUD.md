# 🚀 Deploy MapaGov no Google Cloud

Guia completo para fazer deploy do MapaGov usando Google Cloud Platform (GCP).

## 📋 Pré-requisitos

- ✅ Conta Google Cloud ativa (você tem R$ 1.860 em créditos!)
- ✅ Projeto GCP criado (`MapaGov`)
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

### Ver serviços rodando
```bash
gcloud run services list
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

### Erro: "Service not ready"
- Verifique logs: `gcloud run services logs tail mapagov --region us-central1`
- Provável causa: Migrations não rodaram

### Erro: "Secret not found"
- Verifique se os secrets existem no Secret Manager
- Verifique os nomes: `django_secret_key`, `openai_api_key`, `db_password`

### Erro: "Cloud SQL connection failed"
- Verifique se o Cloud SQL está rodando
- Verifique o `CLOUD_SQL_CONNECTION_NAME` (formato: `project:region:instance`)

### Erro: "Frontend não carrega"
- Verifique se o build do React rodou: `frontend/dist` existe?
- Rode localmente: `cd frontend && npm run build`

---

## 📚 Próximos Passos

1. **Domínio Customizado**:
   - Cloud Run → mapagov → Manage Custom Domains
   - Adicione seu domínio (ex: `mapagov.com.br`)

2. **SSL/HTTPS**:
   - Automático no Cloud Run!

3. **Backup Automático**:
   - Cloud SQL já faz backup automático
   - Para código: backups do Git

4. **Escalabilidade**:
   - Ajuste `--max-instances` conforme necessário
   - Cloud Run escala automaticamente de 0 a N instâncias

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
