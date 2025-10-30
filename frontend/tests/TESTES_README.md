# Guia de Testes - Helena POP v2.0

Este documento contém instruções completas para executar todos os testes da aplicação Helena POP.

## Índice

1. [Testes Unitários (Backend)](#testes-unitários-backend)
2. [Testes E2E (Frontend)](#testes-e2e-frontend)
3. [Cobertura de Testes](#cobertura-de-testes)
4. [CI/CD](#cicd)

---

## Testes Unitários (Backend)

### Tecnologia: pytest + Django TestCase

### Instalação

```bash
# Já está instalado no requirements.txt
pip install pytest pytest-django
```

### Execução

#### Rodar todos os testes do Helena POP

```bash
python manage.py test processos.tests_helena_pop --verbosity=2
```

#### Rodar teste específico

```bash
python manage.py test processos.tests_helena_pop.TestPOPStateMachine.test_estado_inicial
```

#### Rodar com pytest (alternativa)

```bash
pytest processos/tests_helena_pop.py -v
```

#### Rodar com coverage

```bash
# Instalar coverage
pip install coverage

# Executar com coverage
coverage run --source='processos' manage.py test processos.tests_helena_pop
coverage report
coverage html  # Gera relatório HTML em htmlcov/index.html
```

### Estrutura dos Testes Unitários

| Classe de Teste | Descrição | Quantidade |
|----------------|-----------|------------|
| `TestPOPStateMachine` | Testa serialização e estado inicial | 2 testes |
| `TestTransicoesEstado` | Testa todas as 21 transições de estado | 8 testes |
| `TestValidacaoDados` | Valida entrada de dados (nome, JSON, etc) | 4 testes |
| `TestSchemaJSON` | Valida schema das respostas da API | 3 testes |
| `TestIntegracaoHelenaAjuda` | Testa fallback IA vs CSV | 2 testes |
| `TestPersistenciaSessao` | Testa Django session persistence | 2 testes |
| `TestTimeout` | Simula timeout de sessão | 1 teste |
| **TOTAL** | | **23 testes** |

### Fixtures Disponíveis

```python
# Fixtures pytest
@pytest.fixture
def helena_instancia():
    """Instância do HelenaPOP"""
    return HelenaPOP()

@pytest.fixture
def state_machine_limpa():
    """State machine vazia"""
    return POPStateMachine()

@pytest.fixture
def state_machine_populada():
    """State machine com dados de exemplo"""
    # ... retorna SM populada
```

### Exemplos de Uso

```python
def test_meu_teste(helena_instancia, state_machine_limpa):
    resultado = helena_instancia.processar("João", state_machine_limpa.to_dict())
    assert 'resposta' in resultado
```

---

## Testes E2E (Frontend)

### Tecnologia: Playwright

### Instalação

```bash
cd frontend

# Instalar Playwright
npm install -D @playwright/test

# Instalar navegadores
npm run test:install
# ou
npx playwright install
```

### Execução

#### Rodar todos os testes E2E

```bash
npm run test:e2e
```

#### Rodar com UI interativa (recomendado para desenvolvimento)

```bash
npm run test:e2e:ui
```

#### Rodar com navegador visível (headed mode)

```bash
npm run test:e2e:headed
```

#### Rodar em modo debug (passo a passo)

```bash
npm run test:e2e:debug
```

#### Rodar teste específico

```bash
npx playwright test helena_pop_e2e.spec.ts -g "Fluxo completo"
```

#### Rodar apenas em um navegador

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Estrutura dos Testes E2E

| Describe | Descrição | Quantidade |
|----------|-----------|------------|
| `Helena POP - Fluxo Completo E2E` | Fluxo de ponta a ponta até transição épica | 2 testes |
| `Persistência e Reconexão` | LocalStorage, refresh, restore | 2 testes |
| `Timeout e Tratamento de Erros` | API timeout, retry | 2 testes |
| `Validação de Schema JSON` | Schema da API, badge | 2 testes |
| `Interfaces Dinâmicas` | Cards, seleção múltipla | 2 testes |
| `Performance e Confiabilidade` | Mensagens rápidas, scroll | 2 testes |
| **TOTAL** | | **12 testes** |

### Helpers Disponíveis

```typescript
// Espera mensagem da Helena
await esperarMensagemHelena(page);

// Envia mensagem
await enviarMensagem(page, 'João');

// Clica em card
await clicarCard(page, 'Explicação objetiva');

// Clica em botão
await clicarBotao(page, 'Concordo');
```

### Relatórios

Após rodar os testes, abra o relatório HTML:

```bash
npx playwright show-report
```

---

## Cobertura de Testes

### Backend (Unitário)

#### Estados da Máquina Cobertos: 21/21 ✅

1. ✅ NOME_USUARIO
2. ✅ CONFIRMA_NOME
3. ✅ ESCOLHA_TIPO_EXPLICACAO
4. ✅ EXPLICACAO_LONGA
5. ✅ PEDIDO_COMPROMISSO
6. ✅ AREA_DECIPEX
7. ✅ SUBAREA_DECIPEX
8. ✅ ARQUITETURA
9. ✅ CONFIRMACAO_ARQUITETURA
10. ✅ SELECAO_HIERARQUICA
11. ✅ NOME_PROCESSO
12. ✅ ENTREGA_ESPERADA
13. ✅ SISTEMAS
14. ✅ NORMAS
15. ✅ OPERADORES
16. ✅ FLUXOS_ENTRADA
17. ✅ FLUXOS_SAIDA
18. ✅ PONTOS_ATENCAO
19. ✅ REVISAO_PRE_DELEGACAO
20. ✅ TRANSICAO_EPICA
21. ✅ DELEGACAO_ETAPAS

#### Validações Cobertas

- ✅ Nome válido vs inválido
- ✅ JSON array (operadores)
- ✅ JSON estruturado (fluxos de saída)
- ✅ Serialização/deserialização
- ✅ Persistência de sessão
- ✅ Timeout

#### Integrações Cobertas

- ✅ helena_ajuda_inteligente (fallback IA)
- ✅ CSV oficial (prioridade)
- ✅ Schema JSON completo
- ✅ Badge metadata

### Frontend (E2E)

#### Fluxos Cobertos

- ✅ Fluxo completo até Transição Épica
- ✅ Edição manual de arquitetura
- ✅ Refresh e restore de sessão
- ✅ LocalStorage persistence
- ✅ Timeout e retry
- ✅ Validação de schema via API
- ✅ Badge de conquista
- ✅ Interfaces dinâmicas (cards, seleção)
- ✅ Performance (mensagens rápidas)
- ✅ Scroll automático

---

## CI/CD

### GitHub Actions (exemplo)

Crie `.github/workflows/tests.yml`:

```yaml
name: Testes Automatizados

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test processos.tests_helena_pop --verbosity=2

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## Troubleshooting

### Backend

**Erro: Django settings not configured**

```bash
# Execute com manage.py
python manage.py test processos.tests_helena_pop
```

**Erro: ImportError models**

```bash
# Verifique DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=mapagovx.settings
```

### Frontend

**Erro: Cannot find module '@playwright/test'**

```bash
cd frontend
npm install -D @playwright/test
```

**Erro: Executable doesn't exist**

```bash
npx playwright install
```

**Erro: baseURL not accessible**

```bash
# Certifique-se que backend está rodando
python manage.py runserver

# Em outro terminal, rode frontend
cd frontend
npm run dev

# Depois execute testes
npm run test:e2e
```

---

## Comandos Rápidos

### Backend
```bash
# Rodar todos os testes
python manage.py test processos.tests_helena_pop

# Com coverage
coverage run manage.py test processos.tests_helena_pop
coverage report
```

### Frontend
```bash
# Instalar (primeira vez)
cd frontend
npm install -D @playwright/test
npm run test:install

# Rodar testes
npm run test:e2e

# Debug interativo
npm run test:e2e:ui
```

---

## Métricas de Sucesso

### Critérios de Aceitação

- ✅ Todos os 23 testes unitários passando
- ✅ Todos os 12 testes E2E passando
- ✅ Cobertura de código > 80%
- ✅ Todos os 21 estados testados
- ✅ Schema JSON validado
- ✅ Persistência funcionando
- ✅ Timeout tratado
- ✅ Fallback IA testado

---

## Próximos Passos

1. ✅ Testes unitários criados (23 testes)
2. ✅ Testes E2E criados (12 testes)
3. ⏳ Rodar em CI/CD
4. ⏳ Adicionar testes de carga (opcional)
5. ⏳ Adicionar testes de acessibilidade (opcional)

---

**Última atualização**: 27/10/2025
**Versão**: Helena POP v2.0
**Responsável**: Dev Senior contratado (FASE 5 completa)
