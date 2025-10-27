# 🚀 PLANO DE AÇÃO - Implementação dos 9 Produtos Helena

**Data:** 22 de Outubro de 2025
**Status:** 🎯 **PRONTO PARA EXECUÇÃO**
**Duração Total:** 7,5 meses (15 sprints de 2 semanas)

---

## 📋 SUMÁRIO EXECUTIVO

### Produtos a Implementar (7 produtos)

| # | Produto | Complexidade | Duração | Prioridade |
|---|---------|--------------|---------|------------|
| **P3** | Oportunidades | Média | 4 sem | Alta ⭐⭐⭐ |
| **P4** | Dashboard | Média | 4 sem | Alta ⭐⭐⭐ |
| **P6** | Plano de Ação | Alta | 6 sem | Alta ⭐⭐⭐ |
| **P8** | Conformidade | Média-Alta | 4 sem | Média ⭐⭐ |
| **P7** | Dossiê Governança | Média | 4 sem | Média ⭐⭐ |
| **P9** | Documentos | Média | 4 sem | Baixa ⭐ |
| **P10** | Artefatos | Média | 4 sem | Baixa ⭐ |

**Total:** 30 semanas (7,5 meses)

---

## 🎯 ESTRATÉGIA DE IMPLEMENTAÇÃO

### Princípios

1. **MVP First:** Implementar funcionalidade mínima viável em cada sprint
2. **Integração Contínua:** Integrar com produtos existentes desde o início
3. **Testes Paralelos:** Executar testes enquanto desenvolve próximo produto
4. **Feedback Rápido:** Deploy incremental para validação contínua
5. **Documentação As-Code:** Documentar enquanto desenvolve

### Ordem de Implementação (Otimizada)

A ordem foi definida com base em:
- **Dependências:** P4 depende de P3, P6, P8; P7 depende de todos
- **Valor de Negócio:** P3 + P4 entregam valor imediato (dashboard executivo)
- **Complexidade:** P6 é o mais complexo, vem no meio quando time já tem experiência

```
Sprint 1-2:  P3 (Oportunidades)         → Entrega valor rápido
Sprint 3-4:  P4 (Dashboard)             → Consolida P3 em métricas
Sprint 5-7:  P6 (Plano de Ação)         → Produto mais complexo
Sprint 8-9:  P8 (Conformidade)          → Alimenta P7
Sprint 10-11: P7 (Dossiê Governança)    → Consolidador final
Sprint 12-13: P9 (Documentos)           → Geração de docs
Sprint 14-15: P10 (Artefatos)           → Otimização de templates
```

---

## 📅 CRONOGRAMA DETALHADO

### **SPRINT 1-2: P3 - Oportunidades (4 semanas)**

**Objetivo:** Sistema de identificação de oportunidades com ROI calculado

#### Semana 1: Backend + IA

**Dias 1-2: Setup + Models**
- [ ] Criar `processos/helena_produtos/p3_oportunidades/`
- [ ] Implementar models:
  ```python
  class OportunidadeAnalise(models.Model):
      pop = models.ForeignKey(POP)
      data_analise = models.DateTimeField(auto_now_add=True)
      score_maturidade = models.IntegerField()  # 0-100
      roi_total_tempo = models.FloatField()  # horas/mês
      roi_total_custo = models.DecimalField()  # R$

  class Oportunidade(models.Model):
      analise = models.ForeignKey(OportunidadeAnalise)
      categoria = models.CharField(
          choices=[
              ('automacao', 'Automação'),
              ('otimizacao', 'Otimização'),
              ('burocracia', 'Redução Burocrática'),
              ('treinamento', 'Treinamento')
          ]
      )
      titulo = models.CharField(max_length=200)
      descricao = models.TextField()
      impacto = models.CharField(
          choices=[('alto', 'Alto'), ('medio', 'Médio'), ('baixo', 'Baixo')]
      )
      roi_tempo = models.FloatField()  # horas/mês
      roi_custo = models.DecimalField()  # R$
      custo_implantacao = models.DecimalField()
      prazo_implantacao = models.IntegerField()  # dias
      prioridade = models.IntegerField()  # 1-10
  ```
- [ ] Criar migration `0013_add_oportunidades_models.py`
- [ ] Aplicar migration: `python manage.py migrate`

**Dias 3-4: Helena Analisadora**
- [ ] Implementar `helena_analisadora.py`:
  ```python
  class HelenaAnalisadora:
      def analisar_pop(self, pop_id):
          # 1. Buscar POP do banco
          # 2. Preparar prompt com dados do POP
          # 3. Chamar Vertex AI
          # 4. Parsear resposta JSON
          # 5. Salvar no banco
          # 6. Retornar lista de oportunidades
  ```
- [ ] Criar prompt especializado:
  ```python
  OPORTUNIDADES_PROMPT = """
  Você é consultora em BPM e otimização de processos públicos.

  Analise o POP abaixo e identifique oportunidades em 4 categorias:
  1. AUTOMAÇÃO (RPA, bots, APIs)
  2. OTIMIZAÇÃO (tempo/custo, paralelização)
  3. REDUÇÃO BUROCRÁTICA (checklists, validação entrada)
  4. TREINAMENTO (capacitação FORA do processo)

  POP: {pop_data}

  Para CADA oportunidade:
  - Categoria
  - Título (max 80 chars)
  - Descrição (2-3 sentenças)
  - Impacto: Alto/Médio/Baixo
  - ROI tempo: horas/mês economizadas
  - Custo implantação: R$
  - Prazo: dias

  Retorne JSON:
  {{
    "oportunidades": [...],
    "score_maturidade": 0-100
  }}
  """
  ```

