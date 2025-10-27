#!/bin/bash
BASE_URL="http://localhost:8000/api/chat-v2/"

# Nova sessão
SESSION=$(curl -s -X POST $BASE_URL -H "Content-Type: application/json" -d '{"mensagem":"Mapear processo de compras"}' | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

echo "Session criada: $SESSION"
echo ""

# Etapa 2
echo "Enviando Etapa 2..."
curl -s -X POST $BASE_URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Gestor aprova solicitacao\",\"session_id\":\"$SESSION\"}" | python -c "import sys,json; d=json.load(sys.stdin); print('Progresso:', d.get('progresso', 'N/A'))"
echo ""

# Etapa 3
echo "Enviando Etapa 3..."
curl -s -X POST $BASE_URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Setor de compras executa\",\"session_id\":\"$SESSION\"}" | python -c "import sys,json; d=json.load(sys.stdin); print('Progresso:', d.get('progresso', 'N/A'))"
echo ""

# Etapa 4
echo "Enviando Etapa 4..."
curl -s -X POST $BASE_URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Acompanhamento semanal\",\"session_id\":\"$SESSION\"}" | python -c "import sys,json; d=json.load(sys.stdin); print('Progresso:', d.get('progresso', 'N/A'))"
echo ""

# Etapa 5
echo "Enviando Etapa 5..."
curl -s -X POST $BASE_URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Processo encerrado\",\"session_id\":\"$SESSION\"}" | python -c "import sys,json; d=json.load(sys.stdin); print('Progresso:', d.get('progresso', 'N/A')); print('Sugestao:', d.get('sugerir_contexto', 'Nenhuma'))"

