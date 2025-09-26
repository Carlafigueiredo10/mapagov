import os
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
django.setup()

# Testar RAG
from processos.rag_indexer import RAGIndexer

print("Inicializando RAG...")
rag = RAGIndexer()
print("✅ RAG funcionando!")
print(f"📁 Diretório: {rag.persist_directory}")