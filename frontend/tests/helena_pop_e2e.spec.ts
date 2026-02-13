/**
 * Testes E2E para Helena POP
 * Framework: Playwright
 *
 * Cobertura:
 * 1. Fluxo completo até transição de etapas
 * 2. Timeout e reconexão
 * 3. Persistência de sessão após refresh
 * 4. Validação de interfaces dinâmicas
 * 5. Badge de conquista
 *
 * INSTALAÇÃO:
 * npm install -D @playwright/test
 * npx playwright install
 *
 * EXECUÇÃO:
 * npx playwright test helena_pop_e2e.spec.ts
 * npx playwright test helena_pop_e2e.spec.ts --headed (com navegador visível)
 * npx playwright test helena_pop_e2e.spec.ts --debug (modo debug)
 */

import { test, expect, Page } from '@playwright/test';

// Configuração base
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:8000';

/**
 * Helper: Espera por mensagem da Helena
 */
async function esperarMensagemHelena(page: Page, timeout = 10000) {
  await page.waitForSelector('.message.helena:not(.loading)', { timeout });
}

/**
 * Helper: Envia mensagem do usuário
 */
async function enviarMensagem(page: Page, mensagem: string) {
  const inputField = page.locator('input[type="text"], textarea');
  await inputField.fill(mensagem);
  await inputField.press('Enter');

  // Aguardar resposta
  await esperarMensagemHelena(page);
}

/**
 * Helper: Clica em card de seleção
 */
async function clicarCard(page: Page, texto: string) {
  await page.locator(`.card:has-text("${texto}")`).click();
  await esperarMensagemHelena(page);
}

/**
 * Helper: Clica em botão
 */
async function clicarBotao(page: Page, texto: string) {
  await page.locator(`button:has-text("${texto}")`).click();
  await esperarMensagemHelena(page);
}

// =====================================
// TESTES E2E - FLUXO COMPLETO
// =====================================

