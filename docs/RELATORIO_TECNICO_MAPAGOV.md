# Relatório Técnico — MapaGov

**Data:** 12 de fevereiro de 2026
**Escopo:** Auditoria técnica completa do repositório MapaGov
**Base:** Código-fonte do repositório (branch `main`, commit `a7b3e84`)

---

## 1. Visao Geral do Sistema

### 1.1 Objetivo

O MapaGov e uma plataforma web de governanca publica voltada ao mapeamento de processos organizacionais, analise de riscos e planejamento estrategico, desenvolvida no contexto da Secretaria de Gestao de Pessoas (SGP) do Ministerio da Gestao e da Inovacao (MGI) do Governo Federal brasileiro. O sistema e orientado a producao de artefatos institucionais — Procedimentos Operacionais Padrao (POPs), matrizes de risco, planos estrategicos — mediante conversas guiadas com uma assistente virtual chamada **Helena**.

### 1.2 Tipo de Aplicacao

Sistema hibrido composto por:

- **Backend:** API REST em Django (Python), servindo tambem o frontend buildado como Single Page Application (SPA).
- **Frontend:** Aplicacao React (TypeScript) com roteamento client-side, buildada pelo Vite e servida pelo Django via WhiteNoise.
- **Arquitetura de deploy:** Monolito (backend + frontend no mesmo servico), preparado para Render (free tier) e Google Cloud Run.

### 1.3 Fluxo Principal do Usuario

```
Acesso ao site (Landing Page)
       |
       v
  Login / Registro  ──→  Verificacao de email  ──→  Aprovacao de acesso (externo: 3 votos)
       |
       v
  Portal (catalogo de produtos Helena)
       |
       ├── POP: Conversa guiada para mapear processo → formulario → revisao → PDF
       ├── Analise de Riscos: Questionario estruturado → matriz 5×5 → plano de resposta
       ├── Planejamento Estrategico: Diagnostico → recomendacao de modelo → construcao guiada
       ├── Fluxograma: Coleta de etapas → geracao Mermaid
       └── Catalogo POP: Consulta publica de POPs publicados por area
```

### 1.4 Papel da IA no Sistema

A IA (OpenAI GPT-4o / GPT-4o-mini via LangChain) exerce **papel de apoio**, nao de nucleo. A maioria dos produtos opera com **maquinas de estado deterministicas** que coletam dados via conversa guiada. A IA e usada em dois cenarios especificos:

1. **Classificacao de atividades** (GPT-4o, temp=0.3): sugere enquadramento na arquitetura DECIPEX com validacao posterior contra CSV.
2. **Orientacao conversacional** (GPT-4o-mini, temp=0.6-0.7): Helena Mapeamento e agentes de Planejamento Estrategico usam LLM para gerar orientacoes contextuais.

Os demais produtos (POP, Etapas, Riscos, Fluxograma, Recepcao) sao 100% deterministicos.

---

## 2. Stack Tecnologica Identificada

### 2.1 Backend

| Aspecto | Tecnologia |
|---------|-----------|
| **Linguagem** | Python 3.11 (Dockerfile) / 3.13 (runtime.txt) |
| **Framework** | Django 5.2.6 + Django REST Framework 3.16.1 |
| **Servidor WSGI** | Gunicorn 23.0.0 |
| **Arquivos estaticos** | WhiteNoise 6.11.0 |
| **IA/NLP** | LangChain 0.3.27, OpenAI 1.108.1, Anthropic 0.69.0 |
| **Embeddings/RAG** | ChromaDB 1.1.0, Sentence-Transformers 5.1.1 |
| **PDF** | ReportLab 4.0.4, PyPDF 6.1.0, PDFPlumber 0.11.7, python-docx 1.1.0 |
| **Validacao** | Pydantic 2.11.9 |
| **Monitoramento** | Sentry SDK 2.41.0, Prometheus (metricas custom) |
| **Cache** | Redis 5.0.1 (opcional, fallback para LocMemCache) |
| **CORS** | django-cors-headers 4.9.0 |
| **NLP auxiliar** | RapidFuzz 3.10.0 (fuzzy matching), tiktoken 0.11.0 (contagem tokens) |

**Estrutura de pastas do backend:**

