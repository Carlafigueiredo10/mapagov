from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import json

class HelenaPOP:
    """Helena especializada em extrair informações para Procedimento Operacional Padrão"""
    
    CAMPOS_POP = {
        "nome_processo": {"valor": None, "estado": None},
        "macroprocesso": {"valor": None, "estado": None},
        "processo": {"valor": None, "estado": None},
        "entrega_esperada": {"valor": None, "estado": None},
        "dispositivos_normativos": {"valor": None, "estado": None},
        "sistemas_utilizados": {"valor": None, "estado": None},
        "operadores": {"valor": None, "estado": None},
        "etapas": {"valor": None, "estado": None},
        "documentos_utilizados": {"valor": None, "estado": None},
        "pontos_atencao": {"valor": None, "estado": None},
        "codigo_arquitetura": {"valor": None, "estado": None}
    }
    
    ORDEM_CAMPOS = [
        "nome_processo", "macroprocesso", "processo", "entrega_esperada",
        "operadores", "etapas", "sistemas_utilizados", "dispositivos_normativos",
        "documentos_utilizados", "pontos_atencao", "codigo_arquitetura"
    ]
    
    # Exemplos contextuais para ajudar o usuário
    EXEMPLOS_CAMPOS = {
        "macroprocesso": ["Gestão de Pessoas", "Gestão de Contratos", "Gestão Orçamentária", "Gestão de TI"],
        "operadores": ["Técnico Especializado", "Coordenador", "Analista", "Gestor"],
        "sistemas_utilizados": ["SEI", "SIGEPE", "SIAPE", "SouGov", "Comprasnet"]
    }
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.8,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.nome_usuario = None
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é Helena, consultora experiente em mapeamento de processos do setor público brasileiro.

SEU PAPEL:
- Seja consultiva, amigável e natural (nunca robótica)
- Faça perguntas abertas e ofereça exemplos quando relevante
- Use o conhecimento de GRC do setor público para SUGERIR, nunca ASSUMIR
- Adapte-se ao contexto que o usuário traz

PRIMEIRA INTERAÇÃO:
- Se não souber o nome: "Como gostaria de ser chamado(a)?"
- Com nome: Use naturalmente ("Perfeito, [nome]! Vamos começar?")

CAMPOS A COLETAR (nesta ordem):
1. nome_processo - Nome da atividade (ex: "Conceder auxílio", "Homologar licitação")
2. macroprocesso - Área ampla (ex: "Gestão de Pessoas", "Compras", "Orçamento")
3. processo - Subárea (ex: "Gestão de Benefícios", "Pregão Eletrônico")
4. entrega_esperada - Resultado concreto (ex: "Auxílio concedido", "Contrato assinado")
5. operadores - Quem faz (ex: "Técnico, Coordenador")
6. etapas - Passo a passo (numere: 1. Receber demanda, 2. Analisar...)
7. sistemas_utilizados - Ferramentas (ex: "SEI, SIGEPE")
8. dispositivos_normativos - Leis/normas (ex: "Lei 8.112/90, IN 97/2022")
9. documentos_utilizados - Docs necessários
10. pontos_atencao - Alertas importantes
11. codigo_arquitetura - Código (ex: "2.3.1" - pergunte por último)

COMO PERGUNTAR:
- Uma pergunta por vez, de forma conversacional
- Ofereça 2-3 exemplos quando ajudar: "Por exemplo: X, Y ou Z"
- Valide respostas: "Entendi! [resumo]. Está correto?"
- Se resposta vaga: peça mais detalhes naturalmente

CONTEXTO: {contexto_campos}
NOME USUÁRIO: {nome_usuario}

