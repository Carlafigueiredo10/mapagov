#!/usr/bin/env bash
# Script de build para Render - Frontend React + Backend Django

set -o errexit  # Sair em caso de erro

echo "======================================"
echo "Iniciando build do MapaGov"
echo "======================================"

# 1. Build do Frontend React
echo ""
echo "Buildando frontend React..."
cd frontend
npm install
npm run build
cd ..

# 2. Instalar dependencias Python
echo ""
echo "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Coletar arquivos estaticos
echo ""
echo "Coletando arquivos estaticos..."
python manage.py collectstatic --no-input

# 4. Executar migracoes
echo ""
echo "Executando migracoes do banco de dados..."
python manage.py migrate --no-input

echo ""
echo "======================================"
echo "Build concluido com sucesso!"
echo "======================================"
