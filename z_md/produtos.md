# 🏗️ Framework de Desenvolvimento - MapaGov (9 Produtos)

## 📋 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────┐
│              HELENA-CORE (Orquestrador)             │
│         Roteia requisições para Helenas             │
│         especializadas (N helenas por produto)      │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┼─────────────────┐
        │         │         │       │
        ▼         ▼         ▼       ▼
   [Helena]  [Helena]  [Helena]  [Helena] ...
    Chat      Análise   Validação  Export
    P3.1      P3.2      P3.3       P3.4
    
Exemplo: P3 pode ter múltiplas Helenas:
- helena_oportunidades_chat.py    (conversa inicial)
- helena_oportunidades_analise.py (análise profunda)
- helena_oportunidades_validacao.py (valida achados)
- helena_oportunidades_export.py  (gera relatório)
```

---

## 🎯 P3 - Relatório de Oportunidades

### **Objetivo**
Helena identifica oportunidades de automação, redução burocrática, otimizações e treinamento fora do fluxo principal do processo.

### **Especificação Técnica**

#### **1. ENTRADA**
- **ID do POP** no banco de dados
- **Acionamento:**
  - Opção 1: Ao final do mapeamento (P1) - botão "Analisar Oportunidades"
  - Opção 2: Posterior - usuário insere CAP do processo no Dashboard

#### **2. DIVISÃO DE RESPONSABILIDADES**

**Helena Revisão (Vertex AI) - Durante Mapeamento (P1):**
- ✅ Gaps documentais
- ✅ Etapas faltantes
- ✅ Redundâncias no fluxo

**Helena Oportunidades (P3) - Análise Posterior:**
- ✅ **Automação** (RPA, bots, APIs)
- ✅ **Otimizações tempo/custo** (contato prévio se necessário)
- ✅ **Redução Burocrática** (ex: checklist preventivo para quem envia)
- ✅ **Treinamento** (oportunidades FORA do processo)

#### **3. ESCOPO DE ANÁLISE**

**3.1. Oportunidades de Automação**
```
IA identifica:
- Etapas manuais repetitivas
- Validações automatizáveis (CPF, CNPJ, APIs gov.br)
- Integrações possíveis (SIGEPE, SEI, SouGov)
- Notificações automáticas
- RPA para preenchimento de formulários
```

**3.2. Otimizações Tempo/Custo**
```
IA analisa:
- Etapas que podem ser paralelizadas
- Gargalos que aumentam prazo
- Necessidade de contato prévio com stakeholders
- Eliminação de etapas desnecessárias
- Consolidação de validações
```

**3.3. Redução Burocrática**
```
IA sugere:
- Checklist preventivo para solicitante
- Documentação única (evitar retrabalho)
- Validação na entrada (evitar devolução)
- Comunicação proativa de requisitos
- Templates preenchíveis
```

**3.4. Oportunidades de Treinamento**
```
IA identifica necessidades FORA do processo:
- Capacitação em sistemas específicos
- Treinamento normativo (LGPD, Lei 8.112)
- Workshop de boas práticas
- Reciclagem de procedimentos
- Onboarding para novos servidores
```

#### **4. FORMATO DE SAÍDA**

**Dashboard Interativo:**
```
┌─────────────────────────────────────────────────┐
│ RELATÓRIO DE OPORTUNIDADES - CAP [XXXX]        │
├─────────────────────────────────────────────────┤
│ Score Geral: 67/100 🟡                          │
│                                                 │
│ 📊 OPORTUNIDADES IDENTIFICADAS: 12              │
│ ├─ 🤖 Automação: 4                              │
│ ├─ ⚡ Otimização: 3                             │
│ ├─ 📋 Redução Burocrática: 3                    │
│ └─ 🎓 Treinamento: 2                            │
│                                                 │
│ 💰 ROI TOTAL ESTIMADO: 120 horas/mês           │
└─────────────────────────────────────────────────┘

[Card 1: Automação - Validação CPF/CNPJ]
├─ Impacto: Alto
├─ ROI: 40h/mês economizadas
├─ Custo: R$ 5.000
├─ Prazo implantação: 30 dias
└─ [Adicionar ao Plano de Ação]

[Card 2: Redução Burocrática - Checklist Preventivo]
├─ Impacto: Médio
├─ ROI: 15% redução devoluções
├─ Custo: R$ 0 (apenas template)
├─ Prazo: 7 dias
└─ [Adicionar ao Plano de Ação]

...
```

**Exportação PDF:**
- Botão "Gerar PDF Estruturado"
- Inclui todas as oportunidades detalhadas
- Seções por categoria
- ROI consolidado
- Roadmap de implementação

#### **5. SCORE E MÉTRICAS**

**Score de Maturidade (0-100):**
```python
score = (
    automacao_possivel * 0.3 +
    otimizacoes_identificadas * 0.3 +
    reducao_burocracia * 0.2 +
    treinamento_necessario * 0.2
)
```

**ROI por Oportunidade:**
- Economia de tempo (horas/mês)
- Redução de custos (R$)
- Redução de erros (%)
- Prazo de retorno (meses)

#### **6. INTEGRAÇÃO COM OUTROS PRODUTOS**

**Sistema de Numeração Incremental:**
```
CAP + [P2 ✅] + [P3 ✅] + [P5 ✅] + [P6 ⏳] + [P7 ⏳] + [P8 ⏳] + [P9 ⏳] + [P10 ⏳]

Exemplo:
12345 + [P2 ✅] + [P3 ✅] = Processo tem Fluxograma + Oportunidades
```

**Alimenta P6 (Plano de Ação):**
- Cada oportunidade pode virar ação no P6
- Botão "Adicionar ao Plano de Ação" em cada card
- Transferência automática de dados:
  - Título da ação
  - Responsável sugerido
  - Prazo estimado
  - Custo
  - ROI

**Compõe Dossiê Completo (P7):**
- P3 é uma seção obrigatória do dossiê
- Mostra indicador: `[P3 ✅]` no cabeçalho
- Timeline mostra quando P3 foi gerado

#### **7. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p3_oportunidades/
├── helena_analisadora.py      # Análise principal
├── helena_roi_calculator.py   # Calcula ROI
├── helena_priorizador.py      # Prioriza oportunidades
└── models.py                  # OportunidadeAnalise, Oportunidade

# APIs
POST /api/p3/analisar/{pop_id}/
GET  /api/p3/oportunidades/{pop_id}/
POST /api/p3/exportar-pdf/{pop_id}/
POST /api/p3/adicionar-ao-p6/  # Integração P6
```

**Frontend:**
```typescript
// pages/Oportunidades.tsx
interface Oportunidade {
  id: string;
  categoria: 'automacao' | 'otimizacao' | 'burocracia' | 'treinamento';
  titulo: string;
  descricao: string;
  impacto: 'alto' | 'medio' | 'baixo';
  roi_tempo: number; // horas/mês
  roi_custo: number; // R$
  custo_implantacao: number;
  prazo_implantacao: number; // dias
  prioridade: number;
  pode_adicionar_p6: boolean;
}
```

**Prompt IA (helena_analisadora.py):**
```python
OPORTUNIDADES_PROMPT = """
Você é consultora especializada em BPM e otimização de processos públicos.

Analise o POP abaixo e identifique SOMENTE:

1. AUTOMAÇÃO (RPA, bots, APIs)
   - Etapas manuais repetitivas
   - Integrações com sistemas gov.br
   - Validações automatizáveis

2. OTIMIZAÇÃO TEMPO/CUSTO
   - Paralelização de etapas
   - Gargalos críticos
   - Necessidade de contato prévio
   - Eliminação de redundâncias

3. REDUÇÃO BUROCRÁTICA
   - Checklist preventivo para solicitante
   - Validação na entrada
   - Comunicação proativa de requisitos

4. TREINAMENTO (FORA DO PROCESSO)
   - Capacitação em sistemas
   - Treinamento normativo
   - Workshops necessários

POP: {pop_data}

Para CADA oportunidade, calcule:
- Impacto: Alto/Médio/Baixo
- ROI tempo: horas economizadas/mês
- Custo implantação: R$
- Prazo: dias

Retorne JSON estruturado.
"""
```

#### **8. FLUXO COMPLETO**

```
1. Usuário aciona P3
   └─ Durante P1 (botão) OU posterior (CAP)

2. Backend busca POP pelo ID/CAP

3. Helena Analisadora processa

4. Helena ROI Calculator calcula métricas

5. Helena Priorizador ordena oportunidades

6. Frontend renderiza Dashboard interativo

7. Usuário pode:
   ├─ Exportar PDF
   ├─ Adicionar oportunidades ao P6
   └─ Marcar como "implementado"

8. Sistema registra [P3 ✅] no processo
```

---

## 🎯 P4 - Dashboard

### **Objetivo**
Painel executivo multinível com métricas e KPIs de governança, mostrando evolução do mapeamento e maturidade organizacional.

### **Especificação Técnica**

#### **1. HIERARQUIA DE VISUALIZAÇÃO**

**Seletor Multinível (Dropdown cascata):**
```
┌─────────────────────────────────────────┐
│ 📊 Visualização:                        │
│ ┌─────────────────────────────────────┐ │
│ │ 🏢 Diretoria (padrão inicial)       │ │
│ ├─────────────────────────────────────┤ │
│ │ 📁 Coordenação Geral                │ │
│ │   ├─ CGRIS                          │ │
│ │   ├─ CGCAF                          │ │
│ │   ├─ CGECO                          │ │
│ │   └─ ...                            │ │
│ ├─────────────────────────────────────┤ │
│ │ 📂 Coordenação (dentro da CG)       │ │
│ ├─────────────────────────────────────┤ │
│ │ 👤 Meus Processos (usuário logado)  │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Comportamento:**
- **Visão inicial:** Sempre DIRETORIA (visão macro)
- **Filtros dinâmicos:** Drill-down até nível de usuário
- **Permissões:** Baseadas no perfil (gestor vê mais)

#### **2. KPIs PRINCIPAIS**

**2.1. Total de Atividades Mapeadas por Macroprocesso**
```
┌─────────────────────────────────────────────────┐
│ ATIVIDADES MAPEADAS (Agrupado por Macro)       │
├─────────────────────────────────────────────────┤
│ 📊 Gráfico de Barras Horizontais:              │
│                                                 │
│ Gestão de Riscos        ████████████ 45        │
│ Gestão de Benefícios    ████████ 32            │
│ Gestão Cadastral        ██████ 28              │
│ Gestão Econômica        ████ 18                │
│                                                 │
│ TOTAL: 123 atividades                          │
└─────────────────────────────────────────────────┘
```

**2.2. POPs Criados vs Total Mapeado**
```
┌─────────────────────────────────────────────────┐
│ STATUS DO MAPEAMENTO                            │
├─────────────────────────────────────────────────┤
│ 📋 Total Atividades: 123                        │
│ ✅ POPs Concluídos:  87 (71%)                   │
│ 🔄 Em Andamento:     24 (19%)                   │
│ ⏳ Não Iniciados:    12 (10%)                   │
│                                                 │
│ [Gráfico Pizza ou Barras Empilhadas]           │
└─────────────────────────────────────────────────┘
```

**2.3. Evolução Mensal de Mapeamento**
```
┌─────────────────────────────────────────────────┐
│ EVOLUÇÃO MENSAL (Últimos 6 meses)              │
├─────────────────────────────────────────────────┤
│ Gráfico de Linha:                               │
│                                                 │
│ POPs  │                           ●             │
│  90   │                       ●                 │
│  75   │                   ●                     │
│  60   │               ●                         │
│  45   │           ●                             │
│  30   │       ●                                 │
│       └─────────────────────────────────────    │
│        Mai  Jun  Jul  Ago  Set  Out            │
│                                                 │
│ Taxa crescimento: +15% ao mês                   │
└─────────────────────────────────────────────────┘
```

**2.4. Nível de Maturidade da Governança**
```
┌─────────────────────────────────────────────────┐
│ MATURIDADE DE GOVERNANÇA                        │
├─────────────────────────────────────────────────┤
│ 🏢 DIRETORIA: Nível 3/5 (Gerenciado) - 67%     │
│    ████████████████░░░░░░░░                     │
│                                                 │
│ Por Coordenação Geral:                          │
│ • CGRIS:  Nível 4/5 (Otimizado) - 82% ✅       │
│ • CGCAF:  Nível 3/5 (Gerenciado) - 68% 🟡      │
│ • CGECO:  Nível 2/5 (Definido) - 45% 🟠        │
│                                                 │
│ [Dropdown para ver por área específica]        │
│                                                 │
│ Cálculo: (POP + P2 + P3 + P5 + P6 + P7 + P8 + P9 + P10) / 9
│ - Nível 1 (Inicial):    0-20%  produtos       │
│ - Nível 2 (Definido):   21-40% produtos       │
│ - Nível 3 (Gerenciado): 41-60% produtos       │
│ - Nível 4 (Otimizado):  61-80% produtos       │
│ - Nível 5 (Excelência): 81-100% produtos      │
└─────────────────────────────────────────────────┘
```

**2.5. Principais Riscos Mapeados**
```
┌─────────────────────────────────────────────────┐
│ RISCOS CRÍTICOS (Top 5)                         │
├─────────────────────────────────────────────────┤
│ 🔴 1. Ausência termo LGPD (CGCAF)              │
│        Impacto: Alto | 12 processos afetados    │
│        [Ver Detalhes] [Criar Plano Ação]       │
│                                                 │
│ 🔴 2. Base legal desatualizada (CGECO)         │
│        Impacto: Alto | 8 processos afetados     │
│        [Ver Detalhes]                           │
│                                                 │
│ 🟠 3. Falta segregação funções (CGRIS)         │
│        Impacto: Médio | 5 processos afetados    │
│        [Ver Detalhes]                           │
│                                                 │
│ [Filtro por Coordenação] [Ver Todos]           │
└─────────────────────────────────────────────────┘
```

**2.6. Andamento dos Planos de Ação**
```
┌─────────────────────────────────────────────────┐
│ PLANOS DE AÇÃO (P6)                             │
├─────────────────────────────────────────────────┤
│ Filtro: [Dropdown Cascata]                      │
│ 📊 Diretoria → CGRIS → Gestão Riscos → Ativ.1  │
│                                                 │
│ Status Geral:                                   │
│ ✅ Concluídas:    45 ações (35%)               │
│ 🔄 Em Andamento:  52 ações (40%)               │
│ ⏳ Pendentes:     32 ações (25%)               │
│                                                 │
│ [Gráfico Barras Empilhadas por Área]           │
│                                                 │
│ CGRIS:  ████████████░░░░░░░░ 60% concluído     │
│ CGCAF:  ██████████░░░░░░░░░░ 50% concluído     │
│ CGECO:  ████░░░░░░░░░░░░░░░░ 20% concluído     │
│                                                 │
│ ⚠️  Atrasadas: 8 ações (prazo vencido)         │
│ [Ver Detalhes]                                  │
└─────────────────────────────────────────────────┘
```

#### **3. VISUALIZAÇÃO DE PROCESSOS**

**Tabela Interativa com Badges:**
```
┌────────────────────────────────────────────────────────────────────┐
│ PROCESSOS MAPEADOS (Filtro: Diretoria)                            │
├─────┬────────────────────────┬─────────────────────────────────────┤
│ CAP │ Processo               │ Produtos                            │
├─────┼────────────────────────┼─────────────────────────────────────┤
│12345│ Conceder Ressarcimento │ [P2✅][P3✅][P5✅][P6🔄][P7⏳]...    │
│     │ CGRIS > Benefícios     │ Maturidade: 67% (Nível 3)           │
│     │                        │ [Ver Dossiê] [Adicionar Produto]    │
├─────┼────────────────────────┼─────────────────────────────────────┤
│12346│ Análise Conformidade   │ [P2✅][P3⏳][P5✅][P6⏳]...          │
│     │ CGCAF > Cadastro       │ Maturidade: 45% (Nível 2)           │
│     │                        │ [Continuar Mapeamento]              │
├─────┼────────────────────────┼─────────────────────────────────────┤
│12347│ Gestão Econômica       │ [P2✅][P3✅][P5✅][P6✅][P7✅]...    │
│     │ CGECO > Estudos        │ Maturidade: 89% (Nível 5) 🏆        │
│     │                        │ [Ver Dossiê Completo]               │
└─────┴────────────────────────┴─────────────────────────────────────┘

