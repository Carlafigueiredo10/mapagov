# Analise de Riscos - Codigo Legacy (v1)

**Status:** ARQUIVADO - NAO USAR EM PRODUCAO

## Proposito

Esta pasta contem o codigo legado do modulo de Analise de Riscos, movido em 2026-01-29 para reescrita completa.

## Motivo da Deprecacao

- Imports quebrados para arquivos inexistentes (`z_md/helena_analise_riscos`)
- Multiplos formatos de dados incompativeis (frontend vs backend)
- Endpoint `/api/analyze-risks/` comentado/inexistente
- Abstrações legadas sem implementacao

## Referencia

- **Tag de snapshot:** `analise-riscos-legacy-v1`
- **Commit base:** b651578

## Estrutura

```
legacy/analise_riscos/
├── backend/           # Codigo Python (orquestrador, agente)
├── frontend/          # Componentes React/TypeScript
├── assets/            # Imagens
└── README.md          # Este arquivo
```

## Restauracao (se necessario)

```bash
git checkout analise-riscos-legacy-v1 -- processos/domain/helena_analise_riscos/
git checkout analise-riscos-legacy-v1 -- frontend/src/components/AnaliseRiscos/
# ... etc
```

## Proximos Passos

Nova implementacao sera criada do zero seguindo:
- Arquitetura limpa (Clean Architecture)
- Contratos bem definidos (OpenAPI + TypeScript)
- Testes desde o inicio
- Sem dependencias de codigo legado
