from dotenv import load_dotenv
load_dotenv()  # Carrega .env automaticamente

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def indexar_documentos(pasta="documentos_teste", biblioteca="documentos_produzidos"):
    """
    Indexa todos os PDFs de uma pasta no ChromaDB
    """
    # Configurar embeddings
    embeddings = OpenAIEmbeddings()
    
    # Configurar ChromaDB
    persist_directory = f"./chroma_db/{biblioteca}"
    
    # Splitter para dividir documentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # Listar PDFs
    pdfs = [f for f in os.listdir(pasta) if f.endswith('.pdf')]
    
    print(f"📚 Encontrados {len(pdfs)} PDFs para indexar")
    
    todos_docs = []
    
    for pdf in pdfs:
        caminho = os.path.join(pasta, pdf)
        print(f"📄 Processando: {pdf}")
        
        # Carregar PDF
        loader = PyPDFLoader(caminho)
        documentos = loader.load()
        
        # Dividir em chunks
        chunks = text_splitter.split_documents(documentos)
        
        # Adicionar metadata
        for chunk in chunks:
            chunk.metadata.update({
                "source": pdf,
                "biblioteca": biblioteca
            })
        
        todos_docs.extend(chunks)
        print(f"  ✅ {len(chunks)} chunks criados")
    
    # Criar/atualizar ChromaDB
    print(f"\n💾 Salvando no ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=todos_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"✅ Indexação concluída!")
    print(f"📊 Total de chunks: {len(todos_docs)}")
    print(f"📂 Biblioteca: {biblioteca}")
    
    return vectorstore
if __name__ == "__main__":
    indexar_documentos(pasta="documentos_teste", biblioteca="helena_pop")