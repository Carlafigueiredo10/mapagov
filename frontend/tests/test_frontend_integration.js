/**
 * Teste de Integração Frontend → Backend
 *
 * Simula requisições que o frontend React faria para o endpoint /api/chat-v2/
 * Valida o fluxo completo:
 * - Frontend envia mensagem
 * - HelenaCore processa
 * - SessionManager persiste
 * - Resposta retorna com metadados corretos
 */

const baseURL = 'http://localhost:8000';

async function testeIntegracaoCompleta() {
    console.log('🚀 Iniciando Teste de Integração Frontend → Backend\n');

    let sessionId = null;

    // ===== ETAPA 1 =====
    console.log('📝 ETAPA 1: Enviando primeira mensagem...');
    const resp1 = await fetch(`${baseURL}/api/chat-v2/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: 'Quero mapear o processo de compras'
        })
    });

    const data1 = await resp1.json();
    sessionId = data1.session_id;

    console.log('✅ Session ID:', sessionId.substring(0, 8) + '...');
    console.log('✅ Agente:', data1.metadados.agent_name, 'v' + data1.metadados.agent_version);
    console.log('✅ Progresso:', data1.progresso);
    console.log('✅ Resposta:', data1.resposta.substring(0, 80) + '...\n');

    // ===== ETAPA 2 =====
    console.log('📝 ETAPA 2: Continuando na mesma sessão...');
    const resp2 = await fetch(`${baseURL}/api/chat-v2/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: 'Gestor aprova a solicitação',
            session_id: sessionId
        })
    });

    const data2 = await resp2.json();
    console.log('✅ Session mantida:', data2.session_id === sessionId ? 'SIM ✓' : 'NÃO ✗');
    console.log('✅ Progresso:', data2.progresso);
    console.log('✅ Resposta:', data2.resposta.substring(0, 80) + '...\n');

    // ===== ETAPA 3 =====
    console.log('📝 ETAPA 3: Avançando...');
    const resp3 = await fetch(`${baseURL}/api/chat-v2/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: 'Setor de compras executa a compra',
            session_id: sessionId
        })
    });

    const data3 = await resp3.json();
    console.log('✅ Progresso:', data3.progresso);
    console.log('✅ Resposta:', data3.resposta.substring(0, 80) + '...\n');

    // ===== ETAPA 4 =====
    console.log('📝 ETAPA 4: Quase lá...');
    const resp4 = await fetch(`${baseURL}/api/chat-v2/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: 'Acompanhamento semanal',
            session_id: sessionId
        })
    });

    const data4 = await resp4.json();
    console.log('✅ Progresso:', data4.progresso);
    console.log('✅ Resposta:', data4.resposta.substring(0, 80) + '...\n');

    // ===== ETAPA 5 (FINALIZAÇÃO) =====
    console.log('📝 ETAPA 5: Finalizando...');
    const resp5 = await fetch(`${baseURL}/api/chat-v2/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: 'Processo encerrado',
            session_id: sessionId
        })
    });

    const data5 = await resp5.json();
    console.log('✅ Progresso:', data5.progresso);
    console.log('✅ Sugestão de contexto:', data5.sugerir_contexto || 'Nenhuma');
    console.log('✅ Resposta completa:', data5.resposta.includes('Parabéns') ? 'SIM ✓' : 'NÃO ✗');
    console.log('✅ Resumo das 5 etapas:', data5.resposta.includes('Resumo Final') ? 'SIM ✓' : 'NÃO ✗\n');

    // ===== VALIDAÇÃO FINAL =====
    console.log('\n🎯 RESULTADO FINAL:\n');

    const validacoes = [
        { nome: 'Session ID mantida', ok: data2.session_id === sessionId && data3.session_id === sessionId },
        { nome: 'Progresso 100%', ok: data5.progresso === '5/5 (100%) [##########]' },
        { nome: 'Sugestão de contexto', ok: data5.sugerir_contexto === 'pop' },
        { nome: 'Metadados presentes', ok: data5.metadados && data5.metadados.agent_version },
        { nome: 'Resposta de finalização', ok: data5.resposta.includes('Parabéns') },
        { nome: 'Resumo das etapas', ok: data5.resposta.includes('Resumo Final') }
    ];

    validacoes.forEach(v => {
        console.log(`  ${v.ok ? '✅' : '❌'} ${v.nome}`);
    });

    const todasOk = validacoes.every(v => v.ok);
    console.log(`\n${todasOk ? '🎉 TODOS OS TESTES PASSARAM!' : '⚠️ ALGUNS TESTES FALHARAM'}\n`);

    if (todasOk) {
        console.log('🚀 FASE 1 VALIDADA COM SUCESSO END-TO-END!');
        console.log('   Frontend → /api/chat-v2/ → HelenaCore → SessionManager → PostgreSQL ✓\n');
    }

    return todasOk;
}

// Executar teste
testeIntegracaoCompleta()
    .then(sucesso => process.exit(sucesso ? 0 : 1))
    .catch(erro => {
        console.error('❌ Erro no teste:', erro);
        process.exit(1);
    });
