# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 IMPORTANT: Working with Users of Different Experience Levels

**Remember:** Not all users are experienced developers. When working with beginners or intermediate users:

1. **Always verify before asking users to edit**
   - Read files FIRST before asking users to modify them
   - Check current state before assuming what needs to change
   - Use `cat`, `grep`, or `Read` to verify file contents

2. **Check the basics first**
   - Before diving into complex solutions, verify simple things (file paths, typos, environment variables)
   - Don't assume users did basic setup steps correctly
   - Ask "did you run X command?" instead of assuming they did

3. **Explain what commands do**
   - Don't just give commands - explain what they will accomplish
   - Break down complex commands into simpler parts when possible
   - Tell users what output to expect

4. **One step at a time**
   - Give ONE command, wait for result, then proceed
   - Don't send multiple sequential commands unless they can run in parallel
   - Verify each step worked before moving to the next

5. **Be patient with trial and error**
   - Users may need to try things multiple times
   - Don't get frustrated if solutions don't work immediately
   - Always check if your previous suggestion actually got applied before trying a new one

6. **Remember context**
   - Users may be working in different environments (local terminal vs Cloud Shell vs VSCode terminal)
   - File paths differ between Windows/Linux/Cloud environments
   - What works locally might not work in CI/CD or cloud deployments

7. **⚠️ CRITICAL: React Frontend + Django Integration**
   - **NEVER** uncomment the React fallback route in `mapagov/urls.py` (lines ~30-34) without first verifying:
     - ✅ `frontend/dist/index.html` exists locally
     - ✅ `npm run build` completes successfully
     - ✅ `collectstatic` copies `index.html` to `staticfiles/` in production
   - **WHY:** The fallback tries to serve `index.html`. If it doesn't exist → `TemplateDoesNotExist` error
   - **SEQUENCE:**
     1. Fix frontend build (`npm run build` must succeed)
     2. Verify `frontend/dist/index.html` exists
     3. Check `STATICFILES_DIRS` includes `frontend/dist`
     4. Test `collectstatic` locally
     5. ONLY THEN uncomment the fallback route
     6. Build Docker → Deploy
   - **NEVER assume** frontend build worked just because Docker build succeeded (Dockerfile has `|| mkdir -p dist` fallback that hides errors)

## Project Overview

**MapaGov** is a public sector governance system that combines process mapping, risk analysis, and compliance management with AI-powered conversational assistance. The project uses a **React 19 + TypeScript frontend** (recently migrated from HTML templates) and a **Django 5.2 + Python 3.13 backend** with OpenAI GPT-4 integration via LangChain.

## Architecture

### Backend (Django)
- **Framework:** Django 5.2.6 with Django REST Framework
- **AI/LLM:** OpenAI GPT-4, LangChain, RAG (ChromaDB embeddings)
- **Database:** SQLite (development), PostgreSQL (production via `DATABASE_URL`)
- **CORS:** Configured for React dev servers (ports 5173-5175)
- **Static Files:** WhiteNoise for Render deployment

### Frontend (React)
- **Location:** `frontend/` directory
- **Framework:** React 19 + TypeScript + Vite
- **State Management:** Zustand (`frontend/src/store/`)
- **Styling:** CSS Modules + native CSS
- **HTTP Client:** Axios (`frontend/src/services/`)