RESPONDA EM JSON:
{{
    "resposta": "mensagem natural e consultiva",
    "campo_preenchido": "campo ou null",
    "valor": "valor ou null",
    "progresso": "X/11"
}}"""),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt | self.llm
        self.dados_coletados = self.CAMPOS_POP.copy()
        self.historico = []
    
    def processar_mensagem(self, mensagem_usuario):
        """Processa mensagem de forma consultiva"""
        try:
            # 1. PERGUNTAR NOME (primeira vez)
            if not self.nome_usuario:
                palavras = mensagem_usuario.strip().split()
                if len(palavras) <= 3 and len(palavras[0]) > 2:
                    self.nome_usuario = palavras[0].capitalize()
                    return {
                        "resposta": f"Prazer, {self.nome_usuario}! Vamos mapear um processo? Me conte: qual atividade você quer documentar?",
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": "0/11",
                        "tipo_resposta": "ASK"
                    }
                else:
                    return {
                        "resposta": "Olá! Antes de começar, como gostaria de ser chamado(a)?",
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": "0/11",
                        "tipo_resposta": "ASK"
                    }
            
            # 2. PROCESSAR NORMALMENTE
            self.historico.append({"role": "user", "content": mensagem_usuario})
            
            # Contexto enriquecido
            contexto = self._construir_contexto()
            proximo = self._proximo_campo_vazio()
            
            if proximo and proximo in self.EXEMPLOS_CAMPOS:
                exemplos = ", ".join(self.EXEMPLOS_CAMPOS[proximo][:3])
                contexto += f"\n\nSUGESTÃO: Para '{proximo}', ofereça exemplos como: {exemplos}"
            
            # Chamar LLM
            resposta = self.chain.invoke({
                "input": mensagem_usuario,
                "contexto_campos": contexto,
                "nome_usuario": self.nome_usuario or "você"
            })
            
            resposta_texto = resposta.content if hasattr(resposta, 'content') else str(resposta)
            self.historico.append({"role": "assistant", "content": resposta_texto})
            
            # Parse JSON
            try:
                dados = json.loads(resposta_texto)
                
                # Atualizar campo
                if dados.get('campo_preenchido') and dados.get('valor'):
                    campo = dados['campo_preenchido']
                    if campo in self.dados_coletados:
                        self.dados_coletados[campo]['valor'] = dados['valor']
                        self.dados_coletados[campo]['estado'] = 'confirmado'
                
                progresso = self._calcular_progresso()
                
                return {
                    "resposta": dados.get('resposta', resposta_texto),
                    "dados_extraidos": {dados['campo_preenchido']: dados['valor']} if dados.get('campo_preenchido') else {},
                    "conversa_completa": progresso['confirmados'] == 11,
                    "progresso": f"{progresso['confirmados']}/11",
                    "tipo_resposta": "FILL" if dados.get('campo_preenchido') else "ASK"
                }
                
            except json.JSONDecodeError:
                # Fallback: tentar extrair da resposta natural
                return {
                    "resposta": resposta_texto,
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": f"{self._calcular_progresso()['confirmados']}/11",
                    "tipo_resposta": "ASK"
                }
                
        except Exception as e:
            print(f"🔴 ERRO: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "resposta": f"Desculpe {self.nome_usuario or 'colega'}, tive um problema técnico. Pode repetir?",
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/11",
                "tipo_resposta": "ERROR"
            }
    
    def _construir_contexto(self):
        """Contexto dos campos já coletados"""
        confirmados = [f"✅ {c}: {d['valor']}" for c, d in self.dados_coletados.items() if d['estado'] == 'confirmado']
        
        contexto = "CAMPOS JÁ COLETADOS:\n" + "\n".join(confirmados) if confirmados else "Nenhum campo confirmado ainda"
        
        proximo = self._proximo_campo_vazio()
        if proximo:
            contexto += f"\n\n📍 PRÓXIMO: Pergunte sobre '{proximo}' de forma natural"
        
        return contexto
    
    def _proximo_campo_vazio(self):
        """Próximo campo na ordem"""
        for campo in self.ORDEM_CAMPOS:
            if self.dados_coletados[campo]['estado'] != 'confirmado':
                return campo
        return None
    
    def _calcular_progresso(self):
        """Calcula progresso"""
        confirmados = sum(1 for d in self.dados_coletados.values() if d['estado'] == 'confirmado')
        return {
            'confirmados': confirmados,
            'vazios': 11 - confirmados
        }
    
    def obter_dados_pop(self):
        """Retorna dados coletados"""
        return {campo: dados['valor'] for campo, dados in self.dados_coletados.items() if dados['valor']}
    
    def gerar_pop_completo(self):
        """Gera POP formatado"""
        d = self.dados_coletados
        
        return f"""
PROCEDIMENTO OPERACIONAL PADRÃO (POP)

Código: {d.get('codigo_arquitetura', {}).get('valor', 'A definir')}

MACROPROCESSO: {d.get('macroprocesso', {}).get('valor', 'Não informado')}
PROCESSO: {d.get('processo', {}).get('valor', 'Não informado')}
ATIVIDADE: {d.get('nome_processo', {}).get('valor', 'Não informado')}

1. ENTREGA ESPERADA:
{d.get('entrega_esperada', {}).get('valor', 'Não informado')}

2. DISPOSITIVOS NORMATIVOS:
{d.get('dispositivos_normativos', {}).get('valor', 'Não informado')}

3. SISTEMAS UTILIZADOS:
{d.get('sistemas_utilizados', {}).get('valor', 'Não informado')}

4. OPERADORES:
{d.get('operadores', {}).get('valor', 'Não informado')}

5. TAREFAS/ETAPAS:
{d.get('etapas', {}).get('valor', 'Não informado')}

6. DOCUMENTOS:
{d.get('documentos_utilizados', {}).get('valor', 'Não informado')}

7. PONTOS DE ATENÇÃO:
{d.get('pontos_atencao', {}).get('valor', 'Não informado')}
"""