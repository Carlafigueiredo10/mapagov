#!/bin/bash
URL="http://localhost:8000/api/chat-v2/"

# Etapa 1
echo "=== ETAPA 1 ==="
R1=$(curl -s -X POST $URL -H "Content-Type: application/json" -d '{"mensagem":"Processo de compras"}')
SID=$(echo $R1 | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
echo "Session: $SID"
echo "Progresso:" $(echo $R1 | python -c "import sys,json; print(json.load(sys.stdin)['progresso'])")
echo ""

# Etapa 2
echo "=== ETAPA 2 ==="
R2=$(curl -s -X POST $URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Gestor aprova\",\"session_id\":\"$SID\"}")
echo "Progresso:" $(echo $R2 | python -c "import sys,json; print(json.load(sys.stdin)['progresso'])")
echo ""

# Etapa 3
echo "=== ETAPA 3 ==="
R3=$(curl -s -X POST $URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Compras executa\",\"session_id\":\"$SID\"}")
echo "Progresso:" $(echo $R3 | python -c "import sys,json; print(json.load(sys.stdin)['progresso'])")
echo ""

# Etapa 4
echo "=== ETAPA 4 ==="
R4=$(curl -s -X POST $URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Acompanhamento\",\"session_id\":\"$SID\"}")
echo "Progresso:" $(echo $R4 | python -c "import sys,json; print(json.load(sys.stdin)['progresso'])")
echo ""

# Etapa 5 (finalização)
echo "=== ETAPA 5 (FINAL) ==="
R5=$(curl -s -X POST $URL -H "Content-Type: application/json" -d "{\"mensagem\":\"Encerramento\",\"session_id\":\"$SID\"}")
echo "Resposta completa:"
echo $R5 | python -m json.tool 2>/dev/null || echo $R5
