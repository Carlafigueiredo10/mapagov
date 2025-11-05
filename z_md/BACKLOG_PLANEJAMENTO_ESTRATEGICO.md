# 📋 BACKLOG - Helena Planejamento Estratégico

**Projeto:** MapaGov - Helena PE (Planejamento Estratégico)
**Última atualização:** 04/11/2025
**Responsável:** Equipe de Desenvolvimento

---

## 🎯 VISÃO GERAL

Sistema completo de planejamento estratégico para o setor público, baseado em MGI (Modelo de Gestão Integrada) com 7 domínios e múltiplos modelos de planejamento.

---

## 📊 STATUS ATUAL

### ✅ Concluído
- [x] Domínio 1 - Abordagens e Fundamentos (card de expansão + artefatos)
- [x] Domínio 2 - Escopo e Valor (card de expansão + 4 artefatos funcionais)
- [x] Orquestrador PE (pe_orchestrator.py)
- [x] Agentes especializados (OKR, SWOT, BSC, Tradicional, 5W2H, Hoshin, Cenários)
- [x] Interface Helena PE Moderna
- [x] Dashboard de Governança
- [x] Diagnóstico Guiado (5 perguntas)

### 🚧 Em Andamento
- [ ] Domínios 3-7 (cards de expansão)
- [ ] Artefatos dos Domínios 3-7

### ⏳ Pendente
- [ ] Exportação PDF/DOCX de artefatos
- [ ] Integração completa backend ↔ frontend
- [ ] Persistência de dados no banco
- [ ] Workspaces visuais dos modelos

---

## 🗂️ BACKLOG DETALHADO

### 🔵 DOMÍNIO 3 - Equipe e Responsabilidades

**Prioridade:** Alta
**Estimativa:** 12-16 horas

#### Tarefas:
- [ ] Criar card de expansão do Domínio 3 em `DashboardCard.tsx`
- [ ] Implementar artefatos:
  - [ ] Organograma do Projeto (visual interativo)
  - [ ] Matriz RACI Completa (estendida)
  - [ ] Canvas de Papéis e Responsabilidades
  - [ ] Mapa de Autoridade e Delegação
- [ ] Adicionar rotas no `App.tsx`
- [ ] Criar páginas wrapper

**Conceito:**
Define quem faz o quê, como a equipe se organiza e quem decide. Estabelece papéis, responsabilidades e estrutura de governança.

---

### �� DOMÍNIO 4 - Capacidades e Atividades

**Prioridade:** Alta
**Estimativa:** 16-20 horas

#### Tarefas:
- [ ] Criar card de expansão do Domínio 4
- [ ] Implementar artefatos:
  - [ ] Cronograma (Gantt Simplificado)
  - [ ] Fluxograma de Processos (já existe, integrar)
  - [ ] Matriz de Competências
  - [ ] Backlog e Kanban
- [ ] Adicionar rotas
- [ ] Criar páginas wrapper

**Conceito:**
Mapeia o que precisa ser feito, em que ordem e com quais recursos. Define tarefas, competências necessárias e fluxo de trabalho.

---

### 🟠 DOMÍNIO 5 - Partes Interessadas e Comunicação

**Prioridade:** Média
**Estimativa:** 12-16 horas

#### Tarefas:
- [ ] Criar card de expansão do Domínio 5
- [ ] Implementar artefatos:
  - [ ] Mapa de Stakeholders (visual)
  - [ ] Plano de Comunicação (tabela editável)
  - [ ] Matriz Poder x Interesse (gráfico 2x2)
  - [ ] Calendário de Reuniões e Rituais
- [ ] Adicionar rotas
- [ ] Criar páginas wrapper

**Conceito:**
Identifica quem influencia ou é impactado pelo projeto e como manter todos informados. Define estratégias de engajamento e comunicação.

---

### 🔴 DOMÍNIO 6 - Incerteza e Contexto

**Prioridade:** Média
**Estimativa:** 16-20 horas