Legenda:
✅ Concluído | 🔄 Em andamento | ⏳ Não iniciado | 🏆 Excelência

[Filtros: Coordenação | Status | Maturidade]
[Exportar Lista CSV]
```

**Detalhamento ao clicar na linha:**
```
┌─────────────────────────────────────────────────┐
│ PROCESSO: Conceder Ressarcimento (CAP 12345)   │
├─────────────────────────────────────────────────┤
│ Área: CGRIS > Gestão de Benefícios             │
│ Responsável: João Silva                         │
│ Última atualização: 20/10/2025                  │
│                                                 │
│ PRODUTOS AGREGADOS:                             │
│ ✅ P2 - Fluxograma (15/09/2025)                │
│ ✅ P3 - Oportunidades (18/09/2025)             │
│ ✅ P5 - Riscos (22/09/2025) - 3 críticos       │
│ 🔄 P6 - Plano Ação (em andamento) - 60%        │
│ ⏳ P7 - Dossiê Gov (não iniciado)              │
│ ⏳ P8 - Conformidade (não iniciado)            │
│                                                 │
│ [Adicionar Produto] [Ver Histórico]            │
│ [Exportar Dossiê Parcial] [Notificar Gestor]  │
└─────────────────────────────────────────────────┘
```

#### **4. AÇÕES RÁPIDAS**

```
┌─────────────────────────────────────────────────┐
│ ⚡ AÇÕES RÁPIDAS                                │
├─────────────────────────────────────────────────┤
│ [+ Criar novo POP]          (P1)               │
│ [📊 Gerar Fluxograma]       (P2)               │
│ [💡 Analisar Oportunidades] (P3)               │
│ [⚠️  Analisar Riscos]        (P5)               │
│ [📁 Ver Dossiês Completos]  (filtro P2-P10 ✅) │
│ [📈 Relatório Executivo]    (PDF consolidado)  │
└─────────────────────────────────────────────────┘
```

#### **5. ATUALIZAÇÃO DE DADOS**

**Estratégia:**
- **Deploy noturno:** Atualização automática às 23h
- **Cache diário:** Dados atualizados 1x ao dia
- **Refresh manual:** Botão "Atualizar" (usuário pode forçar)
- **Indicador:** "Última atualização: 21/10/2025 23:00"

**Notificações (opcional):**
- Email diário para gestores com resumo
- Alerta de produtos concluídos
- Avisos de prazos vencendo (P6)

#### **6. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p4_dashboard/
├── helena_agregador.py        # Coleta dados de todos produtos
├── helena_metricas.py         # Calcula KPIs e maturidade
├── helena_evolutivo.py        # Análise temporal (evolução mensal)
└── models.py                  # DashboardCache, Metricas

# APIs
GET /api/p4/metricas/?nivel=diretoria
GET /api/p4/metricas/?nivel=cg&cg_id=CGRIS
GET /api/p4/metricas/?nivel=usuario&user_id=123
GET /api/p4/processos/?filtro=maturidade_alta
GET /api/p4/riscos-criticos/
GET /api/p4/planos-acao/status/
POST /api/p4/refresh-cache/   # Forçar atualização
```

**Frontend:**
```typescript
// pages/Dashboard.tsx
interface DashboardMetricas {
  nivel: 'diretoria' | 'cg' | 'coordenacao' | 'usuario';
  atividades_por_macro: {
    macroprocesso: string;
    total: number;
  }[];
  pops_stats: {
    total_atividades: number;
    pops_concluidos: number;
    em_andamento: number;
    nao_iniciados: number;
  };
  evolucao_mensal: {
    mes: string;
    total_pops: number;
  }[];
  maturidade: {
    nivel: number;  // 1-5
    percentual: number;  // 0-100
    por_area?: {
      area: string;
      nivel: number;
      percentual: number;
    }[];
  };
  riscos_criticos: Risco[];
  planos_acao_status: {
    concluidas: number;
    em_andamento: number;
    pendentes: number;
    atrasadas: number;
  };
}

interface ProcessoLinha {
  cap: string;
  titulo: string;
  area_hierarquica: string;  // "CGRIS > Benefícios"
  produtos: {
    p2: 'concluido' | 'andamento' | 'pendente';
    p3: 'concluido' | 'andamento' | 'pendente';
    // ... p5-p10
  };
  maturidade_percentual: number;
  maturidade_nivel: number;
}
```

**Cálculo de Maturidade:**
```python
def calcular_maturidade(processo):
    produtos_total = 9  # P2 até P10
    produtos_concluidos = sum([
        1 for p in [processo.p2, processo.p3, ..., processo.p10]
        if p.status == 'concluido'
    ])
    
    percentual = (produtos_concluidos / produtos_total) * 100
    
    if percentual >= 81:
        nivel = 5  # Excelência
    elif percentual >= 61:
        nivel = 4  # Otimizado
    elif percentual >= 41:
        nivel = 3  # Gerenciado
    elif percentual >= 21:
        nivel = 2  # Definido
    else:
        nivel = 1  # Inicial
    
    return {
        'percentual': percentual,
        'nivel': nivel,
        'label': NIVEIS[nivel]
    }
```

#### **7. FLUXO COMPLETO**

```
1. Usuário acessa Dashboard (P4)

2. Sistema carrega métricas (visão DIRETORIA)
   └─ Cache do deploy noturno

3. Renderiza KPIs principais:
   ├─ Atividades por macro
   ├─ POPs concluídos
   ├─ Evolução mensal
   ├─ Maturidade governança
   ├─ Riscos críticos
   └─ Planos de ação

4. Usuário pode:
   ├─ Filtrar por nível hierárquico
   ├─ Ver detalhes de processo
   ├─ Acessar ações rápidas
   ├─ Exportar relatórios
   └─ Forçar refresh

5. Sistema registra navegação (analytics)
```

---

## 🎯 P6 - Plano de Ação e Controles

### **Objetivo**
Gestão completa de ações: mitigação de riscos, implementação de oportunidades e planejamento estratégico (incluindo mobilização para mapeamento).

### **Especificação Técnica**

#### **1. ENTRADA DE DADOS (3 Modos)**

**Modo 1: Importar Riscos do P5**
```
Usuário em P5 (Análise de Riscos):
└─ Botão "Criar Plano de Ação"
   ├─ Importa automaticamente riscos identificados
   ├─ IA sugere controles para cada risco
   └─ Redireciona para P6 com dados pré-carregados
```

**Modo 2: Importar Oportunidades do P3**
```
Usuário em P3 (Oportunidades):
└─ Botão "Adicionar ao Plano de Ação" (por oportunidade)
   ├─ Importa descrição da oportunidade
   ├─ ROI e prazo estimado já calculados
   ├─ IA sugere responsáveis e recursos
   └─ Adiciona ao P6
```

**Modo 3: Criar "do Zero" via Chat**
```
Usuário acessa P6 diretamente:
└─ Chat com Helena Planejadora
   
   Helena: "Olá! Vamos criar um Plano de Ação. 
            Ele pode ser para:
            • Mitigar riscos identificados
            • Implementar oportunidades
            • Planejar iniciativas estratégicas
            
            Sobre o que você quer planejar?"
   
   Usuário: "Quero mobilizar minha equipe para mapear 
             todas as atividades da CGRIS nos próximos 3 meses"
   
   Helena: "Excelente! Vou te ajudar a estruturar isso.
            
            📋 Objetivo: Mapear atividades CGRIS
            📅 Prazo: 3 meses
            
            Algumas ações que identifiquei:
            
            1. Reunião de kickoff com equipe
               Prazo: Semana 1
               Responsável: [Sugestão: Coordenador]
            
            2. Levantamento de processos existentes
               Prazo: Semana 2-4
               Responsável: [Sugestão: Equipe técnica]
            
            3. Priorização de atividades para mapeamento
               Prazo: Semana 5
               ...
            
            Quer ajustar algo ou adicionar mais ações?"
```

**Casos de Uso Comuns (Modo 3):**
- Mobilizar equipe para mapeamento de processos (P1)
- Planejar implantação de sistema novo
- Estruturar projeto de conformidade
- Organizar treinamento de equipe
- Preparar auditoria externa
- Implementar melhorias organizacionais

#### **2. SUGESTÃO INTELIGENTE DE CONTROLES**

**IA Sugere Baseado em:**

**2.1. Para Riscos (do P5):**
```python
CONTROLES_POR_TIPO_RISCO = {
    'lgpd_dados_sensíveis': [
        {
            'tipo': 'preventivo',
            'controle': 'Criptografia AES-256 de dados em repouso',
            'custo_estimado': 'R$ 15.000',
            'prazo_implantacao': '45 dias',
            'responsavel_sugerido': 'TI / DPO'
        },
        {
            'tipo': 'detectivo',
            'controle': 'Logs de auditoria de acessos',
            'custo_estimado': 'R$ 5.000',
            'prazo_implantacao': '30 dias',
            'responsavel_sugerido': 'TI'
        },
        {
            'tipo': 'corretivo',
            'controle': 'Plano de resposta a incidentes LGPD',
            'custo_estimado': 'R$ 8.000',
            'prazo_implantacao': '60 dias',
            'responsavel_sugerido': 'DPO / Jurídico'
        }
    ],
    'conformidade_base_legal': [
        {
            'tipo': 'preventivo',
            'controle': 'Checklist de validação normativa',
            'custo_estimado': 'R$ 0',
            'prazo_implantacao': '7 dias',
            'responsavel_sugerido': 'Jurídico'
        }
    ],
    # ... outros tipos de risco
}
```

**2.2. Base de Conhecimento de Controles**

