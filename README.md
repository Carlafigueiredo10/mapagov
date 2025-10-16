# 🏛️ MapaGov - Sistema de Governança Pública

Sistema integrado para mapeamento de processos, análise de riscos e conformidade para o setor público, com IA conversacional Helena.

## 🚀 **Arquitetura do Sistema**

### **Frontend (React/TypeScript)**
- **Framework:** React 19 + TypeScript + Vite
- **Estado Global:** Zustand
- **Estilização:** CSS Modules + CSS nativo
- **Roteamento:** React Router DOM
- **HTTP Client:** Axios

### **Backend (Django)**
- **Framework:** Django 5.2.6 + Python 3.13
- **API:** Django REST Framework
- **IA:** LangChain + OpenAI GPT-4
- **Banco:** SQLite (desenvolvimento) 
- **CORS:** django-cors-headers

## 🛠️ **Setup Completo**

### **Pré-requisitos**
```bash
# Python 3.13+
python --version

# Node.js 18+
node --version
npm --version
```

### **1. Backend (Django)**
```bash
# Clonar repositório
git clone [repo-url]
cd mapagov

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate
# OU no Linux/Mac: source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
# Criar .env na raiz com:
# OPENAI_API_KEY=sua_chave_aqui
# DEBUG=True
# SECRET_KEY=sua_secret_key

# Migrar banco
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser

# Executar servidor
python manage.py runserver 8000
```

### **2. Frontend (React)**
```bash
# Nova aba/terminal
cd frontend

# Instalar dependências
npm install

# Executar desenvolvimento
npm run dev
```

## 🌐 **Acessos do Sistema**

### **React Frontend**
- **Chat Helena (POP):** http://localhost:5174

### **Django Backend + HTML Pages**
- **Landing/Apresentação:** http://localhost:8000/
 **Chat Helena (POP):** http://localhost:5174 (ou :5173). O template `chat.html` faz detecção automática tentando 5174 e fallback em 5173 durante desenvolvimento.
- **Gerador de Fluxogramas:** http://localhost:8000/fluxograma/
 **IA/LLM:** OpenAI GPT-4, LangChain, RAG (Chroma / embeddings)
 **Frontend:** React 19, TypeScript, Zustand, Vite
 **Backend:** Django 5.2, DRF, CORS
 **Banco:** SQLite (dev), PostgreSQL (prod)
 **Persistência RAG:** Diretório `chroma_db/` (não versionar em produção)
 **Backups:** Management commands (`backup_db`, `cleanup_pops`, `verify_database`) + upload S3 compatível (Backblaze B2 testado)
 **Deploy:** Vercel (frontend), Railway (backend) – ou container Docker futuro

```
mapagov/
├── 🐍 Backend (Django)
│   ├── manage.py
│   ├── mapagov/                 # Configurações Django
│   ├── processos/               # App principal
│   │   ├── helena_produtos/     # IA Helena + Produtos
│   │   ├── templates/           # Templates HTML legados
│   │   ├── static/              # Arquivos estáticos
│   │   ├── models.py            # Modelos de dados
│   │   ├── views.py             # Views/APIs
│   │   └── urls.py              # Rotas
│   └── requirements.txt
├── ⚛️ Frontend (React)
REACT_FRONTEND_URL=http://localhost:5174  # Pode apontar para build estático em produção
BACKUP_UPLOAD_PROVIDER=s3        # s3 | none
BACKUP_S3_BUCKET=meu-bucket
BACKUP_S3_REGION=us-east-1       # opcional
BACKUP_S3_BASE_PATH=mapagov/backups  # opcional
BACKUP_S3_PUBLIC=0               # 1 para objetos public-read
BACKUP_UPLOAD_AUTO=0             # 1 para enviar uploads sem precisar --upload
│   ├── src/
│   │   ├── components/
│   │   │   └── Helena/          # Componentes do chat
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # APIs e integrações
│   │   ├── store/               # Estado global (Zustand)
│   │   ├── types/               # TypeScript types
│   │   └── pages/               # Páginas principais
│   ├── package.json
│   └── vite.config.ts
└── 📚 Documentação
    ├── README.md                # Este arquivo
    └── MIGRAÇÃO_REACT.md        # História da migração
```