```
mapagov/                    # Projeto Django (settings, urls, wsgi)
  ├── settings.py
  ├── urls.py
  └── utils/rag_indexer.py

processos/                  # App Django principal
  ├── models.py             # Models: POP, Area, HelenaSession, PopDraft, etc.
  ├── models_new/           # Models FASE 1-2: ChatSession, Orgao, RBAC, Audit
  ├── models_auth.py        # UserProfile, AccessApproval
  ├── models_analise_riscos.py  # AnaliseRiscos, RiscoIdentificado, RespostaRisco
  ├── views.py              # Views principais (chat, PDF, autosave)
  ├── serializers.py        # DRF serializers
  ├── urls.py               # Todas as rotas API
  ├── api/                  # APIs modulares (auth, admin, catalogo, PE, riscos)
  ├── domain/               # Logica de dominio (Helena produtos)
  │   ├── helena_mapeamento/
  │   ├── helena_planejamento_estrategico/
  │   ├── helena_analise_riscos/
  │   ├── helena_fluxograma/
  │   ├── helena_recepcao/
  │   └── governanca/
  ├── infra/                # Infraestrutura transversal
  │   ├── access_control_middleware.py
  │   ├── rls_middleware.py
  │   ├── structured_logging.py
  │   ├── metrics.py
  │   ├── rate_limiting.py
  │   ├── pii_protection.py
  │   ├── rbac_decorators.py
  │   ├── helena_langchain.py
  │   ├── session_manager.py
  │   └── loaders/          # Loaders de CSV (areas, sistemas, operadores)
  ├── app/                  # Helena core e singleton
  ├── export/               # Exportacao PDF/Word
  ├── wizard/               # Wizard de validacao
  └── management/commands/  # Comandos Django custom (backup, verify_database)
```

**Padrao arquitetural:** O backend nao segue MVC ou MVT puro. A camada `domain/` implementa logica de negocio com **maquinas de estado** e **agentes especializados**, enquanto `infra/` fornece servicos transversais (logging, auth, metrics). As `views.py` funcionam como controller/roteador de produtos Helena. O padrao pode ser descrito como **Layered Architecture com Domain Services**.

### 2.2 Frontend

| Aspecto | Tecnologia |
|---------|-----------|
| **Framework** | React 19.1.1 |
| **Linguagem** | TypeScript 5.9.3 |
| **Build tool** | Vite 7.1.7 |
| **Roteamento** | React Router DOM 7.9.4 |
| **Estado** | Zustand 5.0.8 (4 stores com persistencia) |
| **HTTP** | Axios 1.12.2 |
| **Validacao** | Zod 4.3.6 |
| **Markdown** | react-markdown 10.1.0 + remark-gfm |
| **Diagramas** | Mermaid 11.12.0 |
| **Icones** | Lucide React 0.544.0 |
| **Testes E2E** | Playwright (configurado, nao executado nesta auditoria) |

**Organizacao de componentes:**

```
frontend/src/
  ├── App.tsx              # Router principal (~90 rotas)
  ├── main.tsx             # Entry point (StrictMode)
  ├── components/
  │   ├── Auth/            # ProtectedRoute, AdminRoute, PublicRoute
  │   ├── Helena/          # 40+ componentes de interface Helena
  │   │   ├── artefatos/   # 20+ artefatos visuais (Canvas, RACI, Stakeholders...)
  │   │   └── workspaces/  # Workspaces PE (SWOT, OKR, BSC, Hoshin, 5W2H)
  │   ├── AnaliseRiscos/   # Componentes de analise de riscos
  │   ├── Layout/          # Layout wrapper
  │   ├── Portal/          # Cards e sidebar do portal
  │   └── ui/              # Componentes base (Badge, Button, Card)
  ├── pages/               # 50+ paginas (Landing, Portal, POP, PE, Riscos, Dominios...)
  ├── services/            # Camada API (api.ts, authApi, helenaApi, helenaPEApi, etc.)
  ├── store/               # Zustand stores (auth, chat, form, analiseRiscos)
  ├── hooks/               # Hooks (useChat, useRequireAuth, useDashboard, etc.)
  ├── schemas/             # Zod schemas + validacao
  ├── types/               # TypeScript types (pop, portal, analiseRiscos, dashboard)
  ├── constants/           # Constantes (chatCommands)
  ├── data/                # Dados mock e estaticos (products, sugestoesRisco)
  └── utils/               # Utilitarios (sessionManager, dashboardSync)
```

**Comunicacao frontend-backend:** O frontend comunica com o backend exclusivamente via **chamadas HTTP REST** usando Axios. Em desenvolvimento, o Vite proxy redireciona `/api/*` para `http://127.0.0.1:8000`. Em producao, ambos servem do mesmo dominio. A autenticacao usa **cookies de sessao Django** (`withCredentials: true`). O token CSRF e obtido via endpoint dedicado `/api/auth/csrf/`.

### 2.3 Banco de Dados

| Aspecto | Detalhe |
|---------|---------|
| **Producao** | PostgreSQL (via Neon Database / Cloud SQL) |
| **Desenvolvimento** | SQLite3 (arquivo `db.sqlite3` na raiz) |
| **ORM** | Django ORM (BigAutoField como PK padrao) |
| **Migrations** | Django migrations (20+ arquivos em `processos/migrations/`) |
| **Modelos localizados em** | `processos/models.py`, `processos/models_new/`, `processos/models_auth.py`, `processos/models_analise_riscos.py` |

**Modelos principais:**

| Modelo | Descricao |
|--------|-----------|
| `POP` | Procedimento Operacional Padrao (38+ campos, JSONField para etapas/sistemas) |
| `POPSnapshot` | Snapshot imutavel do POP (autosave a cada 5 saves) |
| `POPChangeLog` | Log de alteracoes campo a campo |
| `PopDraft` | Rascunho do wizard (estado da maquina de estados) |
| `PopVersion` | Versao publicada imutavel |
| `Area` | Area organizacional (hierarquica, com slug) |
| `ProcessoMestre` | Arquitetura de processos DECIPEX |
| `HelenaSession` | Sessao de conversa persistente |
| `ChatSession` / `ChatMessage` | Chat V2 (FASE 1) |
| `AnaliseRiscos` / `RiscoIdentificado` / `RespostaRisco` | Analise de riscos completa |
| `UserProfile` / `AccessApproval` | Perfil estendido e aprovacao de acesso |
| `Role` / `Permission` / `UserRole` | RBAC |
| `AuditLog` / `SecurityEvent` | Auditoria e eventos de seguranca |
| `Orgao` | Orgao institucional |
| `ControleGastos` | Controle financeiro (basico) |

### 2.4 Infraestrutura / Deploy

| Aspecto | Detalhe |
|---------|---------|
| **Plataforma primaria** | Render (free tier, Oregon) |
| **Plataforma alternativa** | Google Cloud Run (Dockerfile multi-stage) |
| **Build** | `build.sh` (npm install + build + pip install + collectstatic + migrate) |
| **Start** | Gunicorn com 1 worker + 4 threads (512MB RAM) |
| **Arquivos de deploy** | `Dockerfile`, `render.yaml`, `Procfile`, `build.sh`, `runtime.txt` |
| **Variaveis de ambiente** | `.env.example` com 25+ variaveis (Django, DB, OpenAI, Sentry, Redis, S3, CORS) |
| **SSL** | Gerenciado pelo proxy (Render/Cloud Run), HSTS habilitado |
| **Monitoramento** | Sentry SDK (erros), Prometheus (metricas), logging estruturado (JSON) |

**Configuracao de producao vs desenvolvimento:**

| Aspecto | Desenvolvimento | Producao |
|---------|----------------|----------|
| Database | SQLite3 | PostgreSQL (obrigatorio; RuntimeError se SQLite) |
| Debug | True | False |
| CORS | Allow all origins | Whitelist explicita |
| Cookies | Insecure, SameSite=Lax | Secure, SameSite=None, HttpOnly |
| HSTS | Desabilitado | 1 ano, incluindo subdomains |
| Sentry | Desabilitado | Habilitado (10% sampling) |
| Logging | Console (DEBUG) | Console + arquivo rotativo (INFO/ERROR/Helena) |
| Cache | LocMemCache | Redis (fallback para LocMemCache) |

---

## 3. Arquitetura do Sistema

### 3.1 Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  BrowserRouter → Pages → Components → Zustand Stores → Axios   │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP REST (JSON)
                               │ Cookie: sessionid + csrftoken
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MIDDLEWARE CHAIN                            │
│  CORS → Security → WhiteNoise → Session → CSRF → Auth          │
│  → AccessControl → RLS → StructuredLogging → Prometheus         │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIEWS / API LAYER                             │
│  views.py (chat_api_view)  │  api/auth_api.py                  │
│  api/chat_api.py           │  api/admin_api.py                 │
│  api/planejamento_*        │  api/catalogo_api.py              │
│  api/analise_riscos_*      │  DRF Router (Areas, POPs)         │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                                  │
│  helena_mapeamento/  │  helena_planejamento_estrategico/        │
│    HelenaPOP         │    PEOrchestrator + 7 Agents             │
│    HelenaEtapas      │    (OKR, SWOT, BSC, 5W2H, Hoshin,       │
│    HelenaMapeamento  │     Cenarios, Tradicional)               │
│  helena_analise_riscos/  │  helena_fluxograma/                  │
│  helena_recepcao/        │  helena_semantic_planner.py          │
│  governanca/             │  produto_helena_protocol.py          │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│  helena_langchain.py (LLM)  │  pii_protection.py (LGPD)       │
│  rate_limiting.py           │  session_manager.py              │
│  structured_logging.py      │  metrics.py (Prometheus)         │
│  rbac_decorators.py         │  loaders/ (CSV → Domain)         │
│  redis_cache.py             │  pdf_generator.py                │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
│  Django ORM → PostgreSQL (prod) / SQLite (dev)                  │
│  ChromaDB (vectorstore RAG)                                     │
│  Redis (cache sessoes, rate limiting)                           │
│  CSV (documentos_base/ → arquitetura DECIPEX)                   │
│  Media (PDFs gerados)                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Fluxo de uma Requisicao de Chat

```
1. Frontend (useChat hook) envia POST /api/chat/
   Body: { message, contexto, session_id, dados_atuais }

2. Middleware chain processa (CORS, auth, logging, metrics)

3. chat_api_view() roteia por contexto:
   - 'gerador_pop'  → HelenaPOP.processar()
   - 'fluxograma'   → HelenaFluxograma.processar_mensagem()
   - 'mapeamento'   → helena_mapeamento() [LangChain]
   - 'analise_riscos'→ HelenaAnaliseRiscos.processar_mensagem()
   - etc.

4. Produto processa mensagem:
   a. Restaura estado da Django session (request.session[key])
   b. Avanca maquina de estados
   c. Gera resposta + novo estado + metadados

5. Estado salvo na Django session
   - request.session[key] = novo_estado
   - request.session.modified = True

6. Resposta JSON retornada:
   { resposta, tipo_interface, dados_interface, metadados, novo_estado }

7. Frontend atualiza Zustand store e renderiza interface
```

### 3.3 Gerenciamento de Estado

O estado do sistema e distribuido em tres camadas:

1. **Django Session** (server-side): Estado da conversa Helena (maquina de estados serializada como dict). Armazenada no banco de sessoes Django (cookie `sessionid`).
2. **Banco de dados**: POPs, rascunhos, snapshots, analises de risco, planejamentos. Persistencia de longo prazo.
3. **Zustand stores** (client-side): Estado da UI, dados do formulario, historico de mensagens. Persistido via localStorage/sessionStorage.

### 3.4 Roteamento de Produtos Helena

O roteamento de multiplos produtos Helena opera em dois niveis:

**Nivel 1 — Roteamento por contexto** (`chat_api_view`): O campo `contexto` da requisicao determina qual produto processar (gerador_pop, fluxograma, mapeamento, analise_riscos, etc.).

**Nivel 2 — Transicao interna** (POP ↔ Etapas): Dentro do contexto `gerador_pop`, existe um sub-roteador que alterna entre `HelenaPOP` e `HelenaEtapas` de forma transparente, baseado em metadados (`mudar_contexto`, `retornar_para`).

### 3.5 Separacao de Responsabilidades

A separacao existe e e razoavelmente clara:

- **Views/API**: Recebem HTTP, validam entrada, roteiam para dominio, serializam resposta.
- **Domain**: Logica de negocio pura (maquinas de estado, agentes, regras).
- **Infra**: Servicos transversais (logging, auth, cache, LLM).
- **Models**: Persistencia e integridade de dados.
- **Frontend Services**: Comunicacao HTTP isolada dos componentes.
- **Frontend Stores**: Estado centralizado por feature.

Observacao: O arquivo `views.py` concentra muita logica (1540 linhas), incluindo parse de PDF e logica de roteamento que poderia estar em camada separada.

---

## 4. Sistema de Autenticacao

### 4.1 Mecanismo de Login

O sistema utiliza **autenticacao baseada em sessao Django** (nao JWT). O fluxo completo:

1. Frontend obtem token CSRF via `GET /api/auth/csrf/`.
2. Usuario envia `POST /api/auth/login/` com email e senha.
3. Backend autentica via `django.contrib.auth.authenticate()`.
4. Se valido, chama `django.contrib.auth.login(request, user)` que cria sessao server-side.
5. Cookie `sessionid` retornado (HttpOnly, Secure em producao).
6. Requisicoes subsequentes enviam cookie automaticamente (`withCredentials: true`).

### 4.2 Armazenamento de Senha

Utiliza o **hash padrao do Django: PBKDF2-SHA256** com salt aleatorio e iteracoes multiplas. O metodo `User.objects.create_user()` e usado no registro, que aplica hashing automaticamente. Nao ha armazenamento de senhas em texto plano observado no codigo.

### 4.3 Verificacao de Email

Apos registro, um email de verificacao e enviado com token temporizado (24h). O token usa `django.contrib.auth.tokens.default_token_generator`. A verificacao e obrigatoria para acesso ao sistema.

### 4.4 Aprovacao de Acesso

Usuarios com email `@gestao.gov.br` sao auto-aprovados. Usuarios externos requerem **3 votos de aprovadores** (membros do grupo `ACCESS_APPROVER`). O modelo `AccessApproval` garante unicidade (um voto por aprovador por usuario).

### 4.5 Logout

`POST /api/auth/logout/` chama `django.contrib.auth.logout(request)` que invalida a sessao server-side.

### 4.6 Modo MVP

A flag `PUBLIC_MVP_MODE=1` (variavel de ambiente) desabilita completamente a autenticacao, permitindo acesso publico a todas as APIs. Isso e usado para desenvolvimento e demonstracoes.

### 4.7 Protecoes de Seguranca

| Protecao | Status | Implementacao |
|----------|--------|--------------|
| **CSRF** | Implementado | Middleware Django + token via endpoint dedicado |
| **XSS** | Parcialmente implementado | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, React auto-escape. Headers `X-XSS-Protection` habilitado via `SECURE_BROWSER_XSS_FILTER` |
| **SQL Injection** | Protegido | Uso exclusivo de Django ORM (queries parametrizadas) |
| **Session Hijacking** | Protegido | Cookies HttpOnly + Secure + SameSite em producao |
| **Brute Force** | Protegido | Rate limiting: 5 tentativas/5min por IP no login |
| **HSTS** | Implementado | 1 ano, incluindo subdomains, preload |
| **CORS** | Implementado | Whitelist explicita de origens (produção), `CORS_ALLOW_ALL_ORIGINS` somente em DEBUG |
| **PII/LGPD** | Implementado | `PIIProtector` mascara CPF/CNPJ/email antes de enviar para LLM |
| **Rate Limiting** | Implementado | Sliding window com Redis (por IP, usuario, organizacao) |
| **RLS** | Implementado | Variaveis de sessao PostgreSQL para filtragem por orgao |
| **RBAC** | Implementado | Roles + permissions + decorators |

**Configuracoes de seguranca localizadas em:** `mapagov/settings.py` (linhas 55-75), `processos/infra/access_control_middleware.py`, `processos/infra/rate_limiting.py`, `processos/infra/pii_protection.py`.

---

## 5. Integracao com IA

### 5.1 Onde a IA e Chamada

| Produto | Modelo | Temperatura | Uso |
|---------|--------|------------|-----|
| Helena Mapeamento | GPT-4o-mini | 0.6 | Orientacao conversacional sobre mapeamento |
| Ajuda Inteligente (Classificacao) | GPT-4o | 0.3 | Classificar atividade na arquitetura DECIPEX |
| PE Orchestrator (7 agentes) | GPT-4o-mini | 0.7 | Construcao guiada de planos estrategicos |
| Helena POP | Nenhum | — | Maquina de estados deterministica |
| Helena Etapas | Nenhum | — | Coleta estruturada de etapas |
| Helena Riscos | Nenhum | — | Matriz de risco deterministica |
| Helena Fluxograma | Nenhum | — | Geracao Mermaid template-based |
| Helena Recepcao | Nenhum | — | Pattern matching para roteamento |
| Semantic Planner | Nenhum | — | Regex + pattern matching |

### 5.2 Biblioteca Utilizada

**LangChain 0.3.27** com os seguintes componentes:
- `ChatOpenAI` para instanciacao do LLM
- `ChatPromptTemplate` para prompts estruturados
- `LLMChain` para orquestracao
- `ConversationBufferMemory` para historico (apenas Mapeamento)
- `OpenAIEmbeddings` + `Chroma` para RAG

**OpenAI SDK 1.108.1** tambem esta instalado (usado diretamente em `views.py` via `import openai`).

### 5.3 Fallback Deterministico

Sim. O sistema implementa uma **estrategia de 3 camadas** para classificacao de atividades:
1. **Match exato** contra CSV de arquitetura
2. **Fuzzy matching** via RapidFuzz (threshold >= 85%)
3. **LLM inference** somente se os dois anteriores falharem

Para os demais produtos, o fallback e intrinseco: os produtos deterministicos (POP, Etapas, Riscos) nao dependem de IA.

### 5.4 Prompts

Os prompts estao **hardcoded** nos arquivos Python de cada agente/produto. Exemplos:
- `helena_mapeamento.py`: system prompt definindo persona Helena
- `helena_ajuda_inteligente.py`: prompt de classificacao com lista de macroprocessos validos
- Agentes PE: prompts por modelo (SWOT, OKR, BSC, etc.)

Nao ha sistema de templates externos ou banco de prompts. Os prompts sao versionados junto com o codigo.

### 5.5 Controle de Custo

Observados no codigo:
- **Lazy loading** de instancias LLM (so carrega quando usado)
- **HELENA_LITE_MODE**: flag para desabilitar produtos pesados em ambientes com RAM limitada
- **tiktoken** instalado (contagem de tokens), embora uso explicito nao tenha sido localizado em chamadas de producao
- **Temperatura baixa** (0.3) para classificacao reduz tokens de saida
- Nao foi identificado um sistema explicito de orcamento/limite de tokens por usuario ou organizacao

### 5.6 Logging de Chamadas

- `LogUtils.criar_log_entrada()` registra cada interacao com Helena (usuario, acao, metadados)
- `LogUtils.log_helena_interacao()` registra pergunta/resposta/estado
- Logger dedicado `processos.helena_produtos` com arquivo rotativo `helena.log`
- Structured logging JSON para integracao com ELK/Datadog

### 5.7 Montagem de Contexto

- **Mapeamento**: `ConversationBufferMemory` mantem historico completo da conversa
- **POP**: Estado serializado como dict (`to_dict()` / `from_dict()`) passado entre chamadas
- **PE**: Diagnostico acumulativo (5 perguntas com scoring) determina recomendacao
- **RAG**: ChromaDB com embeddings OpenAI (`text-embedding-3-small`), chunks de 1000 tokens com 200 overlap

---

## 6. Engenharia de Dados

### 6.1 Entrada de Dados

Os dados entram no sistema por tres vias:

1. **Conversa guiada**: Usuario responde perguntas da Helena, dados coletados pela maquina de estados.
2. **Upload PDF**: Extracao de texto via PyPDF para alimentar fluxograma ou classificacao.
3. **CSV de arquitetura**: Arquivo `documentos_base/Arquitetura_DECIPEX_mapeada.csv` carregado via loaders (`ArquiteturaDecipex`).

### 6.2 Uso de CSV

Sim. Arquivos CSV em `documentos_base/` fornecem:
- Arquitetura de processos DECIPEX (macroprocesso → processo → subprocesso → atividade)
- Areas organizacionais
- Sistemas utilizados
- Operadores
- Canais de orgaos

Loaders dedicados em `processos/infra/loaders/` processam estes CSVs.

### 6.3 Versionamento de Dados

- **POPSnapshot**: Snapshot automatico a cada 5 autosaves (imutavel)
- **POPChangeLog**: Registro de alteracoes campo a campo com valor anterior e novo
- **PopVersion**: Versao publicada imutavel (publish-driven, distinta do snapshot)
- **AnaliseSnapshot**: Snapshot de analise de riscos com motivo
- **integrity_hash**: SHA256 calculado sobre dados completos do POP para deteccao de conflitos
- **Controle de concorrencia**: Rejeicao 409 Conflict se hash do cliente diverge do servidor

### 6.4 Rastreabilidade

- `AuditLog` e `SecurityEvent` para registrar acoes administrativas
- `POPChangeLog` para rastrear alteracoes campo a campo
- `StructuredLogger` com `correlation_id` por requisicao
- Campos `created_at`, `updated_at`, `created_by` em modelos principais

### 6.5 Estrutura do Banco

O banco segue o padrao Django ORM com:
- `BigAutoField` como chave primaria padrao
- JSONField extensivo (etapas, sistemas, payload, dados de sessao)
- UUIDField para identificadores externos (POP, analise de riscos)
- ForeignKey com `on_delete` apropriado (PROTECT, CASCADE, SET_NULL)
- UniqueConstraint condicional (`unique_cap_ativo` para codigo de processo)
- Indexes explicitos em campos de busca frequente (session_id, is_active, user)

### 6.6 Risco de Crescimento

- **HelenaSession**: Dados de conversa em JSONField podem crescer significativamente. Metodo `limpar_sessoes_antigas()` existe para cleanup.
- **POPSnapshot**: Crescimento proporcional ao uso (1 snapshot a cada 5 autosaves).
- **ChromaDB**: Vectorstore local pode crescer com documentos indexados; sem politica de poda observada.
- **Django sessions**: Nao ha rotina automatizada de limpeza de sessoes expiradas observada.
- **Logs rotativos**: Configurados com 10MB max e 5 backups, controlando crescimento em disco.

---

## 7. Padroes e Modularidade

### 7.1 Separacao de Responsabilidades

O projeto apresenta **separacao razoavel** entre camadas:

- `processos/domain/`: Logica de negocio encapsulada por produto Helena
- `processos/infra/`: Servicos transversais (cross-cutting concerns)
- `processos/api/`: Endpoints REST modulares
- `processos/models*`: Persistencia
- `frontend/src/services/`: Comunicacao HTTP
- `frontend/src/store/`: Estado da aplicacao
- `frontend/src/components/`: Apresentacao

### 7.2 Organizacao de Servicos

Cada produto Helena e um modulo autonomo com seu proprio diretorio:
- `helena_mapeamento/`: HelenaPOP, HelenaEtapas, HelenaMapeamento, AjudaInteligente
- `helena_planejamento_estrategico/`: Orchestrator + 7 agents + schemas
- `helena_analise_riscos/`: Matriz, adapter, contexto
- `helena_fluxograma/`: FlowchartAgent, orchestrator
- `helena_recepcao/`: Orchestrator

### 7.3 Uso de Utils/Helpers

- `processos/utils.py` (rebatizado `utils_gerais.py`): ValidadorUtils, FormatadorUtils, CodigoUtils, ArquivoUtils, LogUtils, SegurancaUtils, PDFGenerator
- `processos/infra/loaders/`: 5 loaders de dados CSV
- `processos/infra/parsers.py`: Parsing auxiliar
- `frontend/src/utils/`: sessionManager, dashboardSync

### 7.4 Acoplamento

**Baixo acoplamento entre produtos**: Cada produto Helena opera independentemente, comunicando apenas via interface padronizada (dict com `resposta`, `tipo_interface`, `dados_interface`, `metadados`).

**Acoplamento moderado no roteador**: `views.py:chat_api_view()` e um ponto central que conhece todos os produtos, mas os imports sao lazy.

**Acoplamento frontend-backend**: O frontend depende de contratos de API implicitos (sem OpenAPI/Swagger gerado). Schemas Zod no frontend validam parcialmente a interface.

**Dependencia forte de Django session**: O estado da conversa depende do mecanismo de sessao Django, criando acoplamento com a infraestrutura de sessao.

### 7.5 Protocol Pattern

O arquivo `produto_helena_protocol.py` define um **Protocol** (duck typing) que todos os produtos devem seguir, estabelecendo contrato sem heranca forcada.

---

## 8. Pontos Fortes Tecnicos do Sistema

1. **Arquitetura de maquinas de estado**: Os produtos Helena usam FSMs deterministicas bem definidas, garantindo previsibilidade e testabilidade. O padrao `to_dict()` / `from_dict()` permite serializacao simples.

2. **Estrategia de IA em camadas**: Uso criterioso de IA — somente onde agrega valor (classificacao, orientacao). Produtos que nao precisam de IA sao 100% deterministicos, reduzindo custo e latencia.

3. **Seguranca em profundidade**: Multiplas camadas de protecao (CSRF, rate limiting, RLS, RBAC, PII masking, HSTS, HttpOnly cookies) demonstram preocupacao consistente com seguranca.

4. **Protecao LGPD**: Modulo `pii_protection.py` mascara dados sensiveis (CPF, CNPJ, email, telefone) antes de enviar para LLMs externos, atendendo requisitos de privacidade.

5. **Variaveis de ambiente**: Todas as configuracoes sensiveis (SECRET_KEY, DATABASE_URL, OPENAI_API_KEY, SENTRY_DSN) sao gerenciadas via variaveis de ambiente, com `.env.example` documentado.

6. **Integridade de dados POP**: Hash SHA256 + controle de concorrencia (409 Conflict) + snapshots automaticos + changelog campo a campo demonstram cuidado com integridade e auditabilidade.

7. **Logging estruturado**: Sistema de logging em 3 niveis (console, arquivo rotativo, JSON estruturado) com correlation_id por requisicao, pronto para integracao com ELK/Datadog.

8. **Metricas Prometheus**: Endpoint `/metrics` com metricas HTTP, database e business, pronto para Grafana.

9. **Deploy multi-plataforma**: Suporte simultaneo a Render (render.yaml) e Google Cloud Run (Dockerfile multi-stage), com fallback gracioso para SQLite em desenvolvimento.

10. **Separacao frontend/backend**: Frontend React completamente desacoplado, comunicando via API REST, com stores Zustand bem organizados por feature.

11. **Validacao em multiplas camadas**: Django validators no backend, Zod schemas no frontend, validacao de entrada na camada de views.

12. **Aprovacao de acesso com votacao**: Mecanismo de 3 votos para usuarios externos demonstra preocupacao com governanca de acesso.

---

## 9. Riscos Tecnicos Identificados

1. **`views.py` monolitico (1540 linhas)**: O arquivo concentra chat API, PDF generation, autosave, draft management, e analise de conteudo PDF. Dificulta manutencao e testes isolados.

2. **`@csrf_exempt` em views de API**: Multiplas views usam `@csrf_exempt`, desabilitando protecao CSRF. Embora comum em APIs REST com autenticacao por sessao que usam header CSRF, o uso generalizado merece atencao.

3. **Modo `PUBLIC_MVP_MODE=1` em producao**: A flag esta configurada para desabilitar autenticacao. Se acidentalmente mantida em producao, todas as APIs ficam publicas. Observado no commit recente: `fix: desabilita exigencia de login em producao (VITE_PUBLIC_MVP_MODE=1)`.

4. **Dependencia de sessao Django para estado conversacional**: O estado da maquina de estados e armazenado na Django session. Em cenarios de multiplos workers sem Redis, a sessao pode se perder. O `HelenaSession` model existe como alternativa, mas o roteador principal (`chat_api_view`) ainda usa `request.session`.

5. **SECRET_KEY hardcoded como fallback**: Em `settings.py`, a SECRET_KEY tem um valor padrao inseguro (`django-insecure-ol5&...`). Se a variavel de ambiente nao for definida, esse valor sera usado.

6. **Arquivo `.env` presente no repositorio**: O `.env` esta na raiz do projeto (visivel no `ls`). Embora o `.gitignore` provavelmente o exclua, sua presenca no diretorio de trabalho pode causar vazamento acidental.

7. **Imports de modulos legados**: `views.py` importa de `../z_md/` (diretorio legacy) para `analise_riscos` e `plano_acao`. Esses caminhos relativos saindo do pacote sao frageis.

8. **ChromaDB local sem persistencia garantida**: O vectorstore ChromaDB persiste em `./chroma_db/` local. Em ambientes containerizados (Cloud Run), o diretorio e efemero e dados sao perdidos a cada deploy.

9. **Ausencia de testes automatizados abrangentes**: Existem poucos testes em `processos/tests/` (smoke test, riscos test). A cobertura de testes nao foi mensurada, mas a quantidade de arquivos de teste e desproporcional ao tamanho do sistema.

10. **Inconsistencia de versao Python**: `runtime.txt` especifica Python 3.13.0, enquanto o Dockerfile usa `python:3.11-slim`. Pode causar incompatibilidades.

11. **JSONField extensivo nos models**: Multiplos campos JSONField (etapas, sistemas, payload, dados) reduzem a capacidade de query/indexacao do banco relacional. Dados estruturados dentro de JSON nao sao consultaveis via ORM padrao.

12. **Ausencia de schema de API documentado**: Nao foi identificado OpenAPI/Swagger ou documentacao automatizada de endpoints. Os contratos de API sao implicitos.

13. **Redis opcional mas assumido**: Rate limiting e cache assumem Redis disponivel, com fallback para LocMemCache. Em producao sem Redis, rate limiting pode nao funcionar adequadamente.

---

## 10. Resumo Executivo

### O que e o sistema

O **MapaGov** e uma plataforma web de governanca publica que auxilia servidores do Ministerio da Gestao e da Inovacao (MGI) na producao de artefatos institucionais — Procedimentos Operacionais Padrao, analises de risco e planos estrategicos. A producao dos artefatos e conduzida por uma assistente virtual chamada **Helena**, que guia o usuario por conversas estruturadas.

### Como foi construido

O sistema foi desenvolvido como um **monolito hibrido** com backend Django (Python) e frontend React (TypeScript), ambos servidos pela mesma instancia. A arquitetura interna segue o padrao de **maquinas de estado deterministicas** para cada produto, com integracao seletiva de IA (OpenAI GPT-4o/4o-mini via LangChain) somente onde a analise semantica e necessaria.

O backend implementa camadas bem definidas: `domain/` para logica de negocio, `infra/` para servicos transversais, `api/` para endpoints REST, com Django ORM para persistencia. O frontend utiliza Zustand para estado, Axios para comunicacao, e Zod para validacao em runtime.

### Principais tecnologias

- **Backend:** Django 5.2, Django REST Framework, Gunicorn, PostgreSQL
- **Frontend:** React 19, TypeScript, Vite, Zustand, React Router
- **IA:** LangChain, OpenAI (GPT-4o, GPT-4o-mini), ChromaDB (RAG)
- **Seguranca:** Sessoes Django, RBAC, Rate Limiting, PII Protection, HSTS
- **Observabilidade:** Sentry, Prometheus, Structured JSON Logging
- **Deploy:** Render (free tier), Google Cloud Run (alternativa)

### Solidez tecnica

O sistema demonstra **maturidade tecnica acima da media** para um projeto de governanca publica. A arquitetura de seguranca em camadas (middleware chain com 8 componentes), o controle de integridade de dados (SHA256 + snapshots + changelog), a estrategia de IA em 3 camadas (match exato → fuzzy → LLM), e a protecao LGPD nativa (mascaramento de PII antes de LLMs) sao indicadores de engenharia cuidadosa.

A decisao de usar maquinas de estado deterministicas como nucleo — reservando IA para apoio — garante previsibilidade, testabilidade e controle de custos, caracteristicas essenciais em sistemas de governo.

### Onde pode evoluir

Os principais pontos de evolucao incluem: refatoracao do `views.py` monolitico em modulos menores, ampliacao da cobertura de testes automatizados, documentacao formal de API (OpenAPI/Swagger), resolucao da inconsistencia de versao Python entre ambientes, e revisao do modo MVP que atualmente desabilita autenticacao em producao. A migracao do estado conversacional de Django sessions para o modelo `HelenaSession` (ja existente) tambem aumentaria a resiliencia em ambientes com multiplos workers.

---

*Relatorio gerado exclusivamente com base no codigo-fonte do repositorio MapaGov. Nenhuma informacao foi presumida ou inferida de fontes externas.*