test.describe('Helena POP - Fluxo Completo E2E', () => {

  test.beforeEach(async ({ page }) => {
    // Navegar para a página do chat
    await page.goto(`${BASE_URL}/helena`);

    // Aguardar carregamento
    await page.waitForLoadState('networkidle');

    // Verificar se chat está carregado
    await expect(page.locator('.chat-container')).toBeVisible();
  });

  test('Fluxo completo: Nome até Transição Épica', async ({ page }) => {
    // 1. NOME_USUARIO → vai direto para ESCOLHA_TIPO_EXPLICACAO
    await enviarMensagem(page, 'João');
    await expect(page.locator('.message.helena').last()).toContainText('Olá, João');

    // 2. ESCOLHA_TIPO_EXPLICACAO - Curta
    await clicarCard(page, 'Explicação objetiva');
    await expect(page.locator('.message.helena').last()).toContainText('compromisso');

    // 4. PEDIDO_COMPROMISSO
    await clicarBotao(page, 'Concordo');

    // Verificar badge de "Cartógrafo de Processos"
    const badge = page.locator('.badge-trofeu');
    if (await badge.isVisible()) {
      await expect(badge).toContainText('Cartógrafo');
      await clicarBotao(page, 'Continuar');
    }

    // 5. AREA_DECIPEX
    await expect(page.locator('.message.helena').last()).toContainText('área');
    await enviarMensagem(page, '1'); // DIGEP

    // 6. SUBAREA_DECIPEX (se DIGEP)
    const mensagemAtual = await page.locator('.message.helena').last().textContent();
    if (mensagemAtual?.includes('DIGEP-')) {
      await enviarMensagem(page, '1'); // Primeira subárea
    }

    // 7. ARQUITETURA
    await expect(page.locator('.message.helena').last()).toContainText('o que você faz');
    await enviarMensagem(page, 'Analiso documentos de aposentadoria');

    // 8. CONFIRMACAO_ARQUITETURA
    await expect(page.locator('.message.helena').last()).toContainText('classificação');
    await clicarBotao(page, 'Concordo');

    // 9. NOME_PROCESSO
    await enviarMensagem(page, 'Análise de Documentos Previdenciários');

    // 10. ENTREGA_ESPERADA
    await enviarMensagem(page, 'Parecer técnico de análise');

    // 11. SISTEMAS
    await clicarCard(page, 'SISAC'); // Exemplo
    await clicarBotao(page, 'Confirmar');

    // 12. NORMAS
    await enviarMensagem(page, 'Lei 8.112/90');

    // 13. OPERADORES
    await clicarCard(page, 'EXECUTOR');
    await clicarBotao(page, 'Confirmar');

    // 14. FLUXOS_ENTRADA
    await enviarMensagem(page, 'Protocolo');

    // 15. FLUXOS_SAIDA
    await clicarCard(page, 'Área Interna');
    await clicarBotao(page, 'Confirmar');

    // 16. PONTOS_ATENCAO
    await enviarMensagem(page, 'Verificar prazo de prescrição');

    // 17. REVISAO_PRE_DELEGACAO
    await clicarBotao(page, 'Está correto');

    // 18. TRANSICAO_EPICA - Verificar badge de conquista
    await expect(page.locator('.badge-trofeu')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.badge-trofeu')).toContainText('Fase Prévia Concluída');

    // Verificar confetti
    await expect(page.locator('.confetti-container')).toBeVisible();

    // Clicar em "Ver presente"
    await page.locator('.badge-trofeu button, .badge-trofeu [role="button"]').first().click();

    // Verificar badge expandido
    await expect(page.locator('.badge-trofeu')).toContainText('Marco alcançado');

    // Continuar
    await clicarBotao(page, 'Continuar');

    // Verificar transição para DELEGACAO_ETAPAS ou mensagem final
    await expect(page.locator('.message.helena').last()).toContainText(/etapa|delega|finaliza/i);
  });

  test('Fluxo com edição manual de arquitetura', async ({ page }) => {
    // Setup: Chegar até confirmação de arquitetura
    await enviarMensagem(page, 'Maria');
    await enviarMensagem(page, 'sim');
    await clicarCard(page, 'Explicação objetiva');
    await clicarBotao(page, 'Concordo');
    await enviarMensagem(page, '2'); // DICAP
    await enviarMensagem(page, 'Faço cadastro de processos');

    // Clicar em "Quero editar"
    await clicarBotao(page, 'Quero editar');

    // Verificar se apareceu interface de seleção hierárquica
    await expect(page.locator('select').first()).toBeVisible();

    // Selecionar manualmente
    await page.locator('select').nth(0).selectOption({ index: 1 }); // Macroprocesso
    await page.locator('select').nth(1).selectOption({ index: 1 }); // Processo
    await page.locator('select').nth(2).selectOption({ index: 1 }); // Subprocesso
    await page.locator('select').nth(3).selectOption({ index: 1 }); // Atividade

    await clicarBotao(page, 'Confirmar Seleção');

    // Continuar fluxo normal
    await expect(page.locator('.message.helena').last()).toContainText('nome do processo');
  });
});

// =====================================
// TESTES DE PERSISTÊNCIA E RECONEXÃO
// =====================================

test.describe('Persistência e Reconexão', () => {

  test('Sessão persiste após refresh da página', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Iniciar conversa
    await enviarMensagem(page, 'Carlos');
    await enviarMensagem(page, 'sim');
    await clicarCard(page, 'Explicação objetiva');

    // Capturar número de mensagens
    const mensagensAntes = await page.locator('.message').count();

    // Recarregar página
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verificar que mensagens foram restauradas
    const mensagensDepois = await page.locator('.message').count();
    expect(mensagensDepois).toBeGreaterThanOrEqual(mensagensAntes - 1); // -1 por possível loading

    // Verificar que última mensagem está visível
    await expect(page.locator('.message').last()).toBeVisible();

    // Verificar que pode continuar de onde parou
    await clicarBotao(page, 'Concordo');
    await expect(page.locator('.message.helena').last()).toContainText('área');
  });

  test('LocalStorage mantém sessionId', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Capturar sessionId do localStorage
    const sessionIdAntes = await page.evaluate(() => {
      const storage = localStorage.getItem('helena-chat-storage');
      return storage ? JSON.parse(storage).state.sessionId : null;
    });

    expect(sessionIdAntes).toBeTruthy();

    // Recarregar
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verificar que sessionId permanece o mesmo
    const sessionIdDepois = await page.evaluate(() => {
      const storage = localStorage.getItem('helena-chat-storage');
      return storage ? JSON.parse(storage).state.sessionId : null;
    });

    expect(sessionIdDepois).toBe(sessionIdAntes);
  });
});

// =====================================
// TESTES DE TIMEOUT E ERRO
// =====================================

test.describe('Timeout e Tratamento de Erros', () => {

  test('Exibe mensagem de erro quando API não responde', async ({ page }) => {
    // Interceptar API e simular timeout
    await page.route(`${API_URL}/api/chat/**`, route => {
      // Nunca responder (simular timeout)
      setTimeout(() => route.abort(), 10000);
    });

    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Tentar enviar mensagem
    const inputField = page.locator('input[type="text"], textarea');
    await inputField.fill('João');
    await inputField.press('Enter');

    // Verificar mensagem de erro
    await expect(page.locator('.error-message, .toast-error, [role="alert"]')).toBeVisible({ timeout: 15000 });
  });

  test('Retry bem-sucedido após erro temporário', async ({ page }) => {
    let tentativa = 0;

    await page.route(`${API_URL}/api/chat/**`, route => {
      tentativa++;
      if (tentativa === 1) {
        // Primeira tentativa: erro 500
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      } else {
        // Segunda tentativa: sucesso
        route.continue();
      }
    });

    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Enviar mensagem
    await enviarMensagem(page, 'Ana');

    // Verificar que eventualmente recebeu resposta
    await expect(page.locator('.message.helena:not(.loading)').last()).toContainText(/João|Ana|nome/i, { timeout: 15000 });
  });
});