### Key Django Apps
- **processos**: Main application containing all POP (Standard Operating Procedure) logic, Helena AI products, and APIs
- **processos/helena_produtos/**: Modular AI products (POP mapping, risk analysis, flowcharts, etc.)

### Database (Development vs Production)
- **Development**: SQLite (default, `db.sqlite3`)
- **Production**: PostgreSQL via Cloud SQL (requires `DATABASE_URL` environment variable)
- Migration is automatic when `DATABASE_URL` is set - Django detects and uses PostgreSQL
- See [DEPLOY_GOOGLE_CLOUD.md](DEPLOY_GOOGLE_CLOUD.md) for Cloud SQL setup instructions

## Common Development Commands

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver 8000

# Collect static files
python manage.py collectstatic
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server (usually port 5174)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint TypeScript/React code
npm run lint
```

### Database Management Commands

Custom management commands located in `processos/management/commands/`:

```bash
# Create backup of POPs, snapshots, and changelog
python manage.py backup_db
python manage.py backup_db --tag pre-migracao --pretty
python manage.py backup_db --upload  # Upload to S3-compatible storage

# Verify database health
python manage.py verify_database
python manage.py verify_database --max-latency-ms 800

# Cleanup redundant snapshots
python manage.py cleanup_pops
```

### Switching to PostgreSQL (Development → Production)

The project automatically detects and uses PostgreSQL when `DATABASE_URL` is set:

1. Set `DATABASE_URL` environment variable:
   ```bash
   # Local PostgreSQL
   export DATABASE_URL=postgresql://user:pass@localhost:5432/mapagov

   # Or Cloud SQL (production)
   export DATABASE_URL=postgresql://user:pass@/mapagov?host=/cloudsql/PROJECT:REGION:INSTANCE
   ```

2. Run migrations (Django auto-detects PostgreSQL):
   ```bash
   python manage.py migrate
   ```

3. Optional: Migrate existing data from SQLite:
   ```bash
   # Export from SQLite
   python manage.py dumpdata auth.user processos.POP processos.POPSnapshot processos.POPChangeLog > dump_pops.json

   # Switch to PostgreSQL (set DATABASE_URL)

   # Import to PostgreSQL
   python manage.py loaddata dump_pops.json
   ```

For Cloud SQL setup in production, see [DEPLOY_GOOGLE_CLOUD.md](DEPLOY_GOOGLE_CLOUD.md) "PARTE 1: Criar Banco de Dados".

## Code Architecture

### Django Models (processos/models.py)

**POP (Procedimento Operacional Padrão)**
- Core model for Standard Operating Procedures
- Key fields: `uuid` (immutable identifier), `session_id` (chat session), `nome_processo`, `etapas` (JSONField), `sistemas_utilizados` (JSONField)
- Auto-save support: `last_autosave_at`, `autosave_sequence`, `last_activity_at`
- Status workflow: draft → in_progress → review → approved → archived
- Integrity tracking: `integrity_hash` (SHA256), `raw_payload` (debug JSON)
- Methods: `get_dados_completos()`, `compute_integrity_hash()`, `create_snapshot()`

**POPSnapshot**
- Versioned snapshots of POP state
- Supports milestones with `milestone` and `milestone_label`
- Stores full payload + metadata (sequence, versão, autosave_sequence)

**POPChangeLog**
- Audit trail for all POP field changes
- Tracks old_value → new_value with user attribution
- Linked to autosave_sequence for granular history

### Django URLs (processos/urls.py)

**Page Routes:**
- `/` - Landing page
- `/portal/` - Dashboard
- `/chat/` - Chat interface (legacy, now React-based at :5174)
- `/fluxograma/` - Flowchart generator
- `/riscos/fluxo/` - Risk analysis flow

**API Endpoints:**
- `POST /api/chat/` - Main chat API
- `POST /api/chat-recepcao/` - Helena reception chat
- `POST /api/pop-autosave/` - Auto-save POP data
- `POST /api/pop-backup-session/` - Backup session POPs
- `POST /api/pop-restore-snapshot/` - Restore from snapshot
- `POST /api/pop-snapshot-diff/` - Compare snapshots
- `POST /api/pop-snapshot-milestone/` - Mark milestone
- `GET /api/pop-historico/<pop_id>/` - List POP history
- `POST /api/gerar-pdf-pop/` - Generate POP PDF
- `POST /api/validar-dados-pop/` - Validate POP data
- `POST /api/consultar-rag-sugestoes/` - RAG suggestions
- `POST /api/extract-pdf/` - Extract text from PDF
- `POST /api/analyze-risks/` - Risk analysis
- `POST /api/fluxograma-from-pdf/` - Generate flowchart from PDF

### Helena AI Products (processos/helena_produtos/)

Modular AI-powered products:
- **helena_pop.py** - POP mapping conversational AI
- **helena_recepcao.py** - Reception/routing agent
- **helena_mapeamento.py** - Process mapping
- **helena_fluxograma.py** - Flowchart generation
- **helena_analise_riscos.py** - Risk analysis
- **helena_conformidade.py** - Compliance checking
- **helena_dashboard.py** - Dashboard generation
- **helena_dossie.py** - Governance dossier
- Others (artefatos, documentos, governança, plano_ação, relatorio_riscos)

Each product is a Python module with its own LangChain agent configuration.

### React Frontend Structure

```
frontend/
├── public/                  # Static assets served by Vite
│   ├── helena_avatar.png
│   ├── helena_em_pe.png
│   ├── helena_fluxograma.png
│   ├── helena_mapeamento.png
│   ├── helena_riscos.png
│   ├── helena_sobre.png
│   ├── logo_mapa.png
│   └── vite.svg
├── src/
│   ├── components/
│   │   └── Helena/          # Chat components
│   │       ├── ChatContainer.tsx
│   │       ├── FormularioPOP.tsx
│   │       ├── InterfaceDinamica.tsx
│   │       ├── SaveIndicator.tsx
│   │       └── AreasSelector.tsx
│   ├── hooks/
│   │   ├── useChat.ts       # Chat logic
│   │   └── useAutoSave.ts   # Auto-save hook (30s interval)
│   ├── services/
│   │   └── helenaApi.ts     # API client
│   ├── store/
│   │   └── chatStore.ts     # Zustand global state
│   ├── types/               # TypeScript definitions
│   ├── pages/               # Page components
│   └── data/                # Static data (areas, etc.)
```

**Key Frontend Features:**
- **Auto-save system** (FASE 6): Saves POP data every 30s, after Helena responses, and on page unload
- **Save indicator**: Visual feedback (Salvando... / Salvo há Xs / Erro ao salvar)
- **Session persistence**: Stores `popId` and `popUuid` for editing
- **Dynamic forms**: Collects POP data through conversational interface

**Static Assets & Images:**
- **Location**: All images are stored in `frontend/public/` directory
- **Build process**: Vite copies files from `public/` to `dist/` (root, no subfolders)
- **Django serving**: WhiteNoise serves built files from `staticfiles/` at `/static/` URL
- **Image references in code**: ALWAYS use `/static/filename.png` (e.g., `/static/helena_avatar.png`)
- **NEVER use**: `/static/img/filename.png` or just `/filename.png` - these paths will fail in production
- **Available images**: helena_avatar.png, helena_em_pe.png, helena_fluxograma.png, helena_mapeamento.png, helena_riscos.png, helena_sobre.png, logo_mapa.png

### Environment Variables (.env)

Required variables:
```env
# AI
OPENAI_API_KEY=sk-...

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Production)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5174,http://127.0.0.1:5174

# Frontend URL
REACT_FRONTEND_URL=http://localhost:5174

# Backup (S3-compatible, e.g., Backblaze B2)
BACKUP_UPLOAD_PROVIDER=s3
BACKUP_S3_BUCKET=bucket-name
BACKUP_S3_REGION=us-east-1
BACKUP_S3_BASE_PATH=mapagov/backups
BACKUP_UPLOAD_AUTO=0  # 1 to auto-upload backups
```

See `.env.example` for full template.

## Development Workflow

### Running Both Servers Simultaneously

You need **two terminal windows**:

**Terminal 1 (Backend):**
```bash
python manage.py runserver 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Access:
- React app: http://localhost:5174
- Django backend: http://localhost:8000
- Django admin: http://localhost:8000/admin

### Testing Backend APIs

Use Django admin or tools like curl/Postman:
```bash
# Test chat API
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá Helena"}'

# Test auto-save
curl -X POST http://localhost:8000/api/pop-autosave/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "nome_processo": "Teste"}'
```

### Database Inspection

```bash
# Django shell
python manage.py shell

# Check database
python manage.py dbshell

# View POPs
python manage.py shell -c "from processos.models import POP; print('POPs:', POP.objects.count())"
```

## Important Implementation Details

### Auto-Save System (FASE 6)

Fully implemented auto-save with:
- **Trigger conditions**: Every 30s, after Helena responses, on page unload
- **Change detection**: Only saves if data changed (JSON comparison)
- **Error handling**: Non-blocking errors, visual feedback
- **Session recovery**: Stores `popId`/`popUuid` in state for editing

Files involved:
- `frontend/src/hooks/useAutoSave.ts` (137 lines)
- `frontend/src/components/Helena/SaveIndicator.tsx` (89 lines)
- `frontend/src/components/Helena/ChatContainer.tsx` (integration)
- Backend: `processos/views.py::autosave_pop`

See `FASE_6_AUTOSAVE_COMPLETO.md` for complete documentation.

### Snapshot & History System

POPs support versioned snapshots:
- Created automatically by backend on significant changes
- Can be marked as milestones for important versions
- Diff comparison between snapshots available
- Full audit trail in POPChangeLog

API endpoints:
- `POST /api/pop-restore-snapshot/` - Restore from snapshot
- `POST /api/pop-snapshot-milestone/` - Mark milestone
- `POST /api/pop-snapshot-diff/` - Compare two snapshots
- `GET /api/pop-historico/<pop_id>/` - List history

### RAG (Retrieval-Augmented Generation)

ChromaDB vector database in `chroma_db/` directory:
- Stores embeddings for process documents
- Used by Helena for context-aware suggestions
- **Do not version `chroma_db/` in production** (add to .gitignore if not present)

### Migration to React

The system recently migrated from HTML/JavaScript to React (October 2025):
- Old chat templates in `processos/templates/backup/`
- Legacy routes commented out in `processos/urls.py`
- Other pages (landing, portal, fluxograma) still use HTML templates
- See `MIGRAÇÃO_REACT.md` for migration history

### Backup Strategy

Automated backup system for production:
- **Backups location**: `backups/YYYY/MM/DD/` with timestamped JSON files
- **Upload support**: S3-compatible (Backblaze B2 tested)
- **Recommended schedule**:
  - Daily: `python manage.py backup_db --upload --tag diario`
  - Weekly: `python manage.py backup_db --upload --tag semanal --pretty`
  - Weekly cleanup: `python manage.py cleanup_pops`

Files backed up:
- `pops_TIMESTAMP.json` - POP records
- `pop_snapshots_TIMESTAMP.json` - Snapshot history
- `pop_changelog_TIMESTAMP.json` - Change logs
- `meta_TIMESTAMP.json` - Backup metadata

## Deployment

### Production Settings

- **Frontend**: Vercel (or build + serve static via Django)
- **Backend**: Google Cloud Run / Railway / Render (configured for Render with WhiteNoise)
- **Database**: PostgreSQL (required for production)
- **Static files**: Collected via `python manage.py collectstatic`

### Google Cloud Run Deployment (Primary - LIVE)

**Current Production:** https://mapagov-113328225062.us-central1.run.app

Successfully deployed with:
- **Cloud Run**: Serverless container platform
- **Cloud SQL PostgreSQL**: Managed database
- **Secret Manager**: Secure credential storage
- **Multi-stage Docker build**: Frontend (Vite) + Backend (Django) in single container

**⚠️ CRITICAL LESSONS LEARNED from Google Cloud Deploy:**

1. **Dockerfile Frontend Build Issues:**
   - ❌ **NEVER use `npm ci --only=production`** - Vite is in devDependencies and won't be installed!
   - ❌ **NEVER hide build errors** with `|| mkdir -p dist` - fail-fast is better than silent failures
   - ✅ **Always verify** `frontend/dist/index.html` exists and has content (> 0 bytes) before deploying
   - ✅ Use full `npm ci` to install ALL dependencies needed for build

2. **Django Settings Gotchas:**
   - **CSRF_TRUSTED_ORIGINS** must include FULL domain (no wildcards): `https://mapagov-123.run.app`
   - **SKIP_DB_CHECK** flag needed during Docker build to allow `collectstatic` without PostgreSQL
   - **React fallback route** (`mapagov/urls.py` lines 30-34) MUST be commented until frontend build is verified working

3. **Cloud Shell vs Local:**
   - Cloud Shell has 5GB limit - clean `~/.cache/*` regularly
   - Always `git pull origin main` in Cloud Shell before building
   - Or use local terminal (with gcloud installed) to avoid sync issues

4. **Service Management:**
   - **ALWAYS** run `gcloud run services list` before deploy to check existing service names
   - Use exact same service name to update (not create duplicate)
   - Example: `gcloud run deploy mapagov` (updates), NOT `mapagov-backend` (creates new)

**Complete troubleshooting guide:** See [DEPLOY_GOOGLE_CLOUD.md](DEPLOY_GOOGLE_CLOUD.md) section "Problemas Resolvidos Durante o Deploy"

### Render Deployment (Legacy - Configured)

Configured for Render:
- `Procfile`: Gunicorn WSGI server
- `runtime.txt`: Python version
- `ALLOWED_HOSTS`: Includes `mapagov.onrender.com`, `.onrender.com`
- WhiteNoise serves static files
- Set `DATABASE_URL` in Render dashboard

## Known Issues & Notes

1. **Import/Export app temporarily disabled** in `settings.py` (line 34 commented)
2. **SQLite in production blocked** by safety check (line 103-104) - temporarily disabled for local dev
3. **Future products** commented out in `processos/urls.py` (lines 59-66): dashboard, conformidade, dossie, etc.
4. **ChromaDB persistence**: Ensure `chroma_db/` directory is in `.gitignore` and persists on disk in production
5. **PDF uploads**: Stored in `media/pdfs/`, ensure proper permissions and backup

## Testing

While the project doesn't have formal test coverage yet, you can:
1. Test backend endpoints via Django admin or curl
2. Test frontend with `npm run lint` for TypeScript errors
3. Verify database health: `python manage.py verify_database`
4. Test backups: `python manage.py backup_db --limit 10` (small sample)

## Additional Documentation

- **README.md**: Comprehensive setup guide and feature list
- **DEPLOY_GOOGLE_CLOUD.md**: Complete Google Cloud Run deployment guide with troubleshooting (⭐ Essential reading!)
- **DESENVOLVIMENTO.md**: Development notes and technical details

## Git Workflow

Standard Git practices:
- Main branch: `main`
- Create feature branches: `git checkout -b feature/nova-funcionalidade`
- Commit with descriptive messages
- Push and create pull requests

## Questions & Support

For questions about:
- **Django models/views**: Check `processos/models.py`, `processos/views.py`
- **API endpoints**: See `processos/urls.py`
- **Helena AI products**: Explore `processos/helena_produtos/` modules
- **React components**: Navigate `frontend/src/components/Helena/`
- **Database setup**: See "Database (Development vs Production)" section above or `DEPLOY_GOOGLE_CLOUD.md`
- **Auto-save system**: See `frontend/src/hooks/useAutoSave.ts` implementation
- **Deployment issues**: Read `DEPLOY_GOOGLE_CLOUD.md` troubleshooting section