**Fontes de Aprendizado (Auto-Learning):**
```python
BASE_CONTROLES = {
    'pops_existentes': 'Controles já implementados em outros POPs',
    'planos_anteriores': 'Ações bem-sucedidas de planos anteriores',
    'normas_rag': 'Bucket de normas e boas práticas',
    'feedback_usuarios': 'Controles validados/rejeitados por usuários'
}

# Sistema aprende com:
1. Controles que foram eficazes (marcados como "sucesso")
2. Tempo real de implementação vs estimado
3. ROI alcançado vs planejado
4. Frequência de uso de controles específicos
5. Feedback direto dos usuários (👍 👎)
```

**Bucket de Normas e Boas Práticas (RAG Dedicado):**
```
📂 chroma_db_controles/
├── COSO (Framework de Controle Interno)
├── ISO 31000 (Gestão de Riscos)
├── ISO 27001 (Segurança da Informação)
├── Acórdãos TCU (Recomendações de controle)
├── Normas CGU (Controle interno)
├── LGPD - Guia ANPD (Controles de dados)
├── Cobit 2019 (Governança de TI)
├── PMBOK (Gestão de projetos)
└── Melhores práticas setor público brasileiro
```

**Prompt com Auto-Learning:**
```python
CONTROLES_PROMPT_AUTO_LEARNING = """
Você é especialista em controles internos e gestão de riscos.

Sugira controles baseado em:

1. NORMAS E FRAMEWORKS (RAG):
   {bucket_normas_resultados}

2. CONTROLES DE POPS SIMILARES:
   {controles_de_pops_similares}

3. PLANOS DE AÇÃO BEM-SUCEDIDOS:
   {acoes_eficazes_historico}

4. APRENDIZADO DE FEEDBACK:
   Controles com alta taxa de sucesso: {controles_aprovados}
   Evitar controles com baixa eficácia: {controles_rejeitados}

Risco a mitigar:
{risco_descricao}

Retorne 3-5 controles (preventivo, detectivo, corretivo).
"""
```
```python
ACOES_POR_TIPO_OPORTUNIDADE = {
    'automacao_validacao': [
        {
            'acao': 'Contratar integração API ReceitaFederal',
            'custo': 'R$ 5.000',
            'prazo': '30 dias',
            'roi': '8.3 horas/mês economizadas',
            'responsavel_sugerido': 'TI'
        },
        {
            'acao': 'Desenvolver script de validação',
            'custo': 'R$ 2.000',
            'prazo': '15 dias',
            'responsavel_sugerido': 'Desenvolvedor'
        }
    ],
    'reducao_burocracia': [
        {
            'acao': 'Criar checklist preventivo',
            'custo': 'R$ 0',
            'prazo': '7 dias',
            'roi': '15% redução devoluções',
            'responsavel_sugerido': 'Analista'
        }
    ]
}
```

**2.3. Para Planejamento Estratégico (Chat):**
```python
TEMPLATES_PLANEJAMENTO = {
    'mapeamento_processos': [
        'Reunião de kickoff',
        'Levantamento de processos',
        'Priorização de atividades',
        'Treinamento em P1 (Helena)',
        'Execução de mapeamento',
        'Revisão e validação',
        'Publicação dos POPs'
    ],
    'implantacao_sistema': [
        'Análise de requisitos',
        'Homologação',
        'Treinamento de usuários',
        'Go-live',
        'Suporte pós-implantação'
    ],
    'preparacao_auditoria': [
        'Levantamento de documentação',
        'Identificação de gaps',
        'Adequação de processos',
        'Simulação de auditoria',
        'Ajustes finais'
    ]
}
```

**RAG para Controles:**
- Base de conhecimento com controles COSO, ISO 31000
- Acórdãos TCU com recomendações
- Normas CGU de controle interno
- Melhores práticas LGPD (ANPD)

#### **3. ESTRUTURA DO PLANO**

**Visualização Dual (Usuário escolhe):**

**3.1. Formato 5W2H (Tabela Estruturada)**
```
┌────────────────────────────────────────────────────────────────────────────┐
│ PLANO DE AÇÃO: Mobilização para Mapeamento CGRIS                          │
├────┬────────────┬───────┬────────┬──────────┬────────────┬─────┬──────────┤
│What│Why         │Where  │When    │Who       │How         │How  │Status    │
│O QUE│POR QUE    │ONDE   │QUANDO  │QUEM      │COMO        │Custo│          │
├────┼────────────┼───────┼────────┼──────────┼────────────┼─────┼──────────┤
│Kick│Alinhar     │Sala   │05/11   │João Silva│Apresentação│R$   │⏳        │
│off │objetivos   │reunião│        │(Coord)   │projeto     │0    │Pendente  │
├────┼────────────┼───────┼────────┼──────────┼────────────┼─────┼──────────┤
│Lev │Identificar │CGRIS  │06-20/11│Maria     │Entrevistas │R$   │⏳        │
│proc│processos   │       │        │Santos    │+ docs      │0    │Pendente  │
│    │críticos    │       │        │(Analista)│            │     │          │
├────┼────────────┼───────┼────────┼──────────┼────────────┼─────┼──────────┤
│Trei│Capacitar   │Online │21/11   │Equipe TI │Workshop    │R$   │⏳        │
│P1  │equipe      │       │        │          │Helena      │3.000│Pendente  │
├────┼────────────┼───────┼────────┼──────────┼────────────┼─────┼──────────┤
│Map │Documentar  │CGRIS  │22/11-  │Toda      │Chat Helena │R$   │⏳        │
│POPs│45 ativ.    │       │31/01   │equipe    │+ P1        │0    │Pendente  │
└────┴────────────┴───────┴────────┴──────────┴────────────┴─────┴──────────┘

RESUMO:
• Total de ações: 4
• Prazo total: 3 meses
• Custo total: R$ 3.000
• ROI esperado: 45 atividades mapeadas
```

**3.2. Kanban Interativo (Arrastar e Soltar)**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 📋 BACKLOG  │ 🔄 FAZENDO  │ ✅ REVISÃO  │ ✔️ CONCLUÍDO│
├─────────────┼─────────────┼─────────────┼─────────────┤
│ ┌─────────┐ │ ┌─────────┐ │             │             │
│ │ Kickoff │ │ │Levant.  │ │             │             │
│ │ 05/11   │ │ │Processos│ │             │             │
│ │ João    │ │ │         │ │             │             │
│ │ [...]   │ │ │ Maria   │ │             │             │
│ └─────────┘ │ │ 80% ████│ │             │             │
│             │ └─────────┘ │             │             │
│ ┌─────────┐ │             │             │             │
│ │Treino P1│ │             │             │             │
│ │ 21/11   │ │             │             │             │
│ │ [...]   │ │             │             │             │
│ └─────────┘ │             │             │             │
│             │             │             │             │
│ ┌─────────┐ │             │             │             │
│ │Map POPs │ │             │             │             │
│ │ 22/11-  │ │             │             │             │
│ │ 31/01   │ │             │             │             │
│ └─────────┘ │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘

[+ Nova Ação] [Filtrar por Responsável] [Ver Linha do Tempo]
```

**Recursos do Kanban:**
- Arrastar cards entre colunas
- Barra de progresso por card
- Indicador visual de prazo (🔴 atrasado, 🟡 próximo, 🟢 no prazo)
- Comentários por ação
- Anexar arquivos
- Atribuir múltiplos responsáveis

#### **4. ACOMPANHAMENTO E ALERTAS**

**4.1. Alertas Automáticos + Cadastro de Usuários:**

**Sistema de Cadastro:**
```python
class Usuario(models.Model):
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)  # Hash bcrypt
    
    # Hierarquia organizacional
    coordenacao_geral = models.CharField(max_length=50)  # CGRIS, CGCAF, etc
    coordenacao = models.CharField(max_length=100, null=True)
    cargo = models.CharField(max_length=100)
    
    # Preferências de notificação
    notificar_email = models.BooleanField(default=True)
    notificar_sms = models.BooleanField(default=False)
    
    # Controle de acesso
    perfil = models.CharField(
        choices=[
            ('servidor', 'Servidor'),
            ('analista', 'Analista'),
            ('coordenador', 'Coordenador'),
            ('gestor_cg', 'Gestor CG'),
            ('diretor', 'Diretor')
        ]
    )
```

**Alertas Expandidos:**
```python
ALERTAS_COMPLETOS = {
    '7_dias_antes_prazo': {
        'destinatarios': ['responsavel', 'email_coordenacao_geral'],
        'mensagem': 'Ação "{titulo}" vence em 7 dias',
        'canal': ['email', 'notificacao_sistema']
    },
    
    'prazo_vencido': {
        'destinatarios': ['responsavel', 'coordenador', 'email_coordenacao_geral'],
        'mensagem': '⚠️ Ação "{titulo}" está ATRASADA',
        'canal': ['email', 'notificacao_sistema'],
        'frequencia': 'diaria_ate_conclusao'
    },
    
    'inatividade_7_dias': {
        'trigger': 'Nenhuma atualização em 7 dias',
        'destinatarios': ['responsavel', 'coordenador'],
        'mensagem': '⚠️ Plano "{titulo}" sem atualizações há 7 dias',
        'canal': ['email']
    },
    
    'inatividade_15_dias': {
        'trigger': 'Nenhuma atualização em 15 dias',
        'destinatarios': ['responsavel', 'coordenador', 'gestor_cg'],
        'mensagem': '🔴 CRÍTICO: Plano "{titulo}" sem atualizações há 15 dias',
        'canal': ['email', 'notificacao_sistema']
    },
    
    'acao_concluida': {
        'destinatarios': ['coordenador', 'email_coordenacao_geral'],
        'mensagem': '✅ Ação "{titulo}" foi concluída por {responsavel}',
        'canal': ['email'],
        'acao_automatica': 'Agendar revisão em 2 anos'
    },
    
    'plano_100_concluido': {
        'trigger': 'Todas ações concluídas',
        'destinatarios': ['coordenador', 'gestor_cg', 'equipe'],
        'mensagem': '🎉 Plano "{titulo}" 100% concluído!',
        'canal': ['email', 'notificacao_sistema'],
        'acao_automatica': 'Solicitar feedback de eficácia'
    }
}
```

**Email da Coordenação Geral:**
```python
# Cada CG tem email coletivo
EMAILS_CG = {
    'CGRIS': 'cgris@exemplo.gov.br',
    'CGCAF': 'cgcaf@exemplo.gov.br',
    'CGECO': 'cgeco@exemplo.gov.br',
    # ...
}

# Todos alertas importantes vão para:
# 1. Responsável direto
# 2. Coordenador imediato
# 3. Email coletivo da CG (visibilidade ampla)
```
```python
ALERTAS = {
    '7_dias_antes_prazo': {
        'destinatarios': ['responsavel', 'coordenador'],
        'mensagem': 'Ação "{titulo}" vence em 7 dias',
        'canal': ['email', 'notificacao_sistema']
    },
    '1_dia_antes_prazo': {
        'destinatarios': ['responsavel'],
        'mensagem': 'URGENTE: Ação "{titulo}" vence amanhã',
        'canal': ['email', 'sms', 'notificacao_sistema']
    },
    'prazo_vencido': {
        'destinatarios': ['responsavel', 'coordenador', 'gestor'],
        'mensagem': '⚠️ Ação "{titulo}" está ATRASADA',
        'canal': ['email', 'notificacao_sistema'],
        'frequencia': 'diaria_ate_conclusao'
    },
    'acao_concluida': {
        'destinatarios': ['coordenador'],
        'mensagem': '✅ Ação "{titulo}" foi concluída por {responsavel}',
        'canal': ['email']
    }
}
```

**4.2. Dashboard de Progresso (Integrado ao P4)**
```
┌─────────────────────────────────────────────────┐
│ PLANOS DE AÇÃO - CGRIS                          │
├─────────────────────────────────────────────────┤
│ Plano 1: Mobilização Mapeamento                │
│ Progresso: ████████░░░░░░░░ 50% (2/4 ações)    │
│ Prazo: 31/01/2026 | Status: 🟢 No prazo        │
│                                                 │
│ Plano 2: Implementar LGPD                      │
│ Progresso: ██████░░░░░░░░░░ 30% (3/10 ações)   │
│ Prazo: 15/12/2025 | Status: 🟡 Atenção         │
│                                                 │
│ Plano 3: Automação Validações                  │
│ Progresso: ████████████████ 100% (5/5 ações)   │
│ Prazo: 30/10/2025 | Status: ✅ Concluído       │
└─────────────────────────────────────────────────┘
```

**4.3. Registro de Conclusão + Obrigação de Revisão:**
```
Quando ação é marcada como "Concluída":

1. Sistema solicita:
   ├─ Data de conclusão (auto: hoje)
   ├─ Comentário (opcional)
   ├─ Anexar evidências (opcional)
   ├─ Validação: "Objetivo foi alcançado?" (sim/não)
   └─ Feedback: "Controle foi eficaz?" (👍 útil / 👎 não útil)

2. Sistema registra:
   ├─ Timestamp exato
   ├─ Usuário que marcou (CPF + nome)
   ├─ Tempo total (planejado vs real)
   ├─ Atualiza [P6 ✅] no processo
   └─ Feedback para auto-learning

3. Sistema notifica:
   ├─ Coordenador
   ├─ Email da CG
   └─ Stakeholders relacionados

