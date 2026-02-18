# Sistema de Numeração Institucional (SNI) — MapaGov

## 1. Numeração de Áreas

Prefixo de área: **sempre 2 dígitos**.
Subárea: `AA.BB` (ex: `05.01`).

| Código | Nome | Prefixo |
|--------|------|---------|
| CGBEN | Coordenação Geral de Benefícios | 01 |
| CGPAG | Coordenação Geral de Pagamentos | 02 |
| COATE | Coordenação de Atendimento | 03 |
| CGGAF | Coordenação Geral de Gestão de Acervos Funcionais | 04 |
| DIGEP | Divisão de Pessoal dos Ex-Territórios | 05 |
| DIGEP-RO | DIGEP Rondônia | 05.01 |
| DIGEP-RR | DIGEP Roraima | 05.02 |
| DIGEP-AP | DIGEP Amapá | 05.03 |
| CGRIS | Coordenação Geral de Riscos e Controle | 06 |
| CGCAF | Coordenação Geral de Complementação da Folha | 07 |
| CGECO | Coordenação Geral de Extinção e Convênio | 08 |
| COADM | Coordenação de Apoio Administrativo | 09 |
| COGES | Coordenação de Gestão | 10 |
| CDGEP | Coordenação Geral dos Ex-Territórios | 11 |

Regras:
- Nunca usar `5.1` — sempre `05.01`
- Fonte de verdade: `documentos_base/areas_organizacionais.csv`
- Backend normaliza via `normalize_area_prefix()` em `processos/domain/governanca/normalize.py`

---

## 2. CAP — Código de Atividade (POP)

Formato:

```
AA.MM.PP.SS.III
```

| Segmento | Significado | Dígitos |
|----------|-------------|---------|
| AA | Área (prefixo) | 2 |
| MM | Macroprocesso | 2 |
| PP | Processo | 2 |
| SS | Subprocesso | 2 |
| III | Índice da atividade | 3 |

Exemplo:

```
01.02.03.04.108
│  │  │  │  └── Atividade 108 (primeira nova da área)
│  │  │  └──── Subprocesso 04
│  │  └─────── Processo 03
│  └────────── Macroprocesso 02
└──────────── Área 01 (CGBEN)
```

### Tipos de CAP

| Tipo | Origem | Faixa |
|------|--------|-------|
| Oficial | CSV `Arquitetura_DECIPEX_mapeada.csv` | 001–107 |
| Provisório | Gerado com lock transacional | 108+ |

### Composição em runtime

O CSV de arquitetura contém `Numero` = `1.1.1.1` (macro.processo.sub.atividade, sem padding).
O pipeline normaliza e concatena com o prefixo da área:

```python
from processos.domain.governanca.normalize import normalize_numero_csv, resolve_prefixo_cap

# numero_csv = "1.1.1.1" (do CSV, sem padding)
prefixo = resolve_prefixo_cap("DIGEP-RO", areas_map)  # "05" (área pai, nunca "05.01")
numero = normalize_numero_csv(numero_csv)               # "01.01.01.001"
cap = f"{prefixo}.{numero}"                             # "05.01.01.01.001"
```

Regras:
- `normalize_numero_csv()` converte `1.1.1.1` → `01.01.01.001` (MM.PP.SS.III)
- `resolve_prefixo_cap()` retorna área pai se subárea (DIGEP-RO → `05`, não `05.01`)
- CAP nunca embute subárea — subárea fica em campo separado (`area_codigo`)

---

## 3. CP — Código de Produto (não-POP)

Formato:

```
AA.PR.III        (área simples)
AA.BB.PR.III     (subárea)
```

Regex: `^\d{2}(?:\.\d{2})?\.\d{2}\.\d{3}$`

| Segmento | Significado | Dígitos |
|----------|-------------|---------|
| AA | Área (prefixo) | 2 |
| BB | Subárea (opcional) | 2 |
| PR | Código do produto | 2 |
| III | Sequência | 3 |

### Catálogo de produtos

| Produto | Código (PR) | Model |
|---------|-------------|-------|
| Análise de Riscos | 01 | `AnaliseRiscos` |
| Planejamento Estratégico | 02 | `PlanejamentoEstrategico` |

### Diferença CP vs CAP

| | CAP | CP |
|---|---|---|
| Subárea | Nunca embutida (usa área pai) | Incluída no prefixo |
| `resolve_prefixo_cap("DIGEP-RO")` | `"05"` | — |
| `resolve_prefixo_cp("DIGEP-RO")` | — | `"05.01"` |

### Composição em runtime

```python
from processos.domain.governanca.cp_generator import gerar_cp

gerar_cp("COATE", "01")     # "03.01.001"
gerar_cp("DIGEP-RO", "03")  # "05.01.03.001"
```

### Geração idempotente

