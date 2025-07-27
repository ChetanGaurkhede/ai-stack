import chromadb
import fitz  # PyMuPDF
import os
import uuid
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.llm_service import LLMService
import structlog

logger = structlog.get_logger()


class KnowledgeBaseService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.llm_service = LLMService()
        self.collection_name = "documents"
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for AI Stack"}
            )
    
    async def process_document(self, file_path: str, document_id: int) -> Dict[str, Any]:
        """Process document and create embeddings"""
        try:
            # Extract text from document
            text_content = await self._extract_text(file_path)
            
            # Split text into chunks
            chunks = self._split_text(text_content)
            
            # Generate embeddings for chunks
            embeddings_data = await self._generate_chunk_embeddings(chunks, document_id)
            
            # Store in ChromaDB
            await self._store_embeddings(embeddings_data, document_id)
            
            return {
                "success": True,
                "document_id": document_id,
                "chunks_processed": len(chunks),
                "text_content": text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            }
            
        except Exception as e:
            logger.error("Document processing failed", error=str(e), document_id=document_id)
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return await self._extract_pdf_text(file_path)
        elif file_extension in ['.txt', '.md']:
            return await self._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error("PDF text extraction failed", error=str(e), file_path=file_path)
            raise
    
    async def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error("Text file extraction failed", error=str(e), file_path=file_path)
            raise
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def _generate_chunk_embeddings(self, chunks: List[str], document_id: int) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks"""
        embeddings_data = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding_result = await self.llm_service.generate_embeddings(
                    chunk, provider="openai"  # Default to OpenAI
                )
                
                embeddings_data.append({
                    "id": f"doc_{document_id}_chunk_{i}",
                    "text": chunk,
                    "embedding": embedding_result["embeddings"],
                    "metadata": {
                        "document_id": document_id,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "embedding_model": embedding_result["model"]
                    }
                })
                
            except Exception as e:
                logger.error("Chunk embedding generation failed", 
                           error=str(e), chunk_index=i, document_id=document_id)
                continue
        
        return embeddings_data
    
    async def _store_embeddings(self, embeddings_data: List[Dict[str, Any]], document_id: int):
        """Store embeddings in ChromaDB"""
        if not embeddings_data:
            return
        
        try:
            # Prepare data for ChromaDB
            ids = [item["id"] for item in embeddings_data]
            texts = [item["text"] for item in embeddings_data]
            embeddings = [item["embedding"] for item in embeddings_data]
            metadatas = [item["metadata"] for item in embeddings_data]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info("Embeddings stored successfully", 
                       document_id=document_id, chunks_count=len(embeddings_data))
            
        except Exception as e:
            logger.error("Failed to store embeddings", error=str(e), document_id=document_id)
            raise
    
    async def search_similar(self, query: str, document_id: Optional[int] = None, 
                           top_k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents/chunks"""
        try:
            # Generate query embedding
            query_embedding = await self.llm_service.generate_embeddings(query, provider="openai")
            
            # Prepare where filter
            where_filter = {}
            if document_id:
                where_filter["document_id"] = document_id
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding["embeddings"]],
                n_results=top_k,
                where=where_filter if where_filter else None
            )
            
            # Process results
            similar_chunks = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Convert distance to similarity score
                    similarity = 1 - distance
                    
                    if similarity >= threshold:
                        similar_chunks.append({
                            "text": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "rank": i + 1
                        })
            
            return similar_chunks
            
        except Exception as e:
            logger.error("Similarity search failed", error=str(e), query=query)
            raise
    
    async def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            chunks = []
            if results["documents"]:
                for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                    chunks.append({
                        "text": doc,
                        "metadata": metadata,
                        "index": i
                    })
            
            return chunks
            
        except Exception as e:
            logger.error("Failed to get document chunks", error=str(e), document_id=document_id)
            raise
    
    async def delete_document_embeddings(self, document_id: int) -> bool:
        """Delete all embeddings for a specific document"""
        try:
            # Get all IDs for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info("Document embeddings deleted", document_id=document_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to delete document embeddings", error=str(e), document_id=document_id)
            raise 