**Dias 5: Helena ROI Calculator**
- [ ] Implementar `helena_roi_calculator.py`:
  ```python
  def calcular_roi(oportunidade):
      # ROI = (ganho_anual - custo_implantacao) / custo_implantacao * 100
      ganho_mensal_reais = oportunidade.roi_tempo * custo_hora_servidor
      ganho_anual = ganho_mensal_reais * 12
      roi_percentual = (ganho_anual - oportunidade.custo_implantacao) / oportunidade.custo_implantacao * 100
      return roi_percentual
  ```

#### Semana 2: API + Frontend

**Dias 1-2: APIs REST**
- [ ] Implementar endpoints em `processos/api/oportunidades_api.py`:
  ```python
  @csrf_exempt
  @require_http_methods(["POST"])
  def analisar_pop(request, pop_id):
      # 1. Buscar POP
      # 2. Chamar Helena Analisadora
      # 3. Retornar JSON com oportunidades

  @require_http_methods(["GET"])
  def listar_oportunidades(request, pop_id):
      # Retornar análise existente

  @csrf_exempt
  @require_http_methods(["POST"])
  def exportar_pdf(request, analise_id):
      # Gerar PDF com oportunidades

  @csrf_exempt
  @require_http_methods(["POST"])
  def adicionar_ao_p6(request, oportunidade_id):
      # Integração com P6 (futuro)
      return JsonResponse({'status': 'pendente_p6'})
  ```
- [ ] Adicionar rotas em `processos/urls.py`:
  ```python
  # P3 - Oportunidades
  path('api/p3/analisar/<int:pop_id>/', oportunidades_api.analisar_pop),
  path('api/p3/oportunidades/<int:pop_id>/', oportunidades_api.listar_oportunidades),
  path('api/p3/exportar-pdf/<int:analise_id>/', oportunidades_api.exportar_pdf),
  path('api/p3/adicionar-ao-p6/<int:oportunidade_id>/', oportunidades_api.adicionar_ao_p6),
  ```

**Dias 3-5: Frontend React**
- [ ] Criar `frontend/src/services/oportunidadesApi.ts`:
  ```typescript
  export const analisarPOP = async (popId: number) => {
    const response = await fetch(`/api/p3/analisar/${popId}/`, {
      method: 'POST',
    });
    return response.json();
  };

  export const listarOportunidades = async (popId: number) => {
    const response = await fetch(`/api/p3/oportunidades/${popId}/`);
    return response.json();
  };
  ```
- [ ] Criar `frontend/src/pages/Oportunidades.tsx`:
  ```typescript
  interface Oportunidade {
    id: number;
    categoria: 'automacao' | 'otimizacao' | 'burocracia' | 'treinamento';
    titulo: string;
    descricao: string;
    impacto: 'alto' | 'medio' | 'baixo';
    roi_tempo: number;
    roi_custo: number;
    custo_implantacao: number;
    prazo_implantacao: number;
    prioridade: number;
  }

  // Componentes:
  // - <OportunidadeCard /> - Card individual
  // - <OportunidadesList /> - Lista com filtros
  // - <DashboardOportunidades /> - Visão geral com score
  ```
- [ ] Adicionar rota em `frontend/src/App.tsx`:
  ```typescript
  <Route path="/oportunidades/:popId" element={<Oportunidades />} />
  ```

**Testing & Deploy:**
- [ ] Testes unitários (backend)
- [ ] Testes de integração (API)
- [ ] Testes E2E (frontend + backend)
- [ ] Deploy em staging
- [ ] Validação com usuários piloto

**Entregáveis Sprint 1-2:**
- ✅ P3 funcionando end-to-end
- ✅ 4 categorias de oportunidades detectadas
- ✅ ROI calculado automaticamente
- ✅ Dashboard visual com cards
- ✅ Botão "Adicionar ao P6" (mock, sem ação)
- ✅ Exportação PDF básica

---

### **SPRINT 3-4: P4 - Dashboard (4 semanas)**

**Objetivo:** Painel executivo multinível com KPIs e métricas de governança

#### Semana 3: Backend + Agregação

**Dias 1-2: Models + Cache**
- [ ] Implementar models:
  ```python
  class DashboardCache(models.Model):
      nivel = models.CharField(
          choices=[
              ('diretoria', 'Diretoria'),
              ('cg', 'Coordenação Geral'),
              ('coordenacao', 'Coordenação'),
              ('usuario', 'Usuário')
          ]
      )
      referencia_id = models.IntegerField(null=True)  # ID da CG, Coordenação, User
      data_atualizacao = models.DateTimeField(auto_now=True)
      metricas = models.JSONField(default=dict)
      # metricas = {
      #   'atividades_por_macro': [...],
      #   'pops_stats': {...},
      #   'evolucao_mensal': [...],
      #   'maturidade': {...},
      #   'riscos_criticos': [...],
      #   'planos_acao_status': {...}
      # }
  ```
- [ ] Migration `0014_add_dashboard_cache.py`

**Dias 3-4: Helena Agregador**
- [ ] Implementar `helena_agregador.py`:
  ```python
  class HelenaAgregador:
      def coletar_metricas_diretoria(self):
          # Agregar dados de TODOS processos
          # Retornar métricas consolidadas

      def coletar_metricas_cg(self, cg_id):
          # Filtrar por Coordenação Geral

      def coletar_metricas_coordenacao(self, coord_id):
          # Filtrar por Coordenação

      def coletar_metricas_usuario(self, user_id):
          # Processos do usuário
  ```

