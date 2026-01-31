"""
RAG (Retrieval-Augmented Generation) module - answers questions using retrieved context
"""
import os
from typing import List, Optional
from app.config import settings
from app.schemas import Citation, RAGResponse
from app.semantic import get_search_engine


class RAGEngine:
    """Handles RAG-based question answering"""
    
    def __init__(self):
        self.search_engine = get_search_engine()
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available and configured"""
        if settings.llm_provider == "watsonx":
            return bool(settings.watsonx_api_key and settings.watsonx_project_id)
        elif settings.llm_provider == "openai":
            return bool(settings.openai_api_key)
        return False
    
    def _build_context(self, search_results: List) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Email {i}]\n"
                f"Subject: {result.subject}\n"
                f"Date: {result.date}\n"
                f"Content: {result.snippet}\n"
            )
        
        return "\n".join(context_parts)
    
    def _call_llm(self, question: str, context: str) -> str:
        """
        Call LLM to generate answer
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        prompt = f"""You are an AI assistant that answers questions based ONLY on the provided email context.

Context (Retrieved Emails):
{context}

Question: {question}

Instructions:
- Answer the question using ONLY information from the provided emails
- If the answer is not in the emails, say "I cannot find this information in the retrieved emails"
- Be concise and specific
- Reference which email(s) you used to answer

Answer:"""

        if settings.llm_provider == "watsonx" and self.llm_available:
            return self._call_watsonx(prompt)
        elif settings.llm_provider == "openai" and self.llm_available:
            return self._call_openai(prompt)
        else:
            # Fallback: return context summary
            return self._fallback_answer(question, context)
    
    def _call_watsonx(self, prompt: str) -> str:
        """Call IBM watsonx LLM"""
        try:
            from ibm_watsonx_ai.foundation_models import Model  # type: ignore[import-untyped]
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams  # type: ignore[import-untyped]
            
            # Validate credentials before attempting to create model
            if not settings.watsonx_api_key or settings.watsonx_api_key == "your_watsonx_api_key_here":
                raise ValueError("Invalid watsonx credentials")
            
            model = Model(
                model_id=settings.llm_model,
                params={
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: settings.llm_max_tokens,
                    GenParams.TEMPERATURE: settings.llm_temperature,
                },
                credentials={
                    "apikey": settings.watsonx_api_key,
                    "url": settings.watsonx_url
                },
                project_id=settings.watsonx_project_id
            )
            
            response = model.generate_text(prompt=prompt)
            return response
        
        except Exception as e:
            # Log the error but return informative message
            error_msg = str(e)
            if "400" in error_msg or "IAM Token" in error_msg:
                return "⚠️ watsonx credentials are invalid or expired. Using fallback mode with retrieved context only."
            return f"⚠️ watsonx LLM unavailable: {error_msg}. Using fallback mode."
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI LLM"""
        try:
            from openai import OpenAI  # type: ignore[import-untyped]
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on email context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    def _fallback_answer(self, question: str, context: str) -> str:
        """
        Fallback answer when LLM is not available
        Returns a summary of retrieved context
        """
        return (
            f"Based on the retrieved emails, here is the relevant information:\n\n"
            f"{context}\n\n"
            f"Note: LLM is not configured. Please set up watsonx or OpenAI credentials "
            f"for AI-generated answers. The above shows the raw retrieved context."
        )
    
    def answer_question(self, question: str, top_k: int = 5) -> RAGResponse:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            top_k: Number of emails to retrieve
            
        Returns:
            RAGResponse with answer and citations
        """
        # Perform semantic search
        search_results = self.search_engine.search(query=question, top_k=top_k)
        
        if not search_results:
            return RAGResponse(
                answer="I couldn't find any relevant emails to answer your question.",
                citations=[]
            )
        
        # Build context from search results
        context = self._build_context(search_results)
        
        # Generate answer using LLM
        answer = self._call_llm(question, context)
        
        # Create citations
        citations = [
            Citation(
                id=result.id,
                subject=result.subject,
                date=result.date,
                snippet=result.snippet
            )
            for result in search_results
        ]
        
        return RAGResponse(
            answer=answer,
            citations=citations
        )


# Global instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create the global RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine