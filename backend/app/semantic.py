"""
Semantic search module - handles embeddings, vector storage, and semantic search
"""
import os
from typing import List, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.schemas import NormalizedMessage, SearchResult


class SemanticSearchEngine:
    """Handles semantic indexing and search using embeddings and vector DB"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and vector database"""
        # Initialize embedding model
        if settings.embedding_provider == "sentence-transformers":
            self.embedding_model = SentenceTransformer(settings.embedding_model)
        else:
            # Placeholder for other providers (watsonx, openai)
            self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize Chroma vector database
        # Telemetry is disabled via ANONYMIZED_TELEMETRY env var to prevent PostHog errors
        self.chroma_client = chromadb.PersistentClient(
            path=str(settings.vector_store_dir),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=settings.collection_name
            )
        except:
            self.collection = self.chroma_client.create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def index_messages(self, messages: List[NormalizedMessage]) -> Tuple[int, dict]:
        """
        Index messages into vector database
        
        Args:
            messages: List of normalized messages to index
            
        Returns:
            Tuple of (chunks_indexed, stats)
        """
        all_chunks = []
        all_ids = []
        all_metadatas = []
        
        for msg in messages:
            # Chunk the message text
            chunks = self._chunk_text(msg.text)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{msg.id}_chunk_{i}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadatas.append({
                    "email_id": msg.id,
                    "from": msg.metadata.from_,
                    "to": msg.metadata.to,
                    "subject": msg.metadata.subject,
                    "date": msg.metadata.date,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Store in vector database
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings.tolist(),
            documents=all_chunks,
            metadatas=all_metadatas
        )
        
        stats = {
            "messages_indexed": len(messages),
            "chunks_created": len(all_chunks),
            "avg_chunks_per_message": round(len(all_chunks) / len(messages), 2)
        }
        
        return len(all_chunks), stats
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Perform semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with scores
        """
        # Check collection size and adjust top_k if necessary
        collection_count = self.collection.count()
        actual_top_k = min(top_k, collection_count) if collection_count > 0 else 1
        
        if collection_count == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        )
        
        # Search vector database with adjusted top_k
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=actual_top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        search_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                document = results['documents'][0][i]
                distance = results['distances'][0][i]
                
                # Convert distance to similarity score (cosine similarity)
                # Chroma returns L2 distance for cosine space, convert to similarity
                score = 1 - distance
                
                search_results.append(
                    SearchResult(
                        id=metadata['email_id'],
                        subject=metadata['subject'],
                        date=metadata['date'],
                        score=round(score, 4),
                        snippet=document[:200] + "..." if len(document) > 200 else document
                    )
                )
        
        return search_results
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the indexed collection"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.collection_name,
                "embedding_model": settings.embedding_model
            }
        except Exception as e:
            return {"error": str(e)}
    
    def reset_collection(self):
        """Reset/clear the collection"""
        try:
            self.chroma_client.delete_collection(name=settings.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            return False


# Global instance
_search_engine: Optional[SemanticSearchEngine] = None


def get_search_engine() -> SemanticSearchEngine:
    """Get or create the global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearchEngine()
    return _search_engine