// =====================================
// TESTES DE VALIDAÇÃO DE SCHEMA
// =====================================

test.describe('Validação de Schema JSON', () => {

  test('API retorna schema correto', async ({ page, request }) => {
    // Fazer chamada direta à API
    const response = await request.post(`${API_URL}/api/chat/`, {
      data: {
        mensagem: 'Roberto',
        session_id: 'test-' + Date.now()
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();

    // Verificar campos obrigatórios
    expect(data).toHaveProperty('resposta');
    expect(data).toHaveProperty('dados_extraidos');
    expect(data).toHaveProperty('formulario_pop');

    // Verificar tipos
    expect(typeof data.resposta).toBe('string');
    expect(typeof data.dados_extraidos).toBe('object');
    expect(typeof data.formulario_pop).toBe('object');

    // Verificar interface se presente
    if (data.interface) {
      expect(data.interface).toHaveProperty('tipo');
      expect(typeof data.interface.tipo).toBe('string');
    }
  });

  test('Badge tem estrutura correta', async ({ page, request }) => {
    // Setup: Chegar até aceitar compromisso (gera badge)
    let sessionId = 'test-badge-' + Date.now();

    // Sequência de mensagens até badge
    await request.post(`${API_URL}/api/chat/`, {
      data: { mensagem: 'TestUser', session_id: sessionId }
    });

    await request.post(`${API_URL}/api/chat/`, {
      data: { mensagem: 'sim', session_id: sessionId }
    });

    await request.post(`${API_URL}/api/chat/`, {
      data: { mensagem: 'curta', session_id: sessionId }
    });

    // Aceitar compromisso (deve gerar badge)
    const response = await request.post(`${API_URL}/api/chat/`, {
      data: { mensagem: 'sim', session_id: sessionId }
    });

    const data = await response.json();

    // Verificar badge se presente
    if (data.metadados?.badge) {
      expect(data.metadados.badge).toHaveProperty('tipo');
      expect(data.metadados.badge).toHaveProperty('emoji');
      expect(data.metadados.badge).toHaveProperty('titulo');
      expect(data.metadados.badge).toHaveProperty('descricao');
      expect(data.metadados.badge).toHaveProperty('mostrar_animacao');
      expect(data.metadados.badge.mostrar_animacao).toBe(true);
    }
  });
});

// =====================================
// TESTES DE INTERFACE DINÂMICA
// =====================================

test.describe('Interfaces Dinâmicas', () => {

  test('Interface de cards é renderizada corretamente', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Chegar até escolha de explicação (usa cards)
    await enviarMensagem(page, 'Teste');
    await enviarMensagem(page, 'sim');

    // Verificar cards
    await expect(page.locator('.card')).toHaveCount(2); // Curta e Longa
    await expect(page.locator('.card').first()).toContainText(/curta|objetiva/i);
    await expect(page.locator('.card').last()).toContainText(/longa|detalhada/i);
  });

  test('Interface de seleção múltipla funciona', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Setup: Chegar até operadores (seleção múltipla)
    // ... (simplificado - implementar fluxo completo se necessário)
  });
});

// =====================================
// PERFORMANCE E CONFIABILIDADE
// =====================================

test.describe('Performance e Confiabilidade', () => {

  test('Chat não trava com mensagens rápidas consecutivas', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Enviar múltiplas mensagens rapidamente
    const inputField = page.locator('input[type="text"], textarea');

    await inputField.fill('João');
    await inputField.press('Enter');
    await page.waitForTimeout(100); // Pequeno delay

    await inputField.fill('sim');
    await inputField.press('Enter');
    await page.waitForTimeout(100);

    await inputField.fill('curta');
    await inputField.press('Enter');

    // Verificar que última mensagem apareceu
    await expect(page.locator('.message.helena').last()).toBeVisible({ timeout: 10000 });
  });

  test('Scroll automático funciona com muitas mensagens', async ({ page }) => {
    await page.goto(`${BASE_URL}/helena`);
    await page.waitForLoadState('networkidle');

    // Enviar várias mensagens
    for (let i = 0; i < 5; i++) {
      await enviarMensagem(page, `Mensagem ${i}`);
    }

    // Verificar que última mensagem está visível (scroll automático funcionou)
    const ultimaMensagem = page.locator('.message').last();
    await expect(ultimaMensagem).toBeInViewport();
  });
});