#### Tarefas:
- [ ] Criar card de expansão do Domínio 6
- [ ] Implementar artefatos:
  - [ ] Matriz de Riscos (já existe `/riscos`, integrar)
  - [ ] Análise de Cenários
  - [ ] Plano de Contingência
  - [ ] Radar de Contexto Externo
- [ ] Adicionar rotas
- [ ] Criar páginas wrapper

**Conceito:**
Antecipa riscos, mudanças e contextos que podem afetar o projeto. Define estratégias de mitigação e contingência.

---

### 🟣 DOMÍNIO 7 - Impacto e Aprendizado

**Prioridade:** Média
**Estimativa:** 16-20 horas

#### Tarefas:
- [ ] Criar card de expansão do Domínio 7
- [ ] Implementar artefatos:
  - [ ] Dashboard de Indicadores (visual)
  - [ ] Retrospectiva e Lições Aprendidas
  - [ ] Relatório de Impacto
  - [ ] Base de Conhecimento
- [ ] Adicionar rotas
- [ ] Criar páginas wrapper

**Conceito:**
Avalia resultados, coleta aprendizados e documenta lições. Define como medir sucesso e compartilhar conhecimento.

---

## 📥 EXPORTAÇÃO DE ARTEFATOS

**Prioridade:** Média-Alta
**Estimativa:** 150-210 horas (para todos os artefatos)

### Fase 1 - Prova de Conceito (8-12 horas)
- [ ] Instalar dependências:
  - [ ] `npm install jspdf jspdf-autotable`
  - [ ] `npm install docx file-saver`
- [ ] Implementar exportação PDF para Canvas de Escopo
- [ ] Implementar exportação DOCX para Canvas de Escopo
- [ ] Testar formatação e layout

### Fase 2 - Função Genérica (16-24 horas)
- [ ] Criar `utils/exportarArtefato.ts` com funções reutilizáveis
- [ ] Criar templates de PDF por tipo de artefato
- [ ] Criar templates de DOCX por tipo de artefato
- [ ] Adicionar logo e identidade visual

### Fase 3 - Aplicação em Massa (120-170 horas)
- [ ] Aplicar para todos os artefatos do Domínio 2 (4 artefatos)
- [ ] Aplicar para todos os artefatos do Domínio 3 (4 artefatos)
- [ ] Aplicar para todos os artefatos do Domínio 4 (4 artefatos)
- [ ] Aplicar para todos os artefatos do Domínio 5 (4 artefatos)
- [ ] Aplicar para todos os artefatos do Domínio 6 (4 artefatos)
- [ ] Aplicar para todos os artefatos do Domínio 7 (4 artefatos)
- [ ] Aplicar para artefatos do Domínio 1 (5 artefatos)

### Fase 4 - Melhorias (8-12 horas)
- [ ] Adicionar preview antes de exportar
- [ ] Permitir customização de layout
- [ ] Adicionar marca d'água
- [ ] Exportação em lote (múltiplos artefatos em um PDF/DOCX)

---

## 🎨 WORKSPACES VISUAIS

**Prioridade:** Média
**Estimativa:** 80-120 horas

### Implementação por Modelo:
- [ ] Workspace SWOT (matriz 2x2 interativa) - 12h
- [ ] Workspace OKR (cards + KRs) - 16h
- [ ] Workspace BSC (4 perspectivas) - 16h
- [ ] Workspace Tradicional (Missão/Visão/Valores) - 12h
- [ ] Workspace Cenários (funil de incertezas) - 16h
- [ ] Workspace 5W2H (tabela interativa) - 12h
- [ ] Workspace Hoshin Kanri (matriz X) - 16h

---

## 🔗 INTEGRAÇÃO BACKEND ↔ FRONTEND

**Prioridade:** Alta
**Estimativa:** 40-60 horas

### Tarefas:
- [ ] Criar endpoints REST para artefatos:
  - [ ] POST `/api/artefatos/criar`
  - [ ] GET `/api/artefatos/{id}`
  - [ ] PUT `/api/artefatos/{id}`
  - [ ] DELETE `/api/artefatos/{id}`
  - [ ] GET `/api/artefatos/dominio/{numero}`
