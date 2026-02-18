# Exemplo Didático — Como pensar uma Etapa

> Antes de preencher, entenda a lógica.
> Uma etapa é sempre composta por:
>
> 1. **Ação principal** — o que é feito
> 2. **Verificações** — o que é conferido
> 3. **Decisão ou continuidade** — se o resultado muda o caminho
> 4. **Responsável e registros** — quem faz, com quais sistemas e documentos
>
> O exemplo abaixo usa um processo que todo servidor conhece: **análise de pedido de férias**.
> Cada campo mostra exatamente o que colocar — e como pensar antes de colocar.

---

## BLOCO 1 — O que é feito

> _"Descreva a ação principal desta etapa. Use verbo no infinitivo."_

| Campo | Preenchimento |
|-------|---------------|
| **Ação principal** | Analisar pedido de férias recebido pelo sistema |

A ação principal deve responder à pergunta: "O que é feito nesta etapa?"
Sempre no infinitivo: _Analisar_, _Conferir_, _Encaminhar_, _Registrar_...

> ❌ Errado: "Férias do servidor"  (não é ação, é assunto)
> ❌ Errado: "O analista verifica as férias"  (não está no infinitivo)
> ✅ Certo: "Analisar pedido de férias recebido pelo sistema"

**Atenção:** Evite dividir uma única ação em múltiplas etapas artificiais.
Cada etapa deve produzir um resultado verificável.
Se não há resultado distinto, não é etapa — é parte de outra.

---

## BLOCO 2 — O que é verificado / conferido

> _"Liste o que precisa ser checado ou conferido nesta etapa."_

| # | Verificação |
|---|-------------|
| 1 | Conferir saldo de férias disponível no sistema |
| 2 | Verificar compatibilidade do período com outros afastamentos |
| 3 | Confirmar ciência da chefia imediata no processo; (obs: sem ciência, não prosseguir) |

**Dica:** Use sempre a estrutura **verbo no infinitivo + objeto direto**.
Cada item é uma checagem específica. Se você faz 3 conferências, coloque 3 itens.
A observação entre parênteses é opcional — use para regras ou exceções importantes.

> ❌ Errado: "Verificar tudo" (genérico demais)
> ❌ Errado: "Conferir se o servidor tem saldo" (frase narrativa, não padrão)
> ✅ Certo: "Conferir saldo de férias disponível no sistema" (infinitivo + objeto)

---

## BLOCO 3 — Encerramento da etapa

> _"Esta etapa tem caminhos diferentes dependendo do resultado?"_

| Campo | Preenchimento |
|-------|---------------|
| **É condicional?** | ✅ Sim |
| **Tipo** | Binário (2 caminhos) |

### Antes da decisão

| Campo | Preenchimento |
|-------|---------------|
| **O que é feito antes de decidir?** | Consolidar resultado das verificações e definir encaminhamento |

Este campo não repete as verificações do Bloco 2.
Descreve a **ação-síntese** que consolida as conferências e define o encaminhamento.

> ❌ Errado: "Analisar a documentação e o saldo" (repete verificações)
> ✅ Certo: "Consolidar resultado das verificações e definir encaminhamento"

### Cenários

| Cenário | Se... | Então... |
|---------|-------|----------|
| **1.1** | Se documentação completa e saldo disponível | Deferir o pedido e registrar no sistema |
| **1.2** | Se documentação incompleta ou sem saldo | Devolver ao servidor com despacho de pendência |

### Subetapas do Cenário 1.1 (documentação OK)

| # | O que fazer |
|---|-------------|
| 1.1.1 | Abrir processo no SEI |
| 1.1.2 | Gerar despacho de deferimento |
| 1.1.3 | Registrar período no SIAPE |
| 1.1.4 | Notificar servidor e chefia |

### Subetapas do Cenário 1.2 (pendência)

| # | O que fazer |
|---|-------------|
| 1.2.1 | Gerar despacho de pendência no SEI |
| 1.2.2 | Devolver processo ao servidor para correção |

Marque "Sim" apenas quando a decisão gerar caminhos com **ações diferentes**.
Se o fluxo apenas continua, não é condicional — é continuidade linear.

> ❌ Errado: marcar condicional para etapa que sempre faz a mesma coisa
> ❌ Errado: "Se tudo certo → prosseguir" (continuidade não é decisão)
> ✅ Certo: dois ou mais caminhos com ações realmente distintas

