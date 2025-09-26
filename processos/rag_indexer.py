# processos/rag_indexer.py - Sistema RAG para indexação de documentos

import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
import pypdf

class RAGIndexer:
    """Sistema de indexação e recuperação de documentos (RAG)"""
    
    def __init__(self, persist_directory="./processos/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Carregar ou criar vectorstore
        if os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = None
    
    def indexar_pdf(self, pdf_path: str, metadata: dict = None):
        """Indexa um PDF no sistema RAG"""
        try:
            # Extrair texto do PDF
            reader = pypdf.PdfReader(pdf_path)
            texto_completo = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    texto_completo += page_text + "\n"
            
            # Criar documento com metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'source': pdf_path,
                'filename': os.path.basename(pdf_path),
                'total_pages': len(reader.pages)
            })
            
            doc = Document(page_content=texto_completo, metadata=metadata)
            
            # Dividir em chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Indexar no vectorstore
            if self.vectorstore is None:
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
            else:
                self.vectorstore.add_documents(chunks)
            
            self.vectorstore.persist()
            
            return {
                'success': True,
                'chunks': len(chunks),
                'filename': metadata['filename']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def indexar_diretorio(self, diretorio: str, filtro_orgao: str = None):
        """Indexa todos os PDFs de um diretório"""
        resultados = []
        
        for root, dirs, files in os.walk(diretorio):
            for file in files:
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    
                    # Extrair metadata do nome do arquivo
                    metadata = self._extrair_metadata_nome(file)
                    
                    # Filtrar por órgão se especificado
                    if filtro_orgao and metadata.get('orgao') != filtro_orgao:
                        continue
                    
                    resultado = self.indexar_pdf(pdf_path, metadata)
                    resultados.append(resultado)
        
        return resultados
    
    def buscar_documentos(self, query: str, k: int = 3, filtro: dict = None):
        """Busca documentos relevantes usando RAG"""
        if self.vectorstore is None:
            return []
        
        try:
            # Busca por similaridade
            if filtro:
                docs = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=filtro
                )
            else:
                docs = self.vectorstore.similarity_search(query, k=k)
            
            return docs
            
        except Exception as e:
            print(f"Erro na busca RAG: {e}")
            return []
    
    def _extrair_metadata_nome(self, filename: str) -> dict:
        """Extrai metadata do nome do arquivo"""
        metadata = {'tipo': 'POP'}
        
        # Tentar identificar órgão no nome
        orgaos_conhecidos = ['MinFra', 'MGI', 'DECIPEX', 'COAUX', 'CGBEN']
        for orgao in orgaos_conhecidos:
            if orgao.lower() in filename.lower():
                metadata['orgao'] = orgao
                break
        
        # Tentar identificar código do processo
        import re
        codigo_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', filename)
        if codigo_match:
            metadata['codigo'] = codigo_match.group(1)
        
        return metadata
    
    def estatisticas(self):
        """Retorna estatísticas do sistema RAG"""
        if self.vectorstore is None:
            return {'total_documentos': 0}
        
        return {
            'status': 'ativo',
            'persist_directory': self.persist_directory
        }


class RAGHelper:
    """Helper para usar RAG com Helena"""
    
    def __init__(self):
        self.indexer = RAGIndexer()
    
    def buscar_contexto(self, pergunta: str, orgao: str = None) -> str:
        """Busca contexto relevante para a pergunta"""
        filtro = {'orgao': orgao} if orgao else None
        docs = self.indexer.buscar_documentos(pergunta, k=3, filtro=filtro)
        
        if not docs:
            return ""
        
        # Formatar contexto
        contexto = "DOCUMENTOS RELEVANTES ENCONTRADOS:\n\n"
        for i, doc in enumerate(docs, 1):
            contexto += f"[Documento {i}]\n"
            contexto += f"Fonte: {doc.metadata.get('filename', 'Desconhecido')}\n"
            contexto += f"Conteúdo: {doc.page_content[:500]}...\n\n"
        
        return contexto
    
    def indexar_pop_upload(self, pdf_file, orgao: str, codigo: str = None):
        """Indexa POP que foi feito upload"""
        import tempfile
        
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        
        # Indexar com metadata
        metadata = {
            'orgao': orgao,
            'tipo': 'POP',
            'codigo': codigo
        }
        
        resultado = self.indexer.indexar_pdf(tmp_path, metadata)
        
        # Limpar arquivo temporário
        os.unlink(tmp_path)
        
        return resultado