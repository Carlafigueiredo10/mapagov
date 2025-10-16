# DESENVOLVIMENTO.md

Este arquivo contém orientações essenciais para desenvolver o MapaGov. **LEIA ANTES DE INICIAR QUALQUER SESSÃO DE DESENVOLVIMENTO!**

---

## 🚨 REGRAS DE OURO (NUNCA QUEBRE!)

### 1. **NUNCA altere código sem entender o contexto atual**
- ❌ NÃO rode comandos automaticamente
- ✅ SEMPRE pergunte ao desenvolvedor:
  - "Em que passo estamos?"
  - "O que está funcionando agora?"
  - "Qual o objetivo desta sessão?"

### 2. **SEMPRE peça aprovação ANTES de fazer alterações**
- ❌ NÃO edite arquivos sem mostrar o ANTES/DEPOIS
- ✅ SEMPRE mostre:
  ```
  Arquivo: X
  Linha: Y
  ANTES: código atual
  DEPOIS: código proposto
  PODE FAZER? (SIM/NÃO)
  ```

### 3. **NUNCA assuma que algo "óbvio" precisa ser feito**
- ❌ "Vou instalar as dependências automaticamente"
- ❌ "Vou fazer commit das alterações"
- ✅ SEMPRE pergunte: "Posso fazer X?"

### 4. **RESPEITE o nível de experiência do desenvolvedor**
- Nem todos são desenvolvedores sênior
- Explique comandos ANTES de pedir para rodar
- Um passo de cada vez, aguarde confirmação

---

## 📋 CHECKLIST INICIAL (TODO INÍCIO DE SESSÃO)

Antes de fazer QUALQUER coisa, faça estas perguntas:

```
□ Qual o objetivo desta sessão?
□ O que está funcionando atualmente?
□ O que NÃO está funcionando?
□ Houve algum deploy recente?
□ Há quanto tempo o backend está no ar sem problemas?
□ Posso fazer alterações ou só investigar?
```

**NUNCA pule estas perguntas!** Especialmente depois de sessões longas (30+ horas) para fazer algo funcionar.

---

## 🛡️ PROTEÇÃO DO CÓDIGO EM PRODUÇÃO

### Regra: **Se está funcionando, NÃO MEXA sem backup!**

Antes de qualquer alteração arriscada:

```bash
# 1. Criar branch de backup
git branch backup-$(date +%Y%m%d-%H%M%S)

# 2. Verificar o que vai mudar
git status

# 3. Mostrar ao desenvolvedor e AGUARDAR aprovação
```

### Ambientes:

- **Produção (Cloud Run):** NUNCA faça mudanças experimentais aqui!
- **Desenvolvimento (local):** OK para testar
- **Branches:** Use para features em desenvolvimento

---

## 📦 ESTRATÉGIA DE COMMITS

### ✅ QUANDO COMMITAR:

1. **Todo dia** (no mínimo 1 commit por dia de trabalho)
2. **Sempre que algo funcionar** (mesmo que parcialmente)
3. **ANTES de mudanças arriscadas** (ponto de restauração)
4. **Final do dia** (backup do trabalho)
5. **Antes de fazer deploy** (tudo versionado)

### ❌ NÃO COMMITE:

- Código que não compila/não roda
- Arquivos de configuração com secrets (`.env`, `credentials.json`)
- Código comentado pela metade
- Mudanças experimentais não testadas (use branch!)

### 📝 MENSAGENS DE COMMIT PROFISSIONAIS:

**Formato:** `tipo: descrição curta`

**Tipos:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração (melhoria sem mudar comportamento)
- `docs:` Documentação
- `style:` Formatação, indentação
- `test:` Testes
- `chore:` Manutenção (dependências, configs)

**Exemplos:**
```bash
✅ git commit -m "feat: adiciona validação de etapas no helena_pop"
✅ git commit -m "fix: corrige erro 500 ao salvar POP vazio"
✅ git commit -m "refactor: melhora performance do autosave"
✅ git commit -m "docs: atualiza README com instruções de deploy"

❌ git commit -m "mudanças"
❌ git commit -m "teste"
❌ git commit -m "fix"
```

---

## 🌳 ESTRATÉGIA DE BRANCHES

### **Para features em desenvolvimento:**

```bash
# Criar branch de feature
git checkout -b feature/nome-da-feature

# Trabalhar e commitar várias vezes
git add arquivo1.py arquivo2.js
git commit -m "feat: adiciona X"
git push origin feature/nome-da-feature

# Quando estiver PRONTA para produção
git checkout main
git merge feature/nome-da-feature
git push origin main
```

### **Nomenclatura de branches:**

- `feature/nome` - Nova funcionalidade
- `fix/nome` - Correção de bug
- `refactor/nome` - Refatoração
- `hotfix/nome` - Correção urgente em produção

**Exemplo de fluxo:**
```
main (produção) ← só merge quando estiver pronto
  ↑
feature/helena-pop-completa ← commits diários aqui
```

---

## 🚀 ESTRATÉGIA DE DEPLOY

### **Regra: Uma feature completa por vez!**

**BOM (Incremental):**
```
✅ Semana 1: helena_pop completa → deploy → usuários testam
✅ Semana 2: helena_riscos completa → deploy → usuários testam
✅ Semana 3: helena_fluxograma completa → deploy → usuários testam
```

**RUIM (Big Bang):**
```
❌ Mês 1: desenvolve TUDO junto
❌ Mês 2: deploy de tudo de uma vez
❌ Bug em produção afeta tudo
```

### **Checklist de Deploy:**

Antes de fazer deploy em produção:

```
□ Código commitado e versionado?
□ Testado localmente?
□ README/docs atualizados?
□ Secrets configurados no Cloud (não no código)?
□ Backup do banco de dados feito?
□ Branch de backup criada?
□ Desenvolvedor ciente e aprovou?
```

---

## 🔧 BOAS PRÁTICAS DE DESENVOLVIMENTO

### **1. Teste LOCAL antes de fazer deploy**

```bash
# Backend (Django)
python manage.py runserver

# Frontend (React)
cd frontend
npm run dev

# Acesse: http://localhost:8000 (backend) e http://localhost:5174 (frontend)
```

### **2. Nunca confie em "vai funcionar em produção"**

Se não funciona local, NÃO vai funcionar em produção!

### **3. Leia os logs ANTES de fazer alterações**

```bash
# Logs do Cloud Run
gcloud run services logs read mapagov --region us-central1 --limit 50

# Procurar erros
gcloud logging read "resource.type=cloud_run_revision" --limit 100 | grep -i error
```

### **4. Use .gitignore para arquivos sensíveis**

**NUNCA commite:**
- `.env` (variáveis de ambiente)
- `db.sqlite3` (banco de desenvolvimento)
- `__pycache__/` (cache Python)
- `node_modules/` (dependências Node)
- `chroma_db/` (embeddings, pode ser grande)
- `.vscode/settings.json` (configurações pessoais)

### **5. Mantenha dependências atualizadas (com cuidado)**

```bash
# Backend
pip list --outdated

# Frontend
cd frontend
npm outdated

# Atualize UMA de cada vez, teste, depois commite
```

---

## 🐛 DEBUGANDO PROBLEMAS

### **Erro 500 (Internal Server Error)**

```bash
# 1. Ver logs do Cloud Run
gcloud run services logs read mapagov --region us-central1 --limit 50

# 2. Procurar "Traceback" ou "ERROR"
gcloud logging read "resource.type=cloud_run_revision" --limit 100 | grep -A 10 "Traceback"

# 3. Reproduzir localmente
python manage.py runserver
# Tentar a mesma ação que deu erro
```

### **Erro 404 (Not Found)**

```bash
# Verificar rotas do Django
cat mapagov/urls.py
cat processos/urls.py

# Verificar se arquivo existe
ls -la caminho/do/arquivo
```

### **ModuleNotFoundError**

```bash
# Verificar se módulo está instalado
pip list | grep nome-do-modulo

# Verificar se arquivo existe
ls -la processos/nome_do_arquivo.py

# Verificar imports
grep -r "from nome_do_modulo" .
```

### **Build do frontend falhando**

```bash
# Testar build local
cd frontend
npm run build

# Ver erro completo (sem fallbacks)
# Corrigir o erro
# Rebuild
```

---

## 📚 ARQUITETURA DO PROJETO

### **Backend (Django)**

```
mapagov/
├── mapagov/           # Configurações principais
│   ├── settings.py    # ⚠️ CUIDADO! Secrets aqui
│   ├── urls.py        # Rotas principais
│   └── wsgi.py
├── processos/         # App principal
│   ├── models.py      # Modelos (POP, POPSnapshot, etc.)
│   ├── views.py       # APIs e views
│   ├── urls.py        # Rotas do app
│   ├── serializers.py # Serialização JSON
│   ├── helena_produtos/  # Produtos IA da Helena
│   │   ├── helena_pop.py
│   │   ├── helena_riscos.py
│   │   └── ...
│   └── utils_gerais.py  # Utilitários compartilhados
├── frontend/          # Frontend React
│   ├── src/
│   ├── dist/          # Build (gerado, não versionar!)
│   └── package.json
├── staticfiles/       # Arquivos estáticos (gerado!)
├── requirements.txt   # Dependências Python
├── Dockerfile         # Build Docker
└── .env               # ⚠️ NUNCA COMMITAR!
```

### **Frontend (React)**

```
frontend/
├── src/
│   ├── components/    # Componentes React
│   │   └── Helena/    # Chat da Helena
│   ├── pages/         # Páginas
│   ├── services/      # API client (Axios)
│   ├── store/         # Estado global (Zustand)
│   ├── hooks/         # Hooks customizados
│   └── types/         # TypeScript types
├── public/            # Assets estáticos
│   ├── helena_*.png   # Imagens da Helena
│   └── logo_mapa.png
└── dist/              # Build (gerado por Vite)
```

---

## ⚠️ ERROS COMUNS E SOLUÇÕES

### **1. "TemplateDoesNotExist: index.html"**

**Causa:** Build do frontend não copiou `index.html` para lugar certo

**Solução:**
```bash
# Verificar se index.html existe
ls -la frontend/dist/index.html

# Verificar TEMPLATES em settings.py
cat mapagov/settings.py | grep -A 5 "TEMPLATES"

# Rebuild frontend
cd frontend
npm run build
```

### **2. "ModuleNotFoundError: No module named 'X'"**

**Causa:** Arquivo Python não commitado ou dependência não instalada

**Solução:**
```bash
# Verificar se arquivo existe
ls -la processos/X.py

# Se não existe, adicionar ao git
git add processos/X.py
git commit -m "feat: adiciona módulo X"
git push

# Ou instalar dependência
pip install nome-do-pacote
```

### **3. "No space left on device" (Cloud Shell)**

**Causa:** Cache ocupando 4GB+

**Solução:**
```bash
# Limpar cache
rm -rf ~/.cache/*
rm -rf ~/.local/lib/python*/site-packages/*
npm cache clean --force

# Verificar espaço
df -h /home
```

### **4. Build do frontend falha: "vite: command not found"**

**Causa:** Dockerfile com `--only=production` (não instala devDependencies)

**Solução:**
```dockerfile
# Dockerfile linha ~17
# ANTES:
RUN npm ci --only=production

# DEPOIS:
RUN npm ci
```

### **5. "Request failed with status code 500"**

**Causa:** Erro no backend Python

**Solução:**
```bash
# Ver logs
gcloud run services logs read mapagov --region us-central1 --limit 50

# Procurar "Traceback"
# Corrigir erro no código
# Rebuild + redeploy
```

---

## 🔐 SEGURANÇA

### **Secrets e Variáveis de Ambiente**

**NUNCA commite no código:**
- `OPENAI_API_KEY`
- `SECRET_KEY` (Django)
- `DATABASE_URL`
- Senhas, tokens, chaves API

**Use:**
- `.env` local (não commitado)
- Google Secret Manager (produção)

**Verificar antes de commitar:**
```bash
# Ver o que vai ser commitado
git diff --staged

# Procurar por secrets
git diff --staged | grep -i "api_key\|secret\|password"
```

### **.gitignore essencial:**

```
# Python
__pycache__/
*.pyc
*.pyo
db.sqlite3
.env

# Node
node_modules/
frontend/dist/
npm-debug.log

# IDEs
.vscode/settings.json
.idea/

# Dados
chroma_db/
backups/
media/

# Secrets
*.pem
*.key
credentials.json
```

---

## 📞 COMUNICAÇÃO COM O DESENVOLVEDOR

### **Sempre confirme antes de:**

1. Editar código
2. Fazer commit/push
3. Fazer build/deploy
4. Deletar arquivos
5. Instalar dependências
6. Mudar configurações

### **Pergunte de forma clara:**

✅ **BOM:**
```
Vou fazer esta alteração:

Arquivo: mapagov/settings.py
Linha: 45
ANTES: DEBUG = True
DEPOIS: DEBUG = False

Isso vai desabilitar o modo debug em produção.
PODE FAZER? (SIM/NÃO)
```

❌ **RUIM:**
```
Vou corrigir o settings
[faz alteração sem mostrar]
```

### **Respeite o tempo e contexto:**

- Desenvolvedor passou 30h configurando? **Cuidado redobrado!**
- É 3h da manhã? **Sugira parar e continuar descansado**
- Muitos erros seguidos? **Pare, analise, depois continue**

---

## 🎯 FILOSOFIA DE DESENVOLVIMENTO

### **"Funciona > Perfeito"**

Melhor entregar **funcionalidade completa e testada** do que **tudo pela metade**.

### **"Um passo de cada vez"**

Não tente corrigir 5 problemas simultaneamente. Foque em 1, resolva, teste, depois próximo.

### **"Backup antes de arriscar"**

Se tem dúvida se vai funcionar, faça backup (branch, commit) antes!

### **"Usuário em primeiro lugar"**

Um sistema sem interface visual **não serve para nada**, mesmo que o backend seja perfeito.

---

## 📅 ROTINA DIÁRIA RECOMENDADA

### **Início do dia:**
```
1. git pull origin main
2. Ler mensagens/issues
3. Definir objetivo do dia (1 feature/fix)
4. Criar branch se necessário
```

### **Durante o dia:**
```
1. Desenvolver em pequenos incrementos
2. Testar localmente após cada mudança
3. Commit quando algo funcionar (3-5x por dia)
4. Push para branch de feature
```

### **Final do dia:**
```
1. Commit do trabalho do dia (mesmo incompleto)
2. Push para branch
3. Atualizar issues/TODO
4. Documentar próximos passos
```

---

## 🆘 QUANDO PEDIR AJUDA

### **Peça ajuda se:**

- Mesmo erro acontece 3+ vezes seguidas
- Não entende o erro nos logs
- Mudança "simples" quebrou tudo
- Está há 2+ horas travado no mesmo problema

### **Antes de pedir ajuda, tenha em mãos:**

1. Mensagem de erro COMPLETA (logs)
2. O que você estava tentando fazer
3. O que você já tentou
4. Código relevante

---

## 📖 LEITURA OBRIGATÓRIA

Antes de QUALQUER sessão de desenvolvimento, leia:

1. **CLAUDE.md** - Instruções gerais do projeto
2. **README.md** - Visão geral e setup
3. **DESENVOLVIMENTO.md** - Este arquivo (você está aqui!)
4. **DEPLOY_GOOGLE_CLOUD.md** - Se for fazer deploy

---

## ✅ CHECKLIST FINAL ANTES DE DEPLOY

```
□ Código testado localmente?
□ Commits descritivos feitos?
□ .gitignore configurado (sem secrets)?
□ README atualizado se necessário?
□ Variáveis de ambiente configuradas no Cloud?
□ Backup criado (branch ou snapshot)?
□ Desenvolvedor aprovou?
□ Horário adequado (não 3h da manhã)?
□ Usuários avisados se houver downtime?
```

---

## 🎓 PARA ASSISTENTES DE IA

Se você é um assistente de IA (Claude, ChatGPT, etc.) lendo este arquivo:

**REGRAS IMPERATIVAS:**

1. **NUNCA altere código sem aprovação explícita do desenvolvedor**
2. **SEMPRE mostre ANTES e DEPOIS de qualquer mudança**
3. **RESPEITE o contexto**: pergunte "onde estamos?" antes de agir
4. **UM PASSO DE CADA VEZ**: aguarde confirmação antes do próximo
5. **SEGURANÇA PRIMEIRO**: se teve 30h de trabalho, tenha cuidado redobrado
6. **EXPLIQUE comandos**: nem todo desenvolvedor é sênior
7. **NÃO assuma**: pergunte ao invés de adivinhar

**Se o desenvolvedor disser "tenho medo de quebrar":**
- Pare imediatamente
- Faça backup antes de qualquer mudança
- Mostre exatamente o que vai mudar
- Aguarde aprovação explícita
- Ofereça alternativa mais conservadora

---

**Última atualização:** 2025-10-16
**Versão:** 1.0
**Mantenedor:** Equipe MapaGov