## 🏛️ **Funcionalidades do Sistema MapaGov**

### **🤖 Helena - IA Conversacional (React)**
- ✅ **Validação de Dados** - Conferência automática de informações

### **🌐 Páginas Web (HTML)**
- ✅ **Landing Page** - Apresentação do sistema e funcionalidades
- ✅ **Portal Dashboard** - Painel central de navegação
- ✅ **Gerador de Fluxogramas** - Criação de fluxos via PDF
- ✅ **Mapeamento de Processos** - Documentação estruturada
- ✅ **Análise de Conformidade** - Verificação de normas
# Helena - Chat POP
# Análise de Processos
POST /api/extract-pdf/             # Extrair texto de PDF
POST /api/analyze-risks/           # Análise de riscos Helena
POST /api/fluxograma-from-pdf/     # Gerar fluxograma de PDF

# Futuras (em desenvolvimento)
# POST /api/dashboard/             # Dashboard executivo
# POST /api/analise-riscos-completa/ # Análise completa
# POST /api/dossie-governanca/     # Dossiê de governança
```

## 💻 **Desenvolvimento**

### **Comandos Úteis**
```bash
# Backend
python manage.py check           # Verificar configuração
python manage.py makemigrations  # Criar migrações
python manage.py migrate         # Aplicar migrações
python manage.py collectstatic   # Coletar arquivos estáticos

# Frontend
npm run build                    # Build produção
npm run preview                  # Preview do build
npm run lint                     # Verificar ESLint
```

### **Tecnologias Utilizadas**
- **IA/LLM:** OpenAI GPT-4, LangChain
- **Frontend:** React 19, TypeScript, Zustand, Vite
- **Backend:** Django 5.2, DRF, CORS
- **Banco:** SQLite (dev), PostgreSQL (prod)
- **Deploy:** Vercel (frontend), Railway (backend)

## 🔧 **Configuração Avançada**

### 📦 Migração para PostgreSQL
O projeto agora suporta Postgres via variável `DATABASE_URL` (fallback para SQLite em desenvolvimento). 

Passos completos: ver arquivo `MIGRATION_POSTGRES.md`.

Resumo rápido:
1. Criar instância Postgres
2. Definir `DATABASE_URL=postgres://user:pass@host:5432/db`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. (Opcional) `dumpdata` do SQLite → `loaddata` no Postgres
6. Testar endpoints críticos (autosave, backup, restore, diff)
7. Criar índices recomendados (consultar guia)

Arquivo detalhado: `MIGRATION_POSTGRES.md`

### 💾 Backups & Restauração
Após a migração para Postgres é fundamental automatizar backups lógicos dos dados de POPs, snapshots e changelog.

#### Comandos Disponíveis
```bash
# Gera backup lógico (JSON) em pasta backups/YYYY/MM/DD
python manage.py backup_db

# Exemplos de opções
python manage.py backup_db --tag pre-migracao --pretty
python manage.py backup_db --no-snapshots --no-changelog  # backup mínimo
python manage.py backup_db --limit 50  # amostra para teste

# Verifica saúde do banco
python manage.py verify_database
python manage.py verify_database --max-latency-ms 800 --warn-snapshot-ratio 40
```

#### Upload Automático para Armazenamento Externo (S3)
O comando aceita upload automático dos arquivos gerados após o backup.