4. ⭐ AGENDA REVISÃO AUTOMÁTICA EM 2 ANOS:
   ├─ Cria tarefa: "Revisar eficácia do controle [X]"
   ├─ Data: +730 dias da conclusão
   ├─ Responsável: Mesmo da ação original
   ├─ Tipo: 'revisao_periodica'
   └─ Notificação: 30 dias antes da revisão

5. Auto-Learning (Background):
   ├─ Se feedback 👍: Aumenta score do controle no RAG
   ├─ Se feedback 👎: Diminui prioridade nas sugestões
   └─ Armazena métricas de eficácia
```

**Modelo de Revisão Periódica:**
```python
class RevisaoPeriodica(models.Model):
    acao_original = models.ForeignKey(Acao)
    data_agendada = models.DateField()  # +2 anos
    status = models.CharField(
        choices=[
            ('pendente', 'Aguardando revisão'),
            ('em_analise', 'Em análise'),
            ('concluida', 'Revisão concluída'),
            ('prorrogada', 'Prorrogada')
        ]
    )
    resultado_revisao = models.TextField(null=True)
    controle_ainda_eficaz = models.BooleanField(null=True)
    ajustes_necessarios = models.TextField(null=True)
    
    # Notificações automáticas
    notificacao_30_dias = models.BooleanField(default=False)
    notificacao_7_dias = models.BooleanField(default=False)
    
    def enviar_alerta_revisao(self):
        """Enviado 30 dias antes da data agendada"""
        email = f"""
        🔔 REVISÃO PERIÓDICA AGENDADA
        
        Ação: {self.acao_original.what}
        Implementada em: {self.acao_original.data_conclusao}
        Revisão agendada: {self.data_agendada}
        
        É necessário avaliar se o controle continua eficaz.
        
        [Iniciar Revisão] [Prorrogar]
        """
```
```
Quando ação é marcada como "Concluída":
1. Sistema solicita:
   ├─ Data de conclusão (auto: hoje)
   ├─ Comentário (opcional)
   ├─ Anexar evidências (opcional)
   └─ Validação: "Objetivo foi alcançado?" (sim/não)

2. Sistema registra:
   ├─ Timestamp exato
   ├─ Usuário que marcou
   ├─ Tempo total (planejado vs real)
   └─ Atualiza [P6 ✅] no processo

3. Sistema notifica:
   ├─ Coordenador
   └─ Stakeholders relacionados
```

#### **5. INTEGRAÇÃO COM OUTROS PRODUTOS**

**5.1. P6 → P4 (Dashboard)**
```
Dashboard mostra:
• Total de planos ativos
• Ações atrasadas (alerta vermelho)
• Taxa de conclusão (%)
• Próximos vencimentos (7 dias)
```

**5.2. P6 → P7 (Dossiê de Governança)**
```
Dossiê inclui seção:
"PLANOS DE AÇÃO E CONTROLES"
├─ Resumo executivo
├─ Principais ações implementadas
├─ Status de controles de risco
├─ ROI alcançado vs planejado
└─ Roadmap de ações futuras
```

**5.3. P6 ← P5 (Riscos)**
```
Importação automática:
Risco Alto → Ação obrigatória no P6
Risco Médio → Ação sugerida no P6
Risco Baixo → Ação opcional no P6
```

**5.4. P6 ← P3 (Oportunidades)**
```
Importação seletiva:
Usuário escolhe quais oportunidades viram ações
Dados já vêm com ROI calculado
```

**5.5. Notificações por Email:**
```
Template:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 MapaGov - Alerta de Plano de Ação

Olá, João Silva

A ação "Kickoff Mapeamento CGRIS" 
vence em 7 dias (05/11/2025).

Status atual: Pendente
Responsável: Você