**Dia 5: Helena Métricas (Cálculo de Maturidade)**
- [ ] Implementar `helena_metricas.py`:
  ```python
  def calcular_maturidade(processo):
      """
      Maturidade = % de produtos concluídos (P2-P10)
      Nível 1: 0-20% | Nível 2: 21-40% | ... | Nível 5: 81-100%
      """
      produtos_total = 9  # P2 até P10
      produtos_concluidos = sum([
          1 for p in [processo.p2, processo.p3, ..., processo.p10]
          if p and p.status == 'concluido'
      ])
      percentual = (produtos_concluidos / produtos_total) * 100
      nivel = math.ceil(percentual / 20)  # 1-5
      return {'percentual': percentual, 'nivel': nivel}
  ```

#### Semana 4: API + Frontend + Scheduler

**Dias 1-2: APIs**
- [ ] Endpoints em `processos/api/dashboard_api.py`:
  ```python
  @require_http_methods(["GET"])
  def metricas(request):
      nivel = request.GET.get('nivel', 'diretoria')
      id_ref = request.GET.get('id')

      # Buscar cache
      cache = DashboardCache.objects.filter(nivel=nivel, referencia_id=id_ref).first()

      if not cache or (timezone.now() - cache.data_atualizacao).seconds > 3600:
          # Recalcular (se >1h desatualizado)
          metricas = HelenaAgregador().coletar_metricas(nivel, id_ref)
          cache = DashboardCache.objects.update_or_create(...)

      return JsonResponse(cache.metricas)

  @csrf_exempt
  @require_http_methods(["POST"])
  def refresh_cache(request):
      # Força atualização
      ...
  ```

**Dias 3-5: Frontend Dashboard**
- [ ] Criar `frontend/src/pages/Dashboard.tsx`:
  ```typescript
  // Componentes principais:
  // - <SeletorHierarquico /> - Dropdown cascata
  // - <CardsKPI /> - Cards com métricas principais
  // - <GraficoAtividadesMacro /> - Barras horizontais
  // - <GraficoPOPsStatus /> - Pizza ou barras empilhadas
  // - <GraficoEvolucaoMensal /> - Linha temporal
  // - <CardMaturidade /> - Score + nível visual
  // - <TabelaRiscosCriticos /> - Top 5
  // - <CardPlanosAcao /> - Status + % conclusão
  // - <TabelaProcessos /> - Lista com badges [P2✅][P3✅]...
  ```
- [ ] Integração com bibliotecas de charts (Chart.js ou Recharts)

**Deploy Noturno (Celery):**
- [ ] Criar task Celery `processos/tasks.py`:
  ```python
  @shared_task
  def atualizar_dashboard_cache():
      """Roda às 23h todo dia"""
      # Atualizar cache de todos os níveis
      niveis = ['diretoria', 'cg', 'coordenacao']
      for nivel in niveis:
          ...
  ```
- [ ] Configurar Celery Beat:
  ```python
  # mapagov/settings.py
  CELERY_BEAT_SCHEDULE = {
      'atualizar-dashboard-cache': {
          'task': 'processos.tasks.atualizar_dashboard_cache',
          'schedule': crontab(hour=23, minute=0),
      },
  }
  ```

**Entregáveis Sprint 3-4:**
- ✅ Dashboard multinível funcionando
- ✅ 6 KPIs principais implementados
- ✅ Drill-down hierárquico completo
- ✅ Cache diário (deploy noturno)
- ✅ Botão "Refresh manual"
- ✅ Integração com P3 (mostra oportunidades no dashboard)

---

### **SPRINT 5-7: P6 - Plano de Ação e Controles (6 semanas)**

**Objetivo:** Sistema completo de gestão de ações com auto-learning

⚠️ **PRODUTO MAIS COMPLEXO - 3 sprints**

#### Semana 5: Models + Bucket RAG

**Dias 1-3: Models Completos**
- [ ] Implementar models em `processos/models_new/plano_acao.py`:
  ```python
  class PlanoAcao(models.Model):
      titulo = models.CharField(max_length=200)
      objetivo = models.TextField()
      processo = models.ForeignKey(POP, null=True)
      tipo = models.CharField(
          choices=[
              ('risco', 'Mitigação de Risco'),
              ('oportunidade', 'Implementação de Oportunidade'),
              ('estrategico', 'Planejamento Estratégico')
          ]
      )
      status = models.CharField(
          choices=[
              ('ativo', 'Em andamento'),
              ('concluido', 'Concluído'),
              ('cancelado', 'Cancelado')
          ]
      )
      prazo_final = models.DateField()
      progresso = models.IntegerField(default=0)  # 0-100

  class Acao(models.Model):
      plano = models.ForeignKey(PlanoAcao)
      # 5W2H
      what = models.CharField(max_length=200)
      why = models.TextField()
      where = models.CharField(max_length=100)
      when = models.DateField()
      who = models.ForeignKey(User)
      how = models.TextField()
      how_much = models.DecimalField()
      # Kanban
      status = models.CharField(
          choices=[
              ('backlog', 'Backlog'),
              ('fazendo', 'Em andamento'),
              ('revisao', 'Em revisão'),
              ('concluido', 'Concluído')
          ]
      )
      data_conclusao = models.DateTimeField(null=True)
      evidencias = models.JSONField(default=list)

  class RevisaoPeriodica(models.Model):
      acao_original = models.ForeignKey(Acao)
      data_agendada = models.DateField()  # +730 dias
      status = models.CharField(...)
      controle_ainda_eficaz = models.BooleanField(null=True)
  ```

**Dias 4-5: Bucket RAG de Normas**
- [ ] Criar `processos/rag/bucket_normas/`:
  ```
  bucket_normas/
  ├── coso.pdf
  ├── iso_31000.pdf
  ├── iso_27001.pdf
  ├── acordaos_tcu/
  ├── normas_cgu/
  ├── lgpd_guia_anpd.pdf
  ├── cobit_2019.pdf
  └── pmbok.pdf
  ```
- [ ] Indexar no ChromaDB:
  ```python
  def indexar_bucket_normas():
      collection = chroma_client.get_or_create_collection("bucket_normas")

      for arquivo in glob.glob("processos/rag/bucket_normas/**/*.pdf"):
          texto = extrair_texto_pdf(arquivo)
          chunks = dividir_em_chunks(texto, chunk_size=500)

          for i, chunk in enumerate(chunks):
              collection.add(
                  documents=[chunk],
                  metadatas=[{'fonte': arquivo, 'chunk_id': i}],
                  ids=[f"{arquivo}_{i}"]
              )
  ```

#### Semana 6: Helena Sugestão + Auto-Learning

**Dias 1-3: Helena Sugestão (com RAG)**
- [ ] Implementar `helena_sugestao.py`:
  ```python
  class HelenaSugestao:
      def sugerir_controles(self, risco):
          # 1. Buscar no RAG (bucket de normas)
          results_rag = collection.query(
              query_texts=[risco.descricao],
              n_results=5
          )

          # 2. Buscar controles de POPs similares
          controles_similares = self._buscar_controles_historico(risco)

          # 3. Buscar planos bem-sucedidos
          acoes_eficazes = self._buscar_acoes_aprovadas()

          # 4. Prompt com todo contexto
          prompt = CONTROLES_PROMPT_AUTO_LEARNING.format(
              bucket_normas=results_rag,
              controles_similares=controles_similares,
              acoes_eficazes=acoes_eficazes,
              risco=risco.descricao
          )

          # 5. Chamar LLM
          # 6. Retornar 3-5 controles
  ```

**Dias 4-5: Sistema de Auto-Learning**
- [ ] Implementar feedback tracking:
  ```python
  class ControleFeedback(models.Model):
      controle_original = models.ForeignKey(Acao)
      feedback_tipo = models.CharField(
          choices=[('util', 'Útil'), ('nao_util', 'Não Útil')]
      )
      tempo_real_vs_estimado = models.IntegerField()  # dias
      roi_alcancado_vs_planejado = models.FloatField()  # %
      usuario = models.ForeignKey(User)
      data = models.DateTimeField(auto_now_add=True)

  def atualizar_score_controle(controle_id, feedback):
      """Atualiza score no ChromaDB"""
      if feedback == 'util':
          # Aumentar relevância nas buscas futuras
          ...
      else:
          # Diminuir relevância
          ...
  ```

#### Semana 7: API + Frontend + Alertas

**Dias 1-2: APIs**
- [ ] Endpoints em `processos/api/plano_acao_api.py`:
  ```python
  @csrf_exempt
  @require_http_methods(["POST"])
  def criar_do_zero(request):
      # Chat com Helena Planejadora
      # Retorna plano estruturado

  @csrf_exempt
  @require_http_methods(["POST"])
  def importar_riscos(request, p5_id):
      # Importa de P5 (futuro)

  @csrf_exempt
  @require_http_methods(["POST"])
  def importar_oportunidade(request, oportunidade_id):
      # Integração com P3

  @require_http_methods(["GET"])
  def listar_planos(request):
      user_id = request.GET.get('usuario')
      # Filtrar por usuário

  @csrf_exempt
  @require_http_methods(["PATCH"])
  def atualizar_status_acao(request, acao_id):
      # Mover no Kanban

  @csrf_exempt
  @require_http_methods(["POST"])
  def concluir_acao(request, acao_id):
      # Marcar como concluída + agendar revisão em 2 anos
  ```

**Dias 3-5: Frontend (5W2H + Kanban)**
- [ ] Criar `frontend/src/pages/PlanoAcao.tsx`:
  ```typescript
  // Componentes:
  // - <PlanoAcaoCreator /> - Wizard de criação (3 modos)
  // - <TabelaW2H /> - Visualização tabular 5W2H
  // - <KanbanBoard /> - Drag and drop (react-beautiful-dnd)
  // - <ChatPlanejadora /> - Chat com Helena para modo "do zero"
  // - <AlertasPanel /> - Notificações de prazos
  ```

**Scheduler de Alertas (Celery):**
- [ ] Task diária:
  ```python
  @shared_task
  def enviar_alertas_planos():
      hoje = timezone.now().date()

      # 7 dias antes
      acoes_7dias = Acao.objects.filter(
          when=hoje + timedelta(days=7),
          status__in=['backlog', 'fazendo']
      )
      for acao in acoes_7dias:
          enviar_email(acao.who.email, "Ação vence em 7 dias")

      # Prazo vencido
      acoes_atrasadas = Acao.objects.filter(
          when__lt=hoje,
          status__in=['backlog', 'fazendo', 'revisao']
      )
      for acao in acoes_atrasadas:
          enviar_email([acao.who.email, acao.coordenador.email], "Ação ATRASADA")

      # Inatividade 7 e 15 dias
      ...
  ```
- [ ] Task para revisão periódica (2 anos):
  ```python
  @shared_task
  def agendar_revisao_periodica(acao_id):
      """Chamado ao concluir ação"""
      acao = Acao.objects.get(id=acao_id)
      RevisaoPeriodica.objects.create(
          acao_original=acao,
          data_agendada=timezone.now().date() + timedelta(days=730)
      )
  ```

**Entregáveis Sprint 5-7:**
- ✅ P6 completo com 3 modos de entrada
- ✅ Bucket RAG de normas indexado
- ✅ Auto-learning funcionando
- ✅ 5W2H + Kanban implementados
- ✅ Alertas automáticos (7 dias, vencido, inatividade)
- ✅ Revisão periódica em 2 anos (auto-agendada)
- ✅ Integração com P3 (importar oportunidades)

---

### **SPRINT 8-9: P8 - Conformidade (4 semanas)**

**Objetivo:** Verificação automática de conformidade de processos reais vs normas

#### Semana 8: Backend + RAG Customizado

**Dias 1-2: Models**
- [ ] Implementar models:
  ```python
  class NormaCustomizada(models.Model):
      origem = models.CharField(max_length=200)  # "Portaria 456/2024"
      tipo_adicao = models.CharField(
          choices=[('citacao', 'Citação'), ('trecho', 'Trecho'), ('pdf', 'PDF')]
      )
      conteudo = models.TextField()
      arquivo_pdf = models.FileField(null=True)
      adicionado_por = models.ForeignKey(User)
      data_adicao = models.DateTimeField(auto_now_add=True)
      indexado_rag = models.BooleanField(default=False)

  class ComplianceAnalise(models.Model):
      processo_sei = models.CharField(max_length=50)
      atividade_cap = models.ForeignKey(POP, null=True)
      data_analise = models.DateTimeField(auto_now_add=True)
      score = models.FloatField()  # 0-100
      classificacao = models.CharField(...)  # Excelente/Adequado/Insuficiente/Crítico

  class Requisito(models.Model):
      analise = models.ForeignKey(ComplianceAnalise)
      norma = models.CharField(max_length=100)
      artigo = models.CharField(max_length=50)
      descricao = models.TextField()
      status = models.CharField(
          choices=[
              ('atendido', 'Atendido'),
              ('atendido_parcial', 'Atendido Parcialmente'),
              ('nao_atendido', 'Não Atendido')
          ]
      )
      validado_usuario = models.BooleanField(default=False)

  class ComplianceHistorico(models.Model):
      processo_sei = models.CharField(max_length=50)
      mes_referencia = models.DateField()
      score = models.FloatField()
      gaps_criticos = models.IntegerField()
  ```

**Dias 3-4: RAG Normas Customizadas**
- [ ] Implementar `rag_normas_custom.py`:
  ```python
  def adicionar_norma_citacao(origem, artigo):
      # Buscar na web, indexar no RAG
      ...

  def adicionar_norma_trecho(origem, trecho):
      # Indexar trecho diretamente
      ...

  def adicionar_norma_pdf(origem, arquivo_pdf):
      # Extrair texto, dividir em chunks, indexar
      texto = extrair_texto_pdf(arquivo_pdf)
      chunks = dividir_em_chunks(texto)

      for chunk in chunks:
          collection_normas_custom.add(
              documents=[chunk],
              metadatas=[{'origem': origem}],
              ids=[...]
          )

  def verificar_pops_impactados(norma_nova):
      # Identificar POPs que precisam atualizar base legal
      pops = POP.objects.filter(...)
      return pops
  ```

**Dia 5: Helena Auditora**
- [ ] Implementar `helena_auditora.py`:
  ```python
  class HelenaAuditora:
      def analisar_processo(self, processo_sei, descricao):
          # 1. Buscar requisitos aplicáveis (RAG padrão + customizado)
          # 2. Para cada requisito, verificar atendimento
          # 3. Calcular score
          # 4. Retornar análise
  ```

#### Semana 9: Helena Corretor + API + Frontend

**Dias 1-2: Helena Corretor (3 camadas)**
- [ ] Implementar `helena_corretor.py`:
  ```python
  def sugerir_correcoes(gap):
      """
      Retorna correções em 3 camadas:
      1. Processo (caso concreto)
      2. POP (documento)
      3. Produtos (P2-P10)
      """
      correcoes = {
          'processo': [],
          'pop': [],
          'produtos': []
      }

      # Análise do gap e geração de correções específicas
      ...

      return correcoes
  ```

**Dias 3-4: API + Frontend**
- [ ] APIs em `processos/api/conformidade_api.py`
- [ ] Frontend `frontend/src/pages/Conformidade.tsx`:
  ```typescript
  // Componentes:
  // - <AnaliseForm /> - Input processo SEI ou descrição
  // - <ScoreCard /> - Score geral + por dimensão
  // - <ListaRequisitos /> - Requisitos com status
  // - <ValidacaoRequisito /> - Confirmar/Discordar IA
  // - <CorrecoesMultilayer /> - Correções 3 camadas
  // - <GraficoEvolucao /> - Evolução temporal compliance
  ```

**Dia 5: Integração com P9**
- [ ] Botão "Gerar Documento" após análise
- [ ] Passa dados para P9 pré-carregados

**Entregáveis Sprint 8-9:**
- ✅ P8 funcionando end-to-end
- ✅ RAG padrão + customizado
- ✅ Correções em 3 camadas
- ✅ Validação híbrida (IA + humano)
- ✅ Evolução temporal de compliance
- ✅ Integração com P9

---

### **SPRINT 10-11: P7 - Dossiê de Governança (4 semanas)**

**Objetivo:** Consolidador final de todos produtos em relatório executivo

#### Semana 10: IA Relação + Backend

**Dias 1-2: Helena IA Relação**
- [ ] Implementar `helena_ia_relacao.py`:
  ```python
  def identificar_processos_relacionados(atividade_base):
      """
      Critérios:
      1. Hierarquia (macro/processo/subprocesso)
      2. Fluxo (inputs/outputs, sistemas)
      3. Semântico (embeddings, similaridade)
      4. Dados (responsáveis, base legal)
      """
      # Embeddings da atividade base
      embedding_base = gerar_embedding(atividade_base.descricao)

      # Buscar similares
      similares = buscar_vetorial(embedding_base, threshold=0.7)

      # Calcular score composto
      for similar in similares:
          score = (
              score_hierarquia * 0.3 +
              score_fluxo * 0.3 +
              score_semantico * 0.2 +
              score_dados * 0.2
          )

      return processos_relacionados_com_score
  ```

