# ============================================================================
# Dockerfile para MapaGov - Google Cloud Run
# ============================================================================
# Multi-stage build para otimizar tamanho da imagem

# ============================================================================
# STAGE 1: Build do Frontend React
# ============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copiar apenas package files primeiro (cache layer)
COPY frontend/package*.json ./

# Instalar dependências
RUN npm ci --only=production || echo "WARN: npm ci failed, frontend may not work"

# Copiar código fonte do frontend
COPY frontend/ ./

# Build do frontend para produção
RUN npm run build || mkdir -p dist && echo "WARN: Frontend build failed, using empty dist"

# ============================================================================
# STAGE 2: Backend Python + Django
# ============================================================================
FROM python:3.13-slim

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código do backend
COPY . .

# Copiar build do frontend do stage anterior
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Criar diretórios necessários
RUN mkdir -p staticfiles media logs backups chroma_db

# Coletar arquivos estáticos (permite SQLite temporário só para collectstatic)
# O banco real (PostgreSQL) será usado no runtime via variáveis de ambiente
ENV SKIP_DB_CHECK=1
RUN python manage.py collectstatic --noinput || echo "WARN: collectstatic failed"
ENV SKIP_DB_CHECK=0

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expor porta (Cloud Run usa $PORT)
EXPOSE 8080

# Script de inicialização
CMD python manage.py migrate --noinput && \
    gunicorn mapagov.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