[Marcar como Concluída] [Ver Plano Completo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### **6. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p6_plano_acao/
├── helena_planejadora.py      # Chat para criar plano do zero
├── helena_importadora.py      # Importa de P3/P5
├── helena_sugestao.py         # Sugere controles/ações
├── helena_priorizacao.py      # Prioriza ações
├── scheduler.py               # Alertas automáticos (Celery)
└── models.py                  # PlanoAcao, Acao, Alerta

# Models
class PlanoAcao(models.Model):
    titulo = models.CharField(max_length=200)
    objetivo = models.TextField()
    processo = models.ForeignKey(POP, null=True)  # Pode ser null
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
    what = models.CharField(max_length=200)  # O que
    why = models.TextField()  # Por que
    where = models.CharField(max_length=100)  # Onde
    when = models.DateField()  # Quando
    who = models.ForeignKey(User)  # Quem
    how = models.TextField()  # Como
    how_much = models.DecimalField()  # Quanto custa
    # Controle
    status = models.CharField(
        choices=[
            ('backlog', 'Backlog'),
            ('fazendo', 'Em andamento'),
            ('revisao', 'Em revisão'),
            ('concluido', 'Concluído')
        ]
    )
    data_conclusao = models.DateTimeField(null=True)
    evidencias = models.JSONField(default=list)  # URLs de arquivos

# APIs
POST /api/p6/criar-do-zero/         # Via chat
POST /api/p6/importar-riscos/{p5_id}/
POST /api/p6/importar-oportunidade/{oportunidade_id}/
GET  /api/p6/planos/?usuario={id}
PATCH /api/p6/acao/{id}/status/     # Mover no Kanban
POST /api/p6/acao/{id}/concluir/
GET  /api/p6/alertas/pendentes/
```

**Frontend:**
```typescript
// pages/PlanoAcao.tsx
interface PlanoAcaoForm {
  modo: 'importar_risco' | 'importar_oportunidade' | 'criar_zero';
  titulo: string;
  objetivo: string;
  tipo: 'risco' | 'oportunidade' | 'estrategico';
  acoes: Acao5W2H[];
  prazo_final: Date;
}

interface Acao5W2H {
  what: string;
  why: string;
  where: string;
  when: Date;
  who: string;
  how: string;
  how_much: number;
  status: 'backlog' | 'fazendo' | 'revisao' | 'concluido';
  prioridade: 'alta' | 'media' | 'baixa';
}

// Componentes
<PlanoAcaoCreator modo={modo} />
<TabelaW2H plano={plano} />
<KanbanBoard plano={plano} onMoveCard={handleMove} />
<AlertasPanel />
```

#### **7. FLUXO COMPLETO**

**Fluxo 1: Importar de P5 (Riscos)**
```
1. Usuário em P5 vê riscos críticos
2. Clica "Criar Plano de Ação"
3. Sistema cria plano automaticamente
   ├─ Título: "Mitigação de Riscos - [Processo]"
   ├─ Tipo: 'risco'
   └─ Ações sugeridas pela IA (controles)
4. Usuário customiza responsáveis/prazos
5. Salva plano
6. Sistema marca [P6 🔄] no processo
7. Alertas são agendados
```

**Fluxo 2: Criar do Zero via Chat**
```
1. Usuário acessa P6 direto
2. Seleciona "Criar Plano Estratégico"
3. Chat com Helena Planejadora:
   Helena: "Sobre o que quer planejar?"
   Usuário: "Mapear CGRIS em 3 meses"
   Helena: "Identifiquei 7 ações. Quer ver?"
4. Usuário revisa/ajusta sugestões
5. Escolhe visualização (5W2H ou Kanban)
6. Salva plano
7. Sistema notifica equipe
```

**Fluxo 3: Acompanhamento Diário**
```
1. Sistema roda job noturno (Celery)
2. Verifica prazos próximos/vencidos
3. Envia alertas por email
4. Atualiza dashboard (P4)
5. Gestor acessa P4 e vê ações atrasadas
6. Clica para ver detalhes no P6
7. Marca ação como concluída
8. Sistema registra e notifica equipe
```

---

## 🎯 P7 - Dossiê de Governança (Visão 360°)

### **Objetivo**
Consolidação executiva de todos os produtos (P2-P10) de uma atividade ou múltiplas atividades relacionadas.

### **Especificação Técnica**

#### **1. AGREGAÇÃO AUTOMÁTICA**

**Escopo: UMA Atividade (Dossiê Individual)**
```
Usuário seleciona: CAP_12345 (Conceder Ressarcimento)

Sistema agrega AUTOMATICAMENTE:
├─ [P2 ✅] Fluxograma
├─ [P3 ✅] Oportunidades
├─ [P5 ✅] Riscos
├─ [P6 ✅] Plano de Ação
├─ [P8 ✅] Conformidade
├─ [P9 ⏳] Documentos (se houver)
└─ [P10 ⏳] Artefatos (se houver)

Gera: Dossiê Completo da Atividade
```

**Escopo: MÚLTIPLAS Atividades (Dossiê Consolidado)**
```
Seleção por Área:
Usuário escolhe: CGRIS (Coordenação Geral)

Sistema:
1. Lista todas atividades da CGRIS
2. IA identifica atividades relacionadas:
   "Conceder Ressarcimento" → relaciona com →
   "Analisar Elegibilidade Ressarcimento" →
   "Processar Pagamento Ressarcimento"
   
3. Usuário confirma/ajusta seleção

4. Sistema agrega dados de TODAS atividades selecionadas

Gera: Dossiê Consolidado da Área
```

#### **2. IA IDENTIFICA PROCESSOS RELACIONADOS**

**Critérios de Relacionamento:**
```python
def identificar_processos_relacionados(atividade_base):
    """
    IA usa múltiplos critérios para identificar relações
    """
    
    criterios = {
        'hierarquia': [
            'Mesmo macroprocesso',
            'Mesmo processo',
            'Mesmo subprocesso'
        ],
        'fluxo': [
            'Etapas sequenciais (A → B → C)',
            'Inputs/Outputs compartilhados',
            'Sistemas comuns'
        ],
        'semântico': [
            'Similaridade de texto (embeddings)',
            'Palavras-chave comuns',
            'Objetivos correlatos'
        ],
        'dados': [
            'Dados pessoais tratados em comum',
            'Responsáveis compartilhados',
            'Base legal similar'
        ]
    }
    
    # IA analisa e retorna score de relacionamento
    return processos_relacionados_com_score
```

**Exemplo de Saída da IA:**
```
Processo Base: "Conceder Ressarcimento" (CAP 12345)

RELACIONADOS IDENTIFICADOS:
┌─────────────────────────────────────────────┬──────┐
│ Processo                                    │Score │
├─────────────────────────────────────────────┼──────┤
│ Analisar Elegibilidade Ressarcimento        │ 95%  │
│ └─ Justificativa: Etapa anterior, dados... │      │
├─────────────────────────────────────────────┼──────┤
│ Processar Pagamento Ressarcimento           │ 92%  │
│ └─ Justificativa: Etapa posterior...       │      │
├─────────────────────────────────────────────┼──────┤
│ Atualizar Cadastro Beneficiário            │ 78%  │
│ └─ Justificativa: Sistema comum (SIGEPE)   │      │
├─────────────────────────────────────────────┼──────┤
│ Auditar Pagamentos                          │ 65%  │
│ └─ Justificativa: Controle do processo     │      │
└─────────────────────────────────────────────┴──────┘

[Selecionar Todos] [Customizar Seleção] [Gerar Dossiê]
```

#### **3. FORMATO DE SAÍDA**

**3.1. PDF Executivo (~5 páginas)**

```
┌─────────────────────────────────────────────┐
│          DOSSIÊ DE GOVERNANÇA               │
│     CGRIS - Gestão de Benefícios           │
├─────────────────────────────────────────────┤
│                                             │
│ CAPA                                        │
│ • Logo gov.br                               │
│ • Título da área/processo                   │
│ • Data de emissão                           │
│ • Classificação: Executivo                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PÁGINA 1: EXECUTIVE SUMMARY                 │
├─────────────────────────────────────────────┤
│ Resumo Executivo (300-400 palavras)        │
│                                             │
│ • Escopo: 5 atividades mapeadas            │
│ • Maturidade Geral: 78% (Nível 4)          │
│ • Principais Conquistas:                    │
│   - 100% processos com fluxograma          │
│   - 87% com análise de riscos              │
│ • Desafios Principais:                      │
│   - 3 riscos críticos LGPD                 │
│   - 40% planos de ação em atraso           │
│ • Recomendações Estratégicas (Top 3)       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PÁGINA 2: VISÃO GERAL DOS PROCESSOS         │
├─────────────────────────────────────────────┤
│ [Diagrama de Relacionamento]                │
│                                             │
│    ┌─────────┐                              │
│    │ Analisar│──┐                           │
│    │Elegibil.│  │                           │
│    └─────────┘  │                           │
│                 ▼                           │
│           ┌──────────┐                      │
│           │ Conceder │                      │
│           │Ressarcim.│                      │
│           └──────────┘                      │
│                 │                           │
│                 ▼                           │
│           ┌──────────┐                      │
│           │Processar │                      │
│           │Pagamento │                      │
│           └──────────┘                      │
│                                             │
│ Tabela Resumo:                              │
│ CAP   │ Atividade        │ Maturidade       │
│ 12345 │ Conceder Ressarc.│ 89% (Nível 5) ✅ │
│ 12346 │ Analisar Eligib. │ 67% (Nível 3) 🟡 │
│ ...                                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PÁGINA 3: MAPA DE RISCOS E CONTROLES        │
├─────────────────────────────────────────────┤
│ [Heatmap Consolidado]                       │
│                                             │
│ Riscos Críticos (Top 5):                    │
│ 🔴 Ausência termo LGPD (3 processos)        │
│ 🔴 Base legal desatualizada (2 processos)   │
│ 🟠 Segregação de funções (4 processos)      │
│                                             │
│ Status dos Controles:                       │
│ • Implementados: 65%                        │
│ • Em andamento: 25%                         │
│ • Pendentes: 10%                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PÁGINA 4: OPORTUNIDADES E PLANOS DE AÇÃO    │
├─────────────────────────────────────────────┤
│ Principais Oportunidades Identificadas:     │
│                                             │
│ 💡 Automação validação CPF/CNPJ             │
│    ROI: 40h/mês | Custo: R$ 5k             │
│                                             │
│ 💡 Checklist preventivo                     │
│    ROI: 15% redução devoluções              │
│                                             │
│ Status Planos de Ação:                      │
│ ████████████░░░░░░░░ 60% concluído          │
│                                             │
│ • 18 ações concluídas                       │
│ • 12 em andamento                           │
│ • 3 atrasadas ⚠️                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PÁGINA 5: ROADMAP ESTRATÉGICO               │
├─────────────────────────────────────────────┤
│ Próximos 6 Meses:                           │
│                                             │
│ Nov/25 │ Dez/25 │ Jan/26 │ Fev/26          │
│ LGPD   │ Automaç│ Integr │ Audit.          │
│ Termos │ ão     │ APIs   │ Interna         │
│                                             │
│ Metas de Maturidade:                        │
│ • Atual: 78%                                │
│ • Meta 6 meses: 85%                         │
│ • Meta 12 meses: 92% (Excelência)           │
│                                             │
│ Indicadores de Sucesso:                     │
│ • 100% processos conformes LGPD             │
│ • 0 riscos críticos remanescentes           │
│ • 90%+ ações planos concluídas              │
└─────────────────────────────────────────────┘
```

**3.2. Dashboard Navegável Interativo**

```
┌─────────────────────────────────────────────────────┐
│ 📊 DOSSIÊ DE GOVERNANÇA - CGRIS                     │
│ [Filtro: Área ▼] [Macroprocesso ▼] [Atividade ▼]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 🏢 NÍVEL: COORDENAÇÃO GERAL (CGRIS)                 │
│                                                     │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│ │ Maturidade  │  │ Riscos      │  │ Planos Ação │ │
│ │    78%      │  │ 5 críticos  │  │ 60% concl.  │ │
│ │ Nível 4/5   │  │ 12 médios   │  │ 3 atrasadas │ │
│ └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│ [Gráfico Pizza: Distribuição Maturidade]           │
│ [Gráfico Barras: Produtos por Atividade]           │
│                                                     │
│ ↓ Drill-down disponível                            │
└─────────────────────────────────────────────────────┘

# Usuário clica em "Gestão de Benefícios" (Macroprocesso)

┌─────────────────────────────────────────────────────┐
│ 📊 DOSSIÊ - CGRIS > Gestão de Benefícios           │
├─────────────────────────────────────────────────────┤
│ Atividades: 5                                       │
│ Maturidade Média: 82%                               │
│                                                     │
│ LISTA DE ATIVIDADES:                                │
│ ┌─────────────────────────────────────────────────┐│
│ │ CAP 12345 | Conceder Ressarcimento              ││
│ │ [P2✅][P3✅][P5✅][P6✅][P8✅][P9✅][P10✅]        ││
│ │ Maturidade: 89% (Nível 5) 🏆                     ││
│ │ [Ver Detalhes] [Exportar Individual]            ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ ↓ Drill-down para atividade específica             │
└─────────────────────────────────────────────────────┘

# Usuário clica em atividade específica

┌─────────────────────────────────────────────────────┐
│ 📋 DOSSIÊ - Conceder Ressarcimento (CAP 12345)     │
├─────────────────────────────────────────────────────┤
│ PRODUTOS AGREGADOS:                                 │
│                                                     │
│ [Abas]                                              │
│ • Visão Geral                                       │
│ • Fluxograma (P2)                                   │
│ • Oportunidades (P3)                                │
│ • Riscos (P5)                                       │
│ • Plano de Ação (P6)                                │
│ • Conformidade (P8)                                 │
│                                                     │
│ [Conteúdo da aba selecionada renderiza aqui]       │
│                                                     │
│ [Exportar Dossiê Individual PDF] [Compartilhar]    │
└─────────────────────────────────────────────────────┘
```

#### **4. PÚBLICO-ALVO: ALTA GESTÃO**

**Linguagem Executiva:**
```
❌ EVITAR (Técnico demais):
"O processo apresenta não conformidade com o Art. 46, §1º, 
inciso III da Lei 13.709/2018 relativo à implementação de 
medidas técnicas e administrativas..."

✅ USAR (Executivo):
"Processo não está adequado à LGPD. Recomenda-se 
implementar termo de consentimento para tratamento de 
dados pessoais. Custo: R$ 5k | Prazo: 30 dias"
```

**Estrutura Executiva:**
- Bullet points ao invés de parágrafos longos
- Gráficos visuais ao invés de tabelas densas
- Semáforos visuais (🔴🟡🟢) ao invés de scores numéricos
- Recomendações acionáveis ao invés de análises detalhadas
- Resumo de 1 página + detalhamento opcional

#### **5. GERAÇÃO AUTOMÁTICA**

**Fluxo:**
```
1. Usuário acessa P7

2. Seleciona escopo:
   ├─ UMA atividade (CAP)
   └─ ÁREA (CGRIS, CGCAF, etc)

3. Se área selecionada:
   └─ IA identifica processos relacionados
   └─ Usuário confirma seleção

4. Helena Consolidadora executa:
   ├─ Coleta dados de P2-P10 de cada atividade
   ├─ Agrega métricas (maturidade, riscos, etc)
   ├─ Identifica padrões e tendências
   ├─ Gera insights executivos
   └─ Cria recomendações estratégicas

5. Helena Estrategista refina:
   ├─ Linguagem executiva
   ├─ Prioriza informações críticas
   ├─ Destaca oportunidades de melhoria
   └─ Propõe roadmap

6. Sistema gera:
   ├─ PDF executivo (5 páginas)
   └─ Dashboard navegável

7. Marca [P7 ✅] no(s) processo(s)
```

#### **6. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p7_governanca/
├── helena_consolidador.py     # Agrega dados multi-processo
├── helena_estrategista.py     # Gera insights executivos
├── helena_ia_relacao.py       # Identifica processos relacionados
├── pdf_generator.py           # Gera PDF executivo
└── models.py                  # DossieGovernanca

# APIs
POST /api/p7/gerar-dossie/
     Body: {
       "tipo": "individual" | "consolidado",
       "atividade_id": 123,  # Se individual
       "area": "CGRIS"       # Se consolidado
     }

GET /api/p7/processos-relacionados/{atividade_id}/
    # Retorna lista com scores de relacionamento

GET /api/p7/dashboard-navegavel/?area=CGRIS&nivel=atividade

POST /api/p7/exportar-pdf/{dossie_id}/
```

**Frontend:**
```typescript
// pages/DossieGovernanca.tsx

interface DossieConfig {
  tipo: 'individual' | 'consolidado';
  atividade_id?: number;
  area?: string;
  processos_relacionados?: number[];  // IDs confirmados pelo usuário
}

interface DossieConsolidado {
  area: string;
  atividades: Atividade[];
  maturidade_media: number;
  riscos_criticos: Risco[];
  planos_status: {
    concluidos: number;
    em_andamento: number;
    atrasados: number;
  };
  oportunidades_top: Oportunidade[];
  roadmap: {
    mes: string;
    acoes: string[];
  }[];
  executive_summary: string;  // Gerado pela IA
  recomendacoes: string[];
}
```

**Prompt Executive Summary:**
```python
EXECUTIVE_SUMMARY_PROMPT = """
Você é uma executiva sênior de governança corporativa.

Crie um resumo executivo de 300-400 palavras para:

ÁREA: {area}
ATIVIDADES: {lista_atividades}
MATURIDADE: {maturidade_media}%
RISCOS CRÍTICOS: {riscos_criticos}
OPORTUNIDADES: {oportunidades_principais}
STATUS PLANOS: {planos_status}

O resumo deve:
• Ser direto e acionável
• Destacar conquistas e desafios
• Incluir top 3 recomendações estratégicas
• Usar linguagem executiva (não técnica)
• Focar em impacto de negócio

Estilo: Confiante, pragmático, orientado a resultados.
"""
```

#### **7. INTEGRAÇÃO COM OUTROS PRODUTOS**

**P7 é o "Destino Final":**
```
Todos produtos alimentam P7:
├─ P2 (Fluxograma) → Seção "Processos Mapeados"
├─ P3 (Oportunidades) → Seção "Oportunidades Identificadas"
├─ P5 (Riscos) → Seção "Mapa de Riscos"
├─ P6 (Plano Ação) → Seção "Status de Controles"
├─ P8 (Conformidade) → Seção "Compliance Score"
├─ P9 (Documentos) → Anexos (se houver)
└─ P10 (Artefatos) → Anexos (se houver)

P7 é o "consolidador máximo" - não alimenta ninguém.
É o produto final para auditorias/relatórios estratégicos.
```

---

## 🎯 P8 - Relatório de Conformidade

### **Objetivo**
Verificação automática de conformidade de um PROCESSO REAL vs normas aplicáveis, identificando gaps e sugerindo correções específicas.

### **Especificação Técnica**

#### **1. ESCOPO: PROCESSO ESPECÍFICO REAL**

**Diferença Fundamental:**
```
P7 (Dossiê): Visão consolidada de ATIVIDADES mapeadas
P8 (Conformidade): Análise de PROCESSO REAL em execução

Exemplo:
P7 analisa: "POP de Ressarcimento" (documento)
P8 analisa: "Processo SEI 12345/2025 de Ressarcimento da Maria" (caso concreto)
```

## 🎯 P8 - Relatório de Conformidade

### **Objetivo**
Verificação automática de conformidade de um PROCESSO REAL vs normas aplicáveis, identificando gaps e sugerindo correções específicas.

### **Especificação Técnica**

#### **1. ESCOPO: PROCESSO ESPECÍFICO REAL**

**Diferença Fundamental:**
```
P7 (Dossiê): Visão consolidada de ATIVIDADES mapeadas
P8 (Conformidade): Análise de PROCESSO REAL em execução

Exemplo:
P7 analisa: "POP de Ressarcimento" (documento)
P8 analisa: "Processo de Ressarcimento da Maria" (caso concreto)
```

**Entrada (SEM integração externa):**
```
Usuário fornece MANUALMENTE:
├─ Número do processo (referência, não busca automática)
├─ Descrição textual do que aconteceu no processo
├─ Upload de documentos do processo (PDFs)
└─ Atividade relacionada (CAP) - opcional

⚠️ IMPORTANTE: Sistema NÃO busca dados de SEI/NUP automaticamente
   Usuário descreve ou cola informações manualmente
```

#### **2. VERIFICAÇÃO HÍBRIDA**

**Fluxo de Análise:**
```
1. IA ANALISA (Automático via RAG):
   ├─ Compara descrição do processo vs normas aplicáveis
   ├─ Identifica requisitos normativos
   ├─ Verifica atendimento de cada requisito
   └─ Gera relatório preliminar

2. USUÁRIO CONFIRMA (Validação):
   ┌─────────────────────────────────────────┐
   │ REQUISITO: Termo de consentimento LGPD  │
   │ Status IA: ❌ Não atendido              │
   │                                         │
   │ Você confirma?                          │
   │ [✅ Confirmar] [❌ Discordar] [📝 Nota] │
   └─────────────────────────────────────────┘
   
   Se discordar:
   └─ Usuário adiciona evidência/justificativa
   └─ IA reanalisa com novo contexto

3. RELATÓRIO FINAL:
   └─ Combina análise IA + validação humana
```

#### **3. NORMAS: RAG PADRÃO + CUSTOMIZADAS**

**3.1. RAG Padrão (Base de Conhecimento):**
```
📂 chroma_db_normas/
├── LGPD (Lei 13.709/2018)
├── Lei 8.112/1990
├── Instruções Normativas SGP
├── Acórdãos TCU
├── Portarias CGU
├── Decreto 9.094/2017
└── Outras normas federais
```

**3.2. Normas Customizadas (Usuário Adiciona):**

**Opção A: Citar norma**
```
Usuário: "Adicionar Art. 47 da Portaria XYZ/2024"

Sistema:
1. IA busca na internet/base oficial
2. Indexa no RAG
3. Passa a usar em análises futuras
4. Sugere atualizar POPs relacionados
```

**Opção B: Colar trecho**
```
Usuário cola:
"Art. 47. O prazo para análise será de 30 dias corridos,
podendo ser prorrogado por igual período mediante justificativa."

Sistema:
1. IA identifica: Requisito de prazo
2. Solicita: "Qual a norma de origem?"
3. Indexa no RAG com metadados
4. Passa a verificar prazos nos processos
```

**Opção C: Upload de PDF**
```
Usuário faz upload: "portaria_interna_123.pdf"

Sistema:
1. Extrai texto do PDF
2. IA identifica artigos/requisitos
3. Indexa cada requisito separadamente no RAG
4. Confirma com usuário: "Encontrei 47 requisitos. OK?"
5. Passa a usar em análises
```

**Alimentação Retroativa dos POPs:**
```
Quando norma customizada é adicionada:

Sistema verifica:
"Essa norma impacta POPs existentes?"

Se sim:
├─ Lista POPs afetados
├─ Sugere atualização da base legal
├─ Notifica responsáveis
└─ Marca POPs para revisão

Exemplo:
Norma adicionada: "Portaria 456/2024 - Novos prazos"
POPs impactados: 12
└─ [Atualizar Base Legal] [Revisar Processos]
```

#### **4. AÇÕES CORRETIVAS INTELIGENTES**

**IA Sugere Correções em Múltiplas Camadas:**

**4.1. Correções no PROCESSO (Caso Concreto):**
```
Gap identificado: "Falta termo de consentimento LGPD"

IA sugere ações PARA ESTE PROCESSO:
├─ "Solicitar assinatura de termo retroativo ao interessado"
├─ "Justificar base legal alternativa (Art. 7º, II)"
├─ "Regularizar antes de prosseguir com análise"
└─ Prazo sugerido: 15 dias

[Aplicar Correção] [Criar Tarefa] [Notificar Responsável]
```

**4.2. Correções no POP (Documento Normativo):**
```
Gap identificado: "POP não menciona prazo legal de 30 dias"

IA sugere ações PARA O POP:
├─ "Adicionar seção 'Prazos Legais'"
├─ "Incluir referência à Portaria XYZ/2024"
├─ "Criar checklist de validação de prazos"
└─ "Atualizar versão do POP (1.0 → 1.1)"

[Atualizar POP] [Criar Versão] [Notificar Equipe]
```

**4.3. Correções em PRODUTOS (P2-P10):**
```
Gap identificado: "Fluxograma (P2) não mostra etapa de validação LGPD"

IA sugere ações PARA PRODUTOS:
├─ P2 (Fluxograma): "Adicionar nó 'Validar Consentimento'"
├─ P3 (Oportunidades): "Incluir oportunidade de automação"
├─ P5 (Riscos): "Atualizar risco LGPD como 'Mitigado'"
├─ P6 (Plano): "Marcar ação 'Implementar termo' como concluída"

[Atualizar Produtos] [Ver Impactos] [Sincronizar]
```

**Exemplo Completo de Correção:**
```
PROCESSO: "Ressarcimento Maria Silva" (Protocolo informado pelo usuário)

GAP CRÍTICO: Ausência de termo LGPD

┌─────────────────────────────────────────────────┐
│ 🔴 NÃO CONFORMIDADE IDENTIFICADA                │
├─────────────────────────────────────────────────┤
│ Norma: LGPD Art. 7º, I                          │
│ Requisito: Consentimento para tratamento dados │
│ Status: ❌ Não atendido                         │
│                                                 │
│ CORREÇÕES SUGERIDAS:                            │
│                                                 │
│ 📄 NESTE PROCESSO:                              │
│ 1. Enviar termo de consentimento para Maria    │
│    Prazo: 15 dias | Responsável: João Silva    │
│    [Gerar Termo] [Enviar Email]                │
│                                                 │
│ 📋 NO POP (CAP 12345):                          │
│ 2. Adicionar etapa "Coletar Consentimento"    │
│    Seção: 5. Tarefas, item 1.2 (após receber) │
│    [Editar POP] [Ver Preview]                  │
│                                                 │
│ 🔄 NO FLUXOGRAMA (P2):                          │
│ 3. Inserir nó "Validar LGPD" antes de "Analis"│
│    Posição: Entre nós 2 e 3                    │
│    [Atualizar Fluxograma]                      │
│                                                 │
│ ⚠️  NOS RISCOS (P5):                            │
│ 4. Atualizar risco "LGPD-001" para "Mitigado" │
│    Status atual: Crítico → Novo: Controlado   │
│    [Atualizar Status]                          │
│                                                 │
│ [Aplicar Todas Correções] [Customizar]         │
└─────────────────────────────────────────────────┘
```

#### **5. COMPLIANCE SCORE**

**5.1. Fórmula:**
```python
def calcular_compliance_score(processo):
    """
    Score baseado em requisitos normativos
    """
    
    requisitos = buscar_requisitos_aplicaveis(processo)
    
    atendidos = 0
    total = len(requisitos)
    
    for req in requisitos:
        if req.status == 'atendido':
            atendidos += 1
        elif req.status == 'atendido_parcial':
            atendidos += 0.5
        # 'nao_atendido' = 0
    
    score = (atendidos / total) * 100
    
    return {
        'score': round(score, 1),
        'requisitos_total': total,
        'requisitos_atendidos': atendidos,
        'requisitos_nao_atendidos': total - atendidos,
        'classificacao': classificar_score(score)
    }

def classificar_score(score):
    if score >= 90:
        return 'Excelente', '🟢'
    elif score >= 70:
        return 'Adequado', '🟡'
    elif score >= 50:
        return 'Insuficiente', '🟠'
    else:
        return 'Crítico', '🔴'
```

**5.2. Evolução Temporal:**
```python
class ComplianceHistorico(models.Model):
    processo_ref = models.CharField(max_length=100)  # Referência informada pelo usuário
    data = models.DateField(auto_now_add=True)
    score = models.FloatField()
    requisitos_total = models.IntegerField()
    requisitos_atendidos = models.FloatField()
    gaps_criticos = models.IntegerField()
    
    # Salvo mensalmente
    mes_referencia = models.DateField()
```

**5.3. Gráfico de Evolução no P4:**
```
┌─────────────────────────────────────────────────┐
│ EVOLUÇÃO COMPLIANCE - Processo Ressarcimento   │
├─────────────────────────────────────────────────┤
│ Score│                               ●          │
│ 100% │                           ●              │
│  80% │                       ●                  │
│  60% │                   ●                      │
│  40% │               ●                          │
│  20% │           ●                              │
│      └──────────────────────────────────────    │
│       Mai   Jun   Jul   Ago   Set   Out        │
│                                                 │
│ Status Atual: 85% (Adequado) 🟡                │
│ Tendência: ↗️ Melhoria contínua                 │
│                                                 │
│ Principais Melhorias:                           │
│ • Jun: Termo LGPD implementado (+15%)          │
│ • Ago: Base legal atualizada (+10%)            │
│ • Set: Controles implantados (+8%)             │
└─────────────────────────────────────────────────┘
```

#### **6. INTEGRAÇÃO COM OUTROS PRODUTOS**

**P8 → P9 (Gerador de Documentos):**
```
Após análise de conformidade:

Sistema pergunta:
"Deseja gerar documento sobre este processo?"

Opções:
├─ Nota Técnica de Análise
├─ Parecer de Conformidade
├─ Despacho de Regularização
└─ Relatório de Auditoria

[Sim, gerar documento] → Redireciona para P9 com dados pré-carregados
```

**P8 ← P7 (Dossiê):**
```
P7 inclui seção:
"CONFORMIDADE DOS PROCESSOS"

Agregação:
├─ Score médio de conformidade da área
├─ Top gaps mais frequentes
├─ Evolução temporal consolidada
└─ Recomendações estratégicas
```

#### **7. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p8_conformidade/
├── helena_auditora.py         # Análise automática
├── helena_gap_analyzer.py     # Identifica gaps
├── helena_corretor.py         # Sugere correções
├── rag_normas_custom.py       # Gerencia normas customizadas
└── models.py                  # ComplianceAnalise, Requisito

# APIs (SEM integração externa)
POST /api/p8/analisar-processo/
     Body: {
       "processo_referencia": "SEI-12345/2025",  # Apenas referência
       "descricao_processo": "...",  # Texto descritivo
       "atividade_cap": 12345,  # Opcional
       "documentos": [...]  # Upload de PDFs do processo
     }

POST /api/p8/adicionar-norma-custom/
     Body: {
       "tipo": "citacao" | "trecho" | "pdf",
       "conteudo": "...",
       "origem": "Portaria 456/2024"
     }

PATCH /api/p8/validar-requisito/{id}/
      Body: {
        "status": "confirmar" | "discordar",
        "justificativa": "..."
      }

GET /api/p8/compliance-score/{processo_id}/
GET /api/p8/evolucao-temporal/{processo_id}/

POST /api/p8/aplicar-correcoes/
     Body: {
       "processo_id": "...",
       "correcoes_selecionadas": [1, 3, 5, 7]
     }
```

**Frontend:**
```typescript
// pages/Conformidade.tsx

interface ComplianceAnalise {
  processo_referencia: string;  // Informado pelo usuário
  descricao_processo: string;   // Texto descritivo
  data_analise: Date;
  score: number;
  classificacao: 'Excelente' | 'Adequado' | 'Insuficiente' | 'Crítico';
  
  requisitos: Requisito[];
  gaps_criticos: Gap[];
  correcoes_sugeridas: {
    processo: Correcao[];
    pop: Correcao[];
    produtos: {
      produto_code: string;
      correcoes: Correcao[];
    }[];
  };
}

interface Requisito {
  id: number;
  norma: string;
  artigo: string;
  descricao: string;
  status: 'atendido' | 'atendido_parcial' | 'nao_atendido';
  evidencias: string[];
  validado_usuario: boolean;
}

interface Correcao {
  descricao: string;
  prioridade: 'alta' | 'media' | 'baixa';
  prazo_sugerido: number;  // dias
  responsavel_sugerido: string;
  acao_automatica: string;  // Nome da função
}
```

---

#### **2. VERIFICAÇÃO HÍBRIDA**

**Fluxo de Análise:**
```
1. IA ANALISA (Automático via RAG):
   ├─ Compara processo vs normas aplicáveis
   ├─ Identifica requisitos normativos
   ├─ Verifica atendimento de cada requisito
   └─ Gera relatório preliminar

2. USUÁRIO CONFIRMA (Validação):
   ┌─────────────────────────────────────────┐
   │ REQUISITO: Termo de consentimento LGPD  │
   │ Status IA: ❌ Não atendido              │
   │                                         │
   │ Você confirma?                          │
   │ [✅ Confirmar] [❌ Discordar] [📝 Nota] │
   └─────────────────────────────────────────┘
   
   Se discordar:
   └─ Usuário adiciona evidência/justificativa
   └─ IA reanalisa com novo contexto

3. RELATÓRIO FINAL:
   └─ Combina análise IA + validação humana
```

#### **3. NORMAS: RAG PADRÃO + CUSTOMIZADAS**

**3.1. RAG Padrão (Base de Conhecimento):**
```
📂 chroma_db_normas/
├── LGPD (Lei 13.709/2018)
├── Lei 8.112/1990
├── Instruções Normativas SGP
├── Acórdãos TCU
├── Portarias CGU
├── Decreto 9.094/2017
└── Outras normas federais
```

**3.2. Normas Customizadas (Usuário Adiciona):**

**Opção A: Citar norma**
```
Usuário: "Adicionar Art. 47 da Portaria XYZ/2024"

Sistema:
1. IA busca na internet/base oficial
2. Indexa no RAG
3. Passa a usar em análises futuras
4. Sugere atualizar POPs relacionados
```

**Opção B: Colar trecho**
```
Usuário cola:
"Art. 47. O prazo para análise será de 30 dias corridos,
podendo ser prorrogado por igual período mediante justificativa."

Sistema:
1. IA identifica: Requisito de prazo
2. Solicita: "Qual a norma de origem?"
3. Indexa no RAG com metadados
4. Passa a verificar prazos nos processos
```

**Opção C: Upload de PDF**
```
Usuário faz upload: "portaria_interna_123.pdf"

Sistema:
1. Extrai texto do PDF
2. IA identifica artigos/requisitos
3. Indexa cada requisito separadamente no RAG
4. Confirma com usuário: "Encontrei 47 requisitos. OK?"
5. Passa a usar em análises
```

**Alimentação Retroativa dos POPs:**
```
Quando norma customizada é adicionada:

Sistema verifica:
"Essa norma impacta POPs existentes?"

Se sim:
├─ Lista POPs afetados
├─ Sugere atualização da base legal
├─ Notifica responsáveis
└─ Marca POPs para revisão

Exemplo:
Norma adicionada: "Portaria 456/2024 - Novos prazos"
POPs impactados: 12
└─ [Atualizar Base Legal] [Revisar Processos]
```

#### **4. AÇÕES CORRETIVAS INTELIGENTES**

**IA Sugere Correções em Múltiplas Camadas:**

**4.1. Correções no PROCESSO (Caso Concreto):**
```
Gap identificado: "Falta termo de consentimento LGPD"

IA sugere ações PARA ESTE PROCESSO:
├─ "Solicitar assinatura de termo retroativo ao interessado"
├─ "Justificar base legal alternativa (Art. 7º, II)"
├─ "Regularizar antes de prosseguir com análise"
└─ Prazo sugerido: 15 dias

[Aplicar Correção] [Criar Tarefa] [Notificar Responsável]
```

**4.2. Correções no POP (Documento Normativo):**
```
Gap identificado: "POP não menciona prazo legal de 30 dias"

IA sugere ações PARA O POP:
├─ "Adicionar seção 'Prazos Legais'"
├─ "Incluir referência à Portaria XYZ/2024"
├─ "Criar checklist de validação de prazos"
└─ "Atualizar versão do POP (1.0 → 1.1)"

[Atualizar POP] [Criar Versão] [Notificar Equipe]
```

**4.3. Correções em PRODUTOS (P2-P10):**
```
Gap identificado: "Fluxograma (P2) não mostra etapa de validação LGPD"

IA sugere ações PARA PRODUTOS:
├─ P2 (Fluxograma): "Adicionar nó 'Validar Consentimento'"
├─ P3 (Oportunidades): "Incluir oportunidade de automação"
├─ P5 (Riscos): "Atualizar risco LGPD como 'Mitigado'"
├─ P6 (Plano): "Marcar ação 'Implementar termo' como concluída"

[Atualizar Produtos] [Ver Impactos] [Sincronizar]
```

**Exemplo Completo de Correção:**
```
PROCESSO: SEI 12345/2025 (Ressarcimento Maria Silva)

GAP CRÍTICO: Ausência de termo LGPD

┌─────────────────────────────────────────────────┐
│ 🔴 NÃO CONFORMIDADE IDENTIFICADA                │
├─────────────────────────────────────────────────┤
│ Norma: LGPD Art. 7º, I                          │
│ Requisito: Consentimento para tratamento dados │
│ Status: ❌ Não atendido                         │
│                                                 │
│ CORREÇÕES SUGERIDAS:                            │
│                                                 │
│ 📄 NESTE PROCESSO:                              │
│ 1. Enviar termo de consentimento para Maria    │
│    Prazo: 15 dias | Responsável: João Silva    │
│    [Gerar Termo] [Enviar Email]                │
│                                                 │
│ 📋 NO POP (CAP 12345):                          │
│ 2. Adicionar etapa "Coletar Consentimento"    │
│    Seção: 5. Tarefas, item 1.2 (após receber) │
│    [Editar POP] [Ver Preview]                  │
│                                                 │
│ 🔄 NO FLUXOGRAMA (P2):                          │
│ 3. Inserir nó "Validar LGPD" antes de "Analis"│
│    Posição: Entre nós 2 e 3                    │
│    [Atualizar Fluxograma]                      │
│                                                 │
│ ⚠️  NOS RISCOS (P5):                            │
│ 4. Atualizar risco "LGPD-001" para "Mitigado" │
│    Status atual: Crítico → Novo: Controlado   │
│    [Atualizar Status]                          │
│                                                 │
│ [Aplicar Todas Correções] [Customizar]         │
└─────────────────────────────────────────────────┘
```

#### **5. COMPLIANCE SCORE**

**5.1. Fórmula:**
```python
def calcular_compliance_score(processo):
    """
    Score baseado em requisitos normativos
    """
    
    requisitos = buscar_requisitos_aplicaveis(processo)
    
    atendidos = 0
    total = len(requisitos)
    
    for req in requisitos:
        if req.status == 'atendido':
            atendidos += 1
        elif req.status == 'atendido_parcial':
            atendidos += 0.5
        # 'nao_atendido' = 0
    
    score = (atendidos / total) * 100
    
    return {
        'score': round(score, 1),
        'requisitos_total': total,
        'requisitos_atendidos': atendidos,
        'requisitos_nao_atendidos': total - atendidos,
        'classificacao': classificar_score(score)
    }

def classificar_score(score):
    if score >= 90:
        return 'Excelente', '🟢'
    elif score >= 70:
        return 'Adequado', '🟡'
    elif score >= 50:
        return 'Insuficiente', '🟠'
    else:
        return 'Crítico', '🔴'
```

**5.2. Evolução Temporal:**
```python
class ComplianceHistorico(models.Model):
    processo_id = models.CharField(max_length=50)
    data = models.DateField(auto_now_add=True)
    score = models.FloatField()
    requisitos_total = models.IntegerField()
    requisitos_atendidos = models.FloatField()
    gaps_criticos = models.IntegerField()
    
    # Salvo mensalmente
    mes_referencia = models.DateField()
```

**5.3. Gráfico de Evolução no P4:**
```
┌─────────────────────────────────────────────────┐
│ EVOLUÇÃO COMPLIANCE - Processo SEI 12345/2025  │
├─────────────────────────────────────────────────┤
│ Score│                               ●          │
│ 100% │                           ●              │
│  80% │                       ●                  │
│  60% │                   ●                      │
│  40% │               ●                          │
│  20% │           ●                              │
│      └──────────────────────────────────────    │
│       Mai   Jun   Jul   Ago   Set   Out        │
│                                                 │
│ Status Atual: 85% (Adequado) 🟡                │
│ Tendência: ↗️ Melhoria contínua                 │
│                                                 │
│ Principais Melhorias:                           │
│ • Jun: Termo LGPD implementado (+15%)          │
│ • Ago: Base legal atualizada (+10%)            │
│ • Set: Controles implantados (+8%)             │
└─────────────────────────────────────────────────┘
```

#### **6. INTEGRAÇÃO COM OUTROS PRODUTOS**

**P8 → P9 (Gerador de Documentos):**
```
Após análise de conformidade:

Sistema pergunta:
"Deseja gerar documento sobre este processo?"

Opções:
├─ Nota Técnica de Análise
├─ Parecer de Conformidade
├─ Despacho de Regularização
└─ Relatório de Auditoria

[Sim, gerar documento] → Redireciona para P9 com dados pré-carregados
```

**P8 ← P7 (Dossiê):**
```
P7 inclui seção:
"CONFORMIDADE DOS PROCESSOS"

Agregação:
├─ Score médio de conformidade da área
├─ Top gaps mais frequentes
├─ Evolução temporal consolidada
└─ Recomendações estratégicas
```

#### **7. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p8_conformidade/
├── helena_auditora.py         # Análise automática
├── helena_gap_analyzer.py     # Identifica gaps
├── helena_corretor.py         # Sugere correções
├── rag_normas_custom.py       # Gerencia normas customizadas
└── models.py                  # ComplianceAnalise, Requisito

# APIs
POST /api/p8/analisar-processo/
     Body: {
       "processo_id": "SEI-12345/2025",
       "atividade_cap": 12345,  # Opcional
       "documentos": [...]      # Upload de docs do processo
     }

POST /api/p8/adicionar-norma-custom/
     Body: {
       "tipo": "citacao" | "trecho" | "pdf",
       "conteudo": "...",
       "origem": "Portaria 456/2024"
     }

PATCH /api/p8/validar-requisito/{id}/
      Body: {
        "status": "confirmar" | "discordar",
        "justificativa": "..."
      }

GET /api/p8/compliance-score/{processo_id}/
GET /api/p8/evolucao-temporal/{processo_id}/

POST /api/p8/aplicar-correcoes/
     Body: {
       "processo_id": "...",
       "correcoes_selecionadas": [1, 3, 5, 7]
     }
```

**Frontend:**
```typescript
// pages/Conformidade.tsx

interface ComplianceAnalise {
  processo_id: string;
  data_analise: Date;
  score: number;
  classificacao: 'Excelente' | 'Adequado' | 'Insuficiente' | 'Crítico';
  
  requisitos: Requisito[];
  gaps_criticos: Gap[];
  correcoes_sugeridas: {
    processo: Correcao[];
    pop: Correcao[];
    produtos: {
      produto_code: string;
      correcoes: Correcao[];
    }[];
  };
}

interface Requisito {
  id: number;
  norma: string;
  artigo: string;
  descricao: string;
  status: 'atendido' | 'atendido_parcial' | 'nao_atendido';
  evidencias: string[];
  validado_usuario: boolean;
}

interface Correcao {
  descricao: string;
  prioridade: 'alta' | 'media' | 'baixa';
  prazo_sugerido: number;  // dias
  responsavel_sugerido: string;
  acao_automatica: string;  // Nome da função
}
```

---

## 🎯 P9 - Gerador de Documentos de Conclusão

### **Objetivo**
Gerar documentos oficiais (despachos/notas) sobre o que ACONTECEU em um processo real, consolidando toda a tramitação e decisões.

### **IMPORTANTE: Diferença Fundamental**

```
P8 (Conformidade): Compara o que ACONTECEU vs o que DEVERIA ter acontecido
                   → Retorna: Relatório de conformidade com gaps

P9 (Documentos):   Documenta o que ACONTECEU (sem julgamento)
                   → Retorna: Nota/Despacho de conclusão do processo
```

### **Especificação Técnica**

#### **1. FOCO: CONTEÚDO > TEMPLATE**

**Não é biblioteca de templates**, é **gerador inteligente de narrativa processual**.

**O que P9 faz:**
```
Entrada: Processo real (SEI 12345/2025 - Ressarcimento Maria)

IA analisa:
├─ Histórico de tramitação
├─ Documentos juntados
├─ Despachos anteriores
├─ Decisões tomadas
├─ Prazos cumpridos/descumpridos
└─ Resultado final

Saída: Documento narrativo estruturado
```

**Exemplo de Documento Gerado:**
```
NOTA TÉCNICA Nº 123/2025-CGRIS

ASSUNTO: Conclusão do Processo de Ressarcimento

1. HISTÓRICO
Em 15/09/2025, a servidora Maria Silva (SIAPE 1234567) 
protocolou solicitação de ressarcimento de plano de saúde 
referente ao período de jan-jun/2025.

2. TRAMITAÇÃO
O processo foi distribuído à analista João Santos em 
18/09/2025, que identificou pendência documental (falta 
de termo de consentimento LGPD).

Em 22/09/2025, foi solicitada complementação, atendida 
pela interessada em 25/09/2025.

Após análise completa, verificou-se o atendimento de 
todos os requisitos normativos (Lei 8.112/90, Art. 230).

3. ANÁLISE
O pedido está instruído com:
• Contrato de plano de saúde ✓
• Boletos mensais e comprovantes de pagamento ✓
• Termo de consentimento LGPD ✓
• Declaração da operadora ✓

Valor total: R$ 2.340,00 (6 meses × R$ 390,00)

4. CONCLUSÃO
Opino pelo DEFERIMENTO do pedido, com base no Art. 230 
da Lei 8.112/90 e na IN SGP/SEDGG/ME nº 97/2022.

Sugere-se o encaminhamento à CGPAG para providências 
quanto ao pagamento.

[Assinatura digital]
Analista João Santos
CGRIS - Coordenação Geral de Riscos
```

#### **2. TIPOS DE DOCUMENTOS**

**Foco em 3 tipos principais:**

**2.1. Nota Técnica de Conclusão**
- Documenta análise completa do processo
- Estrutura: Histórico → Tramitação → Análise → Conclusão
- Público: Interno (gestores, auditores)

**2.2. Despacho de Decisão**
- Documenta decisão sobre o processo
- Estrutura: Breve histórico → Fundamentação → Decisão
- Público: Interessado + superior hierárquico

**2.3. Parecer Técnico**
- Opinião fundamentada sobre caso complexo
- Estrutura: Relatório → Análise → Parecer
- Público: Alta gestão, assessoria jurídica

#### **3. GERAÇÃO INTELIGENTE**

**Fluxo:**
```
1. Usuário acessa P9

2. Fornece contexto:
   ├─ Número do processo (SEI)
   ├─ OU descrição manual do caso
   └─ Tipo de documento desejado

3. IA Helena Documentadora coleta dados:
   ├─ Se processo SEI: busca automaticamente
   ├─ Se descrição manual: faz perguntas estruturadas
   └─ Se tem P8 associado: importa dados de conformidade

4. IA Helena Redatora gera documento:
   ├─ Linguagem técnica formal
   ├─ Estrutura padrão gov.br
   ├─ Fundamentação legal automática
   └─ Conclusão baseada em fatos

5. Preview + Ajustes:
   ├─ Usuário revisa documento
   ├─ Pode editar livremente
   └─ IA sugere melhorias (se solicitado)

6. Exportação:
   └─ PDF formatado padrão gov.br
```

**IA extrai automaticamente:**
```python
DADOS_EXTRAIDOS = {
    'interessado': {
        'nome': 'Maria Silva',
        'cpf': '123.456.789-00',
        'siape': '1234567'
    },
    'tramitacao': [
        {'data': '15/09/2025', 'evento': 'Protocolado'},
        {'data': '18/09/2025', 'evento': 'Distribuído para João'},
        {'data': '22/09/2025', 'evento': 'Solicitada complementação'},
        {'data': '25/09/2025', 'evento': 'Complementação juntada'},
        {'data': '30/09/2025', 'evento': 'Análise concluída'}
    ],
    'documentos_juntados': [
        'Contrato plano saúde',
        'Boletos jan-jun/2025',
        'Comprovantes pagamento',
        'Termo LGPD'
    ],
    'fundamentacao_legal': [
        'Lei 8.112/90, Art. 230',
        'IN SGP/SEDGG/ME nº 97/2022'
    ],
    'decisao': 'DEFERIMENTO',
    'valor': 'R$ 2.340,00'
}
```

#### **4. INTEGRAÇÃO COM P8**

**Quando P8 existe:**
```
P8 analisa: Processo SEI 12345 está 85% conforme

P9 pode usar:
├─ "O processo atende a 85% dos requisitos normativos"
├─ Gaps identificados (se relevantes para conclusão)
├─ Correções aplicadas durante tramitação
└─ Evolução do compliance ao longo do tempo

Exemplo no documento:
"3. CONFORMIDADE
Conforme análise de conformidade realizada (P8), o processo 
atende a 17 dos 20 requisitos normativos aplicáveis (85%), 
com gaps não críticos já sanados durante a instrução."
```

**P9 DOCUMENTA o processo**, P8 AVALIA o processo.

#### **5. ARQUITETURA TÉCNICA**

**Backend:**
```python
# helena_produtos/p9_documentos/
├── helena_documentadora.py    # Coleta dados do processo
├── helena_redatora.py         # Gera texto formal
├── helena_revisora.py         # Revisa e sugere melhorias
├── templates/                 # Templates base (estrutura)
│   ├── nota_tecnica.md
│   ├── despacho.md
│   └── parecer.md
└── models.py                  # Documento, Versao

# APIs
POST /api/p9/gerar-documento/
     Body: {
       "tipo": "nota" | "despacho" | "parecer",
       "processo_sei": "12345/2025",  # OU
       "descricao_manual": "...",
       "incluir_conformidade_p8": true  # Se existe P8
     }

GET /api/p9/buscar-dados-sei/{processo_id}/
    # Busca dados automaticamente do SEI

POST /api/p9/revisar-documento/
     Body: {
       "documento_id": 123,
       "texto_usuario": "..."
     }

POST /api/p9/exportar-pdf/{documento_id}/
```

**Prompt de Geração:**
```python
DOCUMENTO_PROMPT = """
Você é redatora oficial de documentos técnicos do setor público.

Gere uma {tipo_documento} sobre o processo descrito abaixo.

DADOS DO PROCESSO:
{dados_extraidos}

CONFORMIDADE (P8):
{dados_conformidade}  # Se disponível

ESTRUTURA OBRIGATÓRIA:
1. HISTÓRICO - Contexto inicial do processo
2. TRAMITAÇÃO - Linha do tempo de eventos
3. ANÁLISE - Avaliação técnica dos documentos/requisitos
4. CONCLUSÃO - Decisão fundamentada

REQUISITOS:
• Linguagem técnica formal (Manual de Redação Oficial)
• Fundamentação legal explícita
• Conclusão objetiva e acionável
• Cronologia clara
• Referências a documentos específicos

ESTILO:
• Impessoal (3ª pessoa)
• Conciso mas completo
• Sem adjetivos desnecessários
• Parágrafos curtos (3-5 linhas)

Retorne o documento formatado em Markdown.
"""
```

**Frontend:**
```typescript
// pages/GeradorDocumentos.tsx

interface DocumentoConfig {
  tipo: 'nota' | 'despacho' | 'parecer';
  fonte: 'sei' | 'manual';
  processo_sei?: string;
  descricao_manual?: string;
  incluir_p8?: boolean;
}

interface DocumentoGerado {
  id: number;
  tipo: string;
  conteudo_markdown: string;
  conteudo_html: string;
  metadados: {
    processo: string;
    interessado: string;
    data_geracao: Date;
    autor: string;
  };
  editavel: boolean;
  versao: number;
}

// Componentes
<DocumentoWizard />         // Coleta dados
<PreviewEditor />           // Preview + edição
<ExportOptions />           // PDF, DOCX, etc
```

---

## 🎯 P10 - Análise de Artefatos

### **Objetivo**
Otimização inteligente de templates e documentos existentes.

### **Perguntas de Refinamento:**

1. **Tipos de arquivo suportados:**
   - PDF, Word, ambos?
   - Tamanho máximo de upload?

2. **Dimensões de análise:**
   - Quais aspectos avaliar?
     - [ ] Clareza e objetividade (sentenças longas, jargão)
     - [ ] Conformidade técnica (campos obrigatórios, base legal)
     - [ ] Acessibilidade (linguagem técnica, glossário)
     - [ ] Estrutura (organização lógica)
     - [ ] Completude (informações faltantes)
     - [ ] Outros?

3. **Formato da análise:**
   - Relatório com pontuação por dimensão?
   - Comparação lado a lado (original vs otimizado)?
   - Lista de problemas priorizada?

4. **Versão otimizada:**
   - IA gera documento melhorado automaticamente?
   - Usuário pode aceitar/rejeitar sugestões individualmente?
   - Exporta versão final em qual formato? (Word editável, PDF)

5. **Feedback iterativo:**
   - Usuário pode solicitar ajustes após primeira análise?
   - Histórico de versões mantido?

---

## 📊 Arquitetura Técnica Comum aos 9 Produtos

### **Backend (Django)**

```python
# Helena-Core (Orquestrador)
helena_core/
├── router.py          # Roteia para Helena especializada
├── base_helena.py     # Classe base com métodos comuns
└── product_registry.py # Registro de produtos disponíveis

# Helenas Especializadas (N por produto conforme necessidade)
helena_produtos/
├── p3_oportunidades/
│   ├── helena_chat.py          # Conversa inicial
│   ├── helena_analise.py       # Análise profunda
│   ├── helena_validacao.py     # Valida achados
│   └── helena_export.py        # Gera relatório
├── p4_dashboard/
│   ├── helena_agregador.py     # Coleta dados
│   └── helena_metricas.py      # Calcula KPIs
├── p6_plano_acao/
│   ├── helena_sugestao.py      # Sugere controles
│   └── helena_priorizacao.py   # Prioriza ações
├── p7_governanca/
│   ├── helena_consolidador.py  # Agrega multi-processo
│   └── helena_estrategista.py  # Recomendações executivas
├── p8_conformidade/
│   ├── helena_auditora.py      # Verifica normas
│   └── helena_gap_analyzer.py  # Identifica gaps
├── p9_documentos/
│   ├── helena_redatora.py      # Redação automática
│   └── helena_revisora.py      # Revisão técnica
├── p10_artefatos/
│   ├── helena_analisadora.py   # Analisa documento
│   └── helena_otimizadora.py   # Gera versão melhorada
└── rag_config.py               # RAG compartilhado
```

### **APIs REST**

```
POST /api/produtos/{produto_code}/execute/
GET  /api/produtos/{produto_code}/status/
POST /api/produtos/{produto_code}/export/
```

### **Frontend (React)**

```typescript
// Estrutura de páginas
pages/
├── Oportunidades.tsx    # P3
├── Dashboard.tsx        # P4
├── PlanoAcao.tsx        # P6
├── DossieGovernanca.tsx # P7
├── Conformidade.tsx     # P8
├── GeradorDocumentos.tsx# P9
└── AnaliseArtefatos.tsx # P10

// Serviços de API
services/
├── oportunidadesApi.ts
├── dashboardApi.ts
├── planoAcaoApi.ts
└── ... (um por produto)
```

---

## 🎯 Próximos Passos

**Após refinamento das perguntas acima:**

1. Documentar especificação técnica detalhada de cada produto
2. Definir schemas de dados (TypeScript interfaces + Django models)
3. Criar prompts IA especializados para cada Helena
4. Implementar APIs REST
5. Desenvolver interfaces React
6. Testes de integração
7. Deploy incremental

---

## 📝 Checklist de Entrega por Produto

Para cada produto, entregar:

- [ ] Documentação funcional completa
- [ ] Schemas de dados (backend + frontend)
- [ ] Prompt IA especializado
- [ ] Endpoint(s) Django
- [ ] Interface React
- [ ] Testes básicos
- [ ] Exemplo de uso

---

## 📊 RESUMO EXECUTIVO - 9 Produtos MapaGov

| # | Produto | Escopo | Entrada | Saída | Helena(s) |
|---|---------|--------|---------|-------|-----------|
| **P3** | Oportunidades | Atividade mapeada | ID do POP | Dashboard + PDF com ROI | Analisadora, ROI Calculator, Priorizador |
| **P4** | Dashboard | Multi-nível | Filtro hierárquico | Métricas + KPIs visuais | Agregador, Métricas |
| **P6** | Plano de Ação | Flexível | Riscos/Oportunidades/Chat | 5W2H + Kanban | Planejadora, Sugestão, Priorizador |
| **P7** | Dossiê Governança | Atividade(s) | CAP ou Área | PDF 5 pág + Dashboard | Consolidador, Estrategista, IA Relação |
| **P8** | Conformidade | Processo real | SEI/Descrição | Score + Correções | Auditora, Gap Analyzer, Corretor |
| **P9** | Documentos Conclusão | Processo real | SEI/Descrição | Nota/Despacho oficial | Documentadora, Redatora, Revisora |
| **P10** | Assistente Comunicação | Comunicação externa | Texto/Upload | Análise UX + Versão otimizada | Analisadora UX, Otimizadora, Geradora |

---

## 🔗 Fluxo de Integração Entre Produtos

```
P1 (POP) → P2 (Fluxograma) → P3 (Oportunidades)
                               ↓
                            P6 (Plano Ação) ← P5 (Riscos)
                               ↓
                            P4 (Dashboard) ← P8 (Conformidade)
                               ↓                    ↓
                            P7 (Dossiê) ← P9 (Docs) → P10 (Comunicação)
```

**Legenda:**
- **→** Alimenta diretamente
- **←** Importa dados de
- **P7** é o consolidador final (todos alimentam)

---

## 🎯 Diferenciais Técnicos por Produto

### **P3 - Oportunidades**
✅ Foco em automação, redução burocrática, otimização e treinamento  
✅ ROI calculado para cada oportunidade  
✅ Integração com P6 (botão "Adicionar ao Plano")  

### **P4 - Dashboard**
✅ Hierarquia multinível (Diretoria → CG → Coordenação → Usuário)  
✅ Maturidade calculada por produtos agregados (P2-P10)  
✅ Drill-down completo até nível de atividade  
✅ Deploy noturno (cache diário)  

### **P6 - Plano de Ação**
✅ 3 modos de entrada (riscos, oportunidades, chat do zero)  
✅ Auto-learning de controles (aprende com histórico)  
✅ Bucket RAG de normas e boas práticas  
✅ Alertas de inatividade (7 e 15 dias)  
✅ Revisão obrigatória em 2 anos (auto-agendada)  

### **P7 - Dossiê**
✅ IA identifica processos relacionados automaticamente  
✅ PDF executivo compacto (~5 páginas)  
✅ Linguagem executiva para alta gestão  
✅ Dashboard navegável com drill-down  

### **P8 - Conformidade**
✅ Analisa PROCESSO REAL vs normas  
✅ Normas customizadas (citar/colar/PDF)  
✅ Correções em múltiplas camadas (processo, POP, produtos)  
✅ Evolução temporal de compliance  

### **P9 - Documentos**
✅ Documenta o que ACONTECEU (não julga)  
✅ Foco em conteúdo > template  
✅ Integração com P8 (inclui dados de conformidade)  
✅ Gera narrativa processual estruturada  

### **P10 - Comunicação**
✅ Foco em experiência do usuário FINAL  
✅ Analisa 5 dimensões (clareza, empatia, completude, acessibilidade, ação)  
✅ Identifica pontos cegos críticos  
✅ 2 modos: gerar modelo OU revisar existente  

---

## 🚀 Checklist de Implementação

**Para cada produto, entregar:**

- [ ] **Documentação funcional completa** (este framework)
- [ ] **Schemas de dados** (TypeScript interfaces + Django models)
- [ ] **Prompts IA especializados** (por Helena)
- [ ] **Endpoints Django** (APIs REST)
- [ ] **Páginas React** (componentes + serviços)
- [ ] **Testes básicos** (unitários + integração)
- [ ] **Exemplo de uso** (cenário real documentado)
- [ ] **Integração com outros produtos** (quando aplicável)

---

## 📝 Ordem de Implementação Sugerida

**Sprint 1-2:** P3 (Oportunidades)  
**Sprint 3-4:** P4 (Dashboard)  
**Sprint 5-7:** P6 (Plano de Ação) - mais complexo  
**Sprint 8-9:** P8 (Conformidade)  
**Sprint 10-11:** P7 (Dossiê Governança)  
**Sprint 12-13:** P9 (Documentos)  
**Sprint 14-15:** P10 (Comunicação)  

**Total estimado:** 15 sprints de 2 semanas = ~7.5 meses

---

## 🎓 Glossário Técnico

**CAP:** Código de identificação da atividade mapeada  
**CG:** Coordenação Geral (CGRIS, CGCAF, CGECO, etc)  
**Maturidade:** % de produtos (P2-P10) concluídos para uma atividade  
**RAG:** Retrieval-Augmented Generation (busca semântica + LLM)  
**5W2H:** What, Why, Where, When, Who, How, How Much  
**Helena-Core:** Orquestrador que roteia para Helenas especializadas  
**Bucket de Normas:** Base RAG dedicada a normas e boas práticas  
**Auto-Learning:** Sistema aprende com feedback e histórico de uso  

---

**STATUS FINAL:** Framework completo e pronto para implementação! ✅