**Dias 3-5: Helena Consolidador + Helena Estrategista**
- [ ] `helena_consolidador.py`:
  ```python
  def consolidar_dossie(atividades):
      dados_consolidados = {
          'maturidade_media': ...,
          'riscos_criticos': ...,
          'oportunidades_top': ...,
          'planos_status': ...,
          'produtos_completude': ...
      }
      return dados_consolidados
  ```
- [ ] `helena_estrategista.py`:
  ```python
  EXECUTIVE_SUMMARY_PROMPT = """
  Você é executiva sênior de governança corporativa.

  Crie resumo executivo de 300-400 palavras:
  - Conquistas e desafios
  - Top 3 recomendações estratégicas
  - Linguagem executiva (não técnica)
  - Foco em impacto de negócio

  DADOS:
  {dados_consolidados}
  """
  ```

#### Semana 11: PDF Generator + Frontend

**Dias 1-3: PDF Generator (ReportLab)**
- [ ] Implementar `pdf_generator.py`:
  ```python
  def gerar_pdf_executivo(dossie_data):
      """Gera PDF de 5 páginas"""
      # Página 1: Executive Summary
      # Página 2: Visão Geral dos Processos
      # Página 3: Mapa de Riscos e Controles
      # Página 4: Oportunidades e Planos de Ação
      # Página 5: Roadmap Estratégico
  ```

**Dias 4-5: Frontend Dashboard Navegável**
- [ ] `frontend/src/pages/DossieGovernanca.tsx`:
  ```typescript
  // Componentes:
  // - <SeletorProcessos /> - Individual ou Consolidado
  // - <ProcessosRelacionados /> - Lista com scores IA
  // - <DashboardConsolidado /> - Visão geral
  // - <AbaProdutos /> - Tabs por produto
  // - <ExportPDF /> - Botão de exportação
  ```

**Entregáveis Sprint 10-11:**
- ✅ P7 consolidador funcionando
- ✅ IA identifica processos relacionados
- ✅ PDF executivo 5 páginas
- ✅ Dashboard navegável com drill-down
- ✅ Integração com TODOS produtos (P2-P10)

---

### **SPRINT 12-13: P9 - Gerador de Documentos (4 semanas)**

**Objetivo:** Geração automática de notas/despachos/pareceres

#### Semana 12: Backend + Extração SEI

**Dias 1-2: Models + SEI Processor**
- [ ] Models:
  ```python
  class Documento(models.Model):
      tipo = models.CharField(
          choices=[
              ('nota', 'Nota Técnica'),
              ('despacho', 'Despacho'),
              ('parecer', 'Parecer')
          ]
      )
      processo_sei = models.CharField(max_length=50, null=True)
      conteudo_markdown = models.TextField()
      conteudo_html = models.TextField()
      aprovado = models.BooleanField(default=False)

  class DocumentoVersao(models.Model):
      documento = models.ForeignKey(Documento)
      versao_numero = models.IntegerField()
      conteudo = models.TextField()
  ```
- [ ] SEI processor (mock ou integração real):
  ```python
  def buscar_dados_sei(processo_id):
      # Se integração com SEI disponível, buscar
      # Senão, retornar mock ou solicitar input manual
      return {
          'interessado': {...},
          'tramitacao': [...],
          'documentos_juntados': [...],
          'decisao': '...'
      }
  ```

**Dias 3-5: Helena Redatora**
- [ ] Implementar `helena_redatora.py`:
  ```python
  DOCUMENTO_PROMPT = """
  Você é redatora oficial de documentos técnicos do setor público.

  Gere uma {tipo_documento} sobre o processo:

  DADOS: {dados_extraidos}

  ESTRUTURA:
  1. HISTÓRICO
  2. TRAMITAÇÃO
  3. ANÁLISE
  4. CONCLUSÃO

  REQUISITOS:
  - Manual de Redação Oficial
  - Fundamentação legal explícita
  - Conclusão objetiva
  - 3ª pessoa, conciso

  Retorne Markdown formatado.
  """
  ```

#### Semana 13: API + Frontend + Templates

**Dias 1-2: APIs**
- [ ] `processos/api/documentos_api.py`

**Dias 3-5: Frontend + Templates Base**
- [ ] Templates em `processos/helena_produtos/p9_documentos/templates/`:
  ```markdown
  # nota_tecnica.md
  NOTA TÉCNICA Nº {numero}/{ano}-{area}

  ASSUNTO: {assunto}

  1. HISTÓRICO
  {historico}

  2. TRAMITAÇÃO
  {tramitacao}

  3. ANÁLISE
  {analise}

  4. CONCLUSÃO
  {conclusao}

  [Assinatura digital]
  {autor}
  {cargo} - {area}
  ```
- [ ] Frontend com editor Markdown

**Entregáveis Sprint 12-13:**
- ✅ P9 gerador de documentos funcionando
- ✅ 3 tipos: Nota/Despacho/Parecer
- ✅ Extração SEI (mock ou real)
- ✅ Integração com P8 (dados de conformidade)
- ✅ Exportação PDF formatado gov.br

---

### **SPRINT 14-15: P10 - Análise de Artefatos (4 semanas)**

**Objetivo:** Otimização de templates com análise 5 dimensões

#### Semana 14: Backend + Processadores

