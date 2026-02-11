# MapaGov API — Padroes de Endpoints por Produto

> Referencia: ADR-001 v1.1, secao 2.5
>
> **NAO existe padrao universal de endpoints.** Cada produto segue seu proprio modelo.

---

## 1. POP (Mapeamento de Processos)

### Padrao: Chat-driven State Machine

O fluxo POP e inteiramente conversacional. O backend mantem uma state machine (HelenaPOP/HelenaEtapas)
que avanca conforme mensagens do usuario. Nao ha CRUD de recurso POP via REST.

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/chat/` | POST | Envia mensagem para state machine Helena POP |
| `/api/pop-autosave/` | POST | Sincroniza dados do formulario (frontend → backend) |
| `/api/pop/<identifier>/` | GET | Carrega POP salvo (backend → frontend) |
| `/api/gerar-pdf-pop/` | POST | Gera PDF a partir dos dados do POP |
| `/api/download-pdf/<filename>/` | GET | Download de PDF gerado |
| `/api/validar-dados-pop/` | POST | Validacao de campo em tempo real |
| `/api/helena-mapeamento/` | POST | Chat de ajuda sobre mapeamento |
| `/api/consultar-rag-sugestoes/` | POST | Sugestoes via RAG para campos do POP |

### Request/Response do chat principal

```json
// POST /api/chat/
// Request:
{
  "message": "string",
  "contexto": "gerador_pop",
  "session_id": "uuid"
}

// Response:
{
  "resposta": "string | null",
  "tipo_interface": "string | null",
  "dados_interface": {},
  "dados_extraidos": {},
  "progresso": "3/10",
  "conversa_completa": false,
  "schema_version": "1.0",
  "metadados": {
    "auto_continue": false,
    "auto_continue_delay": 1500,
    "auto_continue_message": "__continue__"
  }
}
```

### Request/Response do autosave

```json
// POST /api/pop-autosave/
// Request:
{
  "id": null,
  "uuid": null,
  "session_id": "uuid",
  "nome_processo": "...",
  "raw_payload": "{...}"
}

// Response:
{
  "success": true,
  "pop": { "id": 1, "uuid": "...", "autosave_sequence": 5 },
  "integrity_hash": "sha256...",
  "snapshot_created": false
}
```

---

## 2. Analise de Riscos

### Padrao: REST com identificadores UUID

CRUD completo com UUIDs. Dois conjuntos de endpoints coexistem (v1 legado + v2 novo fluxo).

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/analise-riscos/criar/` | POST | Cria nova analise |
| `/api/analise-riscos/listar/` | GET | Lista analises |
| `/api/analise-riscos/<uuid>/` | GET | Detalha analise |
| `/api/analise-riscos/<uuid>/questionario/` | PATCH | Atualiza questionario (v1) |
| `/api/analise-riscos/<uuid>/etapa/` | PATCH | Atualiza etapa |
| `/api/analise-riscos/<uuid>/riscos/` | POST | Adiciona risco |
| `/api/analise-riscos/<uuid>/riscos/<uuid>/analise/` | PATCH | Avalia risco (P x I) |
| `/api/analise-riscos/<uuid>/riscos/<uuid>/` | DELETE | Remove risco |
| `/api/analise-riscos/<uuid>/riscos/<uuid>/respostas/` | POST | Adiciona resposta |
| `/api/analise-riscos/<uuid>/finalizar/` | PATCH | Finaliza analise |
| `/api/analise-riscos/<uuid>/exportar/?formato=pdf\|docx` | GET | Exporta relatorio |

**Endpoints v2 (novo fluxo):**

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/analise-riscos/v2/criar/` | POST | Cria analise (v2) |
| `/api/analise-riscos/<uuid>/contexto/` | PATCH | Salva contexto (Bloco A+B) |
| `/api/analise-riscos/<uuid>/blocos/` | PATCH | Salva blocos de identificacao |
| `/api/analise-riscos/<uuid>/inferir/` | POST | Inferencia IA de riscos |

---

## 3. Planejamento Estrategico

### Padrao: RESTful com IDs inteiros + endpoints conversacionais

Combina REST (CRUD de planejamentos) com endpoints conversacionais (`/iniciar/`, `/processar/`).

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/planejamento-estrategico/iniciar/` | POST | Inicia sessao de planejamento |
| `/api/planejamento-estrategico/processar/` | POST | Processa mensagem na conversa |
| `/api/planejamento-estrategico/salvar/` | POST | Salva planejamento |
| `/api/planejamento-estrategico/listar/` | GET | Lista planejamentos |
| `/api/planejamento-estrategico/<id>/` | GET | Detalha planejamento |
| `/api/planejamento-estrategico/<id>/aprovar/` | POST | Aprova planejamento |
| `/api/planejamento-estrategico/<id>/revisar/` | POST | Cria revisao |
| `/api/planejamento-estrategico/<id>/exportar/` | GET | Exporta planejamento |
| `/api/planejamento-estrategico/modelos/` | GET | Lista modelos disponiveis |
| `/api/planejamento-estrategico/diagnostico/` | GET | Obtem diagnostico |
| `/api/planejamento-estrategico/recomendar/` | POST | Calcula recomendacao de modelo |
| `/api/planejamento-estrategico/iniciar-modelo/` | POST | Inicia modelo direto |
| `/api/planejamento-estrategico/confirmar-modelo/` | POST | Confirma modelo selecionado |

---

## 4. Chat V2 (Multi-produto)

### Padrao: Sessao com roteamento automatico

Endpoint unificado que roteia entre produtos via contexto da sessao.

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/chat-v2/` | POST | Envia mensagem (roteamento automatico) |
| `/api/chat-v2/mudar-contexto/` | POST | Troca de produto/contexto |
| `/api/chat-v2/produtos/` | GET | Lista produtos disponiveis |
| `/api/chat-v2/sessao/<session_id>/` | GET | Info da sessao |
| `/api/chat-v2/sessao/<session_id>/mensagens/` | GET | Historico de mensagens |
| `/api/chat-v2/finalizar/` | POST | Finaliza sessao |

---

## 5. Utilitarios

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/extract-pdf/` | POST | Extrai texto de PDF |
| `/api/fluxograma-from-pdf/` | POST | Gera fluxograma a partir de PDF |
| `/api/chat-recepcao/` | POST | Chat do Portal (triagem) |
| `/metrics/` | GET | Metricas Prometheus |

---

## Resumo de Padroes

| Produto | Padrao | IDs | Conversacional |
|---------|--------|-----|----------------|
| POP | Chat-driven state machine | session_id (UUID) | Sim (unico modo) |
| Riscos | REST CRUD | UUID | Nao |
| PE | REST + conversacional | int | Sim (/iniciar, /processar) |
| Chat V2 | Sessao unificada | session_id (UUID) | Sim |
| Portal | Chat simples | session_id | Sim |
