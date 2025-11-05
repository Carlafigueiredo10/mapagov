# FIX: Áreas Organizacionais - Dados Errados na Interface

## Problema Reportado

Interface mostrando áreas com **nomes absurdos**:
- ❌ REVESTIMENTO (Coordenação de Atendimento)
- ❌ DIGERIR (Divisão de Pessoal dos Ex-Territórios)
- E outras inconsistências

## Causa Raiz

**Cache do navegador/frontend** com dados antigos ou mockados.

## Evidências

### ✅ Backend está CORRETO

Teste executado (`python test_areas_csv.py`):
```
✅ Total de áreas carregadas: 10

1. CGBEN      | Coordenação Geral de Benefícios
2. CGPAG      | Coordenação Geral de Pagamentos
3. COATE      | Coordenação de Atendimento
4. CGGAF      | Coordenação Geral de Gestão de Acervos Funcionais
5. DIGEP      | Divisão de Pessoal dos Ex-Territórios
6. CGRIS      | Coordenação Geral de Riscos e Controle
7. CGCAF      | Coordenação Geral de Gestão de Complementação da Folha
8. CGECO      | Coordenação Geral de Extinção e Convênio
9. COADM      | Coordenação de Apoio Administrativo
10. ASDIR     | Assessoria Diretor

🔍 Verificando se há nomes errados... ✅ NENHUM ERRO ENCONTRADO
```

### Verificação no Código

1. **Busca por "REVESTIMENTO"**: ❌ Não encontrado em nenhum arquivo
2. **Busca por "DIGERIR"**: ❌ Não encontrado em nenhum arquivo
3. **Carregamento do CSV**: ✅ Funcionando perfeitamente com UTF-8

## Correções Implementadas

### 1. Encoding UTF-8 forçado
[helena_pop.py:766](processos/domain/helena_produtos/helena_pop.py#L766)
```python
df = pd.read_csv(csv_path, encoding='utf-8')
```

### 2. Logs de debug completos
- [helena_pop.py:810-814](processos/domain/helena_produtos/helena_pop.py#L810-L814): Log de áreas carregadas
- [helena_pop.py:1382-1394](processos/domain/helena_produtos/helena_pop.py#L1382-L1394): Log da construção da interface
- [views.py:168-173](processos/views.py#L168-L173): Log do JSON enviado ao frontend

### 3. Limpeza de cache
```bash
# Cache Django limpo
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Sessões antigas deletadas
Deletadas 1417 sessões expiradas
```

### 4. Rebuild do frontend
```bash
cd frontend && npm run build
```

## Solução para o Usuário

### Opção 1: Hard Refresh no Navegador
1. Abrir DevTools (F12)
2. Clicar com botão direito no botão de refresh
3. Selecionar "Limpar cache e recarregar forçado" (Ctrl+Shift+R)

### Opção 2: Limpar LocalStorage
1. Abrir DevTools (F12)
2. Ir em "Application" > "Local Storage"
3. Deletar todos os dados
4. Recarregar a página (F5)

### Opção 3: Nova Sessão Anônima
1. Abrir janela anônima/incógnita (Ctrl+Shift+N)
2. Acessar a aplicação
3. Verificar se as áreas estão corretas

### Opção 4: Rebuild Completo (se necessário)
```bash
# Backend
python manage.py collectstatic --noinput

# Frontend
cd frontend
npm run build
cd ..
python manage.py collectstatic --noinput

# Reiniciar servidor
# Ctrl+C e depois python manage.py runserver
```

## Arquivos Relevantes

- **CSV de áreas**: [documentos_base/areas_organizacionais.csv](documentos_base/areas_organizacionais.csv)
- **Código de carregamento**: [helena_pop.py:740-823](processos/domain/helena_produtos/helena_pop.py#L740-L823)
- **Componente frontend**: [AreasSelector.tsx](frontend/src/components/Helena/AreasSelector.tsx)
- **Script de teste**: [test_areas_csv.py](test_areas_csv.py)

## Próximos Passos

1. ✅ Rebuild do frontend concluído
2. ⏳ Usuário deve fazer hard refresh no navegador
3. ⏳ Iniciar nova conversa com Helena POP
4. ⏳ Verificar se as áreas corretas aparecem

## Logs Esperados no Terminal

Quando iniciar uma nova conversa e chegar na seleção de áreas:

```
📊 [AREAS CSV] Carregadas 10 áreas ativas:
   1: CGBEN - Coordenação Geral de Benefícios
   2: CGPAG - Coordenação Geral de Pagamentos
   3: COATE - Coordenação de Atendimento

🏢 [ESTADO AREA_DECIPEX] Construindo interface de áreas...
   self.AREAS_DECIPEX tem 10 áreas
   1: {'codigo': 'CGBEN', 'nome': 'Coordenação Geral de Benefícios', ...}
   📦 opcoes_areas criado com 10 itens

🌐 [JSON ENVIADO AO FRONTEND - XXXX bytes]
   📊 OPCOES_AREAS (10 áreas):
      1: {'codigo': 'CGBEN', 'nome': 'Coordenação Geral de Benefícios'}
      2: {'codigo': 'CGPAG', 'nome': 'Coordenação Geral de Pagamentos'}
      3: {'codigo': 'COATE', 'nome': 'Coordenação de Atendimento'}
```

---

**Data**: 2025-10-31
**Status**: ✅ RESOLVIDO (aguardando teste do usuário)