**Dias 1-2: Models**
- [ ] Models conforme especificação (Artefato, ArtefatoVersao, Problema)

**Dias 3-4: PDF + DOCX Processors**
- [ ] Implementar `pdf_processor.py`:
  ```python
  def extrair_texto_pdf(arquivo):
      # PyPDF2 ou pdfplumber
      ...

  def gerar_pdf_otimizado(conteudo_markdown):
      # ReportLab
      ...
  ```
- [ ] Implementar `docx_processor.py`:
  ```python
  def extrair_texto_docx(arquivo):
      # python-docx
      ...

  def gerar_docx_otimizado(conteudo_markdown):
      # python-docx
      ...
  ```

**Dia 5: Helena Analisadora (5 dimensões)**
- [ ] Implementar análise de clareza, conformidade, acessibilidade, estrutura, completude

#### Semana 15: Helena Otimizadora + Frontend

**Dias 1-2: Helena Otimizadora**
- [ ] Aplicar transformações automáticas
- [ ] Gerar versão otimizada

**Dias 3-5: Frontend + Feedback Iterativo**
- [ ] `frontend/src/pages/AnaliseArtefatos.tsx`
- [ ] Comparação lado a lado
- [ ] Chat de feedback
- [ ] Timeline de versões

**Entregáveis Sprint 14-15:**
- ✅ P10 análise de artefatos completo
- ✅ 5 dimensões implementadas
- ✅ Comparação DE → PARA
- ✅ Geração automática (PDF + Word)
- ✅ Feedback iterativo
- ✅ Histórico de versões

---

## 📊 RECURSOS NECESSÁRIOS

### Time Mínimo

| Função | Alocação | Responsabilidades |
|--------|----------|-------------------|
| **Backend Developer (Python/Django)** | Full-time | Models, APIs, Helena's, RAG |
| **Frontend Developer (React/TypeScript)** | Full-time | Interfaces, componentes, integração |
| **IA/ML Engineer** | Part-time (50%) | Prompts, RAG, embeddings, fine-tuning |
| **DevOps** | Part-time (25%) | Deploy, Celery, monitoramento |
| **Product Owner** | Part-time (25%) | Validação, priorização, feedback usuários |
| **QA** | Part-time (50%) | Testes, validação, bugs |

**Total:** ~4 FTEs

### Infraestrutura

| Componente | Especificação | Custo Estimado/mês |
|------------|---------------|---------------------|
| **Servidor Backend** | 4 vCPUs, 16GB RAM | R$ 300 |
| **Banco PostgreSQL** | Managed, 50GB | R$ 200 |
| **Redis** | Managed, 2GB | R$ 100 |
| **Celery Workers** | 2 workers | R$ 150 |
| **ChromaDB / Vector DB** | Self-hosted ou managed | R$ 150 |
| **Vertex AI / LLM API** | Pay-per-use | R$ 500-1000 |
| **Storage (S3/GCS)** | 100GB | R$ 50 |
| **Monitoring (Prometheus+Grafana)** | Self-hosted | R$ 0 |

**Total:** ~R$ 1.450-1.950/mês

### Dependências Técnicas

**Python:**
```
Django==5.2
djangorestframework==3.14
celery==5.3
redis==5.0
psycopg2-binary==2.9
chromadb==0.4
vertexai==1.38
PyPDF2==3.0
python-docx==1.1
reportlab==4.0
pdfplumber==0.10
prometheus-client==0.19
```

**JavaScript:**
```
react==18.2
typescript==5.0
react-router-dom==6.20
@tanstack/react-query==5.0
chart.js / recharts
react-beautiful-dnd==13.1
```

---

## ✅ CHECKLIST DE ENTREGA (Por Sprint)

### Sprint 1-2 (P3)
- [ ] Backend: Models + Migrations aplicadas
- [ ] Backend: Helena Analisadora + ROI Calculator funcionando
- [ ] Backend: 3 APIs implementadas
- [ ] Frontend: Página Oportunidades renderizando
- [ ] Frontend: Cards de oportunidades com filtros
- [ ] Testes: Unitários + integração
- [ ] Deploy: Staging funcionando
- [ ] Docs: API documentada

### Sprint 3-4 (P4)
- [ ] Backend: DashboardCache model + migration
- [ ] Backend: Helena Agregador + Métricas
- [ ] Backend: Celery task (deploy noturno)
- [ ] Frontend: Dashboard multinível
- [ ] Frontend: 6 KPIs visuais
- [ ] Frontend: Drill-down funcionando
- [ ] Testes: E2E do fluxo completo
- [ ] Deploy: Celery Beat configurado

### Sprint 5-7 (P6)
- [ ] Backend: Models PlanoAcao + Acao + RevisaoPeriodica
- [ ] Backend: Bucket RAG indexado
- [ ] Backend: Helena Sugestão + Auto-learning
- [ ] Backend: APIs (7 endpoints)
- [ ] Backend: Celery tasks (alertas + revisão)
- [ ] Frontend: Chat + 5W2H + Kanban
- [ ] Testes: Fluxo 3 modos de entrada
- [ ] Deploy: Alertas funcionando

### Sprint 8-9 (P8)
- [ ] Backend: Models Compliance + Requisito + Histórico
- [ ] Backend: RAG customizado
- [ ] Backend: Helena Auditora + Corretor
- [ ] Frontend: Análise + Validação + Correções 3 camadas
- [ ] Integração: P8 → P9 funcionando
- [ ] Testes: Fluxo completo
- [ ] Deploy: Staging

### Sprint 10-11 (P7)
- [ ] Backend: Helena IA Relação
- [ ] Backend: Helena Consolidador + Estrategista
- [ ] Backend: PDF Generator (5 páginas)
- [ ] Frontend: Dashboard navegável
- [ ] Frontend: Export PDF
- [ ] Testes: Integração com todos produtos
- [ ] Deploy: Produção

### Sprint 12-13 (P9)
- [ ] Backend: Models Documento + Versão
- [ ] Backend: SEI processor
- [ ] Backend: Helena Redatora + Revisora
- [ ] Frontend: Wizard + Editor Markdown
- [ ] Frontend: Preview + Export PDF
- [ ] Integração: P9 ← P8
- [ ] Testes: 3 tipos de documento
- [ ] Deploy: Staging

### Sprint 14-15 (P10)
- [ ] Backend: Models Artefato + Versão + Problema
- [ ] Backend: PDF + DOCX processors
- [ ] Backend: Helena Analisadora (5D) + Otimizadora
- [ ] Frontend: Upload + Dashboard + Comparação
- [ ] Frontend: Feedback iterativo + Timeline
- [ ] Testes: Fluxo completo iterativo
- [ ] Deploy: Produção

---

## 🚨 RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Vertex AI instável** | Média | Alto | Fallback para OpenAI ou modelo local |
| **RAG lento (>5s)** | Média | Médio | Cache de embeddings + otimização chunks |
| **Celery falha** | Baixa | Médio | Monitoring + retry automático |
| **Usuários não adotam** | Média | Alto | Validação contínua + ajustes UX |
| **Dados insuficientes P1** | Alta | Médio | Criar POPs de exemplo + import histórico |
| **Time desbalanceado** | Média | Médio | Cross-training + pair programming |

---

## 📈 MÉTRICAS DE SUCESSO

### Por Produto

| Produto | Métrica de Sucesso | Meta |
|---------|-------------------|------|
| **P3** | % POPs com análise de oportunidades | >80% |
| **P4** | Usuários ativos mensais no dashboard | >50 |
| **P6** | Planos de ação criados | >20 |
| **P6** | Taxa de conclusão de ações | >60% |
| **P8** | Processos analisados | >30 |
| **P7** | Dossiês gerados | >10 |
| **P9** | Documentos gerados | >50 |
| **P10** | Artefatos otimizados | >20 |

### Globais

- **Tempo médio de resposta IA:** <5s (p95)
- **Uptime:** >99%
- **Bugs críticos:** <2 por sprint
- **Satisfação usuários:** >4/5
- **Adoção:** >70% dos usuários piloto usando regularmente

---

## 🎓 TREINAMENTO E DOCUMENTAÇÃO

### Semana 0 (Pré-Sprint 1)

- [ ] Kickoff com stakeholders
- [ ] Apresentação do roadmap
- [ ] Definição de usuários piloto
- [ ] Setup de ambientes (dev/staging/prod)
- [ ] Configuração de ferramentas (Jira, Git, CI/CD)

### Durante Implementação

- [ ] Demo ao final de cada sprint (para stakeholders)
- [ ] Documentação de API (Swagger/OpenAPI)
- [ ] Guias de usuário (screenshots + vídeos)
- [ ] Base de conhecimento (FAQ)

### Pós-Implementação

- [ ] Treinamento presencial (4h) para usuários piloto
- [ ] Vídeos tutoriais (1 por produto)
- [ ] Webinar de lançamento
- [ ] Suporte dedicado (primeiras 4 semanas)

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Semana Atual

1. **Aprovação do plano** ✅ (este documento)
2. **Montar time** (4 FTEs)
3. **Provisionar infraestrutura** (servidores, banco, Redis)
4. **Setup repositório** (Git, branches, CI/CD)
5. **Criar backlog detalhado** (Jira/Linear)

### Próxima Semana (Sprint 1 - Dia 1)

1. **Daily standup** (15min, todo dia 9h)
2. **Começar P3 - Oportunidades**
3. **Setup ChromaDB** para RAG
4. **Implementar primeiro model** (OportunidadeAnalise)
5. **Primeira chamada Vertex AI** (teste)

---

## 📞 CONTATOS E RESPONSABILIDADES

| Papel | Nome | Email | Responsabilidade |
|-------|------|-------|------------------|
| **Product Owner** | [Nome] | [email] | Decisões de produto, priorização |
| **Tech Lead** | [Nome] | [email] | Arquitetura, code review |
| **Backend Lead** | [Nome] | [email] | Django, APIs, IA |
| **Frontend Lead** | [Nome] | [email] | React, UX/UI |
| **DevOps** | [Nome] | [email] | Infra, deploy, monitoring |
| **QA Lead** | [Nome] | [email] | Testes, qualidade |

---

## 🏆 MARCOS (Milestones)

| Data | Marco | Entrega |
|------|-------|---------|
| **Semana 2** | P3 MVP | Primeira análise de oportunidades funcionando |
| **Semana 4** | P4 MVP | Dashboard básico com métricas |
| **Semana 7** | P6 MVP | Primeiro plano de ação criado |
| **Semana 9** | P8 MVP | Primeira análise de conformidade |
| **Semana 11** | P7 MVP | Primeiro dossiê gerado |
| **Semana 13** | P9 MVP | Primeiro documento oficial gerado |
| **Semana 15** | P10 MVP | Primeiro artefato otimizado |
| **Semana 16** | **🎉 GO-LIVE** | **Todos produtos em produção** |

---

**STATUS:** 🟢 **PLANO APROVADO E PRONTO PARA EXECUÇÃO**

**Próxima ação:** Iniciar Sprint 1 (P3 - Oportunidades)

---

**Última atualização:** 22 de Outubro de 2025
**Versão:** 1.0