- [ ] Implementar modelos Django para artefatos
- [ ] Criar serializers
- [ ] Integrar com frontend (axios/fetch)
- [ ] Sincronização automática de dados

---

## 💾 PERSISTÊNCIA DE DADOS

**Prioridade:** Alta
**Estimativa:** 24-32 horas

### Tarefas:
- [ ] Criar tabelas no banco:
  - [ ] `planejamento_estrategico` (já existe)
  - [ ] `artefato_canvas_escopo`
  - [ ] `artefato_matriz_raci`
  - [ ] `artefato_painel_indicadores`
  - [ ] `artefato_mapa_exclusoes`
  - [ ] ... (demais artefatos)
- [ ] Migrations Django
- [ ] API de sincronização
- [ ] Auto-save (salvar a cada mudança)
- [ ] Histórico de versões

---

## 🧪 TESTES E QUALIDADE

**Prioridade:** Média
**Estimativa:** 40-60 horas

### Tarefas:
- [ ] Testes unitários backend (agentes)
- [ ] Testes de integração (API)
- [ ] Testes E2E frontend (Cypress/Playwright)
- [ ] Testes de acessibilidade
- [ ] Testes de performance
- [ ] Code review automatizado

---

## 📱 RESPONSIVIDADE E UX

**Prioridade:** Média
**Estimativa:** 24-32 horas

### Tarefas:
- [ ] Adaptar artefatos para mobile
- [ ] Otimizar tabelas para telas pequenas
- [ ] Adicionar tooltips e hints
- [ ] Melhorar feedback visual (loading, success, error)
- [ ] Atalhos de teclado
- [ ] Modo escuro (dark mode)

---

## 🚀 MELHORIAS FUTURAS

**Prioridade:** Baixa
**Estimativa:** 80-120 horas

### Funcionalidades:
- [ ] Colaboração em tempo real (WebSockets)
- [ ] Comentários em artefatos
- [ ] Versionamento e comparação
- [ ] IA para sugestões de conteúdo
- [ ] Integração com SEI/SIGEPE
- [ ] Notificações por email
- [ ] Gamificação (badges, pontos)
- [ ] Biblioteca de templates

---

## 📊 ESTIMATIVAS TOTAIS

| Categoria | Horas | Dias úteis |
|-----------|-------|------------|
| Domínios 3-7 | 72-92h | 9-12 dias |
| Exportação PDF/DOCX | 150-210h | 19-26 dias |
| Workspaces | 80-120h | 10-15 dias |
| Integração Backend | 40-60h | 5-8 dias |
| Persistência | 24-32h | 3-4 dias |
| Testes | 40-60h | 5-8 dias |
| UX/Responsividade | 24-32h | 3-4 dias |
| **TOTAL** | **430-606h** | **54-77 dias** |

**Estimativa realista:** 2,5 a 3,5 meses de desenvolvimento (1 desenvolvedor full-time)

---

## 🎯 ROADMAP SUGERIDO

### Sprint 1-2 (2 semanas)
- Domínios 3 e 4 completos

### Sprint 3-4 (2 semanas)
- Domínios 5, 6 e 7 completos

### Sprint 5-6 (2 semanas)
- Exportação PDF/DOCX (Fase 1 e 2)

### Sprint 7-10 (4 semanas)
- Exportação em massa (Fase 3)
- Integração Backend
- Persistência

### Sprint 11-12 (2 semanas)
- Workspaces visuais (principais)

### Sprint 13-14 (2 semanas)
- Testes e QA
- UX/Responsividade

---

## 📝 NOTAS

- Priorizar funcionalidades core antes de melhorias estéticas
- Considerar feedback de usuários beta
- Documentar padrões de código
- Manter consistência visual entre artefatos
- Garantir acessibilidade (WCAG 2.1 AA)

---

**Última revisão:** 04/11/2025
**Próxima revisão:** A definir