1. Objeto criado com `codigo_cp=None`
2. CP gerado via `gerar_cp(area_codigo, produto_codigo)` com lock transacional
3. Aplicado com update atômico: `filter(pk=pk, codigo_cp__isnull=True).update(codigo_cp=cp)`
4. Request duplicado não gera segundo CP (idempotência)

Helper: `atribuir_cp_se_necessario(obj, area_codigo)` — em `cp_generator.py`.

### Controle transacional

Tabela `controle_indices_produto` (separada do CAP):

```python
with transaction.atomic():
    controle, _ = ControleIndicesProduto.objects.select_for_update().get_or_create(
        area_codigo=area_codigo,
        produto_codigo=produto_codigo,
        defaults={'ultimo_indice': 0}
    )
    seq = controle.ultimo_indice + 1
    controle.ultimo_indice = seq
    controle.save()
```

### UniqueConstraints

- **AnaliseRiscos**: `UNIQUE(codigo_cp) WHERE codigo_cp IS NOT NULL AND codigo_cp != ''`
- **PlanejamentoEstrategico**: `UNIQUE(codigo_cp) WHERE codigo_cp IS NOT NULL AND codigo_cp != '' AND status != 'cancelado'`

PE cancelado mantém CP no registro (auditoria), mas libera o código para reutilização.

### Endpoint de busca unificado

```
GET /api/produtos/busca/?codigo=03.01.001
```

Identifica formato automaticamente (CAP 5 segmentos vs CP 3-4 segmentos).
Retorna tipo, id, area_codigo, status, nome. Erros: 400 (formato inválido), 404 (não encontrado).

CAP e CP **nunca se misturam**:
- CAP identifica atividade institucional (POP)
- CP identifica produto institucional (não-POP)

---

## 4. Regras de Geração

- Todo registro tem **UUID técnico** (chave primária no banco)
- Códigos humanos (CAP, CP) são **Business Keys**
- Geração de CAP provisório usa `select_for_update()` para evitar race conditions
- Índice sequencial por área, iniciando em 108

---

## 5. Controle Transacional

Tabela `controle_indices`:

```sql
CREATE TABLE controle_indices (
    area_codigo VARCHAR(10) PRIMARY KEY,
    ultimo_indice INTEGER DEFAULT 107
);
```

Algoritmo:

```python
with transaction.atomic():
    controle = ControleIndices.objects.select_for_update().get(area_codigo='CGBEN')
    proximo = controle.ultimo_indice + 1  # 108, 109, ...
    controle.ultimo_indice = proximo
    controle.save()

cap = f"{prefixo_area}.{idx_macro:02d}.{idx_processo:02d}.{idx_sub:02d}.{proximo:03d}"
```

---

## 6. Governança e Versionamento

### Ciclo de vida

```
Sugerida → Validada → Publicada (injetada no CSV oficial)
                   → Rejeitada
```

### Versionamento CSV

```
Arquitetura_DECIPEX_vYYYYMMDD_HHMMSS_NNN.csv
```

Cada versão tem hash SHA256 e changelog JSON.

### Normalização

Funções em `processos/domain/governanca/normalize.py`:
- `normalize_area_prefix()` — normaliza prefixo de área
- `normalize_cap()` — normaliza primeiro segmento de um CAP
- `normalize_numero_csv()` — normaliza Numero do CSV para SNI
- `resolve_prefixo_cap()` — prefixo para CAP (área pai se subárea)
- `resolve_prefixo_cp()` — prefixo para CP (inclui subárea, fail-fast)

Usadas por: loaders, pipelines, migrações, cap_generator, cp_generator.

---

## Referências

- Normalização: [`processos/domain/governanca/normalize.py`](../processos/domain/governanca/normalize.py)
- Gerador CAP: [`processos/domain/governanca/cap_generator.py`](../processos/domain/governanca/cap_generator.py)
- Gerador CP: [`processos/domain/governanca/cp_generator.py`](../processos/domain/governanca/cp_generator.py)
- Controle CP: [`processos/models_new/controle_indices_produto.py`](../processos/models_new/controle_indices_produto.py)
- Busca unificada: [`processos/api/produtos_busca_api.py`](../processos/api/produtos_busca_api.py)
- Áreas CSV: [`documentos_base/areas_organizacionais.csv`](../documentos_base/areas_organizacionais.csv)
- Arquitetura CSV: [`documentos_base/Arquitetura_DECIPEX_mapeada.csv`](../documentos_base/Arquitetura_DECIPEX_mapeada.csv)
- Modelos: [`processos/models.py`](../processos/models.py)
- Pipeline: [`processos/domain/helena_mapeamento/busca_atividade_pipeline.py`](../processos/domain/helena_mapeamento/busca_atividade_pipeline.py)
- Testes CP: [`processos/tests/test_cp_generator.py`](../processos/tests/test_cp_generator.py)

---

**Versão**: 3.0 (SNI + CP)
**Data**: 2026-02-16
