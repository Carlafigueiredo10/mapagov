#!/usr/bin/env bash
# Script de build para Render - Frontend React + Backend Django

set -o errexit  # Sair em caso de erro

echo "======================================"
echo "🚀 Iniciando build do MapaGov"
echo "======================================"

# 1. Build do Frontend React
echo ""
echo "📦 Buildando frontend React..."
cd frontend
npm install  # Instala dependências do package.json
npm run build
cd ..

# 2. Instalar dependências Python
echo ""
echo "🐍 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Coletar arquivos estáticos
echo ""
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# 4. Executar migrações
echo ""
echo "🗄️  Executando migrações do banco de dados..."
python manage.py migrate --no-input

echo ""
echo "======================================"
echo "✅ Build concluído com sucesso!"
echo "======================================"