---

## SEÇÃO COMPLEMENTAR — Responsável, sistemas, documentos e tempo

> _Estes campos ficam na seção que abre ao clicar para expandir._

### Responsável (operador)

| Campo | Preenchimento |
|-------|---------------|
| **Operador** | Analista de Gestão de Pessoas |

**Dica:** Coloque o cargo ou função, não o nome da pessoa.

> ❌ Errado: "Maria" ou "João da Silva"
> ✅ Certo: "Analista de Gestão de Pessoas", "Chefe de Seção", "Estagiário"

---

### Sistemas utilizados

| # | Sistema |
|---|---------|
| 1 | SEI |
| 2 | SIAPE |

**Dica:** Marque todos os sistemas que você abre ou consulta durante esta etapa.
Se usa um sistema que não está na lista, digite o nome e adicione.

---

### Documentos de entrada (o que você recebe / consulta)

| # | Documento |
|---|-----------|
| 1 | Requerimento de férias |
| 2 | Escala de férias do setor |

**Dica:** São os documentos que já existem quando você começa a etapa.
Pense: "o que preciso ter em mãos para começar?"

---

### Documentos de saída (o que você produz / gera)

| # | Documento |
|---|-----------|
| 1 | Despacho de deferimento ou pendência |
| 2 | Registro no SIAPE |

**Dica:** São os documentos que não existiam antes e passam a existir por causa desta etapa.
Pense: "o que eu produzi ao terminar?"

> ❌ Errado: repetir aqui os documentos de entrada
> ✅ Certo: apenas o que foi gerado/criado nesta etapa

---

### Tempo estimado

| Campo | Preenchimento |
|-------|---------------|
| **Tempo** | 30 minutos |

**Dica:** Quanto tempo leva para fazer esta etapa uma vez, em condições normais.
Não é o tempo total do processo — é só desta etapa.

---

## Como o sistema exibe esta etapa depois de preenchida

> _Isto é uma projeção de como o sistema monta a etapa a partir dos campos acima.
> Não é um modelo separado — é o resultado direto do que você preencheu._

```
Etapa 1 — Analisar pedido de férias recebido pelo sistema

  Verificações:
    1. Conferir saldo de férias disponível no sistema
    2. Verificar compatibilidade do período com outros afastamentos
    3. Confirmar ciência da chefia imediata no processo

  Encerramento: Condicional (binário)
    Síntese: Consolidar resultado das verificações e definir encaminhamento

    1.1  Se documentação completa e saldo disponível
         → Deferir o pedido e registrar no sistema
         1.1.1  Abrir processo no SEI
         1.1.2  Gerar despacho de deferimento
         1.1.3  Registrar período no SIAPE
         1.1.4  Notificar servidor e chefia

    1.2  Se documentação incompleta ou sem saldo
         → Devolver ao servidor com despacho de pendência
         1.2.1  Gerar despacho de pendência no SEI
         1.2.2  Devolver processo ao servidor para correção

  Operador:  Analista de Gestão de Pessoas
  Sistemas:  SEI, SIAPE
  Entrada:   Requerimento de férias, Escala de férias do setor
  Saída:     Despacho de deferimento ou pendência, Registro no SIAPE
  Tempo:     30 minutos
```

---

## Perguntas que o exemplo responde

| "Nossa, o que coloco aqui?" | Resposta rápida |
|-----------------------------|-----------------|
| Na **ação principal**? | Uma frase com verbo no infinitivo. O que você FAZ. |
| Nas **verificações**? | Cada conferência que você faz, uma por linha. |
| No **condicional**? | Só marque Sim se existem caminhos diferentes de verdade. |
| Nos **cenários**? | Complete: "Se [situação] → [o que acontece]". |
| Nas **subetapas**? | Os passos miúdos dentro de cada cenário. |
| No **operador**? | Cargo ou função, nunca nome de pessoa. |
| Nos **sistemas**? | Todo sistema que você abre na tela durante a etapa. |
| Nos **docs de entrada**? | O que você precisa ter em mãos para começar. |
| Nos **docs de saída**? | O que você produziu ao terminar. |
| No **tempo**? | Quanto leva para fazer esta etapa UMA vez. |