Ative via variável de ambiente e/ou flag:
```env
BACKUP_UPLOAD_PROVIDER=s3          # ou 'none'
BACKUP_S3_BUCKET=meu-bucket
BACKUP_S3_REGION=us-east-1         # opcional
BACKUP_S3_BASE_PATH=mapagov/backups # opcional (prefixo)
BACKUP_S3_PUBLIC=0                 # 1 para tornar objetos public-read
BACKUP_UPLOAD_AUTO=1               # Executa upload sem precisar da flag --upload
```

Uso manual forçando upload:
```bash
python manage.py backup_db --upload --tag diario
```

Inibir upload mesmo com BACKUP_UPLOAD_AUTO=1:
```bash
python manage.py backup_db --no-upload
```

Estratégia recomendada:
1. Agendar backup diário com `--tag diario`
2. Agendar backup semanal adicional com `--tag semanal --pretty`
3. Habilitar `cleanup_pops` semanal para manter proporção snapshots/POPs controlada
4. Monitorar `verify_database` em pipeline / observabilidade

#### Estrutura dos Arquivos
```
backups/
    2025/01/15/
        pops_20250115T220301Z.json
        pop_snapshots_20250115T220301Z.json
        pop_changelog_20250115T220301Z.json
        meta_20250115T220301Z.json
```

#### Agendamento (Windows / PowerShell)
Crie script `scripts/backup_db.ps1` (exemplo abaixo) e agende no Agendador de Tarefas:
```
powershell.exe -File C:\caminho\repo\scripts\backup_db.ps1
```

#### Restauração
Para restaurar registros específicos utilize `loaddata` (atenção à ordem):
```bash
python manage.py loaddata pops_20250115T220301Z.json
python manage.py loaddata pop_snapshots_20250115T220301Z.json
python manage.py loaddata pop_changelog_20250115T220301Z.json
```
Em produção recomenda-se restaurar em banco isolado e validar antes de promover.

#### Boas Práticas
- Verificar diariamente com `verify_database` em pipeline de monitoramento.
- Prune de snapshots redundantes já é tratado por `cleanup_pops` (agendar semanal).
- Armazenar pasta `backups/` em volume persistente ou bucket (S3 / GCS) via sync periódico.
- Não manter chaves API dentro dos arquivos de backup.

### **Variáveis de Ambiente (.env)**
```env
# IA
OPENAI_API_KEY=sk-...

# Django
DEBUG=True
SECRET_KEY=django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco (Produção)
DATABASE_URL=postgresql://...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
```

### **Deploy Produção**
```bash
# Frontend (Vercel)
npm run build
vercel --prod

# Backend (Railway)
railway login
railway up
```

## 📊 **Status do Projeto**

### **✅ Funcional e Estável**
- **Chat Helena (React)** - Mapeamento de POPs completo
- **Landing Page (HTML)** - Apresentação institucional
- **Portal Dashboard (HTML)** - Navegação central
- **Gerador de Fluxogramas (HTML)** - Criação via PDF
- **Análise de Riscos (HTML)** - Avaliação de processos
- **APIs REST** - Backend Django robusto
- **Migração HTML→React** - Chat modernizado

### **🔄 Em Desenvolvimento**
- **Deploy Produção** - Configuração Vercel/Railway
- **Testes Unitários** - Cobertura de código
- **Novos Produtos Helena** - Dashboard, Conformidade
- **Integração Completa** - Unificação de funcionalidades

## 🤝 **Contribuição**

### **Para Novos Desenvolvedores**
1. Clone o repositório
2. Siga o setup completo acima
3. Teste o sistema localmente
4. Leia `MIGRAÇÃO_REACT.md` para contexto
5. Abra issues/PRs conforme necessário

### **Fluxo de Desenvolvimento**
1. `git checkout -b feature/nova-funcionalidade`
2. Desenvolver e testar
3. `git push origin feature/nova-funcionalidade`
4. Abrir Pull Request

---

**Desenvolvido com ❤️ para o Setor Público**  
*Sistema Helena - IA para Governança e Conformidade*

**Última atualização:** Outubro 2025  
**Versão:** 2.0 (React/